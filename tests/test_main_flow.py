import subprocess
from unittest.mock import patch
import pytest
from challenges.ada_detection.controller import AADController
from redteam_core.validator.models import ComparisonLog


@patch("bittensor.logging")
def test_compare_outputs(
    mock_bt_logging,
    internal_services_health,
    mock_challenge_info,
    mock_miner_commits,
    mock_miner_output,
):
    """Test _compare_outputs method using internal services API."""
    if not internal_services_health:
        pytest.fail("Internal services not available at http://localhost:8000")
    controller = AADController(
        challenge_name="ada_detection_v1",
        challenge_info=mock_challenge_info,
        miner_commits=mock_miner_commits,
        reference_comparison_commits=[],
        seed_inputs=[],
    )
    comparison_result = controller._compare_outputs(
        miner_output=mock_miner_output, reference_output=mock_miner_output
    )
    assert comparison_result is not None


@patch("bittensor.logging")
def test_validate_miner_submission(
    mock_bt_logging,
    internal_services_health,
    mock_challenge_info,
    mock_miner_commits,
    mock_reference_commits,
):
    """Test _validate_miner_submission method using internal services API."""
    if not internal_services_health:
        pytest.fail("Internal services not available at http://localhost:8000")
    controller = AADController(
        challenge_name="ada_detection_v1",
        challenge_info=mock_challenge_info,
        miner_commits=mock_miner_commits,
        reference_comparison_commits=mock_reference_commits,
        seed_inputs=[],
    )
    miner_commit = mock_miner_commits[0]
    is_valid = controller._validate_miner_submission(miner_commit=miner_commit)
    assert isinstance(is_valid, bool)


@patch("bittensor.logging")
def test_compare_with_baseline(
    mock_bt_logging,
    internal_services_health,
    mock_challenge_info,
    mock_miner_commits,
    mock_reference_commits,
):
    """Test _compare_with_baseline method using internal services API."""
    if not internal_services_health:
        pytest.fail("Internal services not available at http://localhost:8000")
    controller = AADController(
        challenge_name="ada_detection_v1",
        challenge_info=mock_challenge_info,
        miner_commits=mock_miner_commits,
        reference_comparison_commits=mock_reference_commits,
        seed_inputs=[],
    )
    miner_commit = mock_miner_commits[0]
    miner_commit.comparison_logs = {}
    controller._compare_with_baseline(miner_commit=miner_commit)
    assert isinstance(miner_commit.comparison_logs, dict)
    if miner_commit.comparison_logs:
        for key, value in miner_commit.comparison_logs.items():
            assert key.startswith("baseline_")
            assert isinstance(value, list)


@patch("redteam_core.challenge_pool.docker_utils.run_container")
def test_score_miner_with_low_comparison(
    mock_run_container,
    challenge_container,
    mock_challenge_info,
    mock_miner_commits,
    mock_reference_commits,
    mock_challenge_inputs,
):
    """Test _score_miner_with_new_inputs when comparison score is LOW (scoring happens)."""
    result = subprocess.run(
        [
            "docker",
            "ps",
            "--filter",
            f"name={challenge_container}",
            "--format",
            "{{.Names}}",
        ],
        capture_output=True,
        text=True,
    )
    assert challenge_container in result.stdout
    controller = AADController(
        challenge_name="ada_detection_v1",
        challenge_info=mock_challenge_info,
        miner_commits=mock_miner_commits,
        reference_comparison_commits=mock_reference_commits,
        seed_inputs=[],
    )
    miner_commit = mock_miner_commits[0]
    mock_run_container.return_value = None
    miner_commit.comparison_logs = {
        "test_ref_1": [
            ComparisonLog(similarity_score=0.3, reason="Low similarity for testing")
        ]
    }
    controller._score_miner_with_new_inputs(
        miner_commit=miner_commit, challenge_inputs=mock_challenge_inputs
    )
    scoring_log = miner_commit.scoring_logs[0]
    assert scoring_log is not None
    assert hasattr(scoring_log, "score")
    assert scoring_log.score is not None
    assert isinstance(scoring_log.score, (int, float))
    if scoring_log.error:
        assert "Skipped scoring" not in scoring_log.error


@patch("redteam_core.challenge_pool.docker_utils.run_container")
def test_score_miner_with_high_comparison_score(
    mock_run_container,
    challenge_container,
    mock_challenge_info,
    mock_miner_commits,
    mock_reference_commits,
    mock_challenge_inputs,
):
    """Test _score_miner_with_new_inputs when comparison score is HIGH (scoring skipped)."""
    result = subprocess.run(
        [
            "docker",
            "ps",
            "--filter",
            f"name={challenge_container}",
            "--format",
            "{{.Names}}",
        ],
        capture_output=True,
        text=True,
    )
    assert challenge_container in result.stdout
    controller = AADController(
        challenge_name="ada_detection_v1",
        challenge_info=mock_challenge_info,
        miner_commits=mock_miner_commits,
        reference_comparison_commits=mock_reference_commits,
        seed_inputs=[],
    )
    miner_commit = mock_miner_commits[0]
    mock_run_container.return_value = None
    miner_commit.comparison_logs = {
        "test_ref_1": [
            ComparisonLog(similarity_score=0.8, reason="High similarity for testing")
        ]
    }
    controller._score_miner_with_new_inputs(
        miner_commit=miner_commit, challenge_inputs=mock_challenge_inputs
    )
    scoring_log = miner_commit.scoring_logs[0]
    assert scoring_log is not None
    assert hasattr(scoring_log, "score")
    assert scoring_log.score == 0.0
    assert scoring_log.error is not None
    assert "Skipped scoring due to high comparison score" in scoring_log.error
