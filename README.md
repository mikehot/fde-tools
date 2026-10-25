# FDE-Tools: Field Deployed Engineer & Applied AI Industrial Toolkit

<p align="center">
  <a href="https://github.com/mikehot/fde-tools/actions/workflows/ci.yml">
    <img alt="CI Status" src="https://github.com/mikehot/fde-tools/actions/workflows/ci.yml/badge.svg">
  </a>
  <a href="https://github.com/mikehot/fde-tools/blob/main/LICENSE">
    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-blue.svg">
  </a>
  <img alt="Python Versions" src="https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-brightgreen.svg">
  <a href="https://github.com/mikehot">
    <img alt="Author: @mikehot" src="https://img.shields.io/badge/Author-%40mikehot-black.svg?logo=github">
  </a>
</p>

```
  ______ _____  ______    _______ ____   ____  _       _____ 
 |  ____|  __ \|  ____|  |__   __/ __ \ / __ \| |     / ____|
 | |__  | |  | | |__        | | | |  | | |  | | |    | (___  
 |  __| | |  | |  __|       | | | |  | | |  | | |     \___ \ 
 | |    | |__| | |____      | | | |__| | |__| | |____ ____) |
 |_|    |_____/|______|     |_|  \____/ \____/|______|_____/ 
```

**`fde-tools`** (executable as `fde`) is an industrial-grade command-line automation toolkit designed for **Forward Deployed Engineers (FDE)**, **Applied AI Architects**, and **Full-Stack Systems Engineers**. It bridges the gap between high-level autonomous agentic orchestration, enterprise RAG data security, and low-level mobile/NDK systems engineering.

---

## 🎯 Engineering Philosophy

* **Zero Mandatory Heavy Dependencies**: Core inspection and evaluation routines run out of the box on vanilla Python 3.9+ without compiling C extensions or dragging in heavyweight runtimes.
* **Pure Python Fallback**: Parses 64-bit ELF segments and ZIP structures directly in Python when LLVM or GNU `readelf` binaries are unavailable on client/field laptops.
* **Sub-Second Execution**: Every command completes within milliseconds, making it ideal for CI/CD gates, pre-commit hooks, and live customer on-site triage.

---

## 📦 Quick Start & Installation

### Option 1: Install from GitHub (Recommended)

```bash
pip install git+https://github.com/mikehot/fde-tools.git
```

### Option 2: Local Editable Mode

```bash
git clone https://github.com/mikehot/fde-tools.git
cd fde-tools
pip install -e .
```

### Option 3: Zero-Install Standalone Execution

```bash
git clone https://github.com/mikehot/fde-tools.git
cd fde-tools
python3 bin/fde info
```

---

## 🛠️ Core Commands & Capabilities

| Command | Capability & Target | Industrial Standard |
| :--- | :--- | :--- |
| **`fde check-16kb <path>`** | Inspect ELF `.so` libraries or unpack `.apk` / `.aab` | **Google Play 2026** mandatory 16KB (`0x4000`) page alignment |
| **`fde hash-doc <image>`** | Perceptual `dHash` + MD5 transaction idempotency key | Zero duplicate ERP submissions, network retry deduplication |
| **`fde eval-run <dataset>`** | Automated Golden Dataset benchmark test harness | Quality gate threshold, latency SLA, tool-calling assertions |
| **`fde scaffold-mcp <dir>`** | Scaffold enterprise FastMCP (Model Context Protocol) server | Pydantic type safety, tenant RBAC isolation, injection defense |
| **`fde guard-scan <dir>`** | Static AST and defensive regex security scanner | Detects API tokens, private keys, legacy 4KB flags, prompt injection |
| **`fde info`** | Print system diagnostics and compiler toolchain availability | Python runtime, OS architecture, LLVM/GNU readelf detection |

---

### 1. `fde check-16kb <file.so | file.apk | dir>`
Inspects Android shared libraries (`.so`) or unpackages `.apk` / `.aab` packages to verify compliance with Google Play's 16KB memory page alignment requirement.

```bash
# Check single shared library
fde check-16kb libnative-bridge.so

# Check full release APK
fde check-16kb app-release.apk
```

Output:
```text
🔍 [FDE 16KB Inspector] Target: libnative-bridge.so
Checking against Google Play 2026 16KB (0x4000) ELF page alignment standards...

[ELF Header] Class: 64-bit | Machine: AArch64 (0xb7)
[Segment 01] Type: LOAD | Flags: R-E | Offset: 0x000000 | Align: 0x4000 (16384 bytes) -> ALIGNED ✅
[Segment 02] Type: LOAD | Flags: RW- | Offset: 0x004000 | Align: 0x4000 (16384 bytes) -> ALIGNED ✅

🌟 RESULT: PASS - All 64-bit LOAD segments comply with 16KB memory page alignment.
```

### 2. `fde hash-doc <image_path> [tenant_id] [order_prefix]`
Computes difference perceptual hash (`dHash`), MD5 checksum, and generates zero-duplicate **Transaction Idempotency Keys** for field service document digitization (preventing duplicate ticket insertion during network retries).

```bash
fde hash-doc invoice_receipt.jpg TENANT-CORP WO
```

Output:
```text
📸 [FDE Document Idempotency Calculator]
Generating physical perceptual hash & transaction Idempotency Keys...

Cryptographic & Perceptual Hashes:
  • Perceptual dHash: a34b8c9d12e4f07a (Hamming distance <= 5 implies identical document)
  • MD5 Hash        : 8f14e45fceea167a5a36dedd4bea2543

Production Transaction Guards:
  • Idempotency Key : WO-TENANT-CORP-A34B8C9D-8F14E45F
  • Redis Lock Key  : lock:intake:WO-TENANT-CORP-A34B8C9D-8F14E45F
  • Suggested TTL   : 3600 seconds (1 Hour deduplication window)

✅ Verified: Ready for zero-duplicate idempotent ERP submission.
```

### 3. `fde eval-run <dataset.jsonl> [threshold=0.90]`
Runs automated regression benchmarks on Agent tool-calling, intent decomposition, and RAG ground truth answers.

```bash
fde eval-run golden_dataset_enterprise.jsonl 0.95
```

### 4. `fde scaffold-mcp <target_dir> [server_name]`
Instantly scaffolds a production-grade FastMCP server with read-only database query tools, Pydantic type validation, and input injection sanitization.

```bash
fde scaffold-mcp ./my-mcp-server enterprise-finance-mcp
```

### 5. `fde guard-scan [directory]`
Recursively scans codebase directories to intercept hardcoded API keys, private keys, legacy 4KB page alignment compiler flags (`-Wl,-z,max-page-size=4096`), and raw prompt injection strings.

```bash
fde guard-scan .
```

### 6. `fde info`
Prints system environment, Python runtime diagnostics, and detects available GNU/LLVM compiler toolchains.

```bash
fde info
```

---

## 🧪 Testing

Run the zero-dependency test suite:

```bash
python3 -m unittest discover tests -v
```

---

## 📄 License

Released under the [MIT License](LICENSE).  
Copyright (c) 2026 Jacky Chou (周亚杰) · [@mikehot](https://github.com/mikehot)
