# 测试数据脱敏详解

> 本文是 `qa-test-data-engineering` 的**测试数据脱敏详解**。做脱敏规则与实现时读本文；
其余部分留在 SKILL.md，不必读本文。

---


> 📌 本节与 qa-test-env-data「数据脱敏」内容同步，修改时请同步更新两处。qa-test-env-data 为简化版，完整版见此处。

### 脱敏规则

```text
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

```text
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
