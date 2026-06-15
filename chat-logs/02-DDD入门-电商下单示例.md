# 02 - DDD 入门：电商下单示例

## 关键概念（以订单系统为例）

### Entity（实体）
- 有唯一标识、可变的对象。例：Order（订单）
- 自身负责自身的行为，不是 getter/setter 数据容器
- 业务规则封装在方法内部：`order.addItem()` 而非 `order.getLines().add()`

### Value Object（值对象）
- 无标识，属性决定相等性，不可变
- 例：Money（金额）、OrderStatus（订单状态）、CustomerId（客户ID）
- 行为内聚：`money.add(otherMoney)`

### Aggregate（聚合）
- 一致性边界，外界只能通过 Aggregate Root 操作内部对象
- 例：Order 是聚合根，OrderLine 只能通过 Order 的方法操作
- 保证了数据一致性，不会有人绕过校验直接写数据

### Domain Service（领域服务）
- 放不进单 Entity 的跨聚合业务逻辑
- 例：VIP vs 普通客户的订单策略

### Domain Event（领域事件）
- 业务行为的"副作用"显式化，用于解耦上下文
- 例：OrderSubmittedEvent → 库存扣减、支付发起

### 分层架构
```
Interface（Controller/API）
    ↓
Application（编排，薄层，不做业务决策）
    ↓
Domain（核心业务逻辑，零外部依赖）
    ↓
Infrastructure（DB/MQ/外部服务实现）
```

## 对比传统 CRUD 写法

| 传统写法 | DDD 写法 |
|---------|---------|
| 业务逻辑散落在 Service 里 | 业务逻辑内聚在 Entity/Value Object 中 |
| 对象是数据容器（getter/setter） | 对象是行为载体，数据只是状态 |
| 规则藏在 if-else 里 | 规则显式建模为方法 |
| 看到的是技术流程 | 看到的是业务语言 |

## 一句话总结
DDD 的本质：**把业务专家脑袋里的规则，翻译成代码里的一等公民，而不是散落在 Service 里没人敢动的 if-else。**
