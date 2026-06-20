#!/bin/bash

# QA Test Skills 批量发布脚本
# 将所有45个skills发布到ClawHub

echo "=== QA Test Skills 批量发布脚本 ==="
echo ""

# 检查clawhub CLI是否安装
if ! command -v clawhub &> /dev/null; then
    echo "❌ clawhub CLI 未安装"
    echo "请先安装: npm i -g clawhub"
    exit 1
fi

# 检查是否已登录
echo "检查登录状态..."
if ! clawhub whoami &> /dev/null; then
    echo "❌ 未登录ClawHub"
    echo "请先登录: clawhub login"
    exit 1
fi

echo "✅ 已登录ClawHub"
echo ""

# 发布元skill
echo "发布元skill: qa-test-skills"
clawhub skill publish ./skills/qa-test-skills --slug qa-test-skills --version 1.3.0
if [ $? -eq 0 ]; then
    echo "✅ qa-test-skills 发布成功"
else
    echo "❌ qa-test-skills 发布失败"
fi
echo ""

# 批量发布所有skills
echo "批量发布所有skills..."
echo ""

for skill_dir in ./skills/*/; do
    skill_name=$(basename "$skill_dir")
    
    # 跳过元skill（已发布）
    if [ "$skill_name" = "qa-test-skills" ]; then
        continue
    fi
    
    # 跳过非技能目录
    if [ ! -f "$skill_dir/SKILL.md" ]; then
        echo "⚠️  跳过 $skill_name (没有SKILL.md文件)"
        continue
    fi
    
    echo "发布: $skill_name"
    clawhub skill publish "$skill_dir" --slug "$skill_name" --version 1.3.0
    
    if [ $? -eq 0 ]; then
        echo "✅ $skill_name 发布成功"
    else
        echo "❌ $skill_name 发布失败"
    fi
    echo ""
done

echo "=== 批量发布完成 ==="
echo ""
echo "总共发布: 46个skills (1个元skill + 45个技能)"
echo ""
echo "用户可以通过以下方式安装:"
echo "1. 安装元skill: clawhub install @kokxi/qa-test-skills"
echo "2. 查看README获取完整安装说明"