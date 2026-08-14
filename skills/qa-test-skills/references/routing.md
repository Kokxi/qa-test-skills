# 输入识别与路由规则

## 1. 输入来源识别

| 输入类型 | 识别特征 | 处理方式 |
|---------|---------|---------|
| 直接描述 | 文字描述需求 | 提取关键信息 |
| 上传文件 | 附件/文件路径 | 读取并解构 |
| URL链接 | http/https开头 | 获取并分析 |
| 需求文档目录 | 包含多个需求文档的目录 | 解析索引并读取所有子模块 |

## 2. 需求文档格式支持

### 支持的文档格式

| 格式 | 扩展名 | 处理方式 |
|------|--------|----------|
| Markdown | .md | 直接读取解析 |
| Word文档 | .docx | 使用pdf-extraction技能提取内容 |
| PDF文档 | .pdf | 使用pdf-extraction技能提取内容 |
| 纯文本 | .txt | 直接读取解析 |
| HTML | .html | 使用webfetch或解析HTML内容 |

**格式识别规则**：
- 根据文件扩展名自动识别格式
- Word/PDF文档需要先提取文本内容再解析
- 提取后的内容按Markdown格式处理

## 3. 需求文档索引解析

当用户提供主需求文档时，必须执行以下步骤：

```
步骤1：识别文档格式并读取主文档
  - Markdown/纯文本：直接读取
  - Word/PDF：使用pdf-extraction技能提取内容
步骤2：解析文档中的索引引用
  - 查找对子模块需求的引用（如"详见 requirements/01-auth.md"）
  - 查找目录结构（如"需求文档目录：docs/requirements/"）
  - 查找链接引用（如"[认证需求](./requirements/01-auth.md)"）
  - Word文档中的目录引用（如"认证模块需求见附件01-auth.docx"）
步骤3：读取所有被引用的子模块需求文档
  - 支持混合格式（主文档是Word，子模块是Markdown等）
步骤4：合并所有需求内容进行分析
```

**识别模式**：
- 相对路径引用：`./requirements/01-auth.md`、`../requirements/01-auth.md`
- 绝对路径引用：`/docs/requirements/01-auth.md`
- 目录引用：`requirements/`、`docs/requirements/`
- 锚点引用：`#认证模块`、`##用户管理`
- 附件引用：`附件01-auth.docx`、`详见附件`
- 跨格式引用：`认证需求见 requirements/01-auth.md`

**处理原则**：
- 主文档包含索引时，必须读取所有被引用的子模块
- 子模块需求是主文档的补充，不能忽略
- 支持混合格式（主文档和子模块可以是不同格式）
- 合并所有需求后，再进行后续的测试设计流程

## 4. 用例类型识别

| 关键词 | 用例类型 | 加载能力 |
|--------|---------|---------|
| "接口测试"/"API测试" | 接口测试 | qa-api-testing |
| "Agent测试"/"智能体" | Agent测试 | qa-agent-testing |
| "性能测试"/"压力测试" | 性能测试 | qa-specialized-testing |
| "安全测试"/"渗透测试" | 安全测试 | qa-specialized-testing |
| 默认 | 功能测试 | 标准流程 |

## 5. 平台专项识别

| 关键词 | 平台类型 | 加载专项 |
|--------|---------|---------|
| "移动端"/"App测试" | 移动端App | platform-mobile-app.md |
| "小程序测试" | 小程序 | platform-mini-program.md |
| "H5测试"/"移动Web" | 移动Web | platform-mobile-web.md |
| "桌面端测试" | 桌面应用 | platform-desktop.md |
| "Web测试"/"PC端" | PC Web | platform-pc-web.md |
| 默认 | 通用 | 无平台专项 |

## 6. 可选增强流程

根据用户需求和识别结果，可选择性调用：

### 按用例类型
```
├─ 接口测试：qa-api-testing（识别到"接口/API"关键词）
├─ Agent测试：qa-agent-testing（识别到"Agent/智能体"关键词）
├─ 性能测试：qa-specialized-testing（识别到"性能/压力"关键词）
└─ 安全测试：qa-specialized-testing（识别到"安全/渗透"关键词）
```

### 按平台类型
```
├─ 移动端App：加载 platform-mobile-app.md
├─ 小程序：加载 platform-mini-program.md
├─ 移动Web/H5：加载 platform-mobile-web.md
├─ 桌面应用：加载 platform-desktop.md
└─ PC Web：加载 platform-pc-web.md
```

### 按用户需求
```
├─ qa-test-estimation：工作量估算（用户需要排期时）
├─ qa-exploratory-testing：探索式测试（需要深度探索时）
├─ qa-expert-review：专家评审（需要质量把关时）
└─ qa-tech-debt-management：技术债务评估（需要评估债务时）
```
