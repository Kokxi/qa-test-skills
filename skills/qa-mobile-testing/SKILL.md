---
name: qa-mobile-testing
description: 移动端测试专项，覆盖iOS/Android应用测试方法。当需要测试移动应用时激活。
when_to_use: 用户说"移动测试"、"App测试"、"Android测试"、"iOS测试"、需要测试移动应用时
allowed-tools: Read Grep Glob Bash
related_skills:
  upstream:
    - qa-test-automation-arch    # 输入：自动化架构设计
    - qa-specialized-testing     # 输入：专项测试方法
  downstream:
    - qa-ci-cd-testing           # 输出：移动端测试用于CI/CD
    - qa-release-risk-governance # 输出：测试结果用于发布评估
input_format: 应用需求 + 自动化架构
output_format: 移动端测试方案（测试维度+自动化策略+兼容性矩阵）
---

# 移动端测试专项

你是一位移动端测试专家，擅长设计和执行iOS/Android应用测试。

## 核心原则

**移动测试的核心挑战：设备碎片化、网络不稳定性、用户场景多样性。**

## 测试维度

### 功能测试

```
测试范围：
├─ 安装/卸载/升级
│   ├─ 全新安装
│   ├─ 覆盖安装
│   ├─ 升级安装
│   ├─ 卸载重装
│   └─ 跨版本升级
│
├─ 核心功能
│   ├─ 业务流程测试
│   ├─ 功能交互测试
│   ├─ 数据持久化测试
│   └─ 离线功能测试
│
└─ 中断测试
    ├─ 来电/短信中断
    ├─ 通知中断
    ├─ 低电量中断
    ├─ 网络切换中断
    └─ 后台/前台切换
```

### 兼容性测试

```
设备维度：
├─ 屏幕尺寸：小屏/标准/大屏/折叠屏
├─ 分辨率：720p/1080p/2K/4K
├─ 系统版本：iOS 14+/Android 8+
├─ 设备类型：手机/平板/折叠屏
└─ 品牌厂商：三星/华为/小米/OPPO

系统特性：
├─ 权限管理：不同权限策略
├─ 通知管理：不同通知行为
├─ 后台策略：不同后台限制
└─ 存储策略：不同存储权限
```

### 性能测试

```
性能指标：
├─ 启动时间
│   ├─ 冷启动：<2秒
│   ├─ 热启动：<1秒
│   └─ 温启动：<1.5秒
│
├─ 内存使用
│   ├─ 内存占用：<200MB
│   ├─ 内存泄漏：无持续增长
│   └─ 内存峰值：<300MB
│
├─ 电量消耗
│   ├─ 待机耗电：<5%/天
│   ├─ 使用耗电：<15%/小时
│   └─ 后台耗电：<3%/小时
│
├─ 流量消耗
│   ├─ 首次加载：<5MB
│   ├─ 每次操作：<1MB
│   └─ 后台同步：<10MB/天
│
└─ 帧率
    ├─ 滑动帧率：>55fps
    ├─ 动画帧率：>55fps
    └─ 页面切换：>50fps
```

### 网络测试

```
网络场景：
├─ 网络类型
│   ├─ WiFi
│   ├─ 4G/5G
│   ├─ 弱网（高延迟、低带宽）
│   └─ 断网
│
├─ 网络切换
│   ├─ WiFi → 4G
│   ├─ 4G → WiFi
│   ├─ 有网 → 断网
│   └─ 断网 → 有网
│
└─ 弱网模拟
    ├─ 高延迟：>500ms
    ├─ 低带宽：<100kbps
    ├─ 高丢包：>10%
    └─ 网络抖动：延迟不稳定
```

## 自动化测试

### 工具选型

```
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

## 验收清单

移动端测试完成后检查：
- [ ] 安装/卸载/升级是否测试？
- [ ] 核心功能是否覆盖？
- [ ] 中断场景是否测试？
- [ ] 兼容性矩阵是否覆盖？
- [ ] 性能指标是否达标？
- [ ] 网络场景是否测试？
- [ ] 自动化脚本是否可维护？
