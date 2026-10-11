@echo off
setlocal
cd /d "%~dp0"

if not exist results mkdir results

set VUS=10
set RAMP_TIME=10s
set DURATION=90s
set REPORT_TITLE=FH Stage API - 10 Users
set RESULT_FILE=results\run-10user-summary.json
set HTML_REPORT=results\run-10user-report.html

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
