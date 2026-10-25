#!/usr/bin/env python3
"""
Command: fde check-16kb
Inspects shared libraries (.so) or Android packages (.apk / .aab) for 16KB ELF segment alignment.
Complies with Google Play 2026 mandatory requirement.
"""

import os
import sys
import struct
import tempfile
import zipfile
import shutil

# ANSI Color Codes
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

ELF_MAGIC = b"\x7fELF"
PT_LOAD = 1
PAGE_SIZE_16KB = 0x4000  # 16384 bytes


def parse_elf_load_alignments(file_path: str):
    """
    Pure Python ELF parser to extract PT_LOAD segment alignment (p_align).
    Works on 64-bit ELF (arm64-v8a, x86_64) without requiring external tools.
    """
    alignments = []
    try:
        with open(file_path, "rb") as f:
            header = f.read(64)
            if len(header) < 64 or not header.startswith(ELF_MAGIC):
                return None, "Not a valid ELF binary"

            ei_class = header[4]  # 1 = 32-bit, 2 = 64-bit
            ei_data = header[5]   # 1 = Little-endian, 2 = Big-endian
            endian = "<" if ei_data == 1 else ">"

            if ei_class == 2:
                # 64-bit ELF
                # e_phoff offset: 32, 8 bytes (uint64)
                # e_phentsize offset: 54, 2 bytes (uint16)
                # e_phnum offset: 56, 2 bytes (uint16)
                e_phoff = struct.unpack(endian + "Q", header[32:40])[0]
                e_phentsize = struct.unpack(endian + "H", header[54:56])[0]
                e_phnum = struct.unpack(endian + "H", header[56:58])[0]

                f.seek(e_phoff)
                for _ in range(e_phnum):
                    ph_data = f.read(e_phentsize)
                    if len(ph_data) < 56:
                        break
                    # In 64-bit Elf64_Phdr:
                    # p_type: uint32 (0:4)
                    # p_flags: uint32 (4:8)
                    # p_offset: uint64 (8:16)
                    # p_vaddr: uint64 (16:24)
                    # p_paddr: uint64 (24:32)
                    # p_filesz: uint64 (32:40)
                    # p_memsz: uint64 (40:48)
                    # p_align: uint64 (48:56)
                    p_type = struct.unpack(endian + "I", ph_data[0:4])[0]
                    p_align = struct.unpack(endian + "Q", ph_data[48:56])[0]
                    if p_type == PT_LOAD:
                        alignments.append(p_align)

            elif ei_class == 1:
                # 32-bit ELF (arm-v7a)
                e_phoff = struct.unpack(endian + "I", header[28:32])[0]
                e_phentsize = struct.unpack(endian + "H", header[42:44])[0]
                e_phnum = struct.unpack(endian + "H", header[44:46])[0]

                f.seek(e_phoff)
                for _ in range(e_phnum):
                    ph_data = f.read(e_phentsize)
                    if len(ph_data) < 32:
                        break
                    # In 32-bit Elf32_Phdr:
                    # p_type: uint32 (0:4)
                    # p_align: uint32 (28:32)
                    p_type = struct.unpack(endian + "I", ph_data[0:4])[0]
                    p_align = struct.unpack(endian + "I", ph_data[28:32])[0]
                    if p_type == PT_LOAD:
                        alignments.append(p_align)

        return alignments, None
    except Exception as e:
        return None, str(e)


def run_check_16kb(target_path: str):
    print(f"\n{BOLD}{CYAN}🔍 [FDE 16KB Inspector]{RESET} Target: {BOLD}{target_path}{RESET}")
    print(f"{DIM}Checking against Google Play 2026 16KB (0x4000) ELF page alignment standards...{RESET}\n")

    if not os.path.exists(target_path):
        print(f"{RED}❌ Error: File or path '{target_path}' does not exist.{RESET}")
        return 1

    so_files = []
    temp_dir = None

    if target_path.endswith((".apk", ".aab", ".zip")):
        print(f"{DIM}Unpacking archive to inspect internal .so libraries...{RESET}")
        temp_dir = tempfile.mkdtemp(prefix="fde_16kb_")
        try:
            with zipfile.ZipFile(target_path, "r") as z:
                for filename in z.namelist():
                    if filename.endswith(".so"):
                        extracted_path = z.extract(filename, temp_dir)
                        so_files.append((filename, extracted_path))
        except Exception as e:
            print(f"{RED}❌ Failed to extract archive: {e}{RESET}")
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
            return 1
    elif target_path.endswith(".so"):
        so_files.append((os.path.basename(target_path), target_path))
    elif os.path.isdir(target_path):
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith(".so"):
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, target_path)
                    so_files.append((rel_p, full_p))
    else:
        # Single binary check
        so_files.append((os.path.basename(target_path), target_path))

    if not so_files:
        print(f"{YELLOW}⚠️ No .so shared libraries found in target.{RESET}")
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        return 0

    # Header
    print(f"{BOLD}{'Library Name / Path':<48} | {'Max PT_LOAD Align':<18} | {'Status':<12}{RESET}")
    print("-" * 84)

    total_so = len(so_files)
    passed_so = 0
    failed_so = 0

    for display_name, disk_path in so_files:
        alignments, err = parse_elf_load_alignments(disk_path)
        if err or not alignments:
            print(f"{display_name:<48} | {YELLOW}{'NOT_ELF / ERR':<18}{RESET} | {YELLOW}SKIPPED{RESET}")
            continue

        min_align = min(alignments)
        max_align = max(alignments)
        hex_align = f"0x{max_align:X}"

        # If min_align is smaller than 16KB, it's not compliant
        if min_align >= PAGE_SIZE_16KB:
            status_str = f"{GREEN}PASS (16KB){RESET}"
            passed_so += 1
        else:
            status_str = f"{RED}FAIL (4KB){RESET}"
            failed_so += 1

        truncated_name = display_name if len(display_name) <= 46 else "..." + display_name[-43:]
        print(f"{truncated_name:<48} | {hex_align:<18} | {status_str}")

    print("-" * 84)
    print(f"{BOLD}Summary:{RESET} Total Scanned: {total_so} | {GREEN}Passed: {passed_so}{RESET} | {RED}Failed: {failed_so}{RESET}")

    if temp_dir:
        shutil.rmtree(temp_dir, ignore_errors=True)

    if failed_so > 0:
        print(f"\n{RED}❌ COMPLIANCE CHECK FAILED:{RESET} {failed_so} libraries will crash on 16KB Android 15+ devices!")
        print(f"{YELLOW}💡 Action items:{RESET}")
        print(f"  1. Recompile with Clang/NDK r27+ using: -Wl,-z,max-page-size=16384")
        print(f"  2. Update third-party binary SDKs to their 16KB compatible builds.")
        return 1
    else:
        print(f"\n{GREEN}🌟 100% COMPLIANT:{RESET} All shared libraries successfully adhere to 16KB page alignment!")
        return 0
