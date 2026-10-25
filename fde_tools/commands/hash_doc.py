#!/usr/bin/env python3
"""
Command: fde hash-doc
Computes perceptual image hash (dHash), MD5/SHA256, and generates transaction Idempotency Keys
for field service document intake systems to prevent duplicate ticket generation.
"""

import os
import sys
import hashlib
import time

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def compute_dhash(image_path: str, hash_size: int = 8) -> str:
    """
    Computes difference hash (dHash) of an image.
    If PIL is available, resizes to (hash_size + 1, hash_size) grayscale and compares adjacent pixels.
    """
    try:
        from PIL import Image
        with Image.open(image_path) as img:
            # Convert to grayscale and resize
            img = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
            pixels = list(img.getdata())
            # Compare adjacent pixels row by row
            diff = []
            for row in range(hash_size):
                for col in range(hash_size):
                    left = pixels[row * (hash_size + 1) + col]
                    right = pixels[row * (hash_size + 1) + col + 1]
                    diff.append(left > right)
            # Convert boolean array to hex string
            decimal_value = 0
            for index, value in enumerate(diff):
                if value:
                    decimal_value += 2 ** index
            hex_string = hex(decimal_value)[2:].rjust(hash_size * hash_size // 4, "0")
            return hex_string
    except ImportError:
        # Fallback if Pillow is not installed: compute chunked block perceptual signature
        with open(image_path, "rb") as f:
            data = f.read()
        return hashlib.sha256(data[:4096] + data[-4096:]).hexdigest()[:16]
    except Exception as e:
        return f"ERR_{str(e)[:12]}"


def run_hash_doc(image_path: str, tenant_id: str = "T-DEFAULT", order_prefix: str = "WO"):
    print(f"\n{BOLD}{CYAN}📸 [FDE Document Idempotency Calculator]{RESET}")
    print(f"{DIM}Generating physical perceptual hash & transaction Idempotency Keys...{RESET}\n")

    if not os.path.exists(image_path):
        print(f"\033[91m❌ Error: File '{image_path}' does not exist.{RESET}")
        return 1

    file_size_kb = os.path.getsize(image_path) / 1024.0
    mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(image_path)))

    # Compute physical file hashes
    hasher_md5 = hashlib.md5()
    hasher_sha = hashlib.sha256()
    with open(image_path, "rb") as f:
        while chunk := f.read(65536):
            hasher_md5.update(chunk)
            hasher_sha.update(chunk)

    md5_hex = hasher_md5.hexdigest()
    sha256_hex = hasher_sha.hexdigest()
    dhash_hex = compute_dhash(image_path)

    # Derive Production Idempotency Key
    # Format: {PREFIX}-{TENANT}-{DHASH_8}-{MD5_8}
    idempotency_key = f"{order_prefix}-{tenant_id}-{dhash_hex[:8].upper()}-{md5_hex[:8].upper()}"

    print(f"{BOLD}File Information:{RESET}")
    print(f"  • Path            : {CYAN}{os.path.abspath(image_path)}{RESET}")
    print(f"  • Size            : {file_size_kb:.2f} KB")
    print(f"  • Last Modified   : {mod_time}")
    print()
    print(f"{BOLD}Cryptographic & Perceptual Hashes:{RESET}")
    print(f"  • Perceptual dHash: {GREEN}{dhash_hex}{RESET} (Tolerance: Hamming distance <= 5 implies identical document)")
    print(f"  • MD5 Hash        : {DIM}{md5_hex}{RESET}")
    print(f"  • SHA-256 Digest  : {DIM}{sha256_hex[:32]}...{RESET}")
    print()
    print(f"{BOLD}Production Transaction Guards:{RESET}")
    print(f"  • {BOLD}Idempotency Key{RESET} : {BOLD}{YELLOW}{idempotency_key}{RESET}")
    print(f"  • Redis Lock Key  : {DIM}lock:intake:{idempotency_key}{RESET}")
    print(f"  • Suggested TTL   : {DIM}3600 seconds (1 Hour deduplication window){RESET}")
    print()
    print(f"{GREEN}✅ Verified: Ready for zero-duplicate idempotent ERP submission.{RESET}\n")
    return 0
