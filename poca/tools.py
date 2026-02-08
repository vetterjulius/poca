import os
import subprocess
from subprocess import run
from langchain.tools import tool
import glob
import re
from pathlib import Path

# Simple in-process terminal manager for background tasks
_terminals = {}

# Track last commands run (synchronous or background) so tools can return them
_last_commands = []

# Store a terminal selection (best-effort placeholder); VS Code selection not directly accessible
_terminal_selection = ""


@tool("Terminal", description="Runs shell commands")
def run_in_terminal(command: str) -> str:
    "Runs shell commands"
    try:
        # record last command
        try:
            _last_commands.append(command)
        except Exception:
            pass

        result = run(command, shell=True, text=True, capture_output=True)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {e}"


@tool("createAndRunTask", description="Runs a command; can start in background (returns id) or run synchronously")
def create_and_run_task(command: str, isBackground: bool = False) -> str:
    "Runs a command; can start in background (returns id) or run synchronously"
    try:
        # record last command
        try:
            _last_commands.append(command)
        except Exception:
            pass

        if isBackground:
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            tid = str(proc.pid)
            _terminals[tid] = proc
            return f"Background task started with id {tid}"
        else:
            result = run(command, shell=True, text=True, capture_output=True)
            return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {e}"


@tool("awaitTerminal", description="Waits for a background terminal/task to finish and returns its output")
def await_terminal(term_id: str, timeout: float = None) -> str:
    "Waits for a background terminal/task to finish and returns its output"
    try:
        proc = _terminals.get(term_id)
        if not proc:
            return f"No terminal with id {term_id}"
        proc.wait(timeout=timeout)
        out, err = proc.communicate()
        # cleanup
        try:
            del _terminals[term_id]
        except KeyError:
            pass
        return (out or "") + (err or "")
    except subprocess.TimeoutExpired:
        return f"Timeout waiting for terminal {term_id}"
    except Exception as e:
        return f"Error: {e}"


@tool("getTerminalOutput", description="Returns the current output status for a background terminal/task")
def get_terminal_output(term_id: str) -> str:
    "Returns the current output status for a background terminal/task"
    try:
        proc = _terminals.get(term_id)
        if not proc:
            return f"No terminal with id {term_id}"
        if proc.poll() is None:
            return f"Terminal {term_id} is still running"
        out, err = proc.communicate()
        # cleanup
        try:
            del _terminals[term_id]
        except KeyError:
            pass
        return (out or "") + (err or "")
    except Exception as e:
        return f"Error: {e}"


@tool("killTerminal", description="Kills a background terminal/task by id")
def kill_terminal(term_id: str) -> str:
    "Kills a background terminal/task by id"
    try:
        proc = _terminals.get(term_id)
        if not proc:
            return f"No terminal with id {term_id}"
        proc.kill()
        out, err = proc.communicate()
        try:
            del _terminals[term_id]
        except KeyError:
            pass
        return f"Terminal {term_id} killed.\n" + (out or "") + (err or "")
    except Exception as e:
        return f"Error: {e}"


@tool("terminal_last_command", description="Returns the last command run via these terminal tools")
def terminal_last_command() -> str:
    "Returns the last command run via these terminal tools"
    try:
        if not _last_commands:
            return "No terminal commands recorded yet"
        return _last_commands[-1]
    except Exception as e:
        return f"Error: {e}"


@tool("terminal_selection", description="Returns the current terminal selection (best-effort placeholder)")
def terminal_selection() -> str:
    "Returns the current terminal selection (best-effort placeholder)"
    try:
        # We cannot access the VS Code terminal selection from this process.
        # This returns an internal stored value (empty by default).
        return _terminal_selection or ""
    except Exception as e:
        return f"Error: {e}"


@tool("createDirectory", description="Creates directories recursively")
def create_directory(path: str) -> str:
    "Creates directories recursively"
    try:
        os.makedirs(path, exist_ok=True)
        return f"Directory {path} created."
    except Exception as e:
        return f"Error: {e}"


@tool("createFile", description="Creates a file with content")
def create_file(path: str, content: str) -> str:
    "Creates a file with content"
    try:
        dirpath = os.path.dirname(path)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File {path} created."
    except Exception as e:
        return f"Error: {e}"


@tool("file_edit_tool", description="Replace a range of lines in an existing file")
def file_edit(path: str, start_line: int, end_line: int, new_lines: list[str]) -> str:
    "Replace a range of lines in an existing file"
    try:
        if not os.path.exists(path):
            return f"Error: File {path} does not exist."

        if start_line < 1 or end_line < start_line:
            return "Error: invalid line range."

        # Read existing file
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if end_line > len(lines):
            return f"Error: file only has {len(lines)} lines."

        # Ensure newline formatting
        replacement = [line.rstrip("\n") + "\n" for line in new_lines]

        # Replace range
        lines[start_line - 1:end_line] = replacement

        # Write back
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return f"Replaced lines {start_line}-{end_line} in {path}."

    except Exception as e:
        return f"Error: {e}"


@tool("read_file", description="Read file contents by line range (1-based inclusive).")
def read_file(path: str, start: int = None, end: int = None) -> str:
    "Read file contents by line range (1-based inclusive)."
    try:
        if not os.path.exists(path):
            return f"File not found: {path}"
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        # Default to full file
        total = len(lines)
        if start is None:
            start = 1
        if end is None:
            end = total

        # Validate
        if start < 1:
            return "Invalid start line: must be >= 1"
        if end < start:
            return "Invalid range: end must be >= start"
        if start > total:
            return "Start line beyond end of file"

        # Convert to 0-based indices
        s = start - 1
        e = min(end, total)
        selected = lines[s:e]
        return "".join(selected)
    except Exception as e:
        return f"Error reading file: {e}"


@tool("list_directory", description="Lists the content of a directory")
def list_directory(path: str = ".") -> str:
    "Lists the content of a directory"
    try:
        p = Path(path)
        if not p.exists():
            return f"Path does not exist: {path}"
        items = []
        for child in sorted(p.iterdir()):
            typ = "dir" if child.is_dir() else "file"
            items.append(f"{typ}\t{child.name}")
        return "\n".join(items)
    except Exception as e:
        return f"Error listing directory: {e}"


@tool("get_problems", description="Attempts to read problems/errors for a file (best-effort)")
def get_problems(path: str) -> str:
    """Try multiple approaches to surface problems for a file.

    1) If `pyflakes` is available, run it.
    2) Otherwise try `python -m py_compile` for syntax errors.
    3) If neither yields anything, return a helpful message.
    """
    try:
        if not os.path.exists(path):
            return f"File not found: {path}"

        # Try pyflakes first (good for showing lint-like issues)
        try:
            result = run(f'python -m pyflakes "{path}"', shell=True, text=True, capture_output=True)
            out = (result.stdout or "") + (result.stderr or "")
            if out.strip():
                return out
        except Exception:
            pass

        # Fallback: try to compile the file to capture syntax errors
        try:
            result = run(["python", "-m", "py_compile", path], text=True, capture_output=True)
            # py_compile reports errors on stderr
            out = (result.stdout or "") + (result.stderr or "")
            if out.strip():
                return out
        except Exception:
            pass

        return "No problems found (no linters available); tried pyflakes and py_compile."
    except Exception as e:
        return f"Error reading problems: {e}"



@tool("semantic_search_in_codebase", description="Find relevant file chunks and symbols using a glob pattern")
def semantic_search_in_codebase(query: str, glob_pattern: str = "**/*.py", max_results: int = 25) -> str:
    """Best-effort semantic-ish search: finds matching lines/chunks for `query`.

    Returns top matches across files matching `glob_pattern` sorted by number of matches.
    """
    try:
        matches = []
        files = glob.glob(glob_pattern, recursive=True)
        for f in files:
            try:
                with open(f, "r", encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except Exception:
                continue

            # simple scoring: count occurrences of query tokens
            score = text.lower().count(query.lower())
            if score <= 0:
                # also check for symbol-like matches
                if re.search(r"\b" + re.escape(query) + r"\b", text):
                    score = 1
                else:
                    continue

            # find up to a few contexts
            contexts = []
            for m in re.finditer(re.escape(query), text, flags=re.IGNORECASE):
                start = max(0, m.start() - 200)
                end = min(len(text), m.end() + 200)
                contexts.append(text[start:end])
                if len(contexts) >= 3:
                    break

            matches.append((score, f, contexts))

        matches.sort(key=lambda x: x[0], reverse=True)
        out_lines = []
        for score, f, contexts in matches[:max_results]:
            out_lines.append(f"File: {f} (score={score})")
            for c in contexts:
                snippet = c.replace("\n", "\n")
                out_lines.append("---")
                out_lines.append(snippet)
            out_lines.append("\n")

        return "\n".join(out_lines) if out_lines else "No matches found."
    except Exception as e:
        return f"Error during semantic search: {e}"


@tool("file_search", description="Find files by glob pattern")
def file_search(pattern: str = "**/*") -> str:
    """Return newline-separated list of files matching `pattern` (glob, recursive)."""
    try:
        files = glob.glob(pattern, recursive=True)
        if not files:
            return "No files matched pattern."
        return "\n".join(files)
    except Exception as e:
        return f"Error searching files: {e}"


@tool("text_search", description="Find text in files using a regular expression")
def text_search(pattern: str, glob_pattern: str = "**/*", ignore_case: bool = True, max_results: int = 200) -> str:
    """Search files matched by `glob_pattern` for regex `pattern` and return matched lines with file:line context."""
    try:
        flags = re.IGNORECASE if ignore_case else 0
        regex = re.compile(pattern, flags)
        out = []
        files = glob.glob(glob_pattern, recursive=True)
        count = 0
        for f in files:
            # skip directories
            if os.path.isdir(f):
                continue
            try:
                with open(f, "r", encoding="utf-8", errors="replace") as fh:
                    for i, line in enumerate(fh, start=1):
                        if regex.search(line):
                            out.append(f"{f}:{i}: {line.rstrip()}")
                            count += 1
                            if count >= max_results:
                                return "\n".join(out)
            except Exception:
                continue

        return "\n".join(out) if out else "No matches found."
    except Exception as e:
        return f"Error during text search: {e}"


@tool("get_usages", description="Find references/usages of a symbol in the codebase")
def get_usages(symbol: str, glob_pattern: str = "**/*.py", max_results: int = 200) -> str:
    """Return occurrences of `symbol` across files matching `glob_pattern`.

    This is a simple textual search (best-effort)."""
    try:
        token_re = re.compile(r"\b" + re.escape(symbol) + r"\b")
        out = []
        files = glob.glob(glob_pattern, recursive=True)
        count = 0
        for f in files:
            if os.path.isdir(f):
                continue
            try:
                with open(f, "r", encoding="utf-8", errors="replace") as fh:
                    for i, line in enumerate(fh, start=1):
                        if token_re.search(line):
                            out.append(f"{f}:{i}: {line.rstrip()}")
                            count += 1
                            if count >= max_results:
                                return "\n".join(out)
            except Exception:
                continue

        return "\n".join(out) if out else "No usages found."
    except Exception as e:
        return f"Error finding usages: {e}"


@tool("get_diffs", description="Returns changed lines in files (uses git diff if available)")
def get_diffs(path: str = None) -> str:
    """Return a git-style diff for `path` or for the repo if path is None.

    Falls back to a message if git is not available or no diffs.
    """
    try:
        # Prefer git if available
        try:
            if path:
                cmd = f'git diff --unified=0 -- "{path}"'
            else:
                cmd = 'git diff --unified=0'
            res = run(cmd, shell=True, text=True, capture_output=True)
            out = (res.stdout or "") + (res.stderr or "")
            if out.strip():
                return out
        except Exception:
            pass

        return "No git diffs found or git not available."
    except Exception as e:
        return f"Error getting diffs: {e}"



@tool("fetch_url", description="Fetches content from a URL (GET request)")
def fetch_url(url: str) -> str:
    "Fetches content from a URL (GET request)"
    try:
        import requests
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching URL: {e}"


@tool("search_git_repository", description="Searches for a query in a remote git repository")
def search_git_repository(repo_url: str, query: str) -> str:
    "Searches for a query in a remote git repository"
    try:
        # Clone the repo to a temp directory
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            run(f"git clone --depth 1 {repo_url} {tmpdir}", shell=True, check=True, text=True, capture_output=True)
            # Use the text_search tool to find the query in the cloned repo
            return text_search(query, glob_pattern=os.path.join(tmpdir, "**/*"))
    except Exception as e:
        return f"Error searching git repository: {e}"
    

# Tool Groups for easier selection

all_tools = [
    run_in_terminal, 
    create_and_run_task, 
    await_terminal, 
    get_terminal_output, 
    kill_terminal,
    terminal_last_command, 
    terminal_selection, 
    create_directory, 
    create_file, 
    file_edit, 
    read_file, 
    list_directory, 
    get_problems, 
    semantic_search_in_codebase, 
    text_search, get_usages, 
    get_diffs, 
    fetch_url, 
    search_git_repository
] 

terminal_tools = [
    run_in_terminal, 
    create_and_run_task, 
    await_terminal, 
    get_terminal_output, 
    kill_terminal, 
    terminal_last_command, 
    terminal_selection
]

write_tools = [
    create_directory, 
    create_file, 
    file_edit
]

read_tools = [
    read_file, 
    list_directory,
    get_problems,
    get_diffs
]

search_tools = [
    semantic_search_in_codebase, 
    text_search, 
    get_usages, 
    file_search, 
    search_git_repository
]

web_tools = [
    fetch_url,
    search_git_repository
]
