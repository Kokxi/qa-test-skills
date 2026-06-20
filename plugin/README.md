# QA Test Skills Plugin

48个专家级测试技能集合，覆盖测试全生命周期。

## 安装

```bash
# 从ClawHub安装
clawhub install @kokxi/qa-test-skills

# 或从GitHub安装
git clone https://github.com/Kokxi/qa-test-skills.git
```

## 使用方式

### 方式1：使用主工作流（推荐）
```
请帮我测试这个项目：[需求文档路径]
```

### 方式2：单独使用技能
```
帮我分析这个场景的边界：[场景描述]
帮我设计测试用例：[需求描述]
```

### 方式3：查看所有可用技能
```javascript
import { getSkills } from '@kokxi/qa-test-skills';

const skills = getSkills();
console.log(skills);
```

## 包含的技能

- 48个专家级测试技能
- 覆盖测试全生命周期
- 从需求分析到测试设计、AI协作、执行监控、质量度量

## 文档

详见 [GitHub仓库](https://github.com/Kokxi/qa-test-skills)

## 许可证

MIT License