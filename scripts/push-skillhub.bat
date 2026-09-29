@echo off
setlocal

REM The SkillHub CLI prints a check mark (U+2713) after a successful publish.
REM On a GBK console that raises UnicodeEncodeError and exits non-zero,
REM which makes a SUCCESSFUL publish look like a failure. Force UTF-8.
set "PYTHONIOENCODING=utf-8"

REM ============================================================
REM  Push All Skills to SkillHub (official CLI)
REM  Publish 49 skills one by one with delay control
REM  (SkillHub has publish rate limits)
REM
REM  Usage:
REM    push-skillhub.bat [version] [delay_seconds]
REM      default version=1.8.0  delay=15 (seconds)
REM
REM  Prerequisites:
REM    - Official CLI: ~/.skillhub/skills_store_cli.py (skillhub 2026.8.5+)
REM      NOT the npm "skillhub" package (it has no publish command)
REM    - Logged in: python ~/.skillhub/skills_store_cli.py auth whoami
REM
REM  Notes:
REM    - Publishes all 49 skills (entry qa-test-skills + 48 subs)
REM    - Waits DELAY seconds after each push to avoid rate limit
REM      (8s is too short - gets rate-limited; 15s works)
REM    - Failed skills are recorded in push-skillhub-failed.txt for retry
REM      NOTE: verify against the platform version, not this file. It mixes
REM      real rate-limit failures with encoding false positives.
REM    - If push-skillhub-pending.txt exists, only those skills are pushed
REM      (rate-limit retry; avoids re-publishing completed ones).
REM      Delete that file to go back to publishing all 49.
REM    - Staging via stage_for_publish.py --platform skillhub adds a TOP-LEVEL
REM      displayName. The SkillHub CLI's frontmatter parser does not understand
REM      nesting and looks for the exact key "displayName"; the repo uses the
REM      spec-compliant "metadata.display-name", so the staged copy needs a
REM      bridge field. Source files stay spec-compliant.
REM ============================================================

set "VER=%~1"
if "%VER%"=="" set "VER=1.8.0"

set "DELAY=%~2"
if "%DELAY%"=="" set "DELAY=15"

REM CLI 解析顺序：
REM   1. SKILLHUB_CLI 环境变量（推荐，显式指定官方 CLI）
REM   2. %~dp0skills_store_cli.py —— 仓库内副本，可能已过期
REM 官方 CLI 装在 ~/.skillhub/skills_store_cli.py（2026.8.5+）。
REM 仓库里那份是 2026.3.3 的旧副本，且随发布变慢。默认走官方那份。
if not defined SKILLHUB_CLI set "SKILLHUB_CLI=%USERPROFILE%\.skillhub\skills_store_cli.py"
set "CLI=%SKILLHUB_CLI%"
if not exist "%CLI%" set "CLI=%~dp0skills_store_cli.py"
if not exist "%CLI%" (
  echo 找不到 SkillHub CLI。
  echo 请先安装官方 CLI，或用 SKILLHUB_CLI 指定路径。
  exit /b 1
)

set "STAGE=.publish-staging\skillhub"
if exist "%STAGE%" rmdir /s /q "%STAGE%"
if not exist "%STAGE%" mkdir "%STAGE%"

echo ============================================
echo  Pushing skills to SkillHub
echo  Version: %VER%
echo  Delay between pushes: %DELAY%s
echo ============================================
echo.

set "FAILED_FILE=push-skillhub-failed.txt"
if exist "%FAILED_FILE%" del "%FAILED_FILE%"

REM 待重试模式：存在 push-skillhub-pending.txt 时只推清单内的技能，
REM 避免重推已完成的（限流后重试场景）。删掉该文件即回到全量模式。
set "PENDING_FILE=push-skillhub-pending.txt"
set "ONLY_PENDING="
set "COUNT=0"
set "PLANNED=49"
if exist "%PENDING_FILE%" (
  set "ONLY_PENDING=1"
  set "PLANNED=0"
  for /f "usebackq delims=" %%L in ("%PENDING_FILE%") do set /a PLANNED+=1
) else (
  set "ONLY_PENDING="
  set "PLANNED=49"
)
REM echo 必须放在计数循环【之后】：批处理读到该行时就展开了 %PLANNED%
if defined ONLY_PENDING (
  echo  Mode: PENDING-ONLY, %PLANNED% skills from %PENDING_FILE%
) else (
  echo  Mode: ALL, %PLANNED% skills
)

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
echo  Done. Pushed %COUNT%/%PLANNED% skills to SkillHub (v%VER%)
if exist "%FAILED_FILE%" (
  echo  FAILED skills recorded in %FAILED_FILE%:
  type "%FAILED_FILE%"
) else (
  echo  All %PLANNED% skills published successfully!
)
echo ============================================
endlocal
exit /b 0

REM ------------------------------------------------------------
REM  push <slug> - publish one skill, then wait DELAY seconds
REM ------------------------------------------------------------
:push
set "SLUG=%~1"

REM pending 模式：不在清单里的直接跳过
if defined ONLY_PENDING (
  findstr /x /l /c:"%SLUG%" "%PENDING_FILE%" >nul
  if errorlevel 1 exit /b 0
)

set /a COUNT+=1

REM 先暂存：补顶层 displayName（SkillHub CLI 的解析器不认嵌套键）
REM 注意 1：DIR 必须在 for 循环【之前】清空。批处理读到该行时就展开了 %DIR%，
REM         循环之后再清空会把刚拿到的路径抹掉。
REM 注意 2：for /f ('...') 里不能出现双引号，cmd 会把命令截断、把引号里的内容
REM         当成独立命令执行（报「'xxx' 不是内部或外部命令」）。
REM         STAGE 路径本身不含空格，所以直接不加引号。
set "DIR="
for /f "delims=" %%P in ('python scripts\stage_for_publish.py %SLUG% --platform skillhub --out %STAGE% 2^>nul') do set "DIR=%%P"
if not defined DIR (
  echo [%COUNT%/%PLANNED%] Publishing %SLUG% ...
  echo  !! STAGE FAILED: %SLUG% 1>>"%FAILED_FILE%"
  timeout /t %DELAY% /nobreak >nul
  exit /b 0
)

echo [%COUNT%/%PLANNED%] Publishing %SLUG% ...
python "%CLI%" publish "%DIR%" --version %VER% --changelog "%VER%"

REM No if/else parenthesised block here: those have broken repeatedly in
REM this project (LF line endings, for /f quoting, and once BOTH branches
REM executing at once, which printed OK unconditionally and made the log
REM useless). goto has none of those hazards.
if errorlevel 1 goto :push_failed
echo  OK: %SLUG%
goto :push_finished

:push_failed
echo  %SLUG% 1>>"%FAILED_FILE%"
echo  !! %SLUG% FAILED ^(see %FAILED_FILE%^)

:push_finished
timeout /t %DELAY% /nobreak >nul
exit /b 0
