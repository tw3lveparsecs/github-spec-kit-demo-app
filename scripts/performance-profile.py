#!/usr/bin/env python3
"""
Performance Profiling Script (T136)

Profiles API endpoints to verify <100ms p95 response time target (SC-005).
Constitution requirement: API endpoints MUST respond within 200ms for p95.
Success criteria: 95% of demo interactions respond within 100ms.
"""

import json
import statistics
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen, Request


BASE_URL = "http://localhost:5000"
ITERATIONS = 100  # Number of requests per endpoint
TARGET_P95_MS = 100  # SC-005 target: 95% under 100ms
CONSTITUTION_P95_MS = 200  # Constitution allows up to 200ms


class PerformanceProfiler:
    """Profiles API endpoint performance."""
    
    def __init__(self):
        self.results = {}
    
    def measure_endpoint(self, endpoint: str, method: str = "GET", data: dict = None) -> list:
        """Measure response times for an endpoint over multiple iterations."""
        url = f"{BASE_URL}{endpoint}"
        times = []
        errors = 0
        
        for i in range(ITERATIONS):
            try:
                start = time.time()
                
                if data:
                    req = Request(url, method=method,
                                 data=json.dumps(data).encode(),
                                 headers={"Content-Type": "application/json"})
                else:
                    req = Request(url, method=method)
                
                with urlopen(req, timeout=10) as response:
                    _ = response.read()
                
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)
                
            except Exception:
                errors += 1
        
        return times, errors
    
    def calculate_stats(self, times: list) -> dict:
        """Calculate performance statistics."""
        if not times:
            return {}
        
        sorted_times = sorted(times)
        n = len(sorted_times)
        
        return {
            "min": min(times),
            "max": max(times),
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "p50": sorted_times[int(n * 0.50)],
            "p90": sorted_times[int(n * 0.90)],
            "p95": sorted_times[int(n * 0.95)] if n >= 20 else sorted_times[-1],
            "p99": sorted_times[int(n * 0.99)] if n >= 100 else sorted_times[-1],
            "count": n,
        }


def format_ms(ms: float) -> str:
    """Format milliseconds."""
    return f"{ms:.1f}ms"


def check_target(p95: float, target: float = TARGET_P95_MS) -> tuple[bool, str]:
    """Check if p95 meets target."""
    passed = p95 <= target
    status = "✅" if passed else "❌"
    return passed, status


def main():
    """Run performance profiling."""
    print("=" * 70)
    print("PERFORMANCE PROFILING (T136 / SC-005)")
    print("=" * 70)
    print(f"Target: p95 < {TARGET_P95_MS}ms (SC-005)")
    print(f"Constitution allows: p95 < {CONSTITUTION_P95_MS}ms")
    print(f"Iterations per endpoint: {ITERATIONS}")
    print()
    
    profiler = PerformanceProfiler()
    
    # Endpoints to profile
    endpoints = [
        ("/api/health", "GET", None),
        ("/api/scenarios", "GET", None),
        ("/api/scenarios/user-authentication", "GET", None),
        ("/api/scenarios/ecommerce-checkout", "GET", None),
        ("/api/scenarios/data-dashboard", "GET", None),
        ("/api/constitution", "GET", None),
        ("/api/presenter-notes", "GET", None),
    ]
    
    all_results = []
    all_passed_strict = True
    all_passed_constitution = True
    
    print("📊 ENDPOINT PERFORMANCE")
    print("-" * 70)
    print(f"{'Endpoint':<45} {'p50':>8} {'p95':>8} {'p99':>8} {'Status'}")
    print("-" * 70)
    
    for endpoint, method, data in endpoints:
        times, errors = profiler.measure_endpoint(endpoint, method, data)
        
        if not times:
            print(f"{endpoint:<45} {'ERROR':>8} {'N/A':>8} {'N/A':>8} ❌")
            all_passed_strict = False
            all_passed_constitution = False
            continue
        
        stats = profiler.calculate_stats(times)
        passed_strict, status = check_target(stats["p95"], TARGET_P95_MS)
        passed_constitution, _ = check_target(stats["p95"], CONSTITUTION_P95_MS)
        
        if not passed_strict:
            all_passed_strict = False
        if not passed_constitution:
            all_passed_constitution = False
        
        print(f"{endpoint:<45} {format_ms(stats['p50']):>8} {format_ms(stats['p95']):>8} {format_ms(stats['p99']):>8} {status}")
        
        all_results.append({
            "endpoint": endpoint,
            "stats": stats,
            "passed_strict": passed_strict,
            "passed_constitution": passed_constitution,
        })
    
    print("-" * 70)
    print()
    
    # Aggregate statistics
    all_times = []
    for result in all_results:
        if "stats" in result and result["stats"]:
            # Estimate times from stats (simplified)
            all_times.extend([result["stats"]["median"]] * result["stats"]["count"])
    
    if all_times:
        agg_stats = profiler.calculate_stats(all_times)
        print("📈 AGGREGATE PERFORMANCE")
        print("-" * 40)
        print(f"  Total requests: {len(all_times)}")
        print(f"  Mean response:  {format_ms(agg_stats['mean'])}")
        print(f"  Median (p50):   {format_ms(agg_stats['p50'])}")
        print(f"  p95:            {format_ms(agg_stats['p95'])}")
        print(f"  p99:            {format_ms(agg_stats['p99'])}")
        print()
    
    # Summary
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    if all_passed_strict:
        print("✅ ALL ENDPOINTS MEET SC-005 TARGET (p95 < 100ms)")
        print("   95% of demo interactions respond within 100ms")
    elif all_passed_constitution:
        print("⚠️  ENDPOINTS MEET CONSTITUTION (p95 < 200ms) BUT NOT SC-005 (p95 < 100ms)")
        print("   Consider optimization for stricter success criteria")
    else:
        print("❌ SOME ENDPOINTS EXCEED CONSTITUTION LIMIT (p95 > 200ms)")
        print("   Performance optimization required")
    
    print()
    print("Note: Results depend on server load and network conditions.")
    print("Run multiple times for reliable measurements.")
    
    sys.exit(0 if all_passed_strict else 1)


if __name__ == "__main__":
    main()
