@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

set LOAD_PROFILE=50
set REPORT_TITLE=FH Stage API - 50 Users

echo.
echo Running Gatling: %REPORT_TITLE%
echo.

call mvn -q gatling:test -Dgatling.simulationClass=fhstage.FhStageSimulation -DloadProfile=%LOAD_PROFILE%
if errorlevel 1 (
    echo Gatling run failed.
    pause
    exit /b 1
)

call :openLatestReport
pause
exit /b 0

:openLatestReport
set "LATEST="
for /f "delims=" %%i in ('dir /b /ad /o-d "target\gatling" 2^>nul') do (
    set "LATEST=target\gatling\%%i"
    goto :found
)
:found
if defined LATEST (
    echo.
    echo HTML report: %LATEST%\index.html
    start "" "%LATEST%\index.html"
) else (
    echo No report folder found under target\gatling
)
exit /b 0
