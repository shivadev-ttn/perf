# FH Stage — k6 Load Tests

Parallel to JMeter (`FH - Load Testing`). JMeter folder is not modified.

## Install k6 (Windows)

```powershell
winget install GrafanaLabs.k6
```

Or download: https://grafana.com/docs/k6/latest/set-up/install-k6/

Verify:

```powershell
k6 version
```

## Project layout

```
K\
├── k6\
│   ├── fh-stage.js          # main test (3 APIs in sequence)
│   ├── lib\
│   │   ├── config.js        # URLs, thresholds, think time
│   │   ├── headers.js       # HTTP headers (same as JMeter)
│   │   └── apis.js          # requests + checks
│   ├── results\             # JSON summaries after runs
│   ├── run-1user.bat
│   ├── run-10user.bat
│   └── run-50user.bat
└── gatling\                 # placeholder for later
```

## Run

Double-click a bat file, or from `k6` folder:

```powershell
k6 run fh-stage.js
```

Custom load:

```powershell
$env:VUS=10; $env:RAMP_TIME="10s"; $env:DURATION="90s"; k6 run fh-stage.js
```

## APIs (same as JMeter)

1. Offers Hotel List
2. Offers List
3. Locations Property Listing

## Checks & thresholds

| API | Functional checks | p95 threshold |
|-----|-------------------|---------------|
| Offers Hotel List | 200, hotels, country, hotelID | 3000 ms |
| Offers List | 200, regional-offer, offerName | 1000 ms |
| Locations Property Listing | 200, countryId, country, hotelID | 1000 ms |

Override thresholds:

```powershell
$env:OFFERS_HOTEL_MAX_MS=6000; $env:HEALTH_MAX_MS=1500; k6 run fh-stage.js
```

## HTML report (optional)

k6 outputs JSON summary. For HTML:

```powershell
k6 run --out json=results/run-1user.json fh-stage.js
```

Use [k6-reporter](https://github.com/benc-uk/k6-reporter) or Grafana Cloud k6 later if needed.
