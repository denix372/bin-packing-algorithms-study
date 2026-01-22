import matplotlib.pyplot as plt
import csv
import os

def plot_backtracking_results():
    # Read results from CSV
    bins_file = "rezultate_bins.csv"
    times_file = "rezultate_timpi.csv"
    n_values = []
    opt_bins = []
    opt_times = []
    test_names = []

    # Read bins and OPT values
    with open(bins_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            n = int(row["N"])
            test_names.append(row["Test"])
            n_values.append(n)
            opt_bins.append(int(row["OPT"]) if row["OPT"] != "N/A" else None)

    # Read OPT times
    with open(times_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            opt_times.append(float(row["OPT (s)"]) if row["OPT (s)"] != "N/A" else None)


    # Filter only tests with OPT results
    valid_indices = [i for i, v in enumerate(opt_bins) if v is not None]
    valid_n = [n_values[i] for i in valid_indices]
    valid_bins = [opt_bins[i] for i in valid_indices]
    valid_times = [opt_times[i] for i in valid_indices]

    # --- Comparison for first 10 tests (all algorithms) ---
    bins_file = "rezultate_bins.csv"
    times_file = "rezultate_timpi.csv"
    results = {k: [] for k in ["NF", "FF", "BF", "WF", "FFD", "OPT"]}
    times = {k: [] for k in ["NF", "FF", "BF", "WF", "FFD", "OPT"]}
    n_values_all = []
    with open(bins_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            n = int(row["N"])
            n_values_all.append(n)
            for k in results.keys():
                results[k].append(int(row[k]) if row[k] != "N/A" else None)
    with open(times_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            for k in times.keys():
                times[k].append(float(row[f"{k} (s)"]) if row[f"{k} (s)"] != "N/A" else None)

    # First 10 tests (small)
    first10_indices = list(range(10))
    first10_n = [n_values_all[i] for i in first10_indices]

    # Plot bins comparison for first 10 tests
    plt.figure(figsize=(10, 6))
    for name in results.keys():
        vals = [results[name][i] for i in first10_indices if results[name][i] is not None]
        ns = [n_values_all[i] for i in first10_indices if results[name][i] is not None]
        plt.plot(ns, vals, marker=('s' if name=="OPT" else 'o'), label=name)
    plt.title('Comparatie Algoritmi - Număr de Bins (Primele 10 teste)')
    plt.xlabel('N')
    plt.ylabel('Bins')
    plt.legend()
    plt.grid(True)
    plt.savefig('grafic_backtracking_vs_algorithms_bins.png')

    # Plot time comparison for first 10 tests
    plt.figure(figsize=(10, 6))
    for name in times.keys():
        vals = [times[name][i] for i in first10_indices if times[name][i] is not None]
        ns = [n_values_all[i] for i in first10_indices if times[name][i] is not None]
        plt.plot(ns, vals, marker=('s' if name=="OPT" else 'o'), label=name)
    plt.yscale('log')
    plt.title('Comparatie Algoritmi - Timp de execuție (Primele 10 teste)')
    plt.xlabel('N')
    plt.ylabel('Secunde')
    plt.legend()
    plt.grid(True)
    plt.savefig('grafic_backtracking_vs_algorithms_timp.png')

    # --- Original backtracking-only plots ---
    plt.figure(figsize=(10, 6))
    plt.plot(valid_n, valid_bins, marker='s', color='purple', label='Backtracking OPT bins')
    plt.title('Backtracking OPT - Număr de Bins')
    plt.xlabel('N')
    plt.ylabel('Bins')
    plt.grid(True)
    plt.legend()
    plt.savefig('grafic_backtracking_bins.png')

    plt.figure(figsize=(10, 6))
    plt.plot(valid_n, valid_times, marker='s', color='red', label='Backtracking OPT time (s)')
    plt.yscale('log')
    plt.title('Backtracking OPT - Timp de execuție (log)')
    plt.xlabel('N')
    plt.ylabel('Secunde')
    plt.grid(True)
    plt.legend()
    plt.savefig('grafic_backtracking_timp.png')


def plot_selected_tests():
    # Read results from CSV
    bins_file = "rezultate_bins.csv"
    times_file = "rezultate_timpi.csv"

    selected_ns = [15, 40, 85, 130, 175, 220, 265, 310, 355, 400, 445]
    selected_indices = []
    n_values = []
    results = {k: [] for k in ["NF", "FF", "BF", "WF", "FFD", "OPT"]}
    times = {k: [] for k in ["NF", "FF", "BF", "WF", "FFD", "OPT"]}

    # Read bins and OPT values
    with open(bins_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            n = int(row["N"])
            n_values.append(n)
            for k in results.keys():
                results[k].append(int(row[k]) if row[k] != "N/A" else None)

    # Read times
    with open(times_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            for k in times.keys():
                times[k].append(float(row[f"{k} (s)"]) if row[f"{k} (s)"] != "N/A" else None)

    # Find indices for selected N
    for n in selected_ns:
        if n in n_values:
            selected_indices.append(n_values.index(n))

    plt.figure(figsize=(8, 5))
    for name in [k for k in results.keys() if k != "OPT"]:
        vals = [results[name][i] for i in selected_indices if results[name][i] is not None]
        ns = [n_values[i] for i in selected_indices if results[name][i] is not None]
        plt.plot(ns, vals, marker='o', label=name)
    plt.title('Algoritmi - Număr de Bins (N=15, 40, 85, 130, 175, 220, 265, 310, 355, 400, 445)')
    plt.xlabel('N')
    plt.ylabel('Bins')
    plt.legend()
    plt.grid(True)
    plt.savefig('grafic_selected_bins.png')

    plt.figure(figsize=(8, 5))
    for name in [k for k in times.keys() if k != "OPT"]:
        vals = [times[name][i] for i in selected_indices if times[name][i] is not None]
        ns = [n_values[i] for i in selected_indices if times[name][i] is not None]
        plt.plot(ns, vals, marker='o', label=name)
    plt.yscale('log')
    plt.title('Algoritmi - Timp de execuție (N=15, 40, 85, 130, 175, 220, 265, 310, 355, 400, 445)')
    plt.xlabel('N')
    plt.ylabel('Secunde')
    plt.legend()
    plt.grid(True)
    plt.savefig('grafic_selected_timp.png')


if __name__ == "__main__":
    plot_backtracking_results()
    plot_selected_tests()
