@echo off
setlocal

REM ============================================================
REM  Push All Skills to ClawHub
REM  Publish 49 skills one by one with delay control
REM  (ClawHub has publish rate limits)
REM
REM  Usage:
REM    push-clawhub.bat [version] [delay_seconds]
REM      default version=1.7.0  delay=10 (seconds)
REM
REM  Notes:
REM    - Publishes all 49 skills (entry qa-test-skills + 48 subs)
REM    - Waits DELAY seconds after each push to avoid rate limit
REM    - Failed skills are recorded in push-failed.txt for retry
REM ============================================================

set "VER=%~1"
if "%VER%"=="" set "VER=1.7.0"

set "DELAY=%~2"
if "%DELAY%"=="" set "DELAY=10"

echo ============================================
echo  Pushing 49 skills to ClawHub
echo  Version: %VER%
echo  Delay between pushes: %DELAY%s
echo ============================================
echo.

set "FAILED_FILE=push-failed.txt"
if exist "%FAILED_FILE%" del "%FAILED_FILE%"

set "COUNT=0"

call :push qa-test-skills
call :push qa-agent-testing
call :push qa-ai-blindspot-compensation
call :push qa-ai-context-engineering
call :push qa-ai-output-critique
call :push qa-ai-prompt-strategy
call :push qa-api-testing
call :push qa-boundary-deep-dive
call :push qa-bug-lifecycle
call :push qa-bug-reporting
call :push qa-bug-root-cause-analysis
call :push qa-ci-cd-testing
call :push qa-code-review-for-test
call :push qa-combination-strategy
call :push qa-critical-thinking
call :push qa-domain-modeling
call :push qa-execution-observation
call :push qa-expert-review
call :push qa-exploratory-testing
call :push qa-heuristic-checklist
call :push qa-input-validation
call :push qa-mobile-testing
call :push qa-output-validation
call :push qa-quality-metrics
call :push qa-question-framework
call :push qa-regression-testing
call :push qa-release-risk-governance
call :push qa-req-deconstruction
call :push qa-requirement-review
call :push qa-retrospective
call :push qa-risk-intuition
call :push qa-scenario-tree
call :push qa-shift-left
call :push qa-shift-right
call :push qa-specialized-testing
call :push qa-stakeholder-communication
call :push qa-state-transition
call :push qa-team-coaching
call :push qa-tech-debt-management
call :push qa-tech-selection
call :push qa-test-automation-arch
call :push qa-test-case-design
call :push qa-test-data-engineering
call :push qa-test-env-data
call :push qa-test-estimation
call :push qa-test-leadership
call :push qa-test-reporting
call :push qa-test-strategy-design
call :push qa-testability-advocacy

echo.
echo ============================================
echo  Done. Pushed %COUNT%/49 skills (version %VER%)
if exist "%FAILED_FILE%" (
  echo  FAILED skills recorded in %FAILED_FILE%:
  type "%FAILED_FILE%"
) else (
  echo  All 49 skills published successfully!
)
echo ============================================
endlocal
exit /b 0

REM ------------------------------------------------------------
REM  push <slug> - publish one skill, then wait DELAY seconds
REM ------------------------------------------------------------
:push
set "SLUG=%~1"
set /a COUNT+=1
echo [%COUNT%/49] Publishing %SLUG% ...
call clawhub skill publish "./skills/%SLUG%" --slug %SLUG% --version %VER%
if errorlevel 1 (
  echo  !! FAILED: %SLUG% 1>>"%FAILED_FILE%"
  echo  !! %SLUG% FAILED (see %FAILED_FILE%)
) else (
  echo  OK: %SLUG%
)
timeout /t %DELAY% /nobreak >nul
exit /b 0
