"""
Task planning engine
"""
from typing import List, Dict, Any, Optional
import re


class Planner:
    """
    Intelligent task decomposition and planning.
    Breaks complex tasks into executable steps.
    """

    def __init__(self, model: Optional[Any] = None):
        self.model = model

    async def decompose(self, task: str, context: Optional[Dict] = None) -> List[Dict]:
        """
        Decompose a complex task into actionable steps.
        """
        steps = []
        task_lower = task.lower()

        # Pattern-based decomposition
        if "search" in task_lower and "and" in task_lower:
            # Multi-part search tasks
            queries = self._extract_queries(task)
            for q in queries:
                steps.append({"tool": "web_search", "params": {"query": q}})
        elif "create" in task_lower and ("file" in task_lower or "document" in task_lower):
            steps.append({"tool": "file_write", "params": {"content": task}})
            steps.append({"tool": "file_read", "params": {"path": "output.txt"}})
        elif any(k in task_lower for k in ["schedule", "calendar", "meeting"]):
            steps.append({"tool": "calendar_create", "params": {"title": task}})
        elif "code" in task_lower or "execute" in task_lower:
            code = self._extract_code(task)
            steps.append({"tool": "code_execute", "params": {"code": code}})
        else:
            # Default: web search
            steps.append({"tool": "web_search", "params": {"query": task}})

        return steps

    def _extract_queries(self, task: str) -> List[str]:
        """Extract multiple search queries from task"""
        # Simple split by "and" or ","
        parts = re.split(r'\s+and\s+|,\s+', task)
        return [p.strip() for p in parts if p.strip()]

    def _extract_code(self, task: str) -> str:
        """Extract code from task description"""
        # Look for code blocks or descriptions
        match = re.search(r'```(.*?)```', task, re.DOTALL)
        if match:
            return match.group(1)
        return task

    async def validate_plan(self, steps: List[Dict]) -> bool:
        """Validate that a plan is executable"""
        required_fields = ["tool", "params"]
        return all(all(f in s for f in required_fields) for s in steps)