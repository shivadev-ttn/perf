@echo off
setlocal
cd /d "%~dp0"

if not exist results mkdir results

set VUS=1
set RAMP_TIME=1s
set DURATION=60s
set REPORT_TITLE=FH Stage API - 1 User Baseline
set RESULT_FILE=results\run-1user-summary.json
set HTML_REPORT=results\run-1user-report.html

echo Running k6: %REPORT_TITLE%
k6 run fh-stage.js
if errorlevel 1 (
    echo k6 run failed.
    pause
    exit /b 1
)

echo Done.
echo JSON summary: %RESULT_FILE%
echo HTML report:  %HTML_REPORT%
pause
