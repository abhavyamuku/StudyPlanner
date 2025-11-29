# backend/study_planner/crew.py
import yaml
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
import logging

# Set up logging to console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
AGENTS_CFG_PATH = BASE_DIR / "config" / "agents.yaml"
TASKS_CFG_PATH = BASE_DIR / "config" / "tasks.yaml"

def load_yaml(path):
    """Load YAML file safely and raise error if empty or invalid"""
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        if not data:
            raise ValueError(f"YAML file is empty or invalid: {path}")
        return data

# Load configurations
try:
    AGENTS_CFG = load_yaml(AGENTS_CFG_PATH)
    TASKS_CFG = load_yaml(TASKS_CFG_PATH)
except Exception as e:
    logger.error(f"Error loading YAML configs: {e}")
    AGENTS_CFG = {}
    TASKS_CFG = {}

class StudyPlannerCrew:
    def __init__(self):
        self.agents = AGENTS_CFG
        self.tasks = TASKS_CFG

        if not self.agents or not self.tasks:
            logger.warning("Agents or tasks configuration is empty. Check your YAML files!")

    def _run_agent(self, agent_key, prompt, cfg):
        """Call LLM adapter safely"""
        from backend.llm_adapter import get_response
        if not cfg:
            return {"agent": agent_key, "raw": f"No config found for agent: {agent_key}"}
        try:
            out = get_response(prompt, model=cfg.get("model"), cfg=cfg)
        except Exception as e:
            out = f"Error generating response: {e}"
        return {"agent": agent_key, "raw": out}

    def run_plan(self, user_message, meta):
        cfg = self.agents.get("planner", {})
        description = self.tasks.get("plan", {}).get("description", "No task description found.")
        prompt = f"""Study Planner:
User input: {user_message}

Task: {description}

Output: Provide a personalized study plan with daily tasks, estimated durations, and priorities. Keep it concise and actionable.
"""
        return self._run_agent("planner", prompt, cfg)

    def run_scheduler(self, plan_output, meta):
        cfg = self.agents.get("scheduler", {})
        description = self.tasks.get("schedule", {}).get("description", "No task description found.")
        prompt = f"""Scheduler:
Plan: {plan_output['raw']}

Task: {description}

Output: Produce a 7-day schedule with time blocks (start-end times), durations, and priority labels. If details missing, make reasonable assumptions.
"""
        return self._run_agent("scheduler", prompt, cfg)

    def run_resources(self, plan_output, meta):
        cfg = self.agents.get("resources", {})
        description = self.tasks.get("resources", {}).get("description", "No task description found.")
        prompt = f"""Resources:
Plan: {plan_output['raw']}

Task: {description}

Output: Recommend 3 resources (title + short description + link if possible). Prefer free resources if available.
"""
        return self._run_agent("resources", prompt, cfg)

    def run_motivator(self, user_message, meta):
        cfg = self.agents.get("motivator", {})
        description = self.tasks.get("motivate", {}).get("description", "No task description found.")
        prompt = f"""Motivator:
User: {user_message}

Task: {description}

Output: A short motivational message (2-3 sentences) and 3 quick focus tips.
"""
        return self._run_agent("motivator", prompt, cfg)

    def run_session(self, user_message, user_id=None, location=None, consent_save=False):
        meta = {"user_id": user_id, "location": location}
        plan_out = self.run_plan(user_message, meta)
        schedule_out = self.run_scheduler(plan_out, meta)
        resources_out = self.run_resources(plan_out, meta)
        motivator_out = self.run_motivator(user_message, meta)
        return {
            "status": "ok",
            "planner": plan_out,
            "schedule": schedule_out,
            "resources": resources_out,
            "motivator": motivator_out
        }
