import csv
import re
import statistics
from collections import defaultdict
from urllib.parse import urlparse


def percentile(data, p):
    if not data:
        return 0.0
    ordered = sorted(data)
    k = (len(ordered) - 1) * p / 100
    f = int(k)
    c = min(f + 1, len(ordered) - 1)
    if f == c:
        return float(ordered[f])
    return ordered[f] + (ordered[c] - ordered[f]) * (k - f)


def stats(data):
    n = len(data)
    return {
        "samples": n,
        "avg": sum(data) / n,
        "median": statistics.median(data),
        "p90": percentile(data, 90),
        "p95": percentile(data, 95),
        "p99": percentile(data, 99),
        "max": max(data),
    }


def site_name(host):
    if "stg" in host or "azurefd" in host:
        return "Stage"
    return "Prod"


CSV_PATH = r"C:\Users\Shiva Dev\Downloads\FH - Load Testing\Aggregate_Report.csv"
rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8-sig")))

by_load_site = defaultdict(list)
by_site = defaultdict(list)
errors = defaultdict(int)
timestamps = []

for row in rows:
    match = re.search(r"(\d+)\s+Users", row["threadName"])
    users = int(match.group(1)) if match else 0
    host = urlparse(row["URL"]).netloc
    site = site_name(host)
    elapsed = int(row["elapsed"])
    latency = int(row.get("Latency") or 0)
    connect = int(row.get("Connect") or 0)
    by_load_site[(users, site)].append(elapsed)
    by_site[site].append({"elapsed": elapsed, "latency": latency, "connect": connect})
    timestamps.append(int(row["timeStamp"]))
    if row.get("success", "true").lower() != "true":
        errors[site] += 1

print("=== Stage vs Prod by load level ===\n")
header = f"{'Load':>6} {'Site':>6} {'Samples':>8} {'Avg':>7} {'Med':>7} {'p90':>7} {'p95':>7} {'p99':>7} {'Max':>7}"
print(header)
print("-" * len(header))

for key in sorted(by_load_site):
    s = stats(by_load_site[key])
    print(
        f"{key[0]:>6} {key[1]:>6} {s['samples']:>8} "
        f"{s['avg']:>7.0f} {s['median']:>7.0f} {s['p90']:>7.0f} "
        f"{s['p95']:>7.0f} {s['p99']:>7.0f} {s['max']:>7.0f}"
    )

print("\n=== Comparison (Prod vs Stage) ===\n")
for users in sorted({k[0] for k in by_load_site}):
    stage = stats(by_load_site.get((users, "Stage"), []))
    prod = stats(by_load_site.get((users, "Prod"), []))
    if not stage["samples"] or not prod["samples"]:
        continue
    avg_delta = ((prod["avg"] - stage["avg"]) / stage["avg"]) * 100
    p95_delta = ((prod["p95"] - stage["p95"]) / stage["p95"]) * 100
    winner_avg = "Stage faster" if stage["avg"] < prod["avg"] else "Prod faster"
    winner_p95 = "Stage faster" if stage["p95"] < prod["p95"] else "Prod faster"
    print(f"{users} users:")
    print(f"  Avg:  Stage {stage['avg']:.0f} ms | Prod {prod['avg']:.0f} ms | Delta {avg_delta:+.1f}% | {winner_avg}")
    print(f"  p95:  Stage {stage['p95']:.0f} ms | Prod {prod['p95']:.0f} ms | Delta {p95_delta:+.1f}% | {winner_p95}")
    print()

duration_sec = (max(timestamps) - min(timestamps)) / 1000
print("=== Overall summary ===\n")
for site in ("Stage", "Prod"):
    data = by_site[site]
    s = stats([d["elapsed"] for d in data])
    avg_lat = sum(d["latency"] for d in data) / len(data)
    avg_conn = sum(d["connect"] for d in data) / len(data)
    err_pct = (errors[site] / len(data)) * 100
    rps = len(data) / duration_sec
    print(f"{site}: {s['samples']} requests, {err_pct:.1f}% errors, ~{rps:.1f} req/s")
    print(f"  Response time avg {s['avg']:.0f} ms (p95 {s['p95']:.0f} ms)")
    print(f"  Latency avg {avg_lat:.0f} ms | Connect avg {avg_conn:.0f} ms")
    print(f"  Test window: {duration_sec:.1f} seconds")
    print()
