# Local Agentic CLI with Memory

A fully local AI-powered CLI tool that understands natural language, reads and modifies code files, maintains conversational context, and recalls past interactions using vector memory. Built on a **daemon + thin client** architecture for instant response times. Runs entirely offline using local LLMs via Ollama.

---

## Features

- **Instant Commands** — background daemon keeps everything warm; no cold-start on every call
- **Natural Language Commands** — talk to your codebase in plain English
- **Code Understanding & Editing** — read, analyze, and modify files based on instructions
- **Multi-Agent Workflow** — planner, executor, and validator agents collaborate on tasks
- **Short-Term Memory** — session-based context for ongoing conversations
- **Long-Term Memory (FAISS)** — vector-stored summaries with similarity search for recall
- **Diff & Safety Layer** — preview changes before applying, with dry-run support
- **Multi-File Context** — automatically identifies and loads related files
- **Streaming Output** — LLM responses stream token-by-token to your terminal

---

## Architecture

The project is split into two components that live in the same repo:

```
┌──────────────────────────────────────────────────────────────────┐
│  You type: agent edit auth.py "add logging"                      │
└──────────────┬───────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────┐       HTTP (localhost:9800)
│     Agent-Client         │  ──────────────────────────┐
│                          │                            │
│  Typer CLI (thin client) │                            ▼
│  Parses args, sends      │            ┌───────────────────────────────┐
│  request, renders output │            │       Agent-Server            │
└──────────────────────────┘            │       (Background Daemon)     │
               ▲                        │                               │
               │                        │  FastAPI + Uvicorn            │
               │  streamed response     │                               │
               └────────────────────────│  ┌─────────────────────────┐  │
                                        │  │  Agent Workflow          │  │
                                        │  │  (LangGraph)            │  │
                                        │  │                         │  │
                                        │  │  Planner → Executor     │  │
                                        │  │            → Validator   │  │
                                        │  └─────────────────────────┘  │
                                        │                               │
                                        │  ┌───────────┐ ┌───────────┐ │
                                        │  │  Memory    │ │  Tools    │ │
                                        │  │  FAISS +   │ │  File I/O │ │
                                        │  │  Session   │ │  Diff     │ │
                                        │  └───────────┘ └───────────┘ │
                                        │                               │
                                        │  Ollama (llama3, local)       │
                                        └───────────────────────────────┘
```

**Why this split?** Loading LangChain, FAISS, connecting to Ollama, and initializing agents takes 3-5 seconds. The daemon does this once on startup and keeps everything in memory. The thin client is just a few lines of code — it starts in milliseconds, sends your command to the daemon, and streams the response back to your terminal.

---

## Prerequisites

- **Python 3.10+**
- **Ollama** installed and running — [install guide](https://ollama.com/download)

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/local-agentic-cli.git
cd local-agentic-cli
```

### 2. Pull a local model

```bash
ollama pull llama3
```

### 3. Install

```bash
pip install -e .
```

This registers the `agent` command globally via a console entry point. No need to call `python` directly ever again.

### 4. Start using it

```bash
agent ask "hello, are you running?"
```

On first run, the daemon auto-starts in the background. Every subsequent command is instant.

---

## Project Structure

```
local-agentic-cli/
│
├── Agent-Client/                  # Thin CLI client
│   ├── __init__.py
│   ├── cli.py                     # Typer app — command definitions
│   ├── client.py                  # HTTP client — talks to the daemon
│   └── renderer.py                # Rich-based terminal output & diff display
│
├── Agent-Server/                  # Background daemon
│   ├── __init__.py
│   ├── daemon.py                  # FastAPI app + Uvicorn runner
│   ├── router.py                  # API routes: /edit, /ask, /history, /health
│   ├── lifecycle.py               # Start, stop, restart, PID management
│   │
│   ├── agents/                    # Multi-agent workflow
│   │   ├── __init__.py
│   │   ├── planner.py             # Intent parsing & action planning
│   │   ├── executor.py            # Code generation & modification
│   │   ├── validator.py           # Output verification & quality checks
│   │   └── workflow.py            # LangGraph state graph wiring
│   │
│   ├── memory/                    # Memory system
│   │   ├── __init__.py
│   │   ├── short_term.py          # Session buffer (last N interactions)
│   │   └── long_term.py           # FAISS vector store for persistent recall
│   │
│   └── tools/                     # Tool system
│       ├── __init__.py
│       ├── file_ops.py            # File read/write operations
│       ├── diff.py                # Diff generation
│       └── context_loader.py      # Multi-file context assembly
│
├── config.py                      # Shared configuration
├── setup.py                       # Package setup & entry point registration
├── requirements.txt
└── README.md
```

---

## How to Use

### Daemon Management

The daemon auto-starts when you run your first command. You can also manage it manually:

```bash
agent start                  # start the daemon in background
agent stop                   # shut down the daemon
agent restart                # restart with fresh state
agent status                 # check if daemon is alive and view uptime
```

---

### `edit` — Modify Code with Natural Language

Tell the agent what to change in plain English. It reads the file, plans the edits, and shows you a diff before writing anything.

```bash
# Single-file edit
agent edit auth.py "add logging to all functions"

# Targeted fix
agent edit utils/db.py "handle the case where connection is None"

# Refactoring
agent edit models/user.py "rename the class from UserModel to User and update all references"
```

**What happens behind the scenes:**

1. Client sends `{file, instruction}` to daemon
2. Planner Agent reads the file and interprets your instruction
3. Executor Agent generates the code changes
4. Validator Agent checks the output for correctness
5. Daemon streams the **diff preview** back to the client
6. Client displays it with Rich formatting and asks for confirmation
7. On confirm, client sends approval → daemon writes the file

---

### `ask` — Ask Questions About Your Code or Past Work

Query your codebase or recall what you've done before. The agent pulls relevant context from vector memory and loaded files to give informed answers.

```bash
# Ask about your code
agent ask "what does the authenticate function do in auth.py?"

# Ask about past interactions
agent ask "what changes did we make to the database layer last week?"

# Get suggestions
agent ask "how can I improve error handling in api/routes.py?"

# Understand relationships
agent ask "which files depend on utils/config.py?"
```

Responses stream token-by-token to your terminal — you see the answer building in real time.

---

### `history` — View Session History

See a log of all interactions in the current session, including commands run, files modified, and agent responses.

```bash
agent history
```

---

### Dry Run Mode

Preview exactly what the agent would change without writing to disk. Useful for reviewing changes before committing, or exploring "what if" edits.

```bash
agent edit auth.py "refactor error handling" --dry-run
```

The full diff is shown but no files are modified.

---

### Multi-File Context

When your instruction involves code that spans multiple files, the agent automatically identifies related files and loads them into context. You don't need to specify every file — just describe what you want.

```bash
# The agent figures out that routes.py imports from auth.py and loads both
agent edit routes.py "use the new JWT auth middleware from auth.py"

# Refactor across a module
agent edit services/ "rename all database helper functions to use snake_case"
```

---

### Diff & Safety Layer

Every edit goes through a confirmation step. The agent shows a color-coded diff in your terminal:

```diff
  def login(user, password):
-     token = generate_token(user)
+     logger.info(f"Login attempt for user: {user}")
+     token = generate_token(user)
+     logger.info(f"Token generated successfully")
      return token
```

```
Apply these changes? [y/n]:
```

Nothing is written until you confirm.

---

### Memory System

#### Short-Term Memory (Session)

The daemon holds the current session in memory. You can refer back to earlier instructions without repeating context.

```bash
agent edit auth.py "add input validation"
# ...later in the same session...
agent ask "what validation did we just add?"   # it remembers
```

#### Long-Term Memory (Persistent)

Interactions are summarized and stored in a FAISS vector database on disk. When the daemon restarts or you start a new session, the agent can still recall relevant past work.

```bash
# New session, days later
agent ask "what changes have we made to the auth module?"
# Retrieves stored summaries from past sessions via similarity search
```

---

### Context-Aware Responses

Every response is enriched by the memory system. When you ask a question or request an edit, the agent:

1. Embeds your query into a vector
2. Searches the FAISS index for the top-k most relevant past interactions
3. Loads the matched context into the LLM prompt
4. Delivers a response grounded in your project's actual history

---

### Command Reference

| Command | Description |
|---|---|
| `agent start` | Start the background daemon |
| `agent stop` | Shut down the daemon |
| `agent restart` | Restart the daemon with fresh state |
| `agent status` | Check daemon health and uptime |
| `agent edit <file> "<instruction>"` | Edit a file using natural language |
| `agent edit <dir/> "<instruction>"` | Edit across a directory with auto file discovery |
| `agent edit <file> "<instruction>" --dry-run` | Preview changes without writing |
| `agent ask "<question>"` | Ask about code, architecture, or past changes |
| `agent history` | View all interactions in the current session |

---

## Configuration

Edit `config.py` to customize:

| Setting | Default | Description |
|---|---|---|
| `MODEL_NAME` | `llama3` | Ollama model to use |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server address |
| `DAEMON_HOST` | `127.0.0.1` | Daemon bind address |
| `DAEMON_PORT` | `9800` | Daemon port |
| `SHORT_TERM_LIMIT` | `10` | Number of recent interactions to keep in session |
| `TOP_K_MEMORY` | `5` | Number of vector search results to inject as context |
| `FAISS_INDEX_PATH` | `./data/faiss_index` | Where the vector DB is persisted |
| `PID_FILE_PATH` | `./data/agent.pid` | PID file for daemon process management |

---

## How It Works

### Request Lifecycle

```
agent edit auth.py "add logging"
  │
  ▼
Client (Typer) parses args
  │
  ▼
Is daemon running? ── No ──→ Auto-start daemon, wait for /health
  │                           │
  Yes ◄─────────────────────────
  │
  ▼
POST /edit  {file: "auth.py", instruction: "add logging"}
  │
  ▼
Daemon: embed query → search FAISS → retrieve top-k memory
  │
  ▼
Daemon: load auth.py + related files into context
  │
  ▼
Planner Agent → decides action plan
  │
  ▼
Executor Agent → generates modified code
  │
  ▼
Validator Agent → verifies correctness (retry if needed)
  │
  ▼
Stream diff back to client
  │
  ▼
Client: render diff with Rich, prompt [y/n]
  │
  ▼
POST /confirm  {apply: true}
  │
  ▼
Daemon: write file + save interaction to FAISS
```

### Agent Workflow (LangGraph)

The three agents run as nodes in a LangGraph state graph:

```
         ┌──────────┐
         │ Planner  │  ← understands intent, picks files, decides actions
         └────┬─────┘
              │
              ▼
         ┌──────────┐
         │ Executor │  ← generates the code changes
         └────┬─────┘
              │
              ▼
         ┌──────────┐     fail
         │Validator │  ──────────→ back to Executor (retry)
         └────┬─────┘
              │ pass
              ▼
           Output
```

The Validator can reject the Executor's output and send it back for another attempt, up to a configurable retry limit.

---

## Tech Stack

| Component | Tool |
|---|---|
| LLM Runtime | [Ollama](https://ollama.com) |
| Agent Framework | [LangChain](https://python.langchain.com) + [LangGraph](https://langchain-ai.github.io/langgraph/) |
| Vector Database | [FAISS](https://github.com/facebookresearch/faiss) |
| Server | [FastAPI](https://fastapi.tiangolo.com) + [Uvicorn](https://www.uvicorn.org) |
| CLI Framework | [Typer](https://typer.tiangolo.com) |
| Terminal UI | [Rich](https://rich.readthedocs.io) |
| HTTP Client | [HTTPX](https://www.python-httpx.org) |
| Language | Python 3.10+ |

---

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m "Add my feature"`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## License

MIT
