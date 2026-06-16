---
name: qa-test-data-engineering
description: 测试数据工程，设计和管理测试数据的构造、脱敏、清理。当需要管理测试数据时激活。
when_to_use: 用户说"测试数据"、"造数"、"数据构造"、"数据脱敏"、需要管理测试数据时
allowed-tools: Read Grep Glob Bash
related_skills:
  upstream:
    - qa-test-env-data           # 输入：环境和数据管理策略
    - qa-req-deconstruction      # 输入：需求分析确定数据需求
  downstream:
    - qa-execution-observation   # 输出：测试数据支持执行
    - qa-api-testing             # 输出：数据构造用于接口测试
input_format: 需求分析 + 环境策略
output_format: 测试数据方案（数据工厂+脱敏策略+清理机制）
---

# 测试数据工程

你是一位测试数据专家，擅长设计和管理测试数据。

## 核心原则

**测试数据是测试的基础，好的数据管理让测试可重复、可追溯。**

## 数据构造方法

### 手动构造

```
适用场景：
├─ 少量数据
├─ 复杂业务数据
├─ 一次性数据
└─ 调试用途

方法：
├─ 数据库直接插入
├─ 管理后台创建
├─ 接口调用创建
└─ 脚本批量创建
```

### 数据工厂

```
适用场景：
├─ 批量数据
├─ 标准化数据
├─ 重复性数据
└─ 自动化测试

工具：
├─ Faker（Python/JS）
├─ Mockaroo（在线）
├─ Factory Bot（Ruby）
└─ 自建工厂类
```

### 数据库脚本

```sql
-- 示例：用户数据构造
INSERT INTO users (username, email, phone, status, created_at)
VALUES 
    ('testuser001', 'test1@example.com', '13800000001', 'active', NOW()),
    ('testuser002', 'test2@example.com', '13800000002', 'active', NOW()),
    ('testuser003', 'test3@example.com', '13800000003', 'inactive', NOW());
```

### API构造

```python
# 示例：通过API构造订单数据
def create_test_order(user_id, product_id, quantity=1):
    response = requests.post(
        f"{BASE_URL}/orders",
        json={
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()["order_id"]
```

## 数据脱敏

### 脱敏规则

```
个人信息：
├─ 手机号：138****1234
├─ 身份证：110***********1234
├─ 邮箱：test****@example.com
├─ 姓名：*三
├─ 地址：北京市***
└─ 银行卡：6222****1234

业务数据：
├─ 金额：保留整数位，小数随机
├─ 订单号：保留格式，数字随机
├─ 时间：保留格式，时间随机
└─ 关联ID：保持关联关系
```

### 脱敏方法

```
├─ 替换法：用*替换部分字符
│   └─ 示例：138****1234
│
├─ 加密法：用加密算法处理
│   └─ 示例：AES加密后存储
│
├─ 截断法：只保留部分字符
│   └─ 示例：北京市***
│
├─ 随机法：用随机值替换
│   └─ 示例：姓名随机生成
│
└─ 哈希法：用哈希值替换
    └─ 示例：SHA256哈希
```

### 脱敏实现

```python
# 示例：Python脱敏函数
import hashlib
import random

def mask_phone(phone):
    """手机号脱敏：138****1234"""
    return phone[:3] + "****" + phone[-4:]

def mask_id_card(id_card):
    """身份证脱敏：110***********1234"""
    return id_card[:3] + "*" * 10 + id_card[-4:]

def mask_name(name):
    """姓名脱敏：*三"""
    return "*" + name[-1]

def mask_email(email):
    """邮箱脱敏：test****@example.com"""
    local, domain = email.split("@")
    return local[:4] + "****@" + domain
```

## 数据清理

### 清理策略

```
├─ 按用例清理
│   ├─ 每个用例执行后清理
│   ├─ 优点：数据隔离好
│   └─ 缺点：效率低
│
├─ 按模块清理
│   ├─ 每个模块测试后清理
│   ├─ 优点：效率较高
│   └─ 缺点：隔离性一般
│
├─ 按批次清理
│   ├─ 每个批次测试后清理
│   ├─ 优点：效率高
│   └─ 缺点：隔离性差
│
└─ 定期清理
    ├─ 定期清理历史数据
    ├─ 优点：保持数据量可控
    └─ 缺点：可能影响测试
```

### 清理实现

```sql
-- 示例：清理测试数据
-- 方法1：按时间清理
DELETE FROM orders WHERE created_at < DATE_SUB(NOW(), INTERVAL 7 DAY);

-- 方法2：按标记清理
DELETE FROM orders WHERE is_test = 1;

-- 方法3：按用户清理
DELETE FROM orders WHERE user_id IN (SELECT id FROM users WHERE is_test = 1);
```

## 数据管理规范

### 命名规范

```
测试用户：
├─ 格式：test_[角色]_[序号]
├─ 示例：test_user_001, test_admin_001
└─ 标记：is_test = 1

测试数据：
├─ 格式：[类型]_test_[序号]
├─ 示例：order_test_001, product_test_001
└─ 标记：is_test = 1
```

### 数据生命周期

```
├─ 构造：测试前准备数据
├─ 使用：测试中使用数据
├─ 验证：测试后验证数据
├─ 清理：测试后清理数据
└─ 归档：历史数据归档
```

## 验收清单

测试数据管理完成后检查：
- [ ] 数据构造方法是否设计？
- [ ] 脱敏规则是否定义？
- [ ] 清理机制是否实现？
- [ ] 命名规范是否统一？
- [ ] 数据生命周期是否管理？
- [ ] 数据可追溯性是否保证？
