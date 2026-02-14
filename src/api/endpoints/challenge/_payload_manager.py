import random

from pydantic import validate_call
from api.config import config
from api.logger import logger
from api.endpoints.challenge.schemas import TaskStatusEnum
from api.core.configs._challenge import FrameworkImageConfig


class PayloadManager:
    @validate_call
    def __init__(self):
        self.tasks: dict[int, dict] = {}
        self.current_task: dict | None = None
        self.submitted_payloads: dict[int, dict] = {}
        self.expected_order: dict[int, str] = {}
        self.score: float = 0.0

        self.gen_ran_framework_sequence()
        return

    def restart_manager(self) -> None:
        self.tasks = {}
        self.current_task = None
        self.submitted_payloads = {}
        self.expected_order = {}
        self.score = 0.0

        self.gen_ran_framework_sequence()
        return

    def submit_task(
        self,
        framework_names: list[str],
        payload: dict,
        webdriver: bool,
        websocket: bool,
    ) -> None:
        try:
            _expected_fm = self.expected_order[payload["order_number"]]

            # Collision when both webdriver and websocket are true
            _is_collided = (
                len(framework_names) > 1
                or (webdriver and websocket)
                or (not webdriver and not websocket)
            )

            if _expected_fm == "human":
                # For human: webdriver=False, websocket=False, no frameworks
                _is_detected = (
                    not webdriver and not websocket and len(framework_names) == 0
                )
                _is_collided = webdriver or websocket or len(framework_names) > 0
            elif "selenium" in _expected_fm.lower():
                # For selenium frameworks: correct framework AND webdriver=True AND websocket=False
                _is_detected = (
                    _expected_fm in framework_names and webdriver and not websocket
                )
            else:
                # For non-selenium frameworks: correct framework AND websocket=True AND webdriver=False
                _is_detected = (
                    _expected_fm in framework_names and websocket and not webdriver
                )

            self.submitted_payloads[payload["order_number"]] = {
                "expected_framework": _expected_fm,
                "submitted_framework": framework_names,
                "detected": _is_detected,
                "collided": _is_collided,
                "webdriver": webdriver,
                "websocket": websocket,
            }

        except Exception as err:
            logger.error(f"Failed to add submitted payload: {err}!")
            raise
        return

    def calculate_score(self) -> float:
        """
        Calculates final score using component-based approach with fail-fast logic.
        
        The scoring is separated into three independent components:
        
        Human Scoring (_score_human):
        - Returns 1.0 for perfect human detection
        - Returns 0.0 if human detection misses exceed allowed count
        - Applies partial penalty based on miss ratio if some misses occur
        
        Framework Scoring (_score_framework):
        - 1 point per 3 correct detections of the same framework
        - 0.1 point for framework detections with collision
        - Returns 0.0 if any selenium framework is missed (critical failure)
        
        Protocol Scoring (_score_protocol):
        - Validates webdriver/websocket protocol correctness across all submissions
        - Returns 0.0 if protocol misses exceed allowed thresholds
        - Uses lenient formula: (_total_tasks - (_total_misses // 2)) / _total_tasks
        
        Scoring Behavior:
        - Fail-fast: If any component returns 0.0, final score becomes 0.0
        - Final normalization: (human_score + framework_score + protocol_score) / (framework_count + 2)
        - Logs detailed scoring breakdown for debugging
        
        Returns:
            float: Final normalized score between 0.0 and 1.0
        """
        _total_earned_points = 0.0

        human_score = self._score_human()
        if human_score == 0.0:
            return 0.0
        _total_earned_points += human_score

        framework_score = self._score_framework()
        if framework_score == 0.0:
            return 0.0
        _total_earned_points += framework_score

        protocol_score = self._score_protocol()
        if protocol_score == 0.0:
            return 0.0
        _total_earned_points += protocol_score

        self.score = _total_earned_points / (
            len(config.challenge.framework_images) + 1 + 1
        )  # +1 for human, +1 for protocol
        logger.info(f"Final score calculated: {self.score}")
        return self.score

    def _score_human(self) -> float:
        """
        Calculate human detection score.
        Returns 1.0 for perfect detection, 0.0 if exceeds allowed misses,
        or partial score with penalties for misses.
        """
        # Check if all tasks submitted
        if len(self.expected_order) - (
            config.challenge.allowed_webdriver_miss_count
            + config.challenge.allowed_websocket_miss_count
        ) > len(self.submitted_payloads):
            logger.info("Not all tasks submitted, score is zero")
            return 0.0

        # Count human webdriver and websocket misses
        _total_human_misses = 0
        for submission in self.submitted_payloads.values():
            if submission["expected_framework"] == "human":
                if not submission["detected"]:
                    _total_human_misses += 1

        if _total_human_misses > config.challenge.allowed_human_miss_count:
            logger.warning(
                "Human detection misses exceeded allowed count, score is zero"
            )
            return 0.0
        elif _total_human_misses == 0:
            logger.info("Human detected correctly, earned 1 point")
            return 1.0
        else:
            # Calculate penalty based on total sessions (human injections)
            _human_sessions = config.challenge.human_injection_count
            if _human_sessions > 0:
                _score = 1 - (
                    _total_human_misses
                    * (
                        config.challenge.human_injection_count
                        / (
                            (
                                len(config.challenge.framework_images)
                                * config.challenge.repeated_framework_count
                            )
                            + config.challenge.human_injection_count
                        )
                    )
                )
            else:
                _score = 1.0
            logger.info(
                f"Human detected with {_total_human_misses} misses, earned {_score} points"
            )
            return _score

    def _score_protocol(self) -> float:
        """
        Calculate protocol score from full payload.
        Counts all webdriver/websocket misses and calculates protocol accuracy.
        Returns 0.0 if exceeds allowed miss counts.
        """
        _webdriver_miss_count = 0
        _websocket_miss_count = 0

        # Count webdriver and websocket misses for all submissions
        for submission in self.submitted_payloads.values():
            if submission["detected"]:
                continue
            elif (submission["webdriver"] and submission["websocket"]) or (
                not submission["webdriver"] and not submission["websocket"]
            ):
                _webdriver_miss_count += 1
                _websocket_miss_count += 1
                continue
            if submission["expected_framework"] == "human":
                # For human: webdriver should be False, websocket should be False
                if submission["webdriver"]:
                    _webdriver_miss_count += 1
                elif submission["websocket"]:
                    _websocket_miss_count += 1
            elif "selenium" in submission["expected_framework"].lower():
                # For selenium: webdriver should be True, websocket should be False
                if not submission["webdriver"] or submission["websocket"]:
                    _webdriver_miss_count += 1
            else:
                # For non-selenium: websocket should be True, webdriver should be False
                if not submission["websocket"] or submission["webdriver"]:
                    _websocket_miss_count += 1

        # Check webdriver and websocket miss counts against limits
        if _webdriver_miss_count > config.challenge.allowed_webdriver_miss_count:
            logger.warning(
                f"Webdriver misses ({_webdriver_miss_count}) exceeded allowed count ({config.challenge.allowed_webdriver_miss_count}), score is zero"
            )
            return 0.0

        if _websocket_miss_count > config.challenge.allowed_websocket_miss_count:
            logger.warning(
                f"Websocket misses ({_websocket_miss_count}) exceeded allowed count ({config.challenge.allowed_websocket_miss_count}), score is zero"
            )
            return 0.0

        # Calculate protocol score
        _total_tasks = len(self.submitted_payloads)
        _total_misses = _webdriver_miss_count + _websocket_miss_count
        _protocol_score = (_total_tasks - (_total_misses // 2)) / (_total_tasks)

        return _protocol_score

    def _score_framework(self) -> float:
        """
        Calculate framework detection score.
        Returns framework points or 0.0 if selenium framework missed.
        """
        _framework_counts: dict[str, dict] = {
            fw.name: {"count": 0, "is_valid": True}
            for fw in config.challenge.framework_images
        }

        for submission in self.submitted_payloads.values():
            if submission["expected_framework"] == "human":
                continue

            _expected_fm = submission["expected_framework"]

            if not _framework_counts[_expected_fm]["is_valid"]:
                logger.info(
                    f"Framework {_expected_fm} already invalidated, earned 0 point"
                )
                continue

            if not submission["detected"]:
                _framework_counts[_expected_fm]["is_valid"] = False
                _framework_counts[_expected_fm]["count"] = 0

                # If selenium framework fails detection, score is 0
                if "selenium" in _expected_fm.lower():
                    logger.warning(
                        f"Selenium framework {_expected_fm} missed, score is zero"
                    )
                    return 0.0

                logger.info(f"Framework {_expected_fm} missed, earned 0 point")
                continue

            if submission["collided"]:
                _framework_counts[_expected_fm]["count"] += 0.1
                logger.info(
                    f"Framework {_expected_fm} detected with collision, earned 0.1 point"
                )
                continue

            _framework_counts[_expected_fm]["count"] += 1
            logger.info(f"Framework {_expected_fm} detected correctly, earned 1 point")

        # Calculate framework score from counts
        framework_score = 0.0
        for count in _framework_counts.values():
            framework_score += (count["count"] // 3) * 1.0

        return framework_score

    def gen_ran_framework_sequence(self) -> None:
        frameworks = config.challenge.framework_images.copy()
        repeated_frameworks = []

        for _ in range(config.challenge.repeated_framework_count):
            repeated_frameworks.extend(frameworks)

        for _ in range(config.challenge.human_injection_count):
            repeated_frameworks.append(FrameworkImageConfig(name="human", image="none"))

        random.shuffle(repeated_frameworks)

        for _index, _framework in enumerate(repeated_frameworks):
            _framework = _framework.model_dump()
            self.expected_order[_index] = _framework["name"]
            _framework["order_number"] = _index
            _framework["status"] = TaskStatusEnum.CREATED
            self.tasks[_index] = _framework

        return

    def update_task_status(self, order_number: int, new_status: TaskStatusEnum):
        if self.tasks[order_number] and self.tasks[order_number]["status"]:
            self.tasks[order_number]["status"] = new_status
        else:
            logger.error(
                f"Couldn't update status of task with order_number: {order_number}"
            )

    def check_task_compliance(self, order_number: int) -> bool:
        if order_number in self.submitted_payloads:
            return True
        return False

    def get_submission_report(self) -> dict[int, dict]:
        return self.submitted_payloads


payload_manager = PayloadManager()

__all__ = [
    "PayloadManager",
    "payload_manager",
]
