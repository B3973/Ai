#!/usr/bin/env python3
"""A lightweight Ironman-style JARVIS/EDITH command assistant.

This assistant is intentionally safe: it supports local commands, a memory file,
and optional OpenAI-powered responses when OPENAI_API_KEY is configured.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

MEMORY_FILE = Path("assistant_memory.json")


@dataclass
class MemoryItem:
    timestamp: str
    type: str
    content: str


class JarvisEdithAI:
    def __init__(self) -> None:
        self.memory: List[MemoryItem] = self._load_memory()

    def _load_memory(self) -> List[MemoryItem]:
        if not MEMORY_FILE.exists():
            return []
        try:
            raw = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
            return [MemoryItem(**item) for item in raw]
        except Exception:
            return []

    def _save_memory(self) -> None:
        MEMORY_FILE.write_text(
            json.dumps([asdict(item) for item in self.memory], indent=2),
            encoding="utf-8",
        )

    def remember(self, text: str) -> str:
        item = MemoryItem(
            timestamp=datetime.now(timezone.utc).isoformat(),
            type="note",
            content=text,
        )
        self.memory.append(item)
        self._save_memory()
        return "Stored in memory, boss."

    def recall(self) -> str:
        if not self.memory:
            return "Memory is currently empty."
        recent = self.memory[-5:]
        lines = [f"- [{m.timestamp}] {m.content}" for m in recent]
        return "Recent memory:\n" + "\n".join(lines)

    def system_status(self) -> str:
        cwd = Path.cwd()
        files = len(list(cwd.iterdir()))
        return (
            "System status:\n"
            f"- Time (UTC): {datetime.now(timezone.utc).isoformat()}\n"
            f"- Working directory: {cwd}\n"
            f"- Items in directory: {files}"
        )

    def run_local_command(self, command: str) -> str:
        blocked = ["rm ", "sudo", "shutdown", "reboot", "mkfs", "dd "]
        if any(token in command for token in blocked):
            return "Command blocked for safety."
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=False,
                capture_output=True,
                text=True,
                timeout=20,
            )
            output = (result.stdout or result.stderr).strip()
            if not output:
                output = "Command completed with no output."
            return f"Exit code {result.returncode}:\n{output[:3000]}"
        except Exception as exc:
            return f"Command failed: {exc}"

    def ask_openai(self, prompt: str) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return (
                "OPENAI_API_KEY is not configured. "
                "Use local commands or set your key for AI responses."
            )

        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            response = client.responses.create(
                model="gpt-5.3-codex",
                input=[
                    {
                        "role": "system",
                        "content": "You are JARVIS/EDITH: concise, tactical, and helpful.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            return response.output_text.strip() or "No response text returned."
        except Exception as exc:
            return f"AI request failed: {exc}"

    def handle(self, text: str) -> str:
        command = text.strip()
        low = command.lower()

        if low in {"exit", "quit", "goodbye"}:
            return "Goodbye, boss."
        if low.startswith("remember "):
            return self.remember(command[9:].strip())
        if low in {"recall", "memory"}:
            return self.recall()
        if low in {"status", "system status"}:
            return self.system_status()
        if low.startswith("run "):
            return self.run_local_command(command[4:].strip())
        if low.startswith("ask "):
            return self.ask_openai(command[4:].strip())

        return (
            "Unknown command. Try: status, remember <note>, recall, run <cmd>, "
            "ask <question>, exit"
        )


def main() -> None:
    assistant = JarvisEdithAI()
    print("JARVIS/EDITH online. Type commands (status, remember, recall, run, ask, exit).")
    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye, boss.")
            break

        if not user_input:
            continue

        reply = assistant.handle(user_input)
        print(f"ai> {reply}")
        if reply == "Goodbye, boss.":
            break


if __name__ == "__main__":
    main()
