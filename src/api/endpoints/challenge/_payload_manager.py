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

    def submit_task(self, framework_names: list[str], payload: dict, automation: dict) -> None:
        try:
            _expected_fm = self.expected_order[payload["order_number"]]
            _is_detected = _expected_fm in framework_names and automation.get("detected", False)
            _is_collided = len(framework_names) > 1

            if _expected_fm == "human":
                _is_detected = True if len(framework_names) == 0 else False
                _is_collided = True if len(framework_names) > 0 else False

            self.submitted_payloads[payload["order_number"]] = {
                "expected_framework": _expected_fm,
                "submitted_framework": framework_names,
                "detected": _is_detected,
                "collided": _is_collided,
                "automation": automation.get("detected", False),
            }

        except Exception as err:
            logger.error(f"Failed to add submitted payload: {err}!")
            raise
        return

    def calculate_score(self) -> float:
        """
        calculates final score for a submission
        1. if script detect human as automation more then allowed -> score 0
        2. If detected human correctly -> 1 point, for each miss -> -0.1 point
        3. if detected framework 3 times correctly -> 1 point
        4. if detected framework but collided with another framework -> 0.1 point
        5. if detected framework but automation is true -> 0 point

        Final score = total points / framework count + 1 (for human)
        """

        #* Step 1 and 2
        _total_earned_points = 0.0
        _automation_miss_count = 0
        for submission in self.submitted_payloads.values():
            if submission["expected_framework"] == "human":
                if submission["automation"]:
                    _automation_miss_count += 1
                
        if _automation_miss_count > config.challenge.allowed_automation_miss_count:
            logger.warning("Exceeded allowed automation misses, score is zero")
            return 0.0
        elif _automation_miss_count == 0:
            _total_earned_points += 1.0  
            logger.info("Human detected correctly, earned 1 point")
        else:
            _total_earned_points += 1 - (_automation_miss_count * 0.1)
            logger.info(f"Human detected with { _automation_miss_count } misses, earned { _total_earned_points } points")

        _framework_counts: dict[str, dict] = {fw.name: {"count": 0,"is_valid": True} for fw in config.challenge.framework_images}

        for submission in self.submitted_payloads.values():
            
            if submission["expected_framework"] == "human":
                continue

            if not _framework_counts[submission["expected_framework"]]["is_valid"]:
                logger.info(f"Framework {submission['expected_framework']} already invalidated, earned 0 point")
                continue

            if not submission["detected"]:
                _framework_counts[submission["expected_framework"]]["is_valid"] = False
                logger.info(f"Framework {submission['expected_framework']} missed, earned 0 point")
                continue

            if submission["collided"]:
                _total_earned_points += 0.1
                logger.info(f"Framework {submission['expected_framework']} detected with collision, earned 0.1 point")
                continue

            _framework_counts[submission["expected_framework"]]["count"] += 1
            logger.info(f"Framework {submission['expected_framework']} detected correctly, earned 1 point")

        for _count in _framework_counts.values():
            _total_earned_points += (_count["count"] // 3) * 1.0
        
        self.score = _total_earned_points / (len(config.challenge.framework_images) + 1)
        
        return self.score

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
