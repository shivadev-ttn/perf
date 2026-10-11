# FH Load Testing — JMeter Project

Load testing for **Frasers Hospitality** APIs using JMeter.

**Project path:** `C:\Users\Shiva Dev\Downloads\FH - Load Testing`

Related tools (separate folders):

| Tool | Path |
|------|------|
| k6 | `C:\Users\Shiva Dev\Downloads\K\k6` |
| Gatling | `C:\Users\Shiva Dev\Downloads\K\gatling` |

---

## Latest test report

**Latest run:** **200 Users** — `05 - 200 Users` thread group

| Result | Value |
|--------|-------|
| Total requests | 4,000 |
| Error rate | **0.00%** |
| Average response time | **288 ms** |
| 90% line | **397 ms** |
| Throughput | **~22 req/sec** |
| API tested | Prod Property Listing Sidebar |
| Host | www.frasershospitality.com |

**Full report guide:** [LOAD-TEST-REPORT-GUIDE - 200 Users.md](LOAD-TEST-REPORT-GUIDE%20-%20200%20Users.md)

---

## Project files

| File | Purpose |
|------|---------|
| `FH - Stage.jmx` | JMeter test plan |
| `Aggregate_Report.csv` | Latest exported Aggregate Report (source for README) |
| `results\run-result.jtl` | Raw results file (CLI runs) |
| `reports\` | HTML dashboards (`run-1user`, `run-10user`, etc.) |
| `run-1user-and-report.bat` | CLI run + HTML report (1 user) |
| `run-10user-and-report.bat` | CLI run + HTML report (10 users) |
| `run-50user-and-report.bat` | CLI run + HTML report (50 users) |
| `generate-readme.bat` | Regenerate report guide from latest CSV |
| `generate-report.bat` | HTML report only (from existing JTL) |
| `LOAD-TEST-REPORT-GUIDE - <N> Users.md` | Auto-generated report documentation |

---

## APIs under test

Current JMeter plan includes (enable/disable per run):

1. Offers Hotel List
2. Offers List
3. Locations Property Listing

Latest CSV export contains **Prod Property Listing Sidebar** only (200-user production run).

---

## How to run (JMeter CLI)

1. Open `FH - Stage.jmx` in JMeter GUI.
2. Enable **one** thread group only.
3. Save the file.
4. Double-click the matching bat file:

```text
run-1user-and-report.bat
run-10user-and-report.bat
run-50user-and-report.bat
```

5. Open HTML report from `reports\` folder.

---

## How to regenerate this README / report guide

After a new test run:

1. Export **Aggregate Report** from JMeter to `Aggregate_Report.csv` (overwrite existing).
2. Run:

```text
generate-readme.bat
```

3. New file created: `LOAD-TEST-REPORT-GUIDE - <N> Users.md` based on detected user count in CSV.

---

## Thread groups (FH - Stage.jmx)

| Step | Thread group | Users | Ramp-up | Duration |
|------|--------------|------:|--------:|---------:|
| 01 | 1 User Baseline | 1 | 1s | 60s |
| 02 | 10 Users | 10 | 10s | 90s |
| 03 | 50 Users | 50 | 25s | 180s |
| 04 | 100 Users | 100 | 30s | 240s |
| 05 | 200 Users | 200 | 40s | 300s |
| 06 | 500 Users | 500 | 60s | 360s |
| 07 | 700 Users | 700 | 90s | 420s |
| 08 | 1000 Users | 1000 | 120s | 600s |

**Enable only ONE thread group at a time.**

---

## Assertions

| API | Functional checks | Duration threshold |
|-----|-------------------|------------------|
| Offers Hotel List | HTTP 200, hotels, country, hotelID | 3,000 ms |
| Offers List | HTTP 200, regional-offer, offerName | 1,000 ms |
| Locations Property Listing | HTTP 200, countryId, country, hotelID | 1,000 ms |

Tune via JMX variables: `OFFERS_HOTEL_MAX_MS`, `HEALTH_MAX_MS`.

---

## Assertions & failures

| Where to check | What you see |
|----------------|--------------|
| JMeter GUI — View Results in Tree | Assertion failure message per sample |
| JMeter GUI — Assertion Results | Failed assertions only |
| HTML report — Errors tab | Failed requests with reason |
| Aggregate Report — Error % | Overall failure rate |

---

*Last report guide generated from `Aggregate_Report.csv` — 200 Users, 0% errors.*
