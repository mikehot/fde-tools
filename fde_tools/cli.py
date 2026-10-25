#!/usr/bin/env python3
"""
FDE-Tools CLI Dispatcher
Author: Jacky Chou · Principal Applied AI Engineer / FDE
"""

import sys
import os
import argparse
import platform
import shutil

# Ensure module can be imported when running script directly
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fde_tools import __version__
from fde_tools.commands.check_16kb import run_check_16kb
from fde_tools.commands.hash_doc import run_hash_doc
from fde_tools.commands.eval_runner import run_eval_runner
from fde_tools.commands.scaffold_mcp import run_scaffold_mcp
from fde_tools.commands.guard_scan import run_guard_scan

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

BANNER = rf"""{CYAN}{BOLD}
  ______ _____  ______    _______ ____   ____  _       _____ 
 |  ____|  __ \|  ____|  |__   __/ __ \ / __ \| |     / ____|
 | |__  | |  | | |__        | | | |  | | |  | | |    | (___  
 |  __| | |  | |  __|       | | | |  | | |  | | |     \___ \ 
 | |    | |__| | |____      | | | |__| | |__| | |____ ____) |
 |_|    |_____/|______|     |_|  \____/ \____/|______|_____/ 
{RESET}{DIM}Field Deployed Engineer & Applied AI Industrial Toolkit v{__version__}{RESET}
{DIM}By Jacky Chou (@mikehot) · Systems, Mobile & Multi-Agent Architecture{RESET}
"""


def show_info():
    print(BANNER)
    print(f"{BOLD}System Environment & Diagnostics:{RESET}")
    print(f"  • Operating System   : {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"  • Python Runtime     : {platform.python_implementation()} {platform.python_version()}")
    print(f"  • Python Executable  : {sys.executable}")
    
    # Check llvm-readelf / readelf availability
    llvm_readelf = shutil.which("llvm-readelf")
    readelf = shutil.which("readelf")
    print(f"  • llvm-readelf Tool  : {GREEN + llvm_readelf if llvm_readelf else YELLOW + 'Not Found (Pure-Python Fallback Active)'}{RESET}")
    print(f"  • GNU readelf Tool   : {GREEN + readelf if readelf else YELLOW + 'Not Found'}{RESET}")
    print()
    print(f"{BOLD}Available Subcommands:{RESET}")
    print(f"  1. {CYAN}fde check-16kb <path>{RESET}    : Check ELF / APK 16KB memory page alignment")
    print(f"  2. {CYAN}fde hash-doc <image>{RESET}     : Compute perceptual dHash & Idempotency Key")
    print(f"  3. {CYAN}fde eval-run <dataset>{RESET}   : Execute automated Golden Dataset benchmark")
    print(f"  4. {CYAN}fde scaffold-mcp <dir>{RESET}  : Scaffold production-grade FastMCP server")
    print(f"  5. {CYAN}fde guard-scan <dir>{RESET}    : Codebase security, token & injection scanner")
    print(f"  6. {CYAN}fde info{RESET}                 : Print environment diagnostic and tool status")
    print()


def main():
    if len(sys.argv) == 1 or sys.argv[1] in ("-h", "--help", "help"):
        print(BANNER)
        show_info()
        sys.exit(0)

    command = sys.argv[1].lower()

    if command in ("-v", "--version", "version"):
        print(f"FDE-Tools v{__version__}")
        sys.exit(0)

    if command == "info":
        show_info()
        sys.exit(0)

    if command in ("check-16kb", "16kb", "check16kb"):
        if len(sys.argv) < 3:
            print(f"{YELLOW}Usage: fde check-16kb <file.so | file.apk | directory>{RESET}")
            sys.exit(1)
        sys.exit(run_check_16kb(sys.argv[2]))

    elif command in ("hash-doc", "hash", "idempotency"):
        if len(sys.argv) < 3:
            print(f"{YELLOW}Usage: fde hash-doc <document_image_path> [tenant_id] [prefix]{RESET}")
            sys.exit(1)
        tenant = sys.argv[3] if len(sys.argv) > 3 else "T-DEFAULT"
        prefix = sys.argv[4] if len(sys.argv) > 4 else "WO"
        sys.exit(run_hash_doc(sys.argv[2], tenant, prefix))

    elif command in ("eval-run", "eval", "evals"):
        if len(sys.argv) < 3:
            print(f"{YELLOW}Usage: fde eval-run <golden_dataset.jsonl> [threshold=0.90]{RESET}")
            sys.exit(1)
        threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 0.90
        sys.exit(run_eval_runner(sys.argv[2], threshold))

    elif command in ("scaffold-mcp", "mcp"):
        if len(sys.argv) < 3:
            print(f"{YELLOW}Usage: fde scaffold-mcp <target_directory> [server_name]{RESET}")
            sys.exit(1)
        target_dir = sys.argv[2]
        s_name = sys.argv[3] if len(sys.argv) > 3 else "enterprise-rag-mcp"
        sys.exit(run_scaffold_mcp(target_dir, s_name))

    elif command in ("guard-scan", "scan", "guard"):
        target_dir = sys.argv[2] if len(sys.argv) > 2 else "."
        sys.exit(run_guard_scan(target_dir))

    else:
        print(f"\033[91mUnknown command: '{command}'{RESET}")
        print(f"Run {CYAN}fde info{RESET} or {CYAN}fde --help{RESET} for available commands.")
        sys.exit(1)


if __name__ == "__main__":
    main()
