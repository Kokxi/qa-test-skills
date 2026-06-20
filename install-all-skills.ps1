# QA Test Skills 批量安装脚本 (Windows PowerShell)
# 一键安装所有48个skills

Write-Host "=== QA Test Skills 批量安装脚本 ===" -ForegroundColor Cyan
Write-Host ""

# 检查clawhub CLI是否安装
if (-not (Get-Command clawhub -ErrorAction SilentlyContinue)) {
    Write-Host "❌ clawhub CLI 未安装" -ForegroundColor Red
    Write-Host "请先安装: npm i -g clawhub" -ForegroundColor Yellow
    exit 1
}

Write-Host "开始安装所有skills..." -ForegroundColor Yellow
Write-Host ""

# 安装元skill
Write-Host "安装元skill: qa-test-skills" -ForegroundColor Cyan
clawhub install "@kokxi/qa-test-skills"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ qa-test-skills 安装成功" -ForegroundColor Green
} else {
    Write-Host "❌ qa-test-skills 安装失败" -ForegroundColor Red
}
Write-Host ""

# 安装所有技能
$skills = @(
    "qa-test-workflow",
    "qa-requirement-review",
    "qa-req-deconstruction",
    "qa-risk-intuition",
    "qa-heuristic-checklist",
    "qa-scenario-tree",
    "qa-boundary-deep-dive",
    "qa-combination-strategy",
    "qa-state-transition",
    "qa-domain-modeling",
    "qa-ai-context-engineering",
    "qa-ai-prompt-strategy",
    "qa-ai-output-critique",
    "qa-ai-blindspot-compensation",
    "qa-output-validation",
    "qa-test-reporting",
    "qa-agent-testing",
    "qa-expert-review",
    "qa-api-testing",
    "qa-mobile-testing",
    "qa-specialized-testing",
    "qa-code-review-for-test",
    "qa-test-strategy-design",
    "qa-release-risk-governance",
    "qa-quality-metrics",
    "qa-test-case-design",
    "qa-input-validation",
    "qa-test-estimation",
    "qa-exploratory-testing",
    "qa-tech-debt-management",
    "qa-test-automation-arch",
    "qa-ci-cd-testing",
    "qa-tech-selection",
    "qa-test-env-data",
    "qa-test-data-engineering",
    "qa-testability-advocacy",
    "qa-shift-left",
    "qa-shift-right",
    "qa-defect-lifecycle",
    "qa-bug-reporting",
    "qa-bug-root-cause-analysis",
    "qa-execution-observation",
    "qa-retrospective",
    "qa-stakeholder-communication",
    "qa-team-coaching",
    "qa-test-leadership",
    "qa-critical-thinking",
    "qa-question-framework"
)

Write-Host "安装所有技能..." -ForegroundColor Yellow
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($skill in $skills) {
    Write-Host "安装: $skill" -ForegroundColor Cyan
    clawhub install "@kokxi/$skill"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $skill 安装成功" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "❌ $skill 安装失败" -ForegroundColor Red
        $failCount++
    }
    Write-Host ""
    
    # 每次安装后等待1秒
    Start-Sleep -Seconds 1
}

Write-Host "=== 批量安装完成 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "安装结果:" -ForegroundColor Yellow
Write-Host "✅ 成功: $successCount 个" -ForegroundColor Green
Write-Host "❌ 失败: $failCount 个" -ForegroundColor Red
Write-Host ""
Write-Host "总共安装: $($successCount + $failCount) 个skills" -ForegroundColor Cyan
Write-Host ""
Write-Host "使用方式:" -ForegroundColor Yellow
Write-Host "1. 直接使用主工作流: 请帮我测试这个项目：[需求文档路径]" -ForegroundColor White
Write-Host "2. 单独使用技能: 帮我分析这个场景的边界：[场景描述]" -ForegroundColor White
Write-Host "3. 查看README获取更多使用说明" -ForegroundColor White