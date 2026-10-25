#!/usr/bin/env python3
"""
Command: fde guard-scan
Performs defensive security scans across codebase directories.
Detects hardcoded secrets, API tokens, prompt injection attack vectors, and 4KB page alignment flags.
"""

import os
import re
import sys

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

SECURITY_RULES = [
    {
        "name": "Hardcoded OpenAI / API Key",
        "pattern": re.compile(r"sk-[a-zA-Z0-9]{32,64}|sk-proj-[a-zA-Z0-9_\-]{40,}"),
        "severity": "CRITICAL"
    },
    {
        "name": "Hardcoded Google API Key",
        "pattern": re.compile(r"AIzaSy[0-9A-Za-z\-_]{33}"),
        "severity": "CRITICAL"
    },
    {
        "name": "RSA / PKCS8 Private Key Block",
        "pattern": re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        "severity": "CRITICAL"
    },
    {
        "name": "Hardcoded Generic Secret Token",
        "pattern": re.compile(r'(api[_\-]?key|secret|password|access[_\-]?token)\s*[:=]\s*["\'][a-zA-Z0-9_\-]{16,}["\']', re.IGNORECASE),
        "severity": "HIGH"
    },
    {
        "name": "Legacy 4KB Page Alignment Flag in Build Script",
        "pattern": re.compile(r"-Wl,-z,max-page-size=4096"),
        "severity": "HIGH"
    },
    {
        "name": "Direct Raw User Input into System Prompt",
        "pattern": re.compile(r'(system_prompt|instructions)\s*=\s*f["\'].*\{user_input\}.*["\']', re.IGNORECASE),
        "severity": "MEDIUM"
    }
]

IGNORED_DIRS = {".git", ".idea", "node_modules", "build", "dist", ".gradle", ".gemini", "__pycache__"}
SCANNABLE_EXTS = {".py", ".dart", ".java", ".kt", ".gradle", ".cmake", ".mk", ".json", ".yaml", ".yml", ".env", ".sh", ".md"}


def run_guard_scan(target_dir: str):
    print(f"\n{BOLD}{CYAN}🛡️ [FDE Defensive Security & Code Guard Scanner]{RESET}")
    print(f"{DIM}Scanning directory: {os.path.abspath(target_dir)}...{RESET}\n")

    if not os.path.exists(target_dir):
        print(f"{RED}❌ Error: Path '{target_dir}' does not exist.{RESET}")
        return 1

    findings = []
    scanned_files_count = 0

    for root, dirs, files in os.walk(target_dir):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in SCANNABLE_EXTS or file.startswith(".env"):
                file_path = os.path.join(root, file)
                scanned_files_count += 1
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_no, line in enumerate(f, 1):
                            for rule in SECURITY_RULES:
                                match = rule["pattern"].search(line)
                                if match:
                                    findings.append({
                                        "file": os.path.relpath(file_path, target_dir),
                                        "line": line_no,
                                        "rule": rule["name"],
                                        "severity": rule["severity"],
                                        "snippet": line.strip()[:60]
                                    })
                except Exception:
                    pass

    print(f"Scanned {BOLD}{scanned_files_count}{RESET} files.")
    print("-" * 80)

    if not findings:
        print(f"{GREEN}🌟 CLEAN SCAN: No critical secrets, 4KB regression flags, or prompt injection hazards detected!{RESET}\n")
        return 0

    critical_count = sum(1 for f in findings if f["severity"] == "CRITICAL")
    high_count = sum(1 for f in findings if f["severity"] == "HIGH")
    medium_count = sum(1 for f in findings if f["severity"] == "MEDIUM")

    for f in findings:
        sev_color = RED if f["severity"] == "CRITICAL" else (YELLOW if f["severity"] == "HIGH" else CYAN)
        print(f"[{sev_color}{f['severity']}{RESET}] {BOLD}{f['file']}:{f['line']}{RESET}")
        print(f"  • Issue   : {f['rule']}")
        print(f"  • Snippet : {DIM}{f['snippet']}{RESET}")
        print()

    print("-" * 80)
    print(f"{BOLD}Summary:{RESET} Critical: {RED}{critical_count}{RESET} | High: {YELLOW}{high_count}{RESET} | Medium: {CYAN}{medium_count}{RESET}")

    if critical_count > 0:
        print(f"\n{RED}❌ GUARD SCAN FAILED: Critical secrets or security risks must be revoked immediately!{RESET}\n")
        return 1
    return 0
