import matplotlib.pyplot as plt
import random
import time
import os
import shutil
import numpy as np
import matplotlib
import csv
import math
from multiprocessing import Pool, cpu_count
matplotlib.use('Agg')

# --- Algoritmi ---
def next_fit(weight, c):
    res, rem = 1, c
    for w in weight:
        if rem >= w:
            rem -= w
        else:
            res += 1
            rem = c - w
    return res

def first_fit(weight, c):
    res, bin_rem = 0, []
    for w in weight:
        for i in range(res):
            if bin_rem[i] >= w:
                bin_rem[i] -= w
                break
        else:
            bin_rem.append(c - w)
            res += 1
    return res

def best_fit(weight, c):
    res, bin_rem = 0, []
    for w in weight:
        best = -1
        best_space = c + 1
        for i in range(res):
            if bin_rem[i] >= w and bin_rem[i] - w < best_space:
                best = i
                best_space = bin_rem[i] - w
        if best == -1:
            bin_rem.append(c - w)
            res += 1
        else:
            bin_rem[best] -= w
    return res

def worst_fit(weight, c):
    res, bin_rem = 0, []
    for w in weight:
        worst = -1
        worst_space = -1
        for i in range(res):
            if bin_rem[i] >= w and bin_rem[i] - w > worst_space:
                worst = i
                worst_space = bin_rem[i] - w
        if worst == -1:
            bin_rem.append(c - w)
            res += 1
        else:
            bin_rem[worst] -= w
    return res

def first_fit_decreasing(weight, c):
    return first_fit(sorted(weight, reverse=True), c)

# --- Backtracking optimizat si paralelizat ---
def _bt_worker(args):
    # procesare paralela a unui subarbore
    
    weights, C, start_idx, bins, current_best = args
    n = len(weights)
    best = [current_best]

    def solve(idx, bins):
        if idx == n:
            best[0] = min(best[0], len(bins))
            return

        # Pruning
        if len(bins) >= best[0]:
            return

        # Evitam duplicate - memoram capacitatile incercate
        used = set()
        for i in range(len(bins)):
            if bins[i] >= weights[idx] and bins[i] not in used:
                used.add(bins[i])
                bins[i] -= weights[idx]
                solve(idx + 1, bins)
                bins[i] += weights[idx]

        # Deschidem un container nou
        bins.append(C - weights[idx])
        solve(idx + 1, bins)
        bins.pop()

    solve(start_idx, bins[:])
    return best[0]

def backtracking_optimal(weights, C):
    # Sortam descrescator pentru pruning
    weights = sorted(weights, reverse=True)
    n = len(weights)

    # Calculam lower bound (suma / capacitate)
    total_w = sum(weights)
    lb = math.ceil(total_w / C)

    # Upper bound initial de la FFD
    ub = first_fit_decreasing(weights, C)

    if lb == ub:
        return ub

    # Cate nivele expandam inainte de paralelizare
    PAR_LEVEL = 2
    tasks = []

    def generate_prefixes(idx, bins):
        # prefixe pentru paralelizare
        if idx == PAR_LEVEL:
            tasks.append((weights, C, idx, bins[:], ub))
            return

        used = set()
        for i in range(len(bins)):
            if bins[i] >= weights[idx] and bins[i] not in used:
                used.add(bins[i])
                bins[i] -= weights[idx]
                generate_prefixes(idx + 1, bins)
                bins[i] += weights[idx]

        bins.append(C - weights[idx])
        generate_prefixes(idx + 1, bins)
        bins.pop()

    generate_prefixes(0, [])

    if not tasks:
        return ub

    # Executam task-urile in paralel
    with Pool() as p:
        results = p.map(_bt_worker, tasks)

    return min(results)


# --- Generare Teste ---
def generate_tests():
    folder = "teste_binpacking"
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

    C = 100
    test_files = []

    # 10 teste mici
    small_ns = [10, 12, 15, 18, 20, 22, 25, 27, 30, 35]
    for i, n in enumerate(small_ns):
        w = [random.randint(10, 60) for _ in range(n)]
        filename = f"{folder}/test_small_{i+1}_n{n}.txt"
        with open(filename, "w") as f:
            f.write(f"{n} {C}\n")
            for weight in w:
                f.write(f"{weight}\n")
        test_files.append(filename)

    # 30 teste mari
    for i in range(30):
        n = 40 + (i * 15) # Incepem de la 40 pentru a nu rula backtracking (limita e 35)
        dist_type = i % 3

        # ne generam 3 categorii de inputuri 
        if dist_type == 0:
            w = [random.randint(10, 60) for _ in range(n)]
        elif dist_type == 1:
            w = [random.randint(51, 95) for _ in range(n)]
        else:
            w = [random.randint(1, 25) for _ in range(n)]
        filename = f"{folder}/test_large_{i+1}_n{n}.txt"
        with open(filename, "w") as f:
            f.write(f"{n} {C}\n")
            for weight in w:
                f.write(f"{weight}\n")
        test_files.append(filename)

    return test_files

# --- Functie pentru un singur test ---
def run_single_test(f_path):
    algos = {
        "NF": next_fit,
        "FF": first_fit,
        "BF": best_fit,
        "WF": worst_fit,
        "FFD": first_fit_decreasing
    }

    with open(f_path, "r") as f:
        first_line = f.readline().split()
        if not first_line: return None
        n = int(first_line[0])
        C = int(first_line[1])
        W = [int(f.readline()) for _ in range(n)]

    results = {}
    times = {}

    for name, func in algos.items():
        t0 = time.perf_counter()
        res = func(W, C)
        times[name] = time.perf_counter() - t0
        results[name] = res

    # Rulam backtracking doar pentru N <= 35
    if n <= 35:
        t0 = time.perf_counter()
        results["OPT"] = backtracking_optimal(W, C)
        times["OPT"] = time.perf_counter() - t0
    else:
        results["OPT"] = None
        times["OPT"] = None

    return (f_path, n, results, times)

# --- Benchmark complet ---
def run_benchmark():
    test_files = generate_tests()
    
    print(f"Folosesc {cpu_count()} core-uri pentru paralelizare\n")

    outputs = [run_single_test(f) for f in test_files]

    outputs = [o for o in outputs if o]
    outputs.sort(key=lambda x: x[1])

    results = {k: [] for k in ["NF", "FF", "BF", "WF", "FFD", "OPT"]}
    times = {k: [] for k in ["NF", "FF", "BF", "WF", "FFD", "OPT"]}
    n_values = []

    print(f"{'Test':<20} | {'N':<4} | NF | FF | BF | WF | FFD | OPT")
    print("-" * 80)

    for f_path, n, res, t in outputs:
        n_values.append(n)
        for k in results.keys():
            results[k].append(res[k])
            times[k].append(t[k])

        opt_val = res["OPT"] if res["OPT"] is not None else "N/A"
        print(f"{os.path.basename(f_path):<20} | {n:<4} | {res['NF']:<2} | {res['FF']:<2} | {res['BF']:<2} | {res['WF']:<2} | {res['FFD']:<3} | {opt_val}")

    # --- TABEL TIMPI (SECUNDE) ---
    print("\n\n--- TABEL TIMPI (SECUNDE) ---\n")
    print(f"| N  |  NF (s)  |  FF (s)  |  BF (s)  |  WF (s)  |  FFD (s) |  OPT (s) |")
    print(f"|----|----------|----------|----------|----------|----------|----------|")
    for i in range(len(n_values)):
        opt_t = f"{times['OPT'][i]:.6f}" if times["OPT"][i] is not None else "N/A"
        print(f"| {n_values[i]} | {times['NF'][i]:.6f} | {times['FF'][i]:.6f} | {times['BF'][i]:.6f} | {times['WF'][i]:.6f} | {times['FFD'][i]:.6f} | {opt_t} |")

        # --- Salvare tabele in CSV ---
    with open("rezultate_bins.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Test","N", "NF", "FF", "BF", "WF", "FFD", "OPT"])
        for i in range(len(n_values)):
            writer.writerow([
                os.path.basename(f_path),
                n_values[i],
                results["NF"][i],
                results["FF"][i],
                results["BF"][i],
                results["WF"][i],
                results["FFD"][i],
                results["OPT"][i] if results["OPT"][i] is not None else "N/A"
            ])

    with open("rezultate_timpi.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["N", "NF (s)", "FF (s)", "BF (s)", "WF (s)", "FFD (s)", "OPT (s)"])
        for i in range(len(n_values)):
            writer.writerow([
                n_values[i],
                f"{times['NF'][i]:.6f}",
                f"{times['FF'][i]:.6f}",
                f"{times['BF'][i]:.6f}",
                f"{times['WF'][i]:.6f}",
                f"{times['FFD'][i]:.6f}",
                f"{times['OPT'][i]:.6f}" if times["OPT"][i] is not None else "N/A"
            ])

    # --- Grafice ---
    plt.figure(figsize=(12, 7))
    for name in results.keys():
        valid_n = [n_values[i] for i in range(len(n_values)) if results[name][i] is not None]
        valid_res = [results[name][i] for i in range(len(results[name])) if results[name][i] is not None]
        plt.plot(valid_n, valid_res, label=name, marker=('s' if name=="OPT" else 'o'))
    plt.title("Eficiența împachetării (Număr de Bins)")
    plt.xlabel("N")
    plt.ylabel("Bins")
    plt.legend()
    plt.grid(True)
    plt.savefig("grafic_bins.png")

    plt.figure(figsize=(12, 7))
    for name in times.keys():
        valid_n = [n_values[i] for i in range(len(n_values)) if times[name][i] is not None]
        valid_times = [times[name][i] for i in range(len(times[name])) if times[name][i] is not None]
        plt.plot(valid_n, valid_times, label=name, marker=('s' if name=="OPT" else 'o'))
    plt.yscale('log')
    plt.title("Timp de execuție (Scală Logaritmică)")
    plt.xlabel("N")
    plt.ylabel("Secunde")
    plt.legend()
    plt.grid(True)
    plt.savefig("grafic_timp.png")

run_benchmark()