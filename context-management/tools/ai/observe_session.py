#!/usr/bin/env python3
"""
Real-Time Session Observer for analyze.py

Streams interactive chat session logs in real-time using file tail pattern.
Works from Claude Code or any non-TTY environment.

Usage:
    # Watch a specific session by PID
    python observe_session.py 12345

    # Watch the most recent session
    python observe_session.py --latest

    # Start analyze.py and watch it (launches in background)
    python observe_session.py --launch --set brain "Your query here"

The observer reads from /tmp/analyze_session_<PID>.jsonl which analyze.py
writes to when SESSION_STREAMING=1 is set.
"""

import argparse
import json
import os
import sys
import time
import subprocess
import signal
from datetime import datetime
from pathlib import Path
from typing import Optional

# Session log directory
SESSION_DIR = Path("/tmp/analyze_sessions")
SESSION_DIR.mkdir(exist_ok=True)

# Colors for terminal output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def get_session_file(pid: int) -> Path:
    """Get session log file path for a PID."""
    return SESSION_DIR / f"session_{pid}.jsonl"


def find_latest_session() -> Optional[Path]:
    """Find the most recently modified session file."""
    sessions = list(SESSION_DIR.glob("session_*.jsonl"))
    if not sessions:
        return None
    return max(sessions, key=lambda p: p.stat().st_mtime)


def format_turn(turn: dict) -> str:
    """Format a chat turn for display."""
    role = turn.get('role', 'unknown')
    content = turn.get('content', turn.get('message', ''))
    timestamp = turn.get('timestamp', 0)

    time_str = datetime.fromtimestamp(timestamp).strftime('%H:%M:%S') if timestamp else ''

    if role == 'user':
        prefix = f"{Colors.GREEN}{Colors.BOLD}USER{Colors.RESET}"
    elif role == 'assistant':
        prefix = f"{Colors.BLUE}{Colors.BOLD}GEMINI{Colors.RESET}"
    elif role == 'system':
        prefix = f"{Colors.YELLOW}SYSTEM{Colors.RESET}"
    elif role == 'error':
        prefix = f"{Colors.RED}ERROR{Colors.RESET}"
    else:
        prefix = f"{Colors.CYAN}{role.upper()}{Colors.RESET}"

    # Truncate very long content
    if len(content) > 2000:
        content = content[:2000] + f"\n{Colors.MAGENTA}... [{len(content) - 2000} more chars]{Colors.RESET}"

    return f"[{time_str}] {prefix}: {content}"


def tail_session(session_file: Path, follow: bool = True):
    """Tail a session log file, displaying turns in real-time."""
    print(f"{Colors.CYAN}Observing session: {session_file}{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}\n")

    # Read existing content first
    if session_file.exists():
        with open(session_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        turn = json.loads(line)
                        print(format_turn(turn))
                        print()
                    except json.JSONDecodeError:
                        print(f"{Colors.RED}[Parse Error] {line}{Colors.RESET}")

    if not follow:
        return

    # Follow mode - wait for new content
    print(f"{Colors.YELLOW}--- Waiting for new messages (Ctrl+C to stop) ---{Colors.RESET}\n")

    try:
        with open(session_file, 'r') as f:
            # Jump to end
            f.seek(0, 2)

            while True:
                line = f.readline()
                if line:
                    line = line.strip()
                    if line:
                        try:
                            turn = json.loads(line)
                            print(format_turn(turn))
                            print()
                        except json.JSONDecodeError:
                            print(f"{Colors.RED}[Parse Error] {line}{Colors.RESET}")
                else:
                    time.sleep(0.1)  # 100ms poll interval
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Observer stopped.{Colors.RESET}")


def launch_and_observe(args_list: list, query: str):
    """Launch analyze.py with PTY and observe its output.

    Uses a pseudo-TTY so analyze.py's input() works properly.
    """
    import pty
    import select

    # Build command
    script_dir = Path(__file__).parent
    analyze_path = script_dir / "analyze.py"

    cmd = [
        sys.executable, str(analyze_path),
        "--interactive",
    ] + args_list

    if query:
        cmd.append(query)

    # Set environment to enable streaming
    env = os.environ.copy()
    env['SESSION_STREAMING'] = '1'

    print(f"{Colors.CYAN}Launching: {' '.join(cmd)}{Colors.RESET}")

    # Create a pseudo-terminal
    master_fd, slave_fd = pty.openpty()

    # Start process with PTY
    proc = subprocess.Popen(
        cmd,
        env=env,
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
    )
    os.close(slave_fd)  # Close slave in parent

    print(f"{Colors.GREEN}Started analyze.py (PID: {proc.pid}){Colors.RESET}")
    print(f"{Colors.YELLOW}Type your queries below. They will be sent to the session.{Colors.RESET}")
    print(f"{Colors.YELLOW}Press Ctrl+C to stop observing (session continues in background).{Colors.RESET}\n")

    # Wait a moment for session file to be created
    session_file = get_session_file(proc.pid)
    for _ in range(50):  # 5 second timeout
        if session_file.exists():
            break
        time.sleep(0.1)

    # Start observer thread for session file
    import threading
    stop_event = threading.Event()

    def observe_thread():
        if session_file.exists():
            tail_session(session_file, follow=True)

    # Interactive loop: read user input and write to PTY
    try:
        while proc.poll() is None:
            # Check if there's output from the process
            readable, _, _ = select.select([master_fd], [], [], 0.1)
            if readable:
                try:
                    output = os.read(master_fd, 1024)
                    if output:
                        sys.stdout.write(output.decode('utf-8', errors='replace'))
                        sys.stdout.flush()
                except OSError:
                    break

            # Check if there's input from user (non-blocking)
            readable_stdin, _, _ = select.select([sys.stdin], [], [], 0)
            if readable_stdin:
                user_input = sys.stdin.readline()
                if user_input:
                    os.write(master_fd, user_input.encode())

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Observer stopped. Session may still be running.{Colors.RESET}")
    finally:
        os.close(master_fd)

    # Wait for process if it's still running
    if proc.poll() is None:
        proc.wait()
    print(f"\n{Colors.GREEN}Session ended (exit code: {proc.returncode}){Colors.RESET}")


def list_sessions():
    """List all available session files."""
    sessions = sorted(SESSION_DIR.glob("session_*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not sessions:
        print(f"{Colors.YELLOW}No sessions found in {SESSION_DIR}{Colors.RESET}")
        return

    print(f"{Colors.CYAN}Available sessions:{Colors.RESET}\n")

    for i, session in enumerate(sessions[:10]):  # Show last 10
        stat = session.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        size = stat.st_size
        pid = session.stem.split('_')[1]

        # Count turns
        with open(session, 'r') as f:
            turns = sum(1 for line in f if line.strip())

        print(f"  {i+1}. PID {pid} | {mtime} | {turns} turns | {size} bytes")
        print(f"     {session}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Real-time observer for analyze.py interactive sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Watch a specific session
    python observe_session.py 12345

    # Watch the most recent session
    python observe_session.py --latest

    # List available sessions
    python observe_session.py --list

    # Launch analyze.py and watch it
    python observe_session.py --launch --set brain "What is the purpose of full_analysis.py?"
""",
    )

    parser.add_argument("pid", nargs="?", type=int, help="Session PID to observe")
    parser.add_argument("--latest", action="store_true", help="Watch the most recent session")
    parser.add_argument("--list", action="store_true", help="List available sessions")
    parser.add_argument("--no-follow", action="store_true", help="Don't follow (just show existing content)")
    parser.add_argument("--launch", action="store_true", help="Launch analyze.py and observe")
    parser.add_argument("--set", help="Analysis set for --launch mode")
    parser.add_argument("query", nargs="?", help="Query for --launch mode")

    args = parser.parse_args()

    if args.list:
        list_sessions()
        return

    if args.launch:
        launch_args = []
        if args.set:
            launch_args.extend(["--set", args.set])
        launch_and_observe(launch_args, args.query or "")
        return

    if args.latest:
        session_file = find_latest_session()
        if not session_file:
            print(f"{Colors.RED}No sessions found{Colors.RESET}")
            sys.exit(1)
    elif args.pid:
        session_file = get_session_file(args.pid)
        if not session_file.exists():
            print(f"{Colors.RED}Session file not found: {session_file}{Colors.RESET}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    tail_session(session_file, follow=not args.no_follow)


if __name__ == "__main__":
    main()
