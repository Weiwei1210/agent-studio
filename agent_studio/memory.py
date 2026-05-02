"""
Memory management module
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json


@dataclass
class MemoryEntry:
    timestamp: datetime
    role: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ShortTermMemory:
    """
    Ephemeral in-memory storage for current conversation context.
    Limited capacity with LRU eviction.
    """

    def __init__(self, max_entries: int = 100):
        self.max_entries = max_entries
        self._entries: List[MemoryEntry] = []

    def add(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add entry to memory"""
        self._entries.append(
            MemoryEntry(
                timestamp=datetime.now(), role=role, content=content, metadata=metadata or {}
            )
        )
        self._evict_if_needed()

    def _evict_if_needed(self):
        """Evict oldest entries if over capacity"""
        while len(self._entries) > self.max_entries:
            self._entries.pop(0)

    def get_recent(self, n: int = 10) -> List[MemoryEntry]:
        """Get n most recent entries"""
        return self._entries[-n:]

    def search(self, query: str) -> List[MemoryEntry]:
        """Search memory for query string"""
        return [e for e in self._entries if query.lower() in e.content.lower()]

    def clear(self):
        """Clear all entries"""
        self._entries = []


class LongTermMemory:
    """
    Persistent storage using file-based backend.
    Stores important memories with retrieval.
    """

    def __init__(self, storage_path: str = "~/.agent_studio/memory.json"):
        import os

        self.storage_path = os.path.expanduser(storage_path)
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self._memory: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load memory from disk"""
        try:
            with open(self.storage_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"entries": [], "tags": {}}

    def _save(self):
        """Persist memory to disk"""
        with open(self.storage_path, "w") as f:
            json.dump(self._memory, f, indent=2, default=str)

    def store(self, key: str, value: Any, tags: Optional[List[str]] = None):
        """Store a memory entry"""
        self._memory["entries"].append(
            {
                "key": key,
                "value": value,
                "tags": tags or [],
                "timestamp": datetime.now().isoformat(),
            }
        )
        for tag in tags or []:
            if tag not in self._memory["tags"]:
                self._memory["tags"][tag] = []
            self._memory["tags"][tag].append(key)
        self._save()

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a specific memory"""
        for entry in self._memory["entries"]:
            if entry["key"] == key:
                return entry["value"]
        return None

    def search_by_tag(self, tag: str) -> List[Any]:
        """Search memories by tag"""
        keys = self._memory["tags"].get(tag, [])
        return [self.retrieve(k) for k in keys]

    def get_all(self) -> List[Dict]:
        """Get all memories"""
        return self._memory["entries"]


class PersistentMemory:
    """
    User preferences and persistent settings.
    """

    def __init__(self, user_id: str, storage_path: str = "~/.agent_studio/preferences"):
        import os

        self.user_id = user_id
        self.storage_path = os.path.expanduser(f"{storage_path}/{user_id}.json")
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self._prefs = self._load()

    def _load(self) -> Dict[str, Any]:
        try:
            with open(self.storage_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save(self):
        with open(self.storage_path, "w") as f:
            json.dump(self._prefs, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self._prefs.get(key, default)

    def set(self, key: str, value: Any):
        self._prefs[key] = value
        self._save()

    def delete(self, key: str):
        if key in self._prefs:
            del self._prefs[key]
            self._save()