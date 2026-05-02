"""
Action execution engine
"""
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time


@dataclass
class ExecutionResult:
    step: int
    tool: str
    success: bool
    output: Any
    error: Optional[str] = None
    duration_ms: float = 0.0
    retries: int = 0


class Executor:
    """
    Executes planned steps with retry logic and error handling.
    """

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self._results: List[ExecutionResult] = []

    async def execute(
        self, steps: List[Dict], tool_registry: Dict[str, Any]
    ) -> List[ExecutionResult]:
        """
        Execute all steps with proper error handling.
        """
        results = []

        for i, step in enumerate(steps):
            result = await self._execute_with_retry(step, tool_registry)
            result.step = i
            results.append(result)
            self._results.append(result)

            # Stop on critical failure
            if not result.success and self._is_critical(result):
                break

        return results

    async def _execute_with_retry(
        self, step: Dict, tool_registry: Dict[str, Any]
    ) -> ExecutionResult:
        """Execute a step with retry logic"""
        tool_name = step.get("tool", "")
        params = step.get("params", {})
        start_time = time.time()

        for attempt in range(self.max_retries + 1):
            try:
                tool = tool_registry.get(tool_name)
                if not tool:
                    return ExecutionResult(
                        step=0,
                        tool=tool_name,
                        success=False,
                        output=None,
                        error=f"Unknown tool: {tool_name}",
                        duration_ms=(time.time() - start_time) * 1000,
                        retries=attempt,
                    )

                if asyncio.iscoroutinefunction(tool):
                    output = await tool(**params)
                else:
                    output = tool(**params)

                return ExecutionResult(
                    step=0,
                    tool=tool_name,
                    success=True,
                    output=output,
                    duration_ms=(time.time() - start_time) * 1000,
                    retries=attempt,
                )

            except Exception as e:
                if attempt < self.max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                    continue

                return ExecutionResult(
                    step=0,
                    tool=tool_name,
                    success=False,
                    output=None,
                    error=str(e),
                    duration_ms=(time.time() - start_time) * 1000,
                    retries=attempt,
                )

    def _is_critical(self, result: ExecutionResult) -> bool:
        """Determine if a failure is critical"""
        critical_errors = ["authentication", "authorization", "data_loss"]
        return any(err in str(result.error).lower() for err in critical_errors)

    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary"""
        return {
            "total_steps": len(self._results),
            "successful": sum(1 for r in self._results if r.success),
            "failed": sum(1 for r in self._results if not r.success),
            "total_retries": sum(r.retries for r in self._results),
        }