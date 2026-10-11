@echo off
setlocal
cd /d "%~dp0"

if not exist results mkdir results

set VUS=50
set RAMP_TIME=25s
set DURATION=180s
set REPORT_TITLE=FH Stage API - 50 Users
set RESULT_FILE=results\run-50user-summary.json
set HTML_REPORT=results\run-50user-report.html

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
