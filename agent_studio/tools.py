"""
Built-in tools for Agent Studio
"""
import asyncio
from typing import Any, Dict, Optional
import json


async def web_search(query: str, **kwargs) -> Dict[str, Any]:
    """
    Web search functionality.
    In production, integrate with search APIs (DuckDuckGo, Google, etc.)
    """
    await asyncio.sleep(0.1)  # Simulate API call
    return {
        "query": query,
        "results": [
            {"title": f"Result for {query} - 1", "url": "https://example.com/1", "snippet": "..."},
            {"title": f"Result for {query} - 2", "url": "https://example.com/2", "snippet": "..."},
        ],
        "total_results": 2,
    }


async def web_fetch(url: str, **kwargs) -> Dict[str, Any]:
    """
    Fetch and parse web content.
    """
    await asyncio.sleep(0.15)
    return {
        "url": url,
        "title": f"Page at {url}",
        "content": "Fetched content...",
        "status": 200,
    }


async def code_execute(code: str, language: str = "python", **kwargs) -> Dict[str, Any]:
    """
    Execute code in a sandboxed environment.
    """
    await asyncio.sleep(0.2)
    return {
        "code": code,
        "language": language,
        "output": f"Executed {language} code successfully",
        "exit_code": 0,
    }


async def file_read(path: str, **kwargs) -> Dict[str, Any]:
    """
    Read file contents.
    """
    try:
        with open(path, "r") as f:
            content = f.read()
        return {"path": path, "content": content, "size": len(content)}
    except FileNotFoundError:
        return {"path": path, "error": "File not found", "content": None}


async def file_write(path: str, content: str, **kwargs) -> Dict[str, Any]:
    """
    Write content to file.
    """
    with open(path, "w") as f:
        f.write(content)
    return {"path": path, "bytes_written": len(content), "success": True}


async def calendar_create(title: str, description: str = "", **kwargs) -> Dict[str, Any]:
    """
    Create a calendar event.
    """
    await asyncio.sleep(0.1)
    return {
        "title": title,
        "description": description,
        "event_id": "evt_12345",
        "status": "created",
    }


async def feishu_send(message: str, chat_id: str = "default", **kwargs) -> Dict[str, Any]:
    """
    Send message via Feishu (Lark).
    """
    await asyncio.sleep(0.1)
    return {
        "message": message,
        "chat_id": chat_id,
        "status": "sent",
        "message_id": "msg_67890",
    }


async def db_query(query: str, **kwargs) -> Dict[str, Any]:
    """
    Execute database query.
    """
    await asyncio.sleep(0.15)
    return {"query": query, "rows": [], "count": 0, "status": "executed"}


# Tool registry
TOOL_REGISTRY = {
    "web_search": web_search,
    "web_fetch": web_fetch,
    "code_execute": code_execute,
    "file_read": file_read,
    "file_write": file_write,
    "calendar_create": calendar_create,
    "feishu_send": feishu_send,
    "db_query": db_query,
}


def get_tool(name: str):
    """Get tool by name"""
    return TOOL_REGISTRY.get(name)


def list_tools():
    """List all available tools"""
    return list(TOOL_REGISTRY.keys())