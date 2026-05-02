"""
Example usage of Agent Studio
"""
import asyncio
from agent_studio import Agent, ModelConfig


async def main():
    # Create an agent
    agent = Agent(
        name="DemoAssistant",
        model=ModelConfig(provider="openai", model="gpt-4"),
        tools=["web_search", "web_fetch", "code_execute", "file_read", "file_write"],
    )

    # Run a task
    print("Running task: Search for latest AI agent research...")
    result = await agent.run("Find the latest research papers on AI agents published this month")

    print(f"\n✅ Task completed!")
    print(f"Success: {result['success']}")
    print(f"Steps executed: {len(result['results'])}")

    for i, r in enumerate(result['results']):
        print(f"  Step {i+1}: {r.tool} - {'✓' if r.success else '✗'}")


if __name__ == "__main__":
    asyncio.run(main())