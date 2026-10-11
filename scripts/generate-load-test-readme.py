#!/usr/bin/env python3
"""Generate LOAD-TEST-REPORT-GUIDE markdown from JMeter Aggregate_Report.csv + JMX."""

from __future__ import annotations

import csv
import re
import statistics
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse


def percentile(data: list[int], p: float) -> float:
    if not data:
        return 0.0
    ordered = sorted(data)
    k = (len(ordered) - 1) * p / 100
    f = int(k)
    c = min(f + 1, len(ordered) - 1)
    if f == c:
        return float(ordered[f])
    return ordered[f] + (ordered[c] - ordered[f]) * (k - f)


def fmt_int(value: float | int) -> str:
    return f"{int(round(value)):,}"


def fmt_ms(value: float, for_summary: bool = False) -> str:
    rounded = int(round(value))
    if for_summary and rounded >= 1000:
        seconds = rounded / 1000
        if abs(seconds - round(seconds)) < 0.05:
            return f"{int(round(seconds))} sec"
        return f"{seconds:.1f} sec"
    return f"{rounded:,} ms"


def fmt_pct(value: float) -> str:
    return f"{value:.2f}%"


def fmt_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds} seconds"
    minutes = seconds // 60
    rem = seconds % 60
    if rem == 0:
        label = "minute" if minutes == 1 else "minutes"
        return f"{seconds} seconds ({minutes} {label})"
    label = "minute" if minutes == 1 else "minutes"
    return f"{seconds} seconds ({minutes} {label} {rem} sec)"


def parse_thread_name(thread_name: str) -> tuple[str | None, int | None]:
    users_match = re.search(r"(\d+)\s+Users", thread_name)
    if not users_match:
        return None, None
    users = int(users_match.group(1))
    group_match = re.match(r"^(.+?\d+\s+Users)", thread_name)
    group_label = group_match.group(1).strip() if group_match else f"{users} Users"
    return group_label, users


def parse_jmx(jmx_path: Path) -> dict:
    tree = ET.parse(jmx_path)
    root = tree.getroot()

    project_name = "FH Stage API"
    base_url = ""
    think_constant = 500
    think_range = 1000
    api_labels: list[str] = []
    thread_groups: list[dict] = []

    for elem in root.iter():
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        if tag == "TestPlan" and elem.get("testname"):
            project_name = elem.get("testname", project_name)
        if tag == "stringProp" and elem.get("name") == "Argument.value":
            parent = elem
            # Walk up is awkward; BASE_URL handled below via variables block
        if tag == "elementProp" and elem.get("name") == "BASE_URL":
            for child in elem:
                if child.get("name") == "Argument.value" and child.text:
                    base_url = child.text.strip()
        if tag == "UniformRandomTimer":
            for child in elem:
                if child.get("name") == "ConstantTimer.delay" and child.text:
                    think_constant = int(child.text)
                if child.get("name") == "RandomTimer.range" and child.text:
                    think_range = int(child.text)
        if tag == "HTTPSamplerProxy" and elem.get("testname"):
            label = elem.get("testname", "").strip()
            if label and label not in api_labels:
                api_labels.append(label)
        if tag == "ThreadGroup" and elem.get("testname"):
            name = elem.get("testname", "")
            users = ramp = duration = None
            for child in elem:
                ctag = child.tag.split("}")[-1]
                if ctag == "intProp" and child.get("name") == "ThreadGroup.num_threads":
                    users = int(child.text or 0)
                if ctag == "intProp" and child.get("name") == "ThreadGroup.ramp_time":
                    ramp = int(child.text or 0)
                if ctag == "longProp" and child.get("name") == "ThreadGroup.duration":
                    duration = int(child.text or 0)
            if users is not None:
                thread_groups.append(
                    {
                        "name": name,
                        "users": users,
                        "ramp_up": ramp or 0,
                        "duration": duration or 0,
                    }
                )

    thread_groups.sort(key=lambda g: g["users"])
    return {
        "project_name": project_name,
        "base_url": base_url,
        "think_constant": think_constant,
        "think_range": think_range,
        "think_max": think_constant + think_range,
        "api_labels": api_labels,
        "thread_groups": thread_groups,
        "jmx_filename": jmx_path.name,
    }


def load_csv_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def compute_label_stats(rows: list[dict[str, str]], duration_sec: float) -> dict:
    by_label: dict[str, list[int]] = defaultdict(list)
    errors: dict[str, int] = defaultdict(int)
    bytes_recv = 0
    bytes_sent = 0

    for row in rows:
        label = row["label"]
        elapsed = int(row["elapsed"])
        by_label[label].append(elapsed)
        bytes_recv += int(row.get("bytes") or 0)
        bytes_sent += int(row.get("sentBytes") or 0)
        if row.get("success", "").lower() != "true":
            errors[label] += 1

    labels = sorted(by_label.keys())
    endpoint_stats = []
    all_elapsed: list[int] = []

    for label in labels:
        data = by_label[label]
        all_elapsed.extend(data)
        n = len(data)
        endpoint_stats.append(
            {
                "label": label,
                "samples": n,
                "average": sum(data) / n,
                "median": statistics.median(data),
                "p90": percentile(data, 90),
                "p95": percentile(data, 95),
                "p99": percentile(data, 99),
                "minimum": min(data),
                "maximum": max(data),
                "error_pct": (errors[label] / n) * 100 if n else 0.0,
                "throughput": n / duration_sec if duration_sec else 0.0,
            }
        )

    total_n = len(all_elapsed)
    total_errors = sum(errors.values())
    total = {
        "samples": total_n,
        "average": sum(all_elapsed) / total_n if total_n else 0.0,
        "median": statistics.median(all_elapsed) if all_elapsed else 0.0,
        "p90": percentile(all_elapsed, 90),
        "p95": percentile(all_elapsed, 95),
        "p99": percentile(all_elapsed, 99),
        "minimum": min(all_elapsed) if all_elapsed else 0,
        "maximum": max(all_elapsed) if all_elapsed else 0,
        "error_pct": (total_errors / total_n) * 100 if total_n else 0.0,
        "throughput": total_n / duration_sec if duration_sec else 0.0,
        "received_kb_sec": (bytes_recv / 1024) / duration_sec if duration_sec else 0.0,
        "sent_kb_sec": (bytes_sent / 1024) / duration_sec if duration_sec else 0.0,
        "error_count": total_errors,
    }

    return {"endpoints": endpoint_stats, "total": total, "labels": labels}


def detect_run_metadata(rows: list[dict[str, str]], jmx: dict) -> dict:
    thread_names = [row["threadName"] for row in rows]
    group_labels = []
    user_counts = []
    for name in thread_names:
        group, users = parse_thread_name(name)
        if group:
            group_labels.append(group)
        if users:
            user_counts.append(users)

    if not user_counts:
        raise ValueError("Could not detect virtual user count from threadName in CSV.")

    users = max(set(user_counts))
    thread_group_name = max(set(group_labels), key=len) if group_labels else f"{users} Users"

    matched_group = next((g for g in jmx["thread_groups"] if g["users"] == users), None)
    if matched_group:
        thread_group_name = matched_group["name"]
        ramp_up = matched_group["ramp_up"]
        planned_duration = matched_group["duration"]
    else:
        ramp_up = 0
        planned_duration = 0

    timestamps = [int(row["timeStamp"]) for row in rows]
    actual_duration_sec = max((max(timestamps) - min(timestamps)) / 1000, 1)

    urls = [row.get("URL", "") for row in rows if row.get("URL")]
    host = jmx["base_url"]
    if urls:
        parsed = urlparse(urls[0])
        host = parsed.netloc or host

    return {
        "users": users,
        "thread_group_name": thread_group_name,
        "ramp_up": ramp_up,
        "planned_duration": planned_duration,
        "actual_duration_sec": actual_duration_sec,
        "host": host,
    }


def loops_per_user(endpoint_stats: list[dict], users: int) -> int:
    if not endpoint_stats or users <= 0:
        return 0
    avg_samples = sum(item["samples"] for item in endpoint_stats) / len(endpoint_stats)
    return max(1, int(round(avg_samples / users)))


def overall_result_text(error_pct: float, error_count: int) -> str:
    if error_pct == 0:
        return "**0% errors — all requests passed**"
    return f"**{fmt_pct(error_pct)} errors** — {error_count:,} failed out of total requests"


def stability_text(error_pct: float, error_count: int) -> str:
    if error_pct == 0:
        return "stable with 0% failures"
    return f"handled with {fmt_pct(error_pct)} errors ({error_count:,} failures)"


def duration_label(seconds: int) -> str:
    text = fmt_duration(seconds)
    if "(" in text:
        return text.split("(", 1)[1].rstrip(")")
    return text


def ordered_labels(jmx_labels: list[str], stats_labels: list[str]) -> list[str]:
    stats_set = set(stats_labels)
    ordered = [label for label in jmx_labels if label in stats_set]
    for label in sorted(stats_labels):
        if label not in ordered:
            ordered.append(label)
    return ordered


def conclusion_stability(users: int, error_pct: float) -> str:
    if error_pct == 0:
        return f"API handled {users} concurrent users with **0% errors**"
    return f"API handled {users} concurrent users with **{fmt_pct(error_pct)} errors**"


def next_step_text(users: int, thread_groups: list[dict]) -> str:
    sorted_users = [g["users"] for g in thread_groups]
    lower = [u for u in sorted_users if u < users]
    higher = [u for u in sorted_users if u > users]
    parts = []
    if lower:
        label = "user" if lower[-1] == 1 else "users"
        parts.append(f"{lower[-1]} {label} (baseline)")
    if higher:
        parts.append(f"{higher[0]} users (higher load)")
    return "Compare with " + " and ".join(parts) if parts else "Run other thread groups and compare"


def build_markdown(
    jmx: dict,
    meta: dict,
    stats: dict,
    csv_name: str,
) -> str:
    users = meta["users"]
    label_order = ordered_labels(jmx["api_labels"], stats["labels"])
    endpoint_by_label = {item["label"]: item for item in stats["endpoints"]}
    ordered_endpoints = [endpoint_by_label[label] for label in label_order]

    api_count = len(label_order)
    loops = loops_per_user(ordered_endpoints, users)
    per_api_all_users = int(round(sum(e["samples"] for e in ordered_endpoints) / api_count))
    per_user_per_api = loops
    per_user_all_apis = loops * api_count
    step4_estimate = per_user_all_apis * users
    total = stats["total"]

    duration_sec = meta["planned_duration"] or int(round(meta["actual_duration_sec"]))
    duration_text = fmt_duration(duration_sec)
    duration_heading = duration_label(duration_sec)
    loop_chain = " → ".join(label_order)
    api_list = ", ".join(label_order)
    think_min = jmx["think_constant"]
    think_max = jmx["think_max"]
    project = jmx["project_name"]
    jmx_file = jmx["jmx_filename"]
    host = meta["host"]
    thread_group = meta["thread_group_name"]
    ramp_up = meta["ramp_up"]

    error_pct = total["error_pct"]
    error_count = total["error_count"]
    result_line = overall_result_text(error_pct, error_count)
    summary_stability = stability_text(error_pct, error_count)
    avg_summary = fmt_ms(total["average"], for_summary=True)
    p90_summary = fmt_ms(total["p90"], for_summary=True)

  # Per-endpoint table rows
    endpoint_rows = []
    for item in ordered_endpoints:
        endpoint_rows.append(
            f"| {item['label']} | {fmt_int(item['samples'])} | {int(round(item['average'])):,} "
            f"| {int(round(item['p90'])):,} | {int(round(item['p99'])):,} | "
            f"{fmt_pct(item['error_pct'])} | {item['throughput']:.1f} |"
        )
    endpoint_rows.append(
        f"| **TOTAL** | **{fmt_int(total['samples'])}** | **{int(round(total['average'])):,}** "
        f"| **{int(round(total['p90'])):,}** | **{int(round(total['p99'])):,}** "
        f"| **{fmt_pct(error_pct)}** | **{total['throughput']:.1f}** |"
    )

    thread_group_table = "\n".join(
        f"| {g['users']} | {g['ramp_up']} sec | {g['duration']} sec | {g['name']} |"
        for g in jmx["thread_groups"]
    )

    present_failures = (
        "with **zero failures**"
        if error_pct == 0
        else f"with **{fmt_pct(error_pct)} failures** ({error_count:,} errors)"
    )
    present_stability = (
        f"The API is **stable at {users} users**."
        if error_pct == 0
        else f"The API is **mostly stable at {users} users** but shows some failures under load."
    )

    return f"""# JMeter Load Test — Report Guide ({users} Users)

This document first shows **what we achieved** in the {users}-user load test, then explains how to read results, Think Time, and other concepts from `{jmx_file}`.

---

## Results Achieved — {users} Users, {duration_heading}

### Test at a glance

| Item | Value |
|------|-------|
| **Thread group** | {thread_group} |
| **Virtual users (load)** | **{users}** concurrent users |
| **Test duration** | **{duration_text}** |
| **Ramp-up** | {ramp_up} seconds |
| **API host** | {host} |
| **APIs tested per loop** | {api_count} ({api_list}) |
| **Think Time** | {think_min}–{think_max} ms between each API call |
| **Overall result** | {result_line} |


### Per-endpoint results

| API | Samples | Avg (ms) | 90% Line (ms) | 99% Line (ms) | Error % | Throughput (/sec) |
|-----|--------:|---------:|--------------:|--------------:|--------:|------------------:|
{chr(10).join(endpoint_rows)}


### How many times did each user hit the APIs?

**Start with One User**

> One virtual user runs one **loop**: {loop_chain}, then repeats until the test ends.
>
> In {duration_heading}, that one user completed about **{loops} full loops**.
>
> So for **one user**:
> - **{loops} hits** to **each** API (one endpoint)
> - **{per_user_all_apis} total hits** across all {api_count} APIs ({loops} × {api_count})

**Step-by-Step Calculation**

```text
Step 1 — one user, one API:       ~{per_user_per_api} calls
Step 2 — one user, all {api_count} APIs:    {per_user_per_api} × {api_count} = ~{per_user_all_apis} calls

Step 3 — {users} users, one API:      {per_user_per_api} × {users} = ~{per_user_per_api * users:,} calls
Step 4 — {users} users, all {api_count} APIs:   {per_user_all_apis} × {users} = ~{step4_estimate:,} calls  (actual: {fmt_int(total['samples'])})
```

| Scope | Per 1 API | All {api_count} APIs |
|-------|----------:|-----------:|
| **1 user** | ~{per_user_per_api} | ~{per_user_all_apis} |
| **{users} users** | ~{per_api_all_users:,} | ~{fmt_int(total['samples'])} |



### What we achieved (summary)

> **{users} virtual users** ran at the same time for **{duration_heading}**. Each user repeatedly called **{api_count} APIs** with realistic pauses between requests. The API stayed **{summary_stability}**. Average response time was **{avg_summary}**, and **90% of requests finished under {p90_summary}**.

**Load testing here means:** {users} users hit the APIs many times — **not** {per_api_all_users:,} users.  
~{per_api_all_users:,} is how many times **one endpoint was called in total** by all {users} users together.


### Conclusion ({users} Users)

| Area | Finding |
|------|---------|
| **Stability** | {conclusion_stability(users, error_pct)} |
| **Speed** | Average **{fmt_ms(total['average'])}**; 90% of requests under **{fmt_ms(total['p90'])}** |
| **Capacity** | Throughput **~{total['throughput']:.0f} requests/sec** sustained over test duration |
| **Worst case** | Max single request **{fmt_ms(total['maximum'], for_summary=True)}** |
| **Next step** | {next_step_text(users, jmx['thread_groups'])} |

### Ready-to-present statement

> We load-tested the {project.replace(' Load Test', '')} with **{users} concurrent virtual users** for **{duration_text}** against **{host}**. Each simulated user called **{api_count} endpoints** in a loop with **{think_min / 1000:.1f}–{think_max / 1000:.1f} second pauses** between actions. We sent **{fmt_int(total['samples'])} total requests** {present_failures}. Average response time was **{fmt_ms(total['average'])}**, **90% of requests completed under {fmt_ms(total['p90'])}**, and the server sustained **~{total['throughput']:.0f} requests per second**. {present_stability}


### Aggregate Report — overall (TOTAL)

| Metric | Result | Meaning |
|--------|-------:|---------|
| **# Samples** | {fmt_int(total['samples'])} | Total HTTP requests in test run |
| **Average** | {fmt_ms(total['average'])} | Typical response time |
| **Median** | {fmt_ms(total['median'])} | Half of requests faster than this |
| **90% Line** | {fmt_ms(total['p90'])} | 90% of requests under this time |
| **95% Line** | {fmt_ms(total['p95'])} | 95% of requests under this time |
| **99% Line** | {fmt_ms(total['p99'])} | 99% of requests under this time |
| **Min** | {fmt_ms(total['minimum'])} | Fastest request |
| **Max** | {fmt_ms(total['maximum'])} | Slowest request |
| **Error %** | **{fmt_pct(error_pct)}** | Failed requests |
| **Throughput** | **{total['throughput']:.1f} /sec** | Requests completed per second |
| **Received KB/sec** | {total['received_kb_sec']:,.2f} | Data sent back by API per second |
| **Sent KB/sec** | {total['sent_kb_sec']:.2f} | Data sent to API per second |



---

## 1. Test setup (example: {users} Users)

From **{thread_group}** in `{jmx_file}`:

| Setting | Value | Meaning |
|---------|------:|---------|
| Virtual users | {users} | {users} simulated users hit the API at the same time |
| Ramp-up | {ramp_up} sec | All {users} users become active within {ramp_up} seconds |
| Duration | {duration_sec} sec | Test stops after scheduled duration |
| Loop | Infinite | Each user keeps repeating until duration ends |
| API host | {host} | Stage/production host under test |

### Timeline

```text
0s ─── {ramp_up}s ─────────────────────── {duration_sec}s
     ramp-up   {users} users looping         STOP
```

---

## 2. Think Time (spacing between requests)

| Setting | Value |
|---------|------:|
| Timer type | Uniform Random Timer |
| Constant delay | {think_min} ms |
| Random range | 0–{jmx['think_range']} ms |
| **Actual wait** | **{think_min}–{think_max} ms** before each API call |

### Order of execution (one loop)

```text
{chr(10).join(f'Wait {think_min / 1000:.1f}–{think_max / 1000:.1f} sec  →  {label}' for label in label_order)}
→ loop again until test ends
```

---

## 3. Samples vs virtual users (important)

**{per_api_all_users:,} samples does NOT mean {per_api_all_users:,} users.**

| Term | Meaning |
|------|---------|
| **Virtual user** | One simulated person (e.g. **{users}** in your test) |
| **Sample** | One HTTP request (one hit to an API) |

| Metric | Value |
|--------|------:|
| Virtual users | {users} |
| Samples per endpoint | ~{per_api_all_users:,} |
| Total samples ({api_count} APIs) | ~{fmt_int(total['samples'])} |

---

## 4. Aggregate Report — column guide

Source file: `{csv_name}`

| Column | What it means | Example ({users} users) |
|--------|---------------|--------------------------|
| **Label** | API request name | {label_order[0]} |
| **# Samples** | How many times this API was called | ~{per_api_all_users:,} per endpoint |
| **Average** | Mean response time (ms) | {int(round(total['average'])):,} ms |
| **90% Line** | 90% of requests finished within this time | {int(round(total['p90'])):,} ms |
| **Error %** | Failed requests | {fmt_pct(error_pct)} |
| **Throughput** | Requests completed per second | {total['throughput']:.1f}/sec (total) |

---

## 5. All thread groups in `{jmx_file}`

| Users | Ramp-up | Duration | Thread group |
|------:|--------:|---------:|--------------|
{thread_group_table}

**Enable only ONE thread group at a time.** Run from low to high and compare reports.

---

## 6. Files in this project

| File | Purpose |
|------|---------|
| `{jmx_file}` | JMeter test plan |
| `{csv_name}` | Exported Aggregate Report (sample-level) |
| `LOAD-TEST-REPORT-GUIDE - {users} Users.md` | This guide (auto-generated) |
| `generate-readme.bat` | Regenerate this guide from CSV + JMX |

---

*Generated by `scripts/generate-load-test-readme.py` — {project} Load Testing Documentation*
"""


def main() -> int:
    base_dir = Path(__file__).resolve().parent.parent
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else base_dir / "Aggregate_Report.csv"
    jmx_path = Path(sys.argv[2]) if len(sys.argv) > 2 else base_dir / "FH - Stage.jmx"

    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        return 1
    if not jmx_path.exists():
        print(f"JMX not found: {jmx_path}")
        return 1

    rows = load_csv_rows(csv_path)
    if not rows:
        print(f"No rows found in CSV: {csv_path}")
        return 1

    jmx = parse_jmx(jmx_path)
    meta = detect_run_metadata(rows, jmx)

    timestamps = [int(row["timeStamp"]) for row in rows]
    duration_sec = max((max(timestamps) - min(timestamps)) / 1000, 1)
    if meta["planned_duration"]:
        duration_sec = meta["planned_duration"]

    stats = compute_label_stats(rows, duration_sec)
    markdown = build_markdown(jmx, meta, stats, csv_path.name)

    output_path = base_dir / f"LOAD-TEST-REPORT-GUIDE - {meta['users']} Users.md"
    output_path.write_text(markdown, encoding="utf-8")

    print(f"Created: {output_path}")
    print(f"Users detected: {meta['users']}")
    print(f"Total samples: {stats['total']['samples']:,}")
    print(f"Error %: {stats['total']['error_pct']:.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
