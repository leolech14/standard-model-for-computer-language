#!/usr/bin/env python3
"""
History Loader
==============
SMoC Role: Loader | Domain: Context

Loads and preprocesses Claude Code conversation history (JSONL) for
ingestion into Gemini long context or RAG systems.

Part of S3 (ACI subsystem).

Usage:
    from aci.history_loader import HistoryLoader, HistoryConfig

    config = HistoryConfig(
        selection_mode="recent",
        count=5,
        include_thinking=False
    )
    loader = HistoryLoader(config)

    # Get formatted content for Gemini
    content = loader.load_for_gemini()

    # Or get structured data for RAG
    chunks = loader.load_for_rag()
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Iterator, Literal
from datetime import datetime
import hashlib


# Default location for Claude Code history
DEFAULT_HISTORY_PATH = Path.home() / ".claude" / "projects"


@dataclass
class HistoryConfig:
    """Configuration for history loading."""

    # Selection mode
    selection_mode: Literal["recent", "specific", "all", "date_range"] = "recent"
    count: int = 5  # For "recent" mode
    session_ids: List[str] = field(default_factory=list)  # For "specific" mode
    start_date: Optional[str] = None  # For "date_range" mode (ISO format)
    end_date: Optional[str] = None

    # Project filter (converts path to Claude's format)
    project_path: str = "/Users/lech/PROJECTS_all/PROJECT_elements"

    # Content extraction
    extract_types: List[str] = field(default_factory=lambda: ["user", "assistant"])
    include_thinking: bool = False
    include_tool_calls: bool = False
    include_tool_results: bool = False

    # Processing limits
    max_tokens_per_session: int = 100000
    max_total_tokens: int = 1000000
    deduplication: bool = True

    # Output format
    output_format: Literal["conversation_turns", "raw_jsonl", "summary", "rag_chunks"] = "conversation_turns"


@dataclass
class ConversationTurn:
    """Single turn in a conversation."""
    session_id: str
    turn_index: int
    role: str  # user | assistant
    content: str
    thinking: Optional[str] = None
    timestamp: Optional[str] = None
    message_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "turn_index": self.turn_index,
            "role": self.role,
            "content": self.content,
            "thinking": self.thinking,
            "timestamp": self.timestamp,
            "message_id": self.message_id
        }


@dataclass
class SessionSummary:
    """Summary of a conversation session."""
    session_id: str
    file_path: str
    turn_count: int
    user_turns: int
    assistant_turns: int
    estimated_tokens: int
    first_message: Optional[str] = None
    last_modified: Optional[str] = None


class HistoryLoader:
    """Loads Claude Code conversation history."""

    def __init__(self, config: HistoryConfig):
        self.config = config
        self.history_dir = self._get_history_dir()
        self._seen_hashes: set = set()  # For deduplication

    def _get_history_dir(self) -> Path:
        """Get the history directory for the configured project."""
        # Claude Code uses path with dashes instead of slashes AND underscores
        project_key = self.config.project_path.replace("/", "-").replace("_", "-")
        return DEFAULT_HISTORY_PATH / project_key

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimate (4 chars per token)."""
        return len(text) // 4

    def _content_hash(self, content: str) -> str:
        """Generate hash for deduplication."""
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def list_sessions(self) -> List[SessionSummary]:
        """List all available sessions with metadata."""
        sessions = []

        if not self.history_dir.exists():
            return sessions

        for jsonl_file in sorted(self.history_dir.glob("*.jsonl"),
                                  key=lambda p: p.stat().st_mtime,
                                  reverse=True):
            session_id = jsonl_file.stem

            # Quick scan for stats
            turn_count = 0
            user_turns = 0
            assistant_turns = 0
            first_message = None
            total_chars = 0

            try:
                with open(jsonl_file) as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            msg_type = entry.get("type")

                            if msg_type == "user":
                                user_turns += 1
                                turn_count += 1
                                content = entry.get("message", {}).get("content", "")
                                if isinstance(content, str):
                                    total_chars += len(content)
                                    if first_message is None:
                                        first_message = content[:100]

                            elif msg_type == "assistant":
                                assistant_turns += 1
                                turn_count += 1
                                msg = entry.get("message", {})
                                content = msg.get("content", [])
                                if isinstance(content, list):
                                    for block in content:
                                        if isinstance(block, dict) and block.get("type") == "text":
                                            total_chars += len(block.get("text", ""))

                        except json.JSONDecodeError:
                            continue

            except Exception:
                continue

            sessions.append(SessionSummary(
                session_id=session_id,
                file_path=str(jsonl_file),
                turn_count=turn_count,
                user_turns=user_turns,
                assistant_turns=assistant_turns,
                estimated_tokens=total_chars // 4,
                first_message=first_message,
                last_modified=datetime.fromtimestamp(jsonl_file.stat().st_mtime).isoformat()
            ))

        return sessions

    def _select_sessions(self) -> List[Path]:
        """Select session files based on config."""
        if not self.history_dir.exists():
            return []

        all_files = sorted(
            self.history_dir.glob("*.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        if self.config.selection_mode == "recent":
            return all_files[:self.config.count]

        elif self.config.selection_mode == "specific":
            return [
                f for f in all_files
                if f.stem in self.config.session_ids
            ]

        elif self.config.selection_mode == "all":
            return all_files

        elif self.config.selection_mode == "date_range":
            selected = []
            start = datetime.fromisoformat(self.config.start_date) if self.config.start_date else None
            end = datetime.fromisoformat(self.config.end_date) if self.config.end_date else None

            for f in all_files:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if start and mtime < start:
                    continue
                if end and mtime > end:
                    continue
                selected.append(f)

            return selected

        return []

    def _parse_session(self, session_file: Path) -> Iterator[ConversationTurn]:
        """Parse a single session file into conversation turns."""
        session_id = session_file.stem
        turn_index = 0

        with open(session_file) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg_type = entry.get("type")

                # User message
                if msg_type == "user" and "user" in self.config.extract_types:
                    message = entry.get("message", {})
                    content = message.get("content", "")

                    if isinstance(content, str) and content.strip():
                        yield ConversationTurn(
                            session_id=session_id,
                            turn_index=turn_index,
                            role="user",
                            content=content,
                            message_id=entry.get("uuid"),
                            timestamp=entry.get("timestamp")
                        )
                        turn_index += 1

                # Assistant message
                elif msg_type == "assistant" and "assistant" in self.config.extract_types:
                    message = entry.get("message", {})
                    content_blocks = message.get("content", [])

                    text_parts = []
                    thinking_parts = []

                    if isinstance(content_blocks, list):
                        for block in content_blocks:
                            if isinstance(block, dict):
                                if block.get("type") == "text":
                                    text_parts.append(block.get("text", ""))
                                elif block.get("type") == "thinking" and self.config.include_thinking:
                                    thinking_parts.append(block.get("thinking", ""))

                    content = "\n".join(text_parts)
                    thinking = "\n".join(thinking_parts) if thinking_parts else None

                    if content.strip():
                        yield ConversationTurn(
                            session_id=session_id,
                            turn_index=turn_index,
                            role="assistant",
                            content=content,
                            thinking=thinking,
                            message_id=message.get("id"),
                            timestamp=entry.get("timestamp")
                        )
                        turn_index += 1

    def _should_include(self, turn: ConversationTurn) -> bool:
        """Check if turn should be included (deduplication)."""
        if not self.config.deduplication:
            return True

        content_hash = self._content_hash(turn.content)
        if content_hash in self._seen_hashes:
            return False

        self._seen_hashes.add(content_hash)
        return True

    def load_turns(self) -> List[ConversationTurn]:
        """Load all conversation turns from selected sessions."""
        turns = []
        total_tokens = 0

        for session_file in self._select_sessions():
            session_tokens = 0

            for turn in self._parse_session(session_file):
                if not self._should_include(turn):
                    continue

                turn_tokens = self._estimate_tokens(turn.content)

                # Check session limit
                if session_tokens + turn_tokens > self.config.max_tokens_per_session:
                    break

                # Check total limit
                if total_tokens + turn_tokens > self.config.max_total_tokens:
                    return turns

                turns.append(turn)
                session_tokens += turn_tokens
                total_tokens += turn_tokens

        return turns

    def load_for_gemini(self) -> str:
        """Format history for Gemini long context ingestion."""
        turns = self.load_turns()

        if self.config.output_format == "conversation_turns":
            lines = ["# Claude Code Conversation History\n"]
            current_session = None

            for turn in turns:
                if turn.session_id != current_session:
                    current_session = turn.session_id
                    lines.append(f"\n## Session: {current_session}\n")

                role_marker = "USER" if turn.role == "user" else "ASSISTANT"
                lines.append(f"\n### [{role_marker}]\n{turn.content}\n")

                if turn.thinking:
                    lines.append(f"\n<thinking>\n{turn.thinking}\n</thinking>\n")

            return "\n".join(lines)

        elif self.config.output_format == "raw_jsonl":
            return "\n".join(json.dumps(turn.to_dict()) for turn in turns)

        elif self.config.output_format == "summary":
            # Condensed format
            lines = ["# Session Summary\n"]
            sessions = {}

            for turn in turns:
                if turn.session_id not in sessions:
                    sessions[turn.session_id] = []
                sessions[turn.session_id].append(turn)

            for session_id, session_turns in sessions.items():
                lines.append(f"\n## {session_id}")
                lines.append(f"Turns: {len(session_turns)}")

                # First and last user messages
                user_turns = [t for t in session_turns if t.role == "user"]
                if user_turns:
                    lines.append(f"First topic: {user_turns[0].content[:200]}...")
                    if len(user_turns) > 1:
                        lines.append(f"Last topic: {user_turns[-1].content[:200]}...")

            return "\n".join(lines)

        return ""

    def load_for_rag(self) -> List[Dict[str, Any]]:
        """Format history as chunks for RAG indexing."""
        turns = self.load_turns()
        chunks = []

        # Group into conversation pairs (user + assistant)
        i = 0
        while i < len(turns):
            chunk = {
                "id": f"{turns[i].session_id}_{turns[i].turn_index}",
                "session_id": turns[i].session_id,
                "type": "conversation_chunk",
                "content": "",
                "metadata": {
                    "source": "claude_code_history",
                    "timestamp": turns[i].timestamp
                }
            }

            # Combine user question with assistant response
            if turns[i].role == "user":
                chunk["content"] = f"Q: {turns[i].content}\n"
                if i + 1 < len(turns) and turns[i + 1].role == "assistant":
                    chunk["content"] += f"A: {turns[i + 1].content}"
                    i += 2
                else:
                    i += 1
            else:
                chunk["content"] = f"A: {turns[i].content}"
                i += 1

            chunks.append(chunk)

        return chunks

    def stats(self) -> Dict[str, Any]:
        """Get statistics about available history."""
        sessions = self.list_sessions()

        return {
            "total_sessions": len(sessions),
            "total_turns": sum(s.turn_count for s in sessions),
            "total_estimated_tokens": sum(s.estimated_tokens for s in sessions),
            "history_dir": str(self.history_dir),
            "exists": self.history_dir.exists(),
            "most_recent": sessions[0].last_modified if sessions else None,
            "oldest": sessions[-1].last_modified if sessions else None
        }


def main():
    """Demo/test."""
    print("=== Claude Code History Loader ===\n")

    config = HistoryConfig(
        selection_mode="recent",
        count=3,
        include_thinking=False
    )

    loader = HistoryLoader(config)

    # Stats
    stats = loader.stats()
    print(f"History directory: {stats['history_dir']}")
    print(f"Exists: {stats['exists']}")
    print(f"Total sessions: {stats['total_sessions']}")
    print(f"Total turns: {stats['total_turns']}")
    print(f"Estimated tokens: {stats['total_estimated_tokens']:,}")

    # List recent sessions
    print("\n--- Recent Sessions ---")
    for session in loader.list_sessions()[:5]:
        print(f"  {session.session_id[:8]}... | {session.turn_count} turns | ~{session.estimated_tokens:,} tokens")
        if session.first_message:
            print(f"    First: {session.first_message[:60]}...")

    # Load sample
    print("\n--- Sample Load ---")
    turns = loader.load_turns()
    print(f"Loaded {len(turns)} turns")

    if turns:
        print(f"First turn: [{turns[0].role}] {turns[0].content[:100]}...")


if __name__ == "__main__":
    main()
