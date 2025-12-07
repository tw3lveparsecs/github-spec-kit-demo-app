#!/usr/bin/env python3
"""
Bundle Size Verification Script (T129)

Verifies frontend bundle size is under 200KB per FR-008 requirement.
Performance budget: <200KB initial JS, <500KB total assets per constitution.
"""

import os
import sys
from pathlib import Path


# Size limits in bytes
LIMITS = {
    "js_total": 200 * 1024,       # 200KB for JavaScript
    "css_total": 100 * 1024,      # 100KB for CSS
    "total_assets": 500 * 1024,   # 500KB total (per constitution)
}


def get_directory_size(path: Path, extensions: list[str] = None) -> dict:
    """Calculate total size of files with given extensions."""
    total = 0
    files = []
    
    for file_path in path.rglob("*"):
        if file_path.is_file():
            if extensions is None or file_path.suffix.lower() in extensions:
                size = file_path.stat().st_size
                total += size
                files.append((file_path.relative_to(path), size))
    
    return {"total": total, "files": sorted(files, key=lambda x: -x[1])}


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    return f"{size_bytes} bytes"


def check_limit(name: str, actual: int, limit: int) -> tuple[bool, str]:
    """Check if size is within limit."""
    passed = actual <= limit
    status = "✅ PASS" if passed else "❌ FAIL"
    pct = (actual / limit) * 100
    return passed, f"{status} {name}: {format_size(actual)} / {format_size(limit)} ({pct:.1f}%)"


def main():
    """Run bundle size verification."""
    # Find frontend directory
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    frontend_src = repo_root / "frontend" / "src"
    
    if not frontend_src.exists():
        print(f"❌ Frontend source directory not found: {frontend_src}")
        sys.exit(1)
    
    print("=" * 60)
    print("BUNDLE SIZE VERIFICATION (T129 / FR-008)")
    print("=" * 60)
    print()
    
    # Measure JavaScript files
    js_result = get_directory_size(frontend_src, [".js"])
    css_result = get_directory_size(frontend_src, [".css"])
    all_result = get_directory_size(frontend_src)
    
    results = []
    
    # Check JavaScript
    js_pass, js_msg = check_limit("JavaScript Bundle", js_result["total"], LIMITS["js_total"])
    results.append(js_pass)
    print(js_msg)
    
    if js_result["files"]:
        print("  Top JavaScript files:")
        for file, size in js_result["files"][:5]:
            print(f"    - {file}: {format_size(size)}")
    print()
    
    # Check CSS
    css_pass, css_msg = check_limit("CSS Bundle", css_result["total"], LIMITS["css_total"])
    results.append(css_pass)
    print(css_msg)
    
    if css_result["files"]:
        print("  Top CSS files:")
        for file, size in css_result["files"][:5]:
            print(f"    - {file}: {format_size(size)}")
    print()
    
    # Check total assets
    total_pass, total_msg = check_limit("Total Assets", all_result["total"], LIMITS["total_assets"])
    results.append(total_pass)
    print(total_msg)
    print()
    
    # Summary
    print("=" * 60)
    if all(results):
        print("✅ ALL BUNDLE SIZE CHECKS PASSED")
        print("Frontend assets are within performance budget.")
        sys.exit(0)
    else:
        print("❌ BUNDLE SIZE CHECKS FAILED")
        print("Consider optimizing assets or reviewing the performance budget.")
        sys.exit(1)


if __name__ == "__main__":
    main()
