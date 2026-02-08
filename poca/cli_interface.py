#!/usr/bin/env python3
"""
POCA CLI - Python Open Coding Agent
"""

import argparse
import sys
import os
from poca_agent import PocaAgent
import config

VERSION = "0.1.0"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="poca",
        description="Python Open Coding Agent CLI (Copilot-style coding assistant)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"POCA {VERSION}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- run command ---
    run_parser = subparsers.add_parser(
        "run",
        help="Run the coding agent with a prompt",
        description="Execute a prompt using the POCA agent",
    )

    run_parser.add_argument(
        "prompt",
        type=str,
        help="Prompt to send to the agent",
    )

    run_parser.add_argument(
        "--model",
        default=config.DEFAULT_MODEL,
        help=f"Model name (default: {config.DEFAULT_MODEL})",
    )

    run_parser.add_argument(
        "--base-url",
        default=config.DEFAULT_BASE_URL,
        help=f"Model base URL (default: {config.DEFAULT_BASE_URL})",
    )

    run_parser.add_argument(
        "--max-tokens",
        type=int,
        default=1000,
        help="Max tokens for model output",
    )

    run_parser.add_argument(
        "--system-prompt",
        default=config.DEFAULT_SYS_PROMPT,
        help="Override system prompt",
    )

    run_parser.add_argument(
        "--root-dir",
        default=os.getcwd(),
        help="Filesystem root directory for agent",
    )

    return parser


def cmd_run(args: argparse.Namespace):
    agent = PocaAgent(
        system_prompt=args.system_prompt,
        model=args.model,
        base_url=args.base_url,
        max_tokens=args.max_tokens,
        root_dir=args.root_dir,
    )

    result = agent.run(args.prompt)
    print(result)


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        cmd_run(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
