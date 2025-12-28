 

import time
import statistics
import random
import csv
import math
from collections import Counter
import matplotlib.pyplot as plt
import os

# ---------------- Configuration ----------------
random_seed = 42
random.seed(random_seed)

# Input sizes to test
small_sizes = [10, 20, 30]            # Run both Naive & Optimized
large_sizes = [1000, 5000, 10000]     # Run Optimized only

# Measurement params
repeats = 5       # number of measured runs (median taken)
warmups = 1       # warmup runs before measuring
max_naive_n = 30  # don't run naive if n > this

# Input value ranges
max_val_small = 10         # for small tests (increases triplet probability)
max_val_large = 10**6      # for large tests (keeps values reasonable)

# Output files
csv_filename = "benchmark_results.csv"
time_plot_file = "time_vs_n.png"
speedup_plot_file = "speedup_vs_n.png"
dpi_save = 200

LIMIT = 10**9  # maximum allowed value in problem



# ---------------- Algorithms ----------------
def naive_triplets(a):
    """Brute-force count for distinct indices (ordered triples)"""
    n = len(a)
    cnt = 0
    for i in range(n):
        for j in range(n):
            if j == i:
                continue
            for k in range(n):
                if k == i or k == j:
                    continue
                if a[j] * a[j] == a[i] * a[k]:
                    cnt += 1
    return cnt


def optimized_triplets(a):
    """
    Optimized correct counting:
    - counts ordered triplets (i, j, k) with distinct indices and a[j]^2 = a[i]*a[k]
    - uses Counter and enumerates divisors b of mid (where mid = a[j]) with b > 1
    """
    freq = Counter(a)
    unique = list(freq.keys())
    result = 0

    # Case b = 1 (same value used 3 times) -> ordered permutations: c*(c-1)*(c-2)
    for v, c in freq.items():
        if c >= 3:
            result += c * (c - 1) * (c - 2)

    # For each mid, enumerate divisors b of mid (b > 1), then left = mid // b, right = mid * b
    for mid in unique:
        cnt_mid = freq[mid]
        if mid <= 1:
            continue  # no b > 1 divides mid

        # collect divisors of mid (b values) efficiently avoiding duplicates
        b_set = set()
        r = int(math.isqrt(mid))
        for d in range(1, r + 1):
            if mid % d == 0:
                b_set.add(d)
                b_set.add(mid // d)

        # iterate over b values (except b == 1)
        for b in b_set:
            if b <= 1:
                continue
            # b divides mid by construction
            left = mid // b
            right = mid * b
            if right > LIMIT:
                continue
            # check existence
            c_left = freq.get(left, 0)
            c_right = freq.get(right, 0)
            if c_left and c_right:
                # ordered triples count: cnt_mid * c_left * c_right
                # careful: this counts all ordered indices (i from left occurrences, j from mid occurrences, k from right occurrences)
                result += cnt_mid * c_left * c_right

    return result


# ---------------- Utilities for measurement & plotting ----------------
def measure_func(func, args=(), repeats=5, warmups=1):
    """Run warmups then measure function execution repeats times; return median seconds."""
    for _ in range(warmups):
        func(*args)
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        func(*args)
        t1 = time.perf_counter()
        times.append(t1 - t0)
    return statistics.median(times)


def safe_for_log(lst, eps=1e-12):
    """Replace zeros/negatives by a tiny eps for log plotting."""
    return [x if (x is not None and x > eps and not math.isinf(x)) else eps for x in lst]


def generate_test_case(n, max_val):
    """Generate random test array with values in [1, max_val]."""
    # ensure values >=1 to avoid divisor issues
    return [random.randint(1, max_val) for _ in range(n)]


# ---------------- Benchmark runner ----------------
def run_benchmark(small_sizes, large_sizes, repeats, warmups,
                  max_val_small, max_val_large, max_naive_n):
    sizes = small_sizes + large_sizes
    rows = []
    print("Running benchmark...")
    print(f"Naive will run for n <= {max_naive_n}. repeats={repeats}, warmups={warmups}\n")

    for n in sizes:
        max_val = max_val_small if n <= max_naive_n else max_val_large
        a = generate_test_case(n, max_val)

        # measure naive only for small n
        if n <= max_naive_n:
            try:
                t_naive = measure_func(naive_triplets, args=(a,), repeats=repeats, warmups=warmups)
                res_naive = naive_triplets(a)
            except Exception as e:
                print(f"Naive failed for n={n}: {e}")
                t_naive = None
                res_naive = None
        else:
            t_naive = None
            res_naive = None

        # measure optimized
        try:
            t_opt = measure_func(optimized_triplets, args=(a,), repeats=repeats, warmups=warmups)
            res_opt = optimized_triplets(a)
        except Exception as e:
            print(f"Optimized failed for n={n}: {e}")
            t_opt = None
            res_opt = None

        # verify correctness when naive exists
        if res_naive is not None and res_opt is not None and res_naive != res_opt:
            print(f"❌ MISMATCH at n={n}: naive={res_naive}, optimized={res_opt}")
            # Still record results, but warn
        result = res_opt if res_opt is not None else res_naive

        # compute speedup if both times available
        if t_naive is not None and t_opt is not None and t_opt > 0:
            speedup = t_naive / t_opt
        else:
            speedup = None

        print(f"n={n}: naive_time={t_naive if t_naive is not None else 'N/A'}s, opt_time={t_opt if t_opt is not None else 'N/A'}s, result={result}")
        rows.append({
            "n": n,
            "time_naive": t_naive,
            "time_opt": t_opt,
            "speedup": speedup,
            "result": result
        })

    # save to CSV
    with open(csv_filename, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["n", "time_naive", "time_opt", "speedup", "result"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"\nResults saved to {csv_filename}\n")

    # Prepare plotting arrays
    n_vals = [r["n"] for r in rows]
    time_naive_list = [r["time_naive"] if r["time_naive"] is not None else float('inf') for r in rows]
    time_opt_list = [r["time_opt"] if r["time_opt"] is not None else float('inf') for r in rows]
    # replace inf by a large value for plotting (keep relative scale)
    finite_max_opt = max([t for t in time_opt_list if not math.isinf(t)], default=1.0)
    time_naive_plot = [t if not math.isinf(t) else finite_max_opt * 100 for t in time_naive_list]
    time_opt_plot = [t if not math.isinf(t) else finite_max_opt * 100 for t in time_opt_list]

    # safe for log
    time_naive_plot_safe = safe_for_log(time_naive_plot)
    time_opt_plot_safe = safe_for_log(time_opt_plot)

    # compute speedup safe
    speedup_list = []
    for tn, to in zip(time_naive_plot_safe, time_opt_plot_safe):
        if to > 0:
            speedup_list.append(tn / to)
        else:
            speedup_list.append(float('inf'))

    # Plot Time vs n (log y)
    plt.figure(figsize=(10, 5))
    plt.plot(n_vals, time_naive_plot_safe, 'o-', label='Naive (O(n^3))')
    plt.plot(n_vals, time_opt_plot_safe, 's-', label='Optimized')
    plt.yscale('log')
    plt.xlabel('Input size n')
    plt.ylabel('Time (seconds, log scale)')
    plt.title('Time vs Input Size')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(time_plot_file, dpi=dpi_save)
    print(f"Saved time plot to {time_plot_file}")
    plt.show()

    # Plot Speedup vs n (log y)
    plt.figure(figsize=(10, 5))
    # replace inf with a large finite number for plotting
    finite_speedups = [s if not math.isinf(s) else max([x for x in speedup_list if not math.isinf(x)], default=1.0) * 10 for s in speedup_list]
    finite_speedups_safe = safe_for_log(finite_speedups)
    plt.plot(n_vals, finite_speedups_safe, 'd-', color='green', label='Speedup (naive/opt)')
    plt.yscale('log')
    plt.xlabel('Input size n')
    plt.ylabel('Speedup (log scale)')
    plt.title('Speedup Factor vs Input Size')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(speedup_plot_file, dpi=dpi_save)
    print(f"Saved speedup plot to {speedup_plot_file}")
    plt.show()

    print("\nBenchmark complete.")


# ---------------- Main ----------------
if __name__ == "__main__":
    # ensure output folder exists
    out_dir = os.path.dirname(os.path.abspath(csv_filename))
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    run_benchmark(
        small_sizes=small_sizes,
        large_sizes=large_sizes,
        repeats=repeats,
        warmups=warmups,
        max_val_small=max_val_small,
        max_val_large=max_val_large,
        max_naive_n=max_naive_n
    )
