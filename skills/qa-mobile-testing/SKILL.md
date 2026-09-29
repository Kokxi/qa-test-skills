---
name: qa-mobile-testing
description: >-
  当需要测试 iOS/Android 原生 App、H5 页面或小程序的移动端专项场景时使用此技能。移动端的坑主要不在功能逻辑上——中断（电话/通知/低电量）、弱网/断网/网络切换、前后台切换、系统权限管理、多机型适配和各种系统版本兼容才是重灾区。不要只测功能流程，移动端的 Bug 有一半以上是中断和兼容性相关的。输出按中断/网络/权限/兼容/性能分类的测试要点清单。 触发场景：移动测试、App测试、Android测试、iOS测试、手机上测、H5测试、小程序测试、移动端中断测试、移动端兼容测试、移动端发版前全面测试时。 Use when the user asks about: mobile testing for iOS and Android apps, H5 pages, and mini programs — interruptions, weak network, background/foreground switching, permissions, and device compatibility.
license: MIT
allowed-tools: Read Grep Glob Bash
metadata:
  slug: "qa-mobile-testing"
  display-name: "移动端测试"
  version: "1.8.0"
  when-to-use: "用户说\"移动测试\"、\"App测试\"、\"Android测试\"、\"iOS测试\"、\"手机上测\"、\"H5测试\"、\"小程序测试\"、\"移动端中断测试\"、\"移动端兼容测试\"、需要测试移动应用、移动端发版前全面测试时"
  related-skills: "{\"upstream\":[\"qa-test-automation-arch\",\"qa-specialized-testing\"],\"downstream\":[\"qa-ci-cd-testing\",\"qa-release-risk-governance\"]}"
  references: "[\"references/mobile-checklist.md\",\"references/platform-desktop.md\",\"references/platform-mini-program.md\",\"references/platform-mobile-app.md\",\"references/platform-mobile-web.md\",\"references/platform-pc-web.md\"]"
  input-format: "{\"required\":[{\"name\":\"测试策略\",\"type\":\"object\",\"description\":\"来自qa-test-strategy-design的测试策略\"},{\"name\":\"移动端需求\",\"type\":\"string\",\"description\":\"移动端的特性需求和平台要求\"}],\"optional\":[{\"name\":\"设备清单\",\"type\":\"array\",\"description\":\"测试设备和OS版本列表\"}]}"
  output-format: "{\"traceability\":[\"每个移动端测试用例带唯一ID（TC_{模块缩写}_{功能缩写}_{序号}，如 TC_API_LOGIN_001）\",\"关联平台和需求ID\"],\"structure\":[\"覆盖率：标注口径（基于现有需求/输入文档），禁止\\\"全覆盖/100%\\\"绝对化表述；缺失模块标注\\\"未覆盖+原因\\\"\",{\"mobile_test_plan\":\"移动端测试方案\"},{\"device_coverage\":\"设备覆盖矩阵\"},{\"platform_specific\":\"平台特性测试清单\"},{\"performance_checks\":\"性能测试要点\"}]}"
  error-recovery-guidance: "{\"on_failure\":\"设备兼容性问题时切换到备用设备或模拟器，记录环境信息\",\"retry_behavior\":\"更换测试设备或修复环境问题后重新执行移动端测试\"}"
  categories: "[\"Development\",\"Testing\"]"
  depth-requirement: "{\"reference_value\":\"根据平台复杂度调整测试深度：简单×1/中等×2/复杂×3\",\"minimum\":\"至少覆盖中断、网络、权限、兼容4个移动端维度\"}"
---
> ⚠️ 本技能单独使用效果有限，建议配合完整技能集（12 步工作流）使用。安装：npx skills add Kokxi/qa-test-skills

# 移动端测试专项

## 核心原则

移动测试的核心挑战——设备碎片化、网络不稳定性、用户场景多样性。

## 移动端测试深度要求（参考值）

| 复杂度 | 用例数要求 | 设备覆盖 |
|--------|-----------|---------|
| 简单App | 30条 | 2-3台主流设备 |
| 中等App | 50条 | 5-8台设备 |
| 复杂App | 80条 | 10+台设备+多系统版本 |

**必须覆盖的6个维度**：

| 维度 | 占比 | 说明 |
|------|------|------|
| 功能测试 | 35% | 核心功能、业务流程 |
| 兼容性测试 | 25% | 设备/系统/屏幕 |
| 中断测试 | 15% | 来电/短信/通知/切换 |
| 性能测试 | 10% | 启动/内存/电量/流量 |
| 弱网测试 | 10% | 网络切换/弱网/离线 |
| 安全测试 | 5% | 权限/数据保护 |

> **平台专项参考**：不同平台有各自的高风险场景，加载对应参考文件可获取专项测试要点：
> - [`references/platform-mobile-app.md`](references/platform-mobile-app.md) — iOS/Android 原生 App 专项
> - [`references/platform-mobile-web.md`](references/platform-mobile-web.md) — H5/移动 Web 专项
> - [`references/platform-mini-program.md`](references/platform-mini-program.md) — 小程序专项
>
> 桌面端 / PC Web 专项不属于本技能范围，如需测试桌面端或 PC Web 请使用通用测试策略技能。

## 加载时机

| 什么时候读 | 读哪个 |
|-----------|--------|
| 需要跨平台通用检查项时，取全平台清单 | [`references/mobile-checklist.md`](references/mobile-checklist.md) |

> `移动端测试检查清单`的完整内容已下沉至 `references/mobile-checklist.md`，避免每次触发都占用上下文。

## 自动化测试

### 工具选型

```text
├─ Appium
│   ├─ 优点：跨平台、语言无关
│   ├─ 缺点：速度较慢、稳定性一般
│   └─ 适用：跨平台项目
│
├─ XCTest（iOS）
│   ├─ 优点：官方支持、性能好
│   ├─ 缺点：仅iOS
│   └─ 适用：iOS原生应用
│
├─ Espresso（Android）
│   ├─ 优点：官方支持、速度快
│   ├─ 缺点：仅Android
│   └─ 适用：Android原生应用
│
└─ Airtest
    ├─ 优点：图像识别、游戏测试
    ├─ 缺点：维护成本高
    └─ 适用：游戏、H5混合应用
```

### Page Object模式

```python
# 示例：Android Page Object
class LoginPage:
    def __init__(self, driver):
        self.driver = driver
    
    username_field = ResourceId("com.example:id/username")
    password_field = ResourceId("com.example:id/password")
    login_button = ResourceId("com.example:id/login")
    
    def login(self, username, password):
        self.driver.find_element(*self.username_field).send_keys(username)
        self.driver.find_element(*self.password_field).send_keys(password)
        self.driver.find_element(*self.login_button).click()
```

## 兼容性测试矩阵

```markdown
| 设备 | 系统版本 | 屏幕尺寸 | 测试状态 |
|------|---------|---------|---------|
| iPhone 14 | iOS 16 | 6.1寸 | ✅ 通过 |
| iPhone 12 | iOS 15 | 6.1寸 | ✅ 通过 |
| Samsung S23 | Android 13 | 6.1寸 | ✅ 通过 |
| Huawei Mate 50 | HarmonyOS 3 | 6.7寸 | ⚠️ 待测 |
| Xiaomi 13 | Android 13 | 6.36寸 | ✅ 通过 |
```

## 输出示例

**测试移动端登录功能**
→ 五维覆盖：
  - 功能：登录/登出/自动登录/多设备登录
  - 兼容性：iOS15/16/17 + Android 12/13/14 + 主流机型
  - 中断：来电/短信/通知/低电量/闹钟弹出
  - 性能：启动时间/页面加载/内存占用
  - 弱网：3G/弱WiFi/飞行模式/网络切换

**App首页加载慢（iOS 3秒，Android 5秒）**
→ 触发性能测试清单，检查首页接口、图片加载、缓存策略

## 检查清单

移动端测试完成后检查：
- [ ] 安装/卸载/升级是否测试？
- [ ] 核心功能是否覆盖？
- [ ] 中断场景是否测试？
- [ ] 兼容性矩阵是否覆盖？
- [ ] 性能指标是否达标？
- [ ] 网络场景是否测试？
- [ ] 自动化脚本是否可维护？
