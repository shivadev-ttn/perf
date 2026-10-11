# FH Stage — Gatling Load Tests

Parallel to JMeter (`FH - Load Testing`) and k6 (`K\k6`). JMeter folder is not modified.

## Prerequisites

1. **Java 17+** (you already have Java for JMeter)
2. **Apache Maven**

```powershell
java -version
mvn -version
```

Install Maven if needed:

```powershell
winget install Apache.Maven
```

## Project layout

```
gatling\
├── pom.xml
├── src\test\scala\fhstage\
│   └── FhStageSimulation.scala
├── run-1user.bat
├── run-10user.bat
├── run-50user.bat
└── target\gatling\          ← HTML reports generated here after run
```

## Run

From `gatling` folder:

```powershell
run-1user.bat
```

Or manually:

```powershell
mvn gatling:test -Dgatling.simulationClass=fhstage.FhStageSimulation -DloadProfile=1
```

| Bat file | Users | Ramp | Steady duration |
|----------|-------|------|-----------------|
| `run-1user.bat` | 1 | 1s | 60s |
| `run-10user.bat` | 10 | 10s | 80s |
| `run-50user.bat` | 50 | 25s | 155s |

## GUI / HTML report

Gatling generates a **built-in HTML dashboard** automatically.

After run, open:

```
target\gatling\<simulation-id>\index.html
```

Bat files open the latest report in your browser automatically.

Report includes:

- Global stats (OK/KO, mean, p95, p99)
- Per-request charts (your 3 APIs)
- Response time distribution
- Assertions pass/fail

## APIs (same as JMeter / k6)

1. Offers Hotel List
2. Offers List
3. Locations Property Listing

## Checks & assertions

| API | Checks | p95 threshold |
|-----|--------|---------------|
| Offers Hotel List | 200, hotels, country, hotelID | 3000 ms |
| Offers List | 200, regional-offer, offerName | 1000 ms |
| Locations Property Listing | 200, countryId, country, hotelID | 1000 ms |

Override thresholds:

```powershell
mvn gatling:test -Dgatling.simulationClass=fhstage.FhStageSimulation -DloadProfile=1 -DoffersHotelMaxMs=6000 -DhealthMaxMs=1500
```

## First run note

First `mvn gatling:test` downloads dependencies (Gatling + Scala). May take a few minutes.

## 3-tool layout

| Tool | Path |
|------|------|
| JMeter | `C:\Users\Shiva Dev\Downloads\FH - Load Testing` |
| k6 | `C:\Users\Shiva Dev\Downloads\K\k6` |
| Gatling | `C:\Users\Shiva Dev\Downloads\K\gatling` |
