# JMeter Load Test — Report Guide (200 Users)

This document first shows **what we achieved** in the 200-user load test, then explains how to read results, Think Time, and other concepts from `FH - Stage.jmx`.

---

## Results Achieved — 200 Users, 3 minutes

### Test at a glance

| Item | Value |
|------|-------|
| **Thread group** | 05 - 200 Users |
| **Virtual users (load)** | **200** concurrent users |
| **Test duration** | **180 seconds (3 minutes)** |
| **Ramp-up** | 30 seconds |
| **API host** | www.frasershospitality.com |
| **APIs tested per loop** | 1 (Prod Property Listing Sidebar) |
| **Think Time** | 500–1500 ms between each API call |
| **Overall result** | **0% errors — all requests passed** |


### Per-endpoint results

| API | Samples | Avg (ms) | 90% Line (ms) | 99% Line (ms) | Error % | Throughput (/sec) |
|-----|--------:|---------:|--------------:|--------------:|--------:|------------------:|
| Prod Property Listing Sidebar | 4,000 | 288 | 397 | 2,504 | 0.00% | 22.2 |
| **TOTAL** | **4,000** | **288** | **397** | **2,504** | **0.00%** | **22.2** |


### How many times did each user hit the APIs?

**Start with One User**

> One virtual user runs one **loop**: Prod Property Listing Sidebar, then repeats until the test ends.
>
> In 3 minutes, that one user completed about **20 full loops**.
>
> So for **one user**:
> - **20 hits** to **each** API (one endpoint)
> - **20 total hits** across all 1 APIs (20 × 1)

**Step-by-Step Calculation**

```text
Step 1 — one user, one API:       ~20 calls
Step 2 — one user, all 1 APIs:    20 × 1 = ~20 calls

Step 3 — 200 users, one API:      20 × 200 = ~4,000 calls
Step 4 — 200 users, all 1 APIs:   20 × 200 = ~4,000 calls  (actual: 4,000)
```

| Scope | Per 1 API | All 1 APIs |
|-------|----------:|-----------:|
| **1 user** | ~20 | ~20 |
| **200 users** | ~4,000 | ~4,000 |



### What we achieved (summary)

> **200 virtual users** ran at the same time for **3 minutes**. Each user repeatedly called **1 APIs** with realistic pauses between requests. The API stayed **stable with 0% failures**. Average response time was **288 ms**, and **90% of requests finished under 397 ms**.

**Load testing here means:** 200 users hit the APIs many times — **not** 4,000 users.  
~4,000 is how many times **one endpoint was called in total** by all 200 users together.


### Conclusion (200 Users)

| Area | Finding |
|------|---------|
| **Stability** | API handled 200 concurrent users with **0% errors** |
| **Speed** | Average **288 ms**; 90% of requests under **397 ms** |
| **Capacity** | Throughput **~22 requests/sec** sustained over test duration |
| **Worst case** | Max single request **4.4 sec** |
| **Next step** | Compare with 100 users (baseline) and 500 users (higher load) |

### Ready-to-present statement

> We load-tested the FH Stage API with **200 concurrent virtual users** for **180 seconds (3 minutes)** against **www.frasershospitality.com**. Each simulated user called **1 endpoints** in a loop with **0.5–1.5 second pauses** between actions. We sent **4,000 total requests** with **zero failures**. Average response time was **288 ms**, **90% of requests completed under 397 ms**, and the server sustained **~22 requests per second**. The API is **stable at 200 users**.


### Aggregate Report — overall (TOTAL)

| Metric | Result | Meaning |
|--------|-------:|---------|
| **# Samples** | 4,000 | Total HTTP requests in test run |
| **Average** | 288 ms | Typical response time |
| **Median** | 215 ms | Half of requests faster than this |
| **90% Line** | 397 ms | 90% of requests under this time |
| **95% Line** | 571 ms | 95% of requests under this time |
| **99% Line** | 2,504 ms | 99% of requests under this time |
| **Min** | 102 ms | Fastest request |
| **Max** | 4,448 ms | Slowest request |
| **Error %** | **0.00%** | Failed requests |
| **Throughput** | **22.2 /sec** | Requests completed per second |
| **Received KB/sec** | 934.05 | Data sent back by API per second |
| **Sent KB/sec** | 63.13 | Data sent to API per second |



---

## 1. Test setup (example: 200 Users)

From **05 - 200 Users** in `FH - Stage.jmx`:

| Setting | Value | Meaning |
|---------|------:|---------|
| Virtual users | 200 | 200 simulated users hit the API at the same time |
| Ramp-up | 30 sec | All 200 users become active within 30 seconds |
| Duration | 180 sec | Test stops after scheduled duration |
| Loop | Infinite | Each user keeps repeating until duration ends |
| API host | www.frasershospitality.com | Stage/production host under test |

### Timeline

```text
0s ─── 30s ─────────────────────── 180s
     ramp-up   200 users looping         STOP
```

---

## 2. Think Time (spacing between requests)

| Setting | Value |
|---------|------:|
| Timer type | Uniform Random Timer |
| Constant delay | 500 ms |
| Random range | 0–1000 ms |
| **Actual wait** | **500–1500 ms** before each API call |

### Order of execution (one loop)

```text
Wait 0.5–1.5 sec  →  Prod Property Listing Sidebar
→ loop again until test ends
```

---

## 3. Samples vs virtual users (important)

**4,000 samples does NOT mean 4,000 users.**

| Term | Meaning |
|------|---------|
| **Virtual user** | One simulated person (e.g. **200** in your test) |
| **Sample** | One HTTP request (one hit to an API) |

| Metric | Value |
|--------|------:|
| Virtual users | 200 |
| Samples per endpoint | ~4,000 |
| Total samples (1 APIs) | ~4,000 |

---

## 4. Aggregate Report — column guide

Source file: `Aggregate_Report.csv`

| Column | What it means | Example (200 users) |
|--------|---------------|--------------------------|
| **Label** | API request name | Prod Property Listing Sidebar |
| **# Samples** | How many times this API was called | ~4,000 per endpoint |
| **Average** | Mean response time (ms) | 288 ms |
| **90% Line** | 90% of requests finished within this time | 397 ms |
| **Error %** | Failed requests | 0.00% |
| **Throughput** | Requests completed per second | 22.2/sec (total) |

---

## 5. All thread groups in `FH - Stage.jmx`

| Users | Ramp-up | Duration | Thread group |
|------:|--------:|---------:|--------------|
| 1 | 1 sec | 10 sec | 01 - 1 User Baseline |
| 10 | 10 sec | 90 sec | 02 - 10 Users |
| 50 | 25 sec | 180 sec | 03 - 50 Users |
| 100 | 30 sec | 240 sec | 04 - 100 Users |
| 200 | 30 sec | 180 sec | 05 - 200 Users |
| 500 | 60 sec | 360 sec | 06 - 500 Users |
| 700 | 90 sec | 420 sec | 07 - 700 Users |
| 1000 | 120 sec | 600 sec | 08 - 1000 Users |

**Enable only ONE thread group at a time.** Run from low to high and compare reports.

---

## 6. Files in this project

| File | Purpose |
|------|---------|
| `FH - Stage.jmx` | JMeter test plan |
| `Aggregate_Report.csv` | Exported Aggregate Report (sample-level) |
| `LOAD-TEST-REPORT-GUIDE - 200 Users.md` | This guide (auto-generated) |
| `generate-readme.bat` | Regenerate this guide from CSV + JMX |

---

*Generated by `scripts/generate-load-test-readme.py` — FH Stage API Load Test Load Testing Documentation*
