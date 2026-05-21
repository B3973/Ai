# Ironman-Style JARVIS / EDITH AI

A lightweight command-line assistant inspired by JARVIS/EDITH.

## Features
- **System status** (`status`)
- **Persistent memory** (`remember <note>`, `recall`)
- **Local command execution** with basic safety filters (`run <command>`)
- **Optional OpenAI responses** (`ask <question>`) when `OPENAI_API_KEY` is set

## Quick Start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 jarvis_edith_ai.py
```

## Commands
- `status`
- `remember Build Mark-42 diagnostics`
- `recall`
- `run pwd`
- `ask Create a mission briefing`
- `exit`

## Notes
- If `OPENAI_API_KEY` is missing, the assistant still works in local mode.
- Memory is stored in `assistant_memory.json`.
