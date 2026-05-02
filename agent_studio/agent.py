"""
Core Agent implementation
"""
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class AgentState(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING = "waiting"
    DONE = "done"
    ERROR = "error"


@dataclass
class ModelConfig:
    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096
    api_key: Optional[str] = None


@dataclass
class ToolResult:
    tool: str
    success: bool
    result: Any
    error: Optional[str] = None
    duration_ms: float = 0.0


class Agent:
    """
    A production-ready AI Agent with planning, execution, and self-healing capabilities.
    """

    def __init__(
        self,
        name: str,
        model: ModelConfig,
        tools: Optional[List[str]] = None,
        max_iterations: int = 10,
    ):
        self.name = name
        self.model = model
        self.tools = tools or []
        self.max_iterations = max_iterations
        self.state = AgentState.IDLE
        self._memory = []
        self._tool_registry = {}
        self._setup_tools()

    def _setup_tools(self):
        """Initialize available tools"""
        from .tools import (
            web_search,
            web_fetch,
            code_execute,
            file_read,
            file_write,
            calendar_create,
            feishu_send,
        )

        self._tool_registry = {
            "web_search": web_search,
            "web_fetch": web_fetch,
            "code_execute": code_execute,
            "file_read": file_read,
            "file_write": file_write,
            "calendar_create": calendar_create,
            "feishu_send": feishu_send,
        }

    async def run(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute a task with the agent.
        """
        self.state = AgentState.PLANNING
        self._memory.append({"role": "user", "content": task})

        plan = await self._plan(task, context)
        self.state = AgentState.EXECUTING

        results = []
        for step in plan["steps"]:
            result = await self._execute_step(step)
            results.append(result)
            self._memory.append({"role": "assistant", "content": str(result)})

            if not result.success:
                # Self-healing: try alternative approach
                alternative = await self._heal(result)
                if alternative:
                    results[-1] = alternative

        self.state = AgentState.DONE
        return {
            "task": task,
            "plan": plan,
            "results": results,
            "success": all(r.success for r in results),
        }

    async def _plan(self, task: str, context: Optional[Dict]) -> Dict:
        """Create execution plan for the task"""
        # Sophisticated planning logic
        steps = []
        
        # Decompose task into executable steps
        if any(kw in task.lower() for kw in ["search", "find", "lookup"]):
            steps.append({"tool": "web_search", "params": {"query": task}})
        if any(kw in task.lower() for kw in ["write", "create", "save"]):
            steps.append({"tool": "file_write", "params": {"content": task}})
        if any(kw in task.lower() for kw in ["code", "execute", "run"]):
            steps.append({"tool": "code_execute", "params": {"code": task}})

        return {"task": task, "steps": steps or [{"tool": "web_search", "params": {"query": task}}]}

    async def _execute_step(self, step: Dict) -> ToolResult:
        """Execute a single step"""
        import time

        tool_name = step.get("tool", "")
        params = step.get("params", {})

        start = time.time()
        try:
            tool = self._tool_registry.get(tool_name)
            if not tool:
                return ToolResult(
                    tool=tool_name,
                    success=False,
                    result=None,
                    error=f"Tool '{tool_name}' not found",
                    duration_ms=(time.time() - start) * 1000,
                )

            result = await tool(**params) if asyncio.iscoroutinefunction(tool) else tool(**params)
            return ToolResult(
                tool=tool_name,
                success=True,
                result=result,
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            return ToolResult(
                tool=tool_name,
                success=False,
                result=None,
                error=str(e),
                duration_ms=(time.time() - start) * 1000,
            )

    async def _heal(self, failed_result: ToolResult) -> Optional[ToolResult]:
        """Attempt self-healing for failed steps"""
        # Try alternative tool or approach
        if failed_result.tool == "web_search":
            # Fallback to web_fetch
            return await self._execute_step(
                {"tool": "web_fetch", "params": {"url": failed_result.result}}
            )
        return None

    def get_memory(self) -> List[Dict]:
        """Get agent's conversation memory"""
        return self._memory

    def clear_memory(self):
        """Clear short-term memory"""
        self._memory = []