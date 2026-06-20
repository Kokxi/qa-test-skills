#!/bin/bash

# QA Test Skills 批量安装脚本
# 一键安装所有48个skills

echo "=== QA Test Skills 批量安装脚本 ==="
echo ""

# 检查clawhub CLI是否安装
if ! command -v clawhub &> /dev/null; then
    echo "❌ clawhub CLI 未安装"
    echo "请先安装: npm i -g clawhub"
    exit 1
fi

echo "开始安装所有skills..."
echo ""

# 安装元skill
echo "安装元skill: qa-test-skills"
clawhub install @kokxi/qa-test-skills
if [ $? -eq 0 ]; then
    echo "✅ qa-test-skills 安装成功"
else
    echo "❌ qa-test-skills 安装失败"
fi
echo ""

# 安装所有技能
skills=(
    "qa-test-workflow"
    "qa-requirement-review"
    "qa-req-deconstruction"
    "qa-risk-intuition"
    "qa-heuristic-checklist"
    "qa-scenario-tree"
    "qa-boundary-deep-dive"
    "qa-combination-strategy"
    "qa-state-transition"
    "qa-domain-modeling"
    "qa-ai-context-engineering"
    "qa-ai-prompt-strategy"
    "qa-ai-output-critique"
    "qa-ai-blindspot-compensation"
    "qa-output-validation"
    "qa-test-reporting"
    "qa-agent-testing"
    "qa-expert-review"
    "qa-api-testing"
    "qa-mobile-testing"
    "qa-specialized-testing"
    "qa-code-review-for-test"
    "qa-test-strategy-design"
    "qa-release-risk-governance"
    "qa-quality-metrics"
    "qa-test-case-design"
    "qa-input-validation"
    "qa-test-estimation"
    "qa-exploratory-testing"
    "qa-tech-debt-management"
    "qa-test-automation-arch"
    "qa-ci-cd-testing"
    "qa-tech-selection"
    "qa-test-env-data"
    "qa-test-data-engineering"
    "qa-testability-advocacy"
    "qa-shift-left"
    "qa-shift-right"
    "qa-defect-lifecycle"
    "qa-bug-reporting"
    "qa-bug-root-cause-analysis"
    "qa-execution-observation"
    "qa-retrospective"
    "qa-stakeholder-communication"
    "qa-team-coaching"
    "qa-test-leadership"
    "qa-critical-thinking"
    "qa-question-framework"
)

echo "安装所有技能..."
echo ""

success_count=0
fail_count=0

for skill in "${skills[@]}"; do
    echo "安装: $skill"
    clawhub install "@kokxi/$skill"
    
    if [ $? -eq 0 ]; then
        echo "✅ $skill 安装成功"
        ((success_count++))
    else
        echo "❌ $skill 安装失败"
        ((fail_count++))
    fi
    echo ""
done

echo "=== 批量安装完成 ==="
echo ""
echo "安装结果:"
echo "✅ 成功: $success_count 个"
echo "❌ 失败: $fail_count 个"
echo ""
echo "总共安装: $((success_count + fail_count)) 个skills"
echo ""
echo "使用方式:"
echo "1. 直接使用主工作流: 请帮我测试这个项目：[需求文档路径]"
echo "2. 单独使用技能: 帮我分析这个场景的边界：[场景描述]"
echo "3. 查看README获取更多使用说明"