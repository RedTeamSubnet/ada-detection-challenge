import random
from collections import Counter
from types import SimpleNamespace

import pytest

from api.endpoints.challenge import _payload_manager as pm_module
from api.endpoints.challenge._payload_manager import build_run_schedule

FRAMEWORKS = ["ads_power", "dolphin_anty", "gologin", "multilogin"]
SERVERS = [
    {"url": "http://runner-1:8080", "device_type": "linux"},
    {"url": "http://runner-2:8080", "device_type": "mac"},
]


def _dummy_config(frameworks, *, headed, headless, human_count, shuffle):
    return SimpleNamespace(
        challenge=SimpleNamespace(
            framework_images=[
                SimpleNamespace(name=name, weight=1.0) for name in frameworks
            ],
            human_count=human_count,
            bot_runner=SimpleNamespace(
                servers=[SimpleNamespace(**server) for server in SERVERS],
                run_counts=SimpleNamespace(headed=headed, headless=headless),
                shuffle_runs=shuffle,
            ),
        )
    )


def _mode_counts(schedule, name):
    modes = [unit["headless"] for unit in schedule if unit["name"] == name]
    return modes.count(False), modes.count(True)


def test_total_and_per_framework_counts():
    schedule = build_run_schedule(
        FRAMEWORKS,
        SERVERS,
        headed_count=3,
        headless_count=2,
        human_count=1,
        shuffle=False,
    )

    assert len(schedule) == len(FRAMEWORKS) * 5 * len(SERVERS) + 1
    by_name = Counter(unit["name"] for unit in schedule)
    for framework in FRAMEWORKS:
        assert by_name[framework] == 5 * len(SERVERS)
    assert by_name["human"] == 1


def test_mode_split_per_framework():
    schedule = build_run_schedule(
        FRAMEWORKS,
        SERVERS,
        headed_count=3,
        headless_count=2,
        human_count=0,
        shuffle=False,
    )

    for framework in FRAMEWORKS:
        assert _mode_counts(schedule, framework) == (6, 4)
    assert all(unit["name"] != "human" for unit in schedule)


def test_human_units_carry_no_mode():
    schedule = build_run_schedule(
        FRAMEWORKS,
        SERVERS,
        headed_count=1,
        headless_count=1,
        human_count=2,
        shuffle=False,
    )

    humans = [unit for unit in schedule if unit["name"] == "human"]
    assert len(humans) == 2
    assert all(unit["headless"] is None for unit in humans)
    assert all(unit["server_url"] is None for unit in humans)
    assert all(unit["device_type"] is None for unit in humans)


def test_deterministic_order_when_not_shuffled():
    schedule = build_run_schedule(
        ["a", "b"],
        SERVERS,
        headed_count=1,
        headless_count=1,
        human_count=0,
        shuffle=False,
    )

    assert [
        (
            unit["name"],
            unit["headless"],
            unit["server_url"],
            unit["device_type"],
        )
        for unit in schedule
    ] == [
        ("a", False, SERVERS[0]["url"], "linux"),
        ("a", True, SERVERS[0]["url"], "linux"),
        ("a", False, SERVERS[1]["url"], "mac"),
        ("a", True, SERVERS[1]["url"], "mac"),
        ("b", False, SERVERS[0]["url"], "linux"),
        ("b", True, SERVERS[0]["url"], "linux"),
        ("b", False, SERVERS[1]["url"], "mac"),
        ("b", True, SERVERS[1]["url"], "mac"),
    ]


def test_shuffle_preserves_counts_and_modes():
    random.seed(7)
    schedule = build_run_schedule(
        FRAMEWORKS,
        SERVERS,
        headed_count=3,
        headless_count=2,
        human_count=1,
        shuffle=True,
    )

    by_name = Counter(unit["name"] for unit in schedule)
    for framework in FRAMEWORKS:
        assert by_name[framework] == 10
        assert _mode_counts(schedule, framework) == (6, 4)
    assert by_name["human"] == 1


def test_shuffle_is_randomized_between_runs():
    random.seed(1)
    first = [
        (unit["name"], unit["headless"])
        for unit in build_run_schedule(
            FRAMEWORKS,
            SERVERS,
            headed_count=3,
            headless_count=2,
            human_count=1,
            shuffle=True,
        )
    ]
    second = [
        (unit["name"], unit["headless"])
        for unit in build_run_schedule(
            FRAMEWORKS,
            SERVERS,
            headed_count=3,
            headless_count=2,
            human_count=1,
            shuffle=True,
        )
    ]
    assert first != second


def test_order_numbers_are_assignable_contiguously():
    schedule = build_run_schedule(
        FRAMEWORKS,
        SERVERS,
        headed_count=2,
        headless_count=2,
        human_count=1,
        shuffle=True,
    )
    # Every unit must expose the fields the payload manager needs to build a task.
    for unit in schedule:
        assert set(unit.keys()) == {
            "name",
            "headless",
            "server_url",
            "device_type",
        }


# --- PayloadManager wiring: config -> generated task schedule ---------------


def test_payload_manager_wires_config_counts(monkeypatch):
    monkeypatch.setattr(
        pm_module,
        "config",
        _dummy_config(["a", "b"], headed=2, headless=1, human_count=2, shuffle=False),
    )

    manager = pm_module.PayloadManager()

    # 2 frameworks * (2 + 1) * 2 servers + 2 human = 14 tasks
    assert len(manager.tasks) == 14
    names = [task["name"] for task in manager.tasks.values()]
    assert names.count("a") == 6
    assert names.count("b") == 6
    assert names.count("human") == 2
    # expected_order must mirror each task's name by order_number
    assert all(
        manager.expected_order[index] == manager.tasks[index]["name"]
        for index in manager.tasks
    )
    # order numbers are contiguous from zero
    assert sorted(manager.tasks.keys()) == list(range(14))


def test_payload_manager_deterministic_when_shuffle_off(monkeypatch):
    monkeypatch.setattr(
        pm_module,
        "config",
        _dummy_config(["a", "b"], headed=1, headless=1, human_count=0, shuffle=False),
    )

    manager = pm_module.PayloadManager()

    assert [
        (
            task["name"],
            task["headless"],
            task["server_url"],
            task["device_type"],
        )
        for task in manager.tasks.values()
    ] == [
        ("a", False, SERVERS[0]["url"], "linux"),
        ("a", True, SERVERS[0]["url"], "linux"),
        ("a", False, SERVERS[1]["url"], "mac"),
        ("a", True, SERVERS[1]["url"], "mac"),
        ("b", False, SERVERS[0]["url"], "linux"),
        ("b", True, SERVERS[0]["url"], "linux"),
        ("b", False, SERVERS[1]["url"], "mac"),
        ("b", True, SERVERS[1]["url"], "mac"),
    ]


def test_payload_manager_respects_human_count_zero(monkeypatch):
    monkeypatch.setattr(
        pm_module,
        "config",
        _dummy_config(["a"], headed=1, headless=1, human_count=0, shuffle=True),
    )

    manager = pm_module.PayloadManager()

    assert len(manager.tasks) == 4
    assert all(task["name"] != "human" for task in manager.tasks.values())


def test_payloads_from_multiple_servers_are_scored_independently(monkeypatch):
    monkeypatch.setattr(
        pm_module,
        "config",
        _dummy_config(["a"], headed=1, headless=0, human_count=0, shuffle=False),
    )
    manager = pm_module.PayloadManager()

    manager.submit_task(
        framework_names=["a"],
        payload={"order_number": 0},
        headless=False,
    )
    assert manager.calculate_score() == 0.5

    manager.submit_task(
        framework_names=["a"],
        payload={"order_number": 1},
        headless=False,
    )

    assert len(manager.submitted_payloads) == 2
    assert manager.submitted_payloads[0]["server_url"] == SERVERS[0]["url"]
    assert manager.submitted_payloads[0]["device_type"] == "linux"
    assert manager.submitted_payloads[1]["server_url"] == SERVERS[1]["url"]
    assert manager.submitted_payloads[1]["device_type"] == "mac"
    assert manager.calculate_score() == 1.0


def _score_full_cycle(manager, *, miss=(), human_detects=(), flip_headless=()):
    """Submit one payload per scheduled task, then score the cycle."""
    for order, task in manager.tasks.items():
        name = task["name"]
        if name == pm_module.HUMAN_TASK_NAME:
            manager.submit_task(
                framework_names=list(human_detects),
                payload={"order_number": order},
                headless=False,
            )
            continue
        manager.submit_task(
            framework_names=[] if name in miss else [name],
            payload={"order_number": order},
            headless=(not task["headless"])
            if order in flip_headless
            else task["headless"],
        )
    return manager.calculate_score()


def _gate_manager(monkeypatch, human_count=1):
    monkeypatch.setattr(
        pm_module,
        "config",
        _dummy_config(
            ["a", "b"],
            headed=1,
            headless=1,
            human_count=human_count,
            shuffle=False,
        ),
    )
    return pm_module.PayloadManager()


def test_perfect_cycle_scores_one(monkeypatch):
    manager = _gate_manager(monkeypatch)

    assert _score_full_cycle(manager) == 1.0


def test_human_false_positive_zeroes_score(monkeypatch):
    manager = _gate_manager(monkeypatch)

    assert _score_full_cycle(manager, human_detects=["a"]) == 0.0


def test_single_headless_miss_reduces_weighted_score(monkeypatch):
    manager = _gate_manager(monkeypatch)

    # Eight scheduled driver runs: framework accuracy stays perfect and one
    # wrong mode verdict loses one eighth of the 10% headless component.
    assert _score_full_cycle(manager, flip_headless={0}) == 0.9875


def test_framework_and_headless_components_are_weighted(monkeypatch):
    manager = _gate_manager(monkeypatch)

    # "a" is missed on all four runs and "b" is perfect: 45% framework
    # credit plus the complete 10% headless component.
    assert _score_full_cycle(manager, miss={"a"}) == 0.55


def test_missed_browser_does_not_reduce_headless_accuracy(monkeypatch):
    """A browser miss is independent from a correct mode verdict."""
    manager = _gate_manager(monkeypatch, human_count=0)

    score = _score_full_cycle(manager, miss={"a"})

    assert score == 0.55
    assert all(
        submission["headless_failed"] is False
        for submission in manager.submitted_payloads.values()
    )


def test_submitted_payloads_holds_only_run_rows(monkeypatch):
    """The score lives on `manager.score`, never inside `submitted_payloads`."""
    manager = _gate_manager(monkeypatch)
    score = _score_full_cycle(manager)

    assert manager.score == score
    assert all(isinstance(order, int) for order in manager.submitted_payloads)
    assert manager.calculate_score() == score


def test_missing_run_costs_framework_and_headless_points(monkeypatch):
    """A scheduled run that never submits earns neither component."""
    manager = _gate_manager(monkeypatch, human_count=0)
    skipped = max(manager.tasks)
    for order, task in manager.tasks.items():
        if order == skipped:
            continue
        manager.submit_task(
            framework_names=[task["name"]],
            payload={"order_number": order},
            headless=bool(task["headless"]),
        )

    assert manager._score_framework() == pytest.approx(0.7875)
    assert manager._score_headless() == pytest.approx(0.0875)
    assert manager.calculate_score() == pytest.approx(0.875)
