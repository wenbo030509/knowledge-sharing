# Python 代码学习指南

> 从"看不懂 AI 写的代码"到"能读、能 Debug、能 Review"。
>
> 本指南不按语法书顺序组织，而是按**你打开一个文件时实际看到的场景**组织。

---

## 前置认知：Python 代码 = Pipeline 的代码实现

你已经理解了 Pipeline 概念——把复杂任务分解为有序阶段，每个阶段有明确的输入输出。

Python 项目的代码组织就是 Pipeline 思想在文件结构上的体现：

```text
CoT 质检 Pipeline                    后端项目
─────────────────                   ──────────
[读取数据]  → load_data.py          routes/     ← 接收请求（翻译官）
[格式检查]  → validate.py           schemas/    ← 格式校验（守门员）
[内容检查]  → validate.py           services/   ← 业务逻辑（大脑）
[LLM修复]   → repair.py             services/   ← 业务逻辑
[保存结果]  → save.py               models/     ← 数据持久化（数据字典）
```

**核心认知：不管多复杂的 AI 模型或后端项目，代码层面就是 `def` 的嵌套。** ChatGPT 的代码和你的 CoT 质检脚本，结构完全相同，只是规模不同。

---

## 一、写代码的五步工作法

> 永远从"数据长什么样"开始，不是从 `def` 开始。

```text
纸上画图 → 写数据样版（注释）→ 写主流程骨架 → 逐个填 def → 跑通 → 拆分文件
 5分钟      5分钟                 10分钟          主要时间     5分钟    按需
```

### Step 0：纸上画 Pipeline 结构图（不需要打开编辑器）

```text
[输入数据] → Stage 1 → Stage 2 → Stage 3 → [输出结果]
```

先把这个图画出来，不画不开工。

### Step 1：写输入和输出的"样版"（Sample）

打开编辑器，第一件事不是写 `def`，是写注释——用具体例子说清楚数据长什么样：

```python
# 输入：学生的考试成绩单
# input = [
#     {"name": "张三", "math": 85, "english": 72, "physics": None},
#     {"name": "李四", "math": -5, "english": 88, "physics": 76},
#     {"name": "王五", "math": 92, "english": 95, "physics": 88},
# ]

# 输出：清洗后的合格成绩
# output = [
#     {"name": "王五", "math": 92, "english": 95, "physics": 88, "avg": 91.67},
# ]
```

强制你想清楚"数据到底长什么样"——这步想不清楚，后面全白写。注释不会报错，不需要会语法就能写。

### Step 2：写主流程——只用函数名串联 Pipeline

```python
def main():
    data = load_data("scores.json")              # Step 1: 读取数据
    valid_data = filter_invalid(data)             # Step 2: 过滤无效数据
    scored_data = calculate_average(valid_data)   # Step 3: 计算平均分
    save_results(scored_data, "output.json")      # Step 4: 保存结果
    print(f"处理完成：{len(data)} 条 → {len(scored_data)} 条合格")
```

这时候每个 `def` 里面都是空的。你的 Pipeline 结构已经变成代码了——只是还没填实现。

### Step 3：逐个填 `def`，从最简单/最独立的开始

**关键原则：写完一个，跑一下验证，确认正确再写下一个。**

填的顺序：
1. 先写最独立的（load_data / save_results）
2. 再写有依赖的（validator / repair）
3. 最后写最复杂的（LLM 调用）

```python
def load_data(path):
    import json
    with open(path, "r") as f:
        return json.load(f)

# 写完立刻验证
data = load_data("scores.json")
print(f"读到 {len(data)} 条数据")  # 看输出是不是预期
print(data[0])                      # 看第一条数据长什么样
```

### Step 4：跑通全流程，修 bug

```python
if __name__ == "__main__":
    main()
```

`if __name__ == "__main__"` = "如果直接运行这个文件，就执行 main()。如果被其他文件引用，就不执行。"

### Step 5：文件太长就拆分（按 Pipeline Stage 拆）

```text
拆分时机：文件超过 200 行

拆分原则：不是"按功能分"，而是"按 Pipeline Stage 分"

project/
├── main.py              ← 主流程：串联 Pipeline
├── load_data.py         ← Stage 1：数据读取
├── validate.py          ← Stage 2：数据校验
├── repair.py            ← Stage 3：数据修复
└── save_output.py       ← Stage 4：结果输出
```

**新手正确顺序：** 先全写在一个 `main.py` 里 → 跑通 → 再拆。不要一上来就建 5 个文件。

---

## 二、四层架构：打开不同文件看到的代码长相不同

后端项目按职责分四层，每层关心的事情不同，所以代码"长相"完全不同：

```text
请求 → routes/（翻译官）→ schemas/（守门员）→ services/（大脑）→ models/（数据字典）→ 数据库
```

### 2.1 Routes 层：翻译官

**职责：** 把 HTTP 请求翻译成函数调用。这一层 90% 不是自己写的逻辑，而是装饰器 + 函数签名。

```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.get("/{user_id}")                          # 装饰器：处理 GET 请求
def get_user(user_id: int,
             current_user = Depends(get_current_user)):  # Depends：自动注入
    """获取用户详情"""
    user = get_user_by_id(user_id)                  # 只负责"转发"
    if not user:
        return {"code": 404, "message": "用户不存在"}  # 返回 HTTP 响应格式
    return {"code": 200, "data": user.to_dict()}
```

**特征：**
- 大量 `@router.get/post/put/delete` 装饰器
- `Depends(...)` 自动注入依赖
- `Query(...)` / `Body(...)` / `Path(...)` 标注参数来源
- 函数很短（< 20 行），只做转发，不写业务逻辑

**常见装饰器含义：**

| 写法 | 含义 |
|------|------|
| `@router.get("/xxx")` | 处理 GET 请求 |
| `@router.post("/xxx")` | 处理 POST 请求（创建） |
| `@router.put("/xxx")` | 处理 PUT 请求（全量更新） |
| `@router.delete("/xxx")` | 处理 DELETE 请求 |

**常见参数来源标注：**

| 写法 | 含义 |
|------|------|
| `Query(...)` | 参数从 URL `?` 后面来（`?keyword=xxx`） |
| `Path(...)` | 参数从 URL 路径里来（`/users/123`） |
| `Body(...)` | 参数从 POST 请求体 JSON 来 |

### 2.2 Schemas 层：守门员

**职责：** 定义 API 的输入/输出格式，校验数据是否合法。

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class UserCreateRequest(BaseModel):           # 继承 BaseModel，不是 db.Model
    """注册用户的请求体格式"""
    username: str = Field(..., min_length=3, max_length=80)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    phone: Optional[str] = None               # Optional = 选填
    birthday: Optional[date] = None


class UserResponse(BaseModel):
    """返回给前端的用户数据格式"""
    id: int
    username: str
    email: str
    status: str
    created_at: str

    class Config:
        from_attributes = True    # 允许从 ORM 对象自动转换
```

**Schemas vs Models 的区别：**

| | models/user.py | schemas/user.py |
|---|---|---|
| 继承什么 | `db.Model` | `BaseModel`（Pydantic） |
| 目的是什么 | 定义数据库表结构 | 定义 API 的输入/输出格式 |
| 校验逻辑 | 数据库约束（unique, nullable） | Python 校验（min_length, pattern） |

数据库关心"存什么"。API 关心"接收什么、返回什么"。这是两件不同的事。

### 2.3 Services 层：大脑

**职责：** 纯 Python 业务逻辑。不引用任何 HTTP 框架的东西。

```python
from models.user import User
from typing import Optional


def get_user_by_id(user_id: int) -> Optional[User]:
    """根据 ID 查用户"""
    return User.query.filter_by(id=user_id).first()


def create_user(username: str, email: str, phone: Optional[str] = None) -> User:
    """创建用户，包含业务校验"""
    existing = User.query.filter_by(username=username).first()
    if existing:
        raise ValueError(f"用户名 {username} 已被占用")
    if "@" not in email:
        raise ValueError("邮箱格式不正确")
    user = User(username=username, email=email, phone=phone)
    db.session.add(user)
    db.session.commit()
    return user
```

**特征：**
- 全是 `def`（或 `class` 包裹的 `def`）
- 函数名是动词+名词：`create_user`、`search_users`、`deactivate_user`
- 输入是 Python 对象（str、int、dict、Model），不是 HTTP 请求
- 输出是 Python 对象，不是 HTTP 响应
- 包含业务规则（用户名不能重复、邮箱要含 @）
- 不引用任何 HTTP 框架的东西（没有 `@router`、没有 `Depends`）

**如果把 services/ 的代码拿出来，它可以被 routes/ 调用，也可以被命令行脚本调用，也可以被定时任务调用——它不依赖任何特定场景。**

### 2.4 Models 层：数据字典

**职责：** Python 类 ↔ 数据库表的映射。代码是"声明式"的——不是在写"做什么"，而是在写"数据长什么样"。

```python
from datetime import datetime
from database import db


class User(db.Model):                          # 继承 db.Model
    """用户表"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default="active")
    birthday = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # 表和表之间的关联
    orders = db.relationship("Order", backref="user", lazy="dynamic")

    def to_dict(self):
        """格式转换：数据库记录 → 字典"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "status": self.status,
        }
```

**特征：**
- 主要是 `class`，继承 `db.Model`
- 主体是 `db.Column(...)` 声明——描述表结构
- 业务方法很少，最多是 `to_dict()` 这种"格式转换"
- **不调用 services/** —— models 是最底层，不依赖任何上层

**常见 Column 类型：**

| 写法 | 含义 |
|------|------|
| `db.Integer` | 整数 |
| `db.String(n)` | 最长 n 字符的文本 |
| `db.Text` | 长文本 |
| `db.Boolean` | 真/假 |
| `db.Float` | 浮点数 |
| `db.DateTime` | 日期时间 |
| `db.Date` | 日期 |

**常见约束：**

| 写法 | 含义 |
|------|------|
| `primary_key=True` | 主键（唯一标识一条记录） |
| `unique=True` | 值不能重复 |
| `nullable=False` | 不能为空 |
| `default=xxx` | 默认值 |

### 2.5 四层完整对比图

```text
                        [HTTP 请求]
                            │
                            ↓
┌─────────────────────────────────────────────────────────┐
│ routes/  ← 翻译官                                       │
│                                                         │
│ 写什么：@router.get(...) 装饰器 + 短函数                  │
│ 关键元素：装饰器、Depends、HTTP 状态码                     │
│ 不做什么：不写业务逻辑、不直接写 SQL                       │
│ 函数长度：< 20 行                                        │
└──────────────────────────┬──────────────────────────────┘
                           │ 调用
                           ↓
┌─────────────────────────────────────────────────────────┐
│ schemas/  ← 守门员                                      │
│                                                         │
│ 写什么：class XxxRequest(BaseModel) + Field 校验规则      │
│ 关键元素：类型标注、min_length、pattern                    │
│ 不做什么：不写业务逻辑、不碰数据库                         │
└──────────────────────────┬──────────────────────────────┘
                           │ 调用
                           ↓
┌─────────────────────────────────────────────────────────┐
│ services/  ← 大脑                                       │
│                                                         │
│ 写什么：def get_xxx() / def create_xxx()                 │
│ 关键元素：纯 Python 函数、异常处理、业务规则               │
│ 不做什么：不处理 HTTP、不引用 @router                     │
│ 函数长度：10-50 行                                       │
└──────────────────────────┬──────────────────────────────┘
                           │ 调用
                           ↓
┌─────────────────────────────────────────────────────────┐
│ models/  ← 数据字典                                     │
│                                                         │
│ 写什么：class Xxx(db.Model) + db.Column(...) 声明         │
│ 关键元素：Column 类型、约束、relationship                 │
│ 不做什么：不写复杂逻辑、不引用 services/                   │
│ 方法数：< 5 个（主要是 to_dict、属性访问器）              │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
                      [数据库表]
```

---

## 三、30 个关键词速查表

> 保证你能看懂代码、Debug、Review 的最小词汇量。

### 第一组：任何文件都能看到的——基础骨架（8 个）

#### 1. `import` / `from ... import`

```python
import json                          # 把 json 工具包拿进来
from models.user import User         # 只拿工具包里的某一个
import numpy as np                   # 拿进来，起个短名字
```

文件顶部 10-30 行。扫一眼看依赖了哪些模块即可，不需要逐行读。报 `NameError` 时才回来看。

#### 2. `def` — 函数定义

定义一个操作（Pipeline 里的一个 Stage）。

```python
def check_format(data: dict) -> bool:
    ...
```

#### 3. `class` — 类定义

定义一个"东西"——它有自己的属性（数据）和方法（操作）。

```python
class User:
    def __init__(self, name):         # __init__ = 初始化：创建对象时自动执行
        self.name = name              # self.xxx = 这个对象的属性

    def greet(self):                  # 方法：这个对象能做什么
        return f"你好，我是{self.name}"
```

**怎么辨识：**
- `class Xxx(db.Model)` → 数据库表（models 层）
- `class Xxx(BaseModel)` → API 输入/输出格式（schemas 层）
- `class Xxx:` → 普通业务对象

#### 4. `return` — 函数输出

```python
def add(a, b):
    return a + b        # 函数在这里结束，把结果交给调用者
```

**读代码技巧：** 读一个 `def` 时，先跳到最下面看 `return` 什么——就知道输出类型。

#### 5. `if / elif / else` — 条件判断

```python
if status == "error":
    return "discarded"          # 如果是错误，废弃
elif status == "warning":
    return "needs_repair"       # 如果是警告，需要修复
else:
    return "qualified"          # 其他情况，合格
```

`if` 是主分支，`elif` 是备选分支，`else` 是兜底。读的时候先读 `if` 条件。

#### 6. `for ... in ...` — 循环

```python
for item in data:               # data 是列表，每次拿出一个 item
    result = process(item)      # 对每个 item 执行操作
    results.append(result)      # 把结果加到列表里
```

`for X in Y` = "Y 里有多少个东西，就做多少次。每次拿出一个，叫 X。"

#### 7. `try / except` — 错误处理

```python
try:
    user = get_user_by_id(123)     # 尝试做这件事
    result = process(user)
except ValueError as e:            # 出了 ValueError 这种错
    print(f"出错了：{e}")           # 不要崩溃，记录错误
    result = None                  # 给一个默认值
```

就是 Pipeline 里的"错误隔离"——一条数据出错不阻塞整体。

#### 8. `f"..."` — 格式化字符串

```python
name = "张三"
greeting = f"你好，{name}！"               # 你好，张三！
log = f"处理了 {len(data)} 条，{failed} 条失败"
```

花括号里的变量会被替换成实际值。写日志和报错信息时大量使用。

---

### 第二组：数据容器——搞清楚数据长什么样（4 个）

#### 9. `list` — 列表（有顺序的一堆东西）

```python
data = [1, 2, 3, 4, 5]                    # 方括号 = list
names = ["张三", "李四", "王五"]

data[0]            # 取第一个 → 1
data[-1]           # 取最后一个 → 5
data.append(6)     # 往末尾加 → [1, 2, 3, 4, 5, 6]
len(data)          # 有几个 → 5
for item in data:  # 遍历每一个
```

#### 10. `dict` — 字典（有名字的一堆东西）

```python
user = {"name": "张三", "age": 25, "status": "active"}
#      花括号 = dict，左边是 key（名字），右边是 value（值）

user["name"]           # 取 name → "张三"
user.get("phone", "")  # 取 phone，不存在返回空字符串（不报错）
"name" in user         # 检查有没有 name 这个 key → True
```

**你的 CoT 数据就是 `list` of `dict`：**
```python
# 整个数据集
[
    {"id": "math_001", "question": "...", "cot": "...", "answer": "-1"},
    {"id": "math_002", "question": "...", "cot": "...", "answer": "0.5"},
]
```

#### 11. `None` — 空/不存在

```python
result = None                    # 表示"还没有值"

if result is None:               # 检查是不是空的
    print("找不到结果")
```

#### 12. `True / False` 和比较符号

```python
a == b    # a 等于 b？（注意两个等号）
a != b    # a 不等于 b？
a in b    # a 在 b 里面？
a and b   # a 和 b 都要成立
a or b    # a 或 b 至少一个成立
not a     # 取反
```

**重要：** `==` 是"等于吗"（比较），`=` 是"赋值"（让左边等于右边）。不是一回事。

---

### 第三组：四层架构专属（10 个）

#### 13. `db.Column(...)` — 定义数据库列（models 层）

```python
username = db.Column(db.String(80), unique=True, nullable=False)
#                    └── 类型      └── 唯一   └── 不能为空
```

#### 14. `db.relationship(...)` — 表和表的关联（models 层）

```python
class User(db.Model):
    orders = db.relationship("Order", backref="user")
    # 一个用户可以有多个订单

class Order(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # 订单属于哪个用户
```

#### 15. `db.session.add()` / `db.session.commit()` — 写入数据库（models 层）

```python
new_user = User(username="张三", email="zhang@example.com")
db.session.add(new_user)       # 加到"待保存"列表
db.session.commit()            # 真的写入数据库
```

`add` = 准备写，`commit` = 真的写。两步分开是因为可能要一次性写好几条。

#### 16. `.query.filter(...)` — 数据库查询（services 层）

```python
User.query.all()                                          # 查所有
User.query.filter_by(id=123).first()                      # 按 ID 查一个
User.query.filter(User.username.contains("张")).all()      # 模糊搜索
User.query.filter(User.status == "active").all()           # 按条件筛选
User.query.order_by(User.created_at.desc()).limit(10).all() # 排序 + 限制
```

| 方法 | 含义 |
|------|------|
| `.all()` | 拿到所有结果（返回 list） |
| `.first()` | 只拿第一条（或 None） |
| `.filter()` | 条件筛选 |
| `.filter_by()` | 等于条件筛选（更简单的语法） |
| `.order_by()` | 排序 |
| `.limit(n)` | 只取前 n 条 |
| `.paginate()` | 分页（返回总数、当前页等） |

#### 17. `raise XxxError(...)` — 主动抛出异常（services 层）

```python
raise ValueError(f"用户名 {username} 已被占用")
```

= "停，这里出错了，我不处理，交给调用者决定怎么办。"相当于 Pipeline 里判 `discarded`。

#### 18. 类型标注 `: str` `-> bool`（services 层）

```python
def check_format(data: dict) -> bool:
    #            └── 参数类型  └── 返回值类型
```

常见类型标注：
```python
name: str                       # 字符串
age: int                        # 整数
score: float                    # 浮点数
is_active: bool                 # 布尔
items: list                     # 列表
config: dict                    # 字典
user: Optional[User]            # 可能是 User，也可能是 None
users: List[User]               # User 的列表
```

类型标注不是强制的，但是最好的"文档"——不看函数体就知道输入输出类型。

#### 19. `@router.get(...)` / `@router.post(...)` — 装饰器（routes 层）

```python
@router.get("/api/users/{user_id}")      # 处理 GET
@router.post("/api/users")               # 处理 POST（创建）
@router.put("/api/users/{user_id}")      # 处理 PUT（全量更新）
@router.delete("/api/users/{user_id}")   # 处理 DELETE
```

`@` 开头的是装饰器。不需要理解怎么工作，只需知道：`@router.get("/xxx")` = "这个函数在 GET `/xxx` 被访问时执行"。

#### 20. `Depends(...)` — 依赖注入（routes 层）

```python
def get_user(current_user = Depends(get_current_user)):
    #                        └── 系统自动填当前登录用户
```

"这个参数不用调用者传，系统自动帮你填。"

#### 21. `Query(...)` / `Body(...)` / `Path(...)` — 参数来源（routes 层）

```python
keyword: str = Query(..., min_length=1)     # 从 ?keyword=xxx 来
user_id: int = Path(...)                     # 从 URL 路径来
data: UserCreateRequest = Body(...)          # 从请求体 JSON 来
```

#### 22. `Field(...)` — 字段校验（schemas 层）

```python
username: str = Field(..., min_length=3, max_length=80)
#                └── 必填  └── 最短3字符   └── 最长80字符

age: int = Field(18, ge=0, le=150)
#                └── 默认18 └── >=0 └── <=150
```

---

## 四、Debug 三件套

### 23. 三种最常见的报错

```text
NameError: name 'xxx' is not defined
→ 用了一个不存在的变量名
→ 检查：拼写对不对？import 了没有？

TypeError: xxx() missing 1 required positional argument: 'yyy'
→ 调用函数时少传了一个参数
→ 检查：函数定义里需要的参数，你都传了吗？

AttributeError: 'Xxx' object has no attribute 'yyy'
→ 在 Xxx 这个对象上访问了不存在的属性或方法
→ 检查：拼写对不对？这个对象真的是 Xxx 类型吗？是不是有可能是 None？
```

### 24. `print()` — 最强 Debug 工具

```python
def process(data):
    print(f"进入 process，数据：{data}")           # 打印输入
    result = complex_logic(data)
    print(f"complex_logic 返回：{result}")         # 打印中间结果
    return result
```

**Debug 铁律：不知道哪里出问题，就在每一步后面加 `print()`，看数据长什么样。** AI 生成的代码出了 bug，不要试图"读代码推理"，直接在关键位置加 print。

### 25. Traceback — 怎么读报错信息

```text
Traceback (most recent call last):
  File "main.py", line 42, in <module>              ← 入口
    result = main()
  File "main.py", line 35, in main                  ← main 调用了 process
    data = process(items)
  File "services/process.py", line 18, in process    ← process 调用了 validate
    valid = validate(item)
  File "services/validate.py", line 7, in validate   ← ← 真正出错的地方！
    return item["cot"] / len(item)
TypeError: unsupported operand type(s) for /: 'str' and 'int'
                                                   └── 错误原因
```

**读 Traceback 的规则：从下往上读。**
1. 最后一行 = "出了什么错"（TypeError）
2. 倒数第二个 File = "错在哪里"（validate.py 第 7 行）← 这就是要改的地方
3. 再往上 = "谁调用了它"（不需要改，只是调用链）

---

## 五、Review 两板斧

### 26. 函数长度

```text
def 超过 50 行 → 🟡 可能做了太多事情，需要拆分
def 超过 100 行 → 🔴 几乎肯定需要拆成多个小函数
```

**Review 技巧：** 拿到 AI 生成的代码，先不读内容，先扫一眼每个 `def` 有多长。找到最长的那个，让 AI 拆分。

### 27. 函数名——判断"它在做什么"

```text
好的函数名                          不好的函数名
─────────────────────────────────────────────
validate_cot_format(data)          check(data)
create_user(username, email)       do_stuff(x)
search_users_by_keyword(kw)        handle(y)
calculate_average_score(items)     process(z)
save_results_to_file(data, path)   run(a, b)
```

**好的函数名 = 动词 + 名词，说清楚做什么、作用于什么。**

看到 `process()`、`handle()`、`do_stuff()` 这种模糊函数名 → 让 AI 改名。

---

## 六、读懂复杂代码的通用策略

### 策略一：先看结构，再看细节

```text
1. 扫一眼文件名 → 判断是哪一层（routes? services? models?）
2. 看 import 区域 → 知道依赖了什么
3. 看最后一个 def/class → 通常是主入口
4. 看每个 def 的函数名 → 知道做了哪些步骤
5. 挑一个你关心的 def，看它的参数和 return
```

**不要从头到尾逐行读。** 先建立"这个文件在做什么"的全局印象。

### 策略二：用 print 代替读代码

代码的行为 = 实际运行时数据的变化。与其盯着代码推理，不如加 print 看实际数据。

### 策略三：遇到不认识的写法，对照速查表

不是你不会，只是还没见过。查一下就知道是什么了。

---

## 七、从旧文件改 vs 新文件建的决策

```text
接到一个新功能需求
    │
    ↓
这个功能属于"已有模块的扩展"还是"全新模块"？
    │
    ├── 已有模块的扩展
    │   └── 在已有文件中加代码
    │       例：用户模块已经存在，要加"手机号登录"→ 在 user.py 里加函数
    │
    └── 全新模块
        └── 新建文件 + 注册到系统中
            例：系统原来没有"消息通知"功能 → 新建 notification.py
```

**改动面评估（PM 视角）：**

| 改动类型 | 涉及文件数 | 大致时间 |
|---------|-----------|---------|
| 改逻辑（加筛选、改排序） | 1-2 个文件 | 0.5-1 天 |
| 加字段（用户加生日） | 3-5 个文件 | 1-2 天 |
| 加模块（优惠券、积分） | 5+ 新文件 | 3 天-2 周 |
| 改架构（拆微服务） | 全局 | 以月计 |

---

## 八、学习路径建议

```text
第一阶段：能读（现阶段目标）
├── 打开 AI 生成的代码，对照速查表，标注每个关键词
├── 练习：用自己的话翻译每个 def 在做什么
└── 练习：看一个文件，判断它是哪一层（routes/services/models）

第二阶段：能 Debug
├── 故意改错代码，看报错信息，练习读 Traceback
├── 在 AI 生成的代码里加 print，追踪数据流向
└── 练习：报错了不慌，先看最后一行，再看倒数第二个 File

第三阶段：能 Review
├── 检查函数长度（> 50 行？）
├── 检查函数名（模糊？）
└── 检查错误处理（有 try/except 吗？）

第四阶段：能自己写
├── 用五步工作法，从纸上画图开始
├── 先在一个文件里写完全部功能，跑通再拆
└── 从改已有代码开始，再尝试建新文件
```

---

## 附录：速查卡（可以打印）

```
┌─────────────────────────────────────────────────────────────┐
│                   Python 代码阅读速查卡                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 【辨识文件类型】                                              │
│   看到 @router.get/post → routes 层（翻译官）                │
│   看到 class Xxx(BaseModel) → schemas 层（守门员）           │
│   看到纯 def 无装饰器 → services 层（大脑）                   │
│   看到 class Xxx(db.Model) → models 层（数据字典）           │
│                                                             │
│ 【基础骨架】                                                 │
│   import / from ... import  → 引入外部工具                   │
│   def 函数名(参数)           → 定义一个操作                   │
│   class 类名                 → 定义有属性+方法的对象          │
│   return 值                  → 函数输出                      │
│   if / elif / else           → 条件判断                      │
│   for x in y                 → 循环遍历                      │
│   try / except               → 尝试，出错兜底                │
│   f"...{变量}..."            → 拼字符串                      │
│                                                             │
│ 【数据容器】                                                 │
│   [] = list    有顺序的一堆东西    [1, 2, 3]                 │
│   {} = dict    key:value 对       {"name": "张三"}          │
│   None         空/不存在           if x is None             │
│   == != > <   比较符号            注意 == 和 = 不是一回事    │
│                                                             │
│ 【Models 层】                                                │
│   db.Column(...)        定义数据库列                         │
│   db.relationship(...)  表关联                              │
│   .add() / .commit()    写入数据库                           │
│                                                             │
│ 【Services 层】                                              │
│   .query.filter(...)    数据库查询                          │
│   raise XxxError        主动抛出异常                        │
│   : str / -> bool       类型标注                            │
│                                                             │
│ 【Routes 层】                                                │
│   @router.get/post/etc  装饰器，绑定 URL                    │
│   Depends(...)          自动注入依赖                        │
│   Query/Body/Path(...)  参数从哪里来                        │
│                                                             │
│ 【Schemas 层】                                               │
│   Field(...)            字段校验规则                         │
│                                                             │
│ 【Debug】                                                    │
│   print(变量)           看数据长什么样                       │
│   Traceback             从下往上读                          │
│   NameError             变量名不存在                         │
│   TypeError             参数类型/数量不对                    │
│   AttributeError        对象没有这个属性                     │
│                                                             │
│ 【Review】                                                   │
│   函数 > 50 行？        需要拆分                             │
│   函数名模糊？process()/handle() → 改成动词+名词             │
└─────────────────────────────────────────────────────────────┘
```
