# QA Test Skills 鎵归噺瀹夎鑴氭湰 (Windows PowerShell)
# 涓€閿畨瑁呮墍鏈?8涓猻kills

Write-Host "=== QA Test Skills 鎵归噺瀹夎鑴氭湰 ===" -ForegroundColor Cyan
Write-Host ""

# 妫€鏌lawhub CLI鏄惁瀹夎
if (-not (Get-Command clawhub -ErrorAction SilentlyContinue)) {
    Write-Host "鉂?clawhub CLI 鏈畨瑁? -ForegroundColor Red
    Write-Host "璇峰厛瀹夎: npm i -g clawhub" -ForegroundColor Yellow
    exit 1
}

Write-Host "寮€濮嬪畨瑁呮墍鏈塻kills..." -ForegroundColor Yellow
Write-Host ""

# 瀹夎鍏僺kill
Write-Host "瀹夎鍏僺kill: qa-test-skills" -ForegroundColor Cyan
clawhub install "@kokxi/qa-test-skills"
if ($LASTEXITCODE -eq 0) {
    Write-Host "鉁?qa-test-skills 瀹夎鎴愬姛" -ForegroundColor Green
} else {
    Write-Host "鉂?qa-test-skills 瀹夎澶辫触" -ForegroundColor Red
}
Write-Host ""

# 瀹夎鎵€鏈夋妧鑳?$skills = @(
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

Write-Host "瀹夎鎵€鏈夋妧鑳?.." -ForegroundColor Yellow
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($skill in $skills) {
    Write-Host "瀹夎: $skill" -ForegroundColor Cyan
    clawhub install "@kokxi/$skill"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "鉁?$skill 瀹夎鎴愬姛" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "鉂?$skill 瀹夎澶辫触" -ForegroundColor Red
        $failCount++
    }
    Write-Host ""
    
    # 姣忔瀹夎鍚庣瓑寰?绉?    Start-Sleep -Seconds 1
}

Write-Host "=== 鎵归噺瀹夎瀹屾垚 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "瀹夎缁撴灉:" -ForegroundColor Yellow
Write-Host "鉁?鎴愬姛: $successCount 涓? -ForegroundColor Green
Write-Host "鉂?澶辫触: $failCount 涓? -ForegroundColor Red
Write-Host ""
Write-Host "鎬诲叡瀹夎: $($successCount + $failCount) 涓猻kills" -ForegroundColor Cyan
Write-Host ""
Write-Host "浣跨敤鏂瑰紡:" -ForegroundColor Yellow
Write-Host "1. 鐩存帴浣跨敤涓诲伐浣滄祦: 璇峰府鎴戞祴璇曡繖涓」鐩細[闇€姹傛枃妗ｈ矾寰刔" -ForegroundColor White
Write-Host "2. 鍗曠嫭浣跨敤鎶€鑳? 甯垜鍒嗘瀽杩欎釜鍦烘櫙鐨勮竟鐣岋細[鍦烘櫙鎻忚堪]" -ForegroundColor White
Write-Host "3. 鏌ョ湅README鑾峰彇鏇村浣跨敤璇存槑" -ForegroundColor White