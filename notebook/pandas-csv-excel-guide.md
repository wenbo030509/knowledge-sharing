# Pandas 结构化数据处理指南

> CSV / Excel 日常处理速查。围绕四个核心操作展开：读取列 → 新增列 → 保存文件 → 批量处理。

---

## 前置认知

结构化数据处理就是一条 Pipeline。pandas 帮你把每个 Stage 都写好了，你只需要调用。

```text
[CSV/Excel] → 读取列 → 过滤 → 新增列 → 分组统计 → [保存]
     ↑           ↑       ↑       ↑        ↑        ↑
  read_csv    df["列名"] df[条件] df["新列"]= groupby  to_excel
```

操作的基本单位是 **DataFrame** = 一张有行有列的表，等于你在 Excel 里看到的东西。

```text
DataFrame 的样子：
     id    subject    status       score
0   001   math       qualified    85
1   002   math       discarded    92
2   003   physics    qualified    78
3   004   chemistry  needs_repair 88
    ↑ 索引（行号），pandas 自动生成
```

---

## 环境准备

```bash
pip install pandas openpyxl
```

```python
import pandas as pd    # pd 是行业惯例缩写
```

---

## 一、读取列

### 1.1 读整个文件

```python
# CSV
df = pd.read_csv("data.csv")

# CSV 中文乱码时
df = pd.read_csv("data.csv", encoding="utf-8")
df = pd.read_csv("data.csv", encoding="gbk")      # Windows 导出常用

# Excel
df = pd.read_excel("data.xlsx")
df = pd.read_excel("data.xlsx", sheet_name="Sheet1")  # 指定 Sheet

# 只读需要的列（文件大的时候省内存）
df = pd.read_csv("data.csv", usecols=["id", "subject", "status"])
df = pd.read_excel("data.xlsx", usecols=["id", "subject", "status"])
```

**读完立刻验证：**

```python
print(df.shape)        # (5497, 5) → 5497 行，5 列
print(df.columns.tolist())  # 看列名列表
print(df.head())       # 看前 5 行数据
```

### 1.2 取一列

```python
df["subject"]                  # 取一列，返回 Series（带索引的数组）
df["subject"].tolist()         # 转成 Python 列表
df["subject"].unique()         # 去重，看这一列有哪些不同的值
df["subject"].value_counts()   # 每个值各出现多少次
```

### 1.3 取多列

```python
df[["id", "subject", "status"]]           # 双括号取多列，返回 DataFrame
```

### 1.4 按条件取列中的值

```python
# 某列满足条件的那些行，取另一列的值
df[df["status"] == "qualified"]["id"]     # 合格数据的所有 id
df[df["score"] > 80]["subject"].unique()  # 高分题涉及哪些学科
```

### 1.5 遍历列

```python
for col in df.columns:
    print(f"列名: {col}, 空值数: {df[col].isnull().sum()}")

# 只看某几列
for col in ["id", "subject", "status"]:
    print(f"{col}: {df[col].unique()}")
```

### 1.6 检查列是否存在、列类型

```python
"subject" in df.columns          # True/False，这列存在吗？
df["subject"].dtype              # 列的数据类型：object(文本)、int64、float64
df.dtypes                        # 所有列的类型
```

### 1.7 读取列速查

```text
需求                               代码
──────────────────────────────────────────────────────
读整个文件                         pd.read_csv("f.csv") / pd.read_excel("f.xlsx")
只读指定列                         pd.read_csv("f.csv", usecols=["A","B"])
取一列                             df["列名"]
取多列                             df[["列名1", "列名2"]]
一列去重                           df["列名"].unique()
一列计数                           df["列名"].value_counts()
取满足条件的行，只看某列            df[df["status"]=="qualified"]["id"]
检查列是否存在                     "列名" in df.columns
看列的数据类型                     df["列名"].dtype
列出所有列名                       df.columns.tolist()
每列空值统计                       df.isnull().sum()
```

---

## 二、新增列

### 2.1 核心语法

```python
df["新列名"] = 值或表达式
```

这是你整个工作流里最高频的操作——读取原始数据，计算新列，保存带新列的文件。

### 2.2 从已有列计算新列

```python
# 数学运算
df["score_double"] = df["score"] * 2
df["score_ratio"] = df["score"] / 100
df["total_score"] = df["math"] + df["english"] + df["physics"]

# 字符串操作
df["subject_upper"] = df["subject"].str.upper()       # 全大写
df["subject_lower"] = df["subject"].str.lower()        # 全小写
df["subject_clean"] = df["subject"].str.strip()        # 去首尾空格
df["cot_length"] = df["cot"].str.len()                 # 字符串长度
df["has_reasoning"] = df["cot"].str.contains("因为")   # 是否包含关键词
```

### 2.3 条件判断新增列——最常用的模式

```python
# 方式一：简单条件（lambda）
df["result"] = df["score"].apply(lambda x: "通过" if x >= 60 else "不通过")

# 方式二：多条分支（自定义函数）
def classify(score):
    if score >= 85:
        return "优秀"
    elif score >= 60:
        return "合格"
    elif score >= 0:
        return "不合格"
    else:
        return "异常分数"

df["grade"] = df["score"].apply(classify)

# 方式三：用 np.select 处理多个条件（数据量大时更快）
import numpy as np
conditions = [
    df["score"] >= 85,
    df["score"] >= 60,
    df["score"] >= 0,
]
choices = ["优秀", "合格", "不合格"]
df["grade"] = np.select(conditions, choices, default="异常分数")
```

### 2.4 跨行新增列——基于多列判断

```python
# 检查 CoT 压缩度：cot 长度 / question 长度
df["compression_ratio"] = df["cot"].str.len() / df["question"].str.len()

# 检查 answer 是否在 cot 中出现
df["answer_in_cot"] = df.apply(
    lambda row: str(row["answer"]) in str(row["cot"]) if pd.notna(row["answer"]) else False,
    axis=1     # axis=1 表示逐行处理
)

# 组合多列生成一个新标识
df["data_key"] = df["subject"] + "_" + df["id"].astype(str)
```

### 2.5 修改已有列的值

```python
# 整列替换
df["status"] = df["status"].str.lower()

# 条件修改——只改满足条件的行
df.loc[df["status"] == "error", "status"] = "discarded"
df.loc[df["score"] < 0, "score"] = 0
df.loc[df["subject"].isnull(), "subject"] = "unknown"

# 条件修改——同时改多列
df.loc[df["status"] == "discarded", "remark"] = "质检不通过"
df.loc[df["status"] == "discarded", "is_valid"] = False
```

### 2.6 删除列、重命名列

```python
# 删除列
df.drop("temp_col", axis=1, inplace=True)       # 删一列
df.drop(["col1", "col2"], axis=1, inplace=True)  # 删多列

# 重命名列
df.rename(columns={"旧名": "新名", "old": "new"}, inplace=True)

# 批量重命名：全部转小写、替换空格
df.columns = df.columns.str.lower()
df.columns = df.columns.str.replace(" ", "_")
```

### 2.7 新增列速查

```text
需求                               代码
──────────────────────────────────────────────────────
数学计算新列                       df["新"] = df["旧"] * 2
字符串长度                         df["新"] = df["列"].str.len()
字符串包含判断                     df["新"] = df["列"].str.contains("关键词")
简单条件：值>=阈值 → 通过/不通过   df["新"] = df["列"].apply(lambda x: "通过" if x>=60 else "不通过")
复杂条件：多分支分类               df["新"] = df["列"].apply(自定义函数)
高效多条件判断                     np.select(conditions, choices, default)
多列组合判断                       df.apply(lambda row: ..., axis=1)
条件修改已有列                     df.loc[df["列"]==条件, "要改的列"] = 新值
条件同时改多列                     df.loc[条件, ["列1","列2"]] = [值1, 值2]
删除列                             df.drop("列名", axis=1)
重命名列                           df.rename(columns={"旧":"新"})
```

---

## 三、保存修改后的文件

### 3.1 核心语法

```python
df.to_csv("output.csv", index=False)
df.to_excel("output.xlsx", index=False)
```

`index=False` 必须加——否则 pandas 会把行号（0,1,2...）也写成一列。

### 3.2 保存为 CSV

```python
# 基本保存
df.to_csv("output.csv", index=False)

# 中文 Excel 打开不乱码
df.to_csv("output.csv", encoding="utf-8-sig", index=False)

# 只保存部分列
df[["id", "subject", "status", "score", "grade"]].to_csv("output.csv", index=False)

# 保存时修改列的顺序
df[["id", "subject", "question", "cot", "answer", "grade"]].to_csv("output.csv", index=False)
```

### 3.3 保存为 Excel

```python
# 基本保存
df.to_excel("output.xlsx", index=False)

# 同一个 Excel 多个 Sheet
with pd.ExcelWriter("output.xlsx") as writer:
    qualified.to_excel(writer, sheet_name="合格数据", index=False)
    discarded.to_excel(writer, sheet_name="废弃数据", index=False)
    needs_repair.to_excel(writer, sheet_name="待修复", index=False)
```

### 3.4 典型的"读取→处理→保存"完整流程

这是你每天最多做的事：

```python
import pandas as pd

# 1. 读取原始文件
df = pd.read_excel("原始数据.xlsx")

# 2. 新增列：根据 score 分等级
def grade(score):
    if score >= 85: return "优秀"
    elif score >= 60: return "合格"
    else: return "不合格"

df["grade"] = df["score"].apply(grade)

# 3. 新增列：标记是否合格
df["is_qualified"] = df["grade"].isin(["优秀", "合格"])

# 4. 修改已有列：subject 统一转小写
df["subject"] = df["subject"].str.lower().str.strip()

# 5. 筛选出需要单独导出的数据
wrong_data = df[df["is_qualified"] == False]

# 6. 保存完整结果
df.to_excel("处理结果.xlsx", index=False)

# 7. 保存不合格清单到单独 Sheet
with pd.ExcelWriter("处理结果.xlsx") as writer:
    df.to_excel(writer, sheet_name="全部数据", index=False)
    wrong_data.to_excel(writer, sheet_name="不合格", index=False)

print(f"处理完成：{len(df)} 条，不合格 {len(wrong_data)} 条")
```

### 3.5 保存过滤结果——筛出什么就保存什么

```python
# 筛选 → 直接保存
df[df["status"] == "qualified"].to_excel("合格数据.xlsx", index=False)
df[df["status"] == "discarded"].to_excel("废弃数据.xlsx", index=False)
df[df["status"] == "needs_repair"].to_excel("待修复数据.xlsx", index=False)

# 按学科拆分保存
for subject, group in df.groupby("subject"):
    filename = f"按学科导出/{subject}.xlsx"
    group.to_excel(filename, index=False)
    print(f"{subject}: {len(group)} 条 → {filename}")
```

### 3.6 保存前检查

```python
# 保存前先看看数据对不对
print(f"即将保存：{len(df)} 行, {len(df.columns)} 列")
print(f"列名：{df.columns.tolist()}")
print(f"空值统计：\n{df.isnull().sum()}")
print(f"status 分布：\n{df['status'].value_counts()}")

# 确认无误再保存
df.to_excel("output.xlsx", index=False)
```

### 3.7 保存文件速查

```text
需求                               代码
──────────────────────────────────────────────────────
保存 CSV                           df.to_csv("o.csv", index=False)
保存 CSV（中文不乱码）              df.to_csv("o.csv", encoding="utf-8-sig", index=False)
保存 Excel                         df.to_excel("o.xlsx", index=False)
只保存部分列                       df[["A","B"]].to_excel("o.xlsx", index=False)
按顺序保存列                       df[["A","B","C","D"]].to_excel(...)
一个 Excel 多个 Sheet              pd.ExcelWriter + to_excel(sheet_name=...)
筛选后直接保存                     df[df["status"]=="qualified"].to_excel("合格.xlsx")
分组保存                           for name, g in df.groupby("col"): g.to_excel(f"{name}.xlsx")
保存前检查数据                     print(df.shape, df.isnull().sum(), df["col"].value_counts())
```

---

## 四、批量处理

### 4.1 多个文件汇总成一个（最高频）

```python
from pathlib import Path
import pandas as pd

all_data = []
folder = Path("data/")

for file in folder.glob("*.csv"):
    df = pd.read_csv(file)
    df["来源文件"] = file.name    # 加一列标记数据来源
    all_data.append(df)
    print(f"已读取: {file.name}, {len(df)} 行")

result = pd.concat(all_data, ignore_index=True)
result.to_excel("汇总结果.xlsx", index=False)
print(f"\n合并完成：{len(all_data)} 个文件 → {len(result)} 行")
```

### 4.2 一个文件按维度拆成多个（按列分组）

```python
# 按 subject 列拆分，每个值一个文件
for value, group in df.groupby("subject"):
    filename = f"output/{value}.xlsx"
    group.to_excel(filename, index=False)
    print(f"{value}: {len(group)} 条 → {filename}")

# 按多列组合拆分
for (subject, status), group in df.groupby(["subject", "status"]):
    filename = f"output/{subject}_{status}.xlsx"
    group.to_excel(filename, index=False)
```

### 4.3 同一个处理逻辑应用到多个文件

```python
# 场景：多个 Excel 都需要做同样的处理（加列、筛选、保存）

def process_file(filepath: str) -> pd.DataFrame:
    """对单个文件做处理，返回处理后的 DataFrame"""
    df = pd.read_excel(filepath)

    # 统一的处理逻辑
    df["subject"] = df["subject"].str.lower().str.strip()
    df["cot_length"] = df["cot"].str.len()
    df["is_valid"] = df["cot_length"] >= 10

    return df

# 批量处理
for file in Path("data/").glob("*.xlsx"):
    result = process_file(file)
    output_path = f"output/{file.stem}_已处理.xlsx"
    result.to_excel(output_path, index=False)
    print(f"{file.name}: {len(result)} 行 → {output_path}")
```

### 4.4 用 pandas 自身的分块读取（文件太大内存放不下时）

```python
# CSV 文件太大（比如几百万行），用 chunksize 分块读取
chunks = []
for chunk in pd.read_csv("huge_file.csv", chunksize=10000):
    # 每次读 10000 行
    chunk = chunk[chunk["status"] == "qualified"]  # 只留合格数据
    chunks.append(chunk)

result = pd.concat(chunks, ignore_index=True)
result.to_csv("filtered_output.csv", index=False)
print(f"过滤后：{len(result)} 行")
```

### 4.5 真正的并发处理——多线程加速

当你要处理几百个文件，串行太慢时：

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import pandas as pd


def process_and_save(filepath: Path) -> dict:
    """处理单个文件并保存，返回统计信息"""
    df = pd.read_excel(filepath)

    # 你的处理逻辑
    df["subject"] = df["subject"].str.lower().str.strip()
    df["is_valid"] = df["cot"].str.len() >= 10

    # 保存
    output_path = f"output/{filepath.stem}_已处理.xlsx"
    df.to_excel(output_path, index=False)

    return {
        "file": filepath.name,
        "rows": len(df),
        "valid": df["is_valid"].sum(),
        "output": output_path
    }


# 并发处理所有文件
files = list(Path("data/").glob("*.xlsx"))
print(f"共 {len(files)} 个文件，开始并发处理...")

results = []
with ThreadPoolExecutor(max_workers=4) as executor:       # 4 个线程同时跑
    futures = {executor.submit(process_and_save, f): f for f in files}
    for future in as_completed(futures):
        result = future.result()
        results.append(result)
        print(f"✅ {result['file']}: {result['rows']}行 → {result['output']}")

print(f"\n全部完成，共处理 {len(results)} 个文件")
```

**什么时候用并发：**
- 文件数量 > 20 个，每个文件独立处理 → 用 `ThreadPoolExecutor`
- 文件 < 10 个 → 串行 for 循环就够，不值得加并发的复杂度

### 4.6 目录不存在时自动创建

```python
import os
from pathlib import Path

output_dir = Path("output/按学科拆分")
output_dir.mkdir(parents=True, exist_ok=True)   # 目录不存在就创建

for value, group in df.groupby("subject"):
    filename = output_dir / f"{value}.xlsx"
    group.to_excel(filename, index=False)
```

### 4.7 批量处理速查

```text
需求                               代码
──────────────────────────────────────────────────────
遍历目录下所有 CSV/Excel            Path("dir/").glob("*.csv")
多文件合并                         pd.concat([df1, df2, ...], ignore_index=True)
加来源标记列                       df["来源"] = file.name
按列值分组导出                     for v, g in df.groupby("列"): g.to_excel(f"{v}.xlsx")
同一逻辑处理多文件                 定义函数 + for 循环调用
大文件分块读取                     pd.read_csv("f.csv", chunksize=10000)
并发处理多文件                     ThreadPoolExecutor(max_workers=4)
自动创建输出目录                   Path("output").mkdir(parents=True, exist_ok=True)
```

---

## 五、其他常用操作速查

### 5.1 看数据概览

```python
df.info()              # 每列类型、多少空值
df.describe()          # 数值列的统计：均值、最大、最小
df.head(10)            # 看前 10 行
df.tail(5)             # 看最后 5 行
df.sample(5)           # 随机抽 5 行
```

### 5.2 筛选数据

```python
df[df["status"] == "qualified"]                         # 等于
df[df["status"] != "discarded"]                         # 不等于
df[df["score"] > 80]                                    # 大于
df[(df["subject"] == "math") & (df["status"] == "qualified")]  # 且（括号不能省）
df[(df["subject"] == "math") | (df["subject"] == "physics")]   # 或
df[df["subject"].isin(["math", "physics", "chemistry"])]       # 在列表中
df[df["score"].isnull()]                                # 为空
df[df["score"].notnull()]                               # 非空
df[~df["subject"].isin(["math"])]                       # 取反
df[df["cot"].str.contains("判别式")]                     # 字符串包含
```

### 5.3 分组统计

```python
df.groupby("subject").size()                                    # 分组计数
df.groupby("subject")["score"].mean()                           # 分组均值
df.groupby("subject").agg({"score": ["mean", "max", "count"]})  # 多指标
df.groupby(["subject", "status"]).size()                        # 多维度分组
```

### 5.4 排序

```python
df.sort_values("score")                                      # 升序
df.sort_values("score", ascending=False)                     # 降序
df.sort_values(["subject", "score"], ascending=[True, False]) # 多列
```

### 5.5 合并

```python
pd.concat([df1, df2], ignore_index=True)                    # 竖着拼
pd.merge(df1, df2, on="id", how="left")                     # 横着拼（SQL JOIN）
```

### 5.6 去重

```python
df.drop_duplicates()                   # 完全重复行去重
df.drop_duplicates(subset=["id"])      # 按某列去重
```

---

## 六、完整示例

### 场景一：benchmark 知识点抽检（你的真实场景）

```python
import pandas as pd

# Step 1: 读取列
df = pd.read_excel("benchmark_knowledge_points.xlsx")
print(f"总行数: {len(df)}")
print(f"列名: {df.columns.tolist()}")

# Step 2: 看分布
print(df["is_correct"].value_counts())

# Step 3: 新增列——标记题型
df["has_error"] = df["is_correct"] == False
df["needs_review"] = df["has_error"] | (df["answer_has_issue"] == True)

# Step 4: 筛选
wrong_kp = df[df["is_correct"] == False]
wrong_answer = df[df["answer_has_issue"] == True]

# Step 5: 保存——筛选结果 + 完整结果一起保存到同一个 Excel
with pd.ExcelWriter("知识点抽检结果.xlsx") as writer:
    df.to_excel(writer, sheet_name="全部数据", index=False)
    wrong_kp.to_excel(writer, sheet_name="知识点错误", index=False)
    wrong_answer.to_excel(writer, sheet_name="答案错误", index=False)

print(f"完成：知识点错误 {len(wrong_kp)} 题，答案错误 {len(wrong_answer)} 题")
```

### 场景二：批量读多个 CSV、新增列、保存汇总

```python
import pandas as pd
from pathlib import Path

all_data = []

for file in Path("原始数据/").glob("*.csv"):
    # 1. 读取
    df = pd.read_csv(file)

    # 2. 新增列
    df["来源文件"] = file.name
    df["处理时间"] = pd.Timestamp.now()
    df["cot_length"] = df["cot"].str.len()
    df["is_valid"] = df["cot_length"] >= 10

    all_data.append(df)
    print(f"读取: {file.name}, {len(df)} 行")

# 3. 合并
result = pd.concat(all_data, ignore_index=True)

# 4. 保存汇总 + 不合格明细
with pd.ExcelWriter("批量处理结果.xlsx") as writer:
    result.to_excel(writer, sheet_name="全部数据", index=False)
    result[result["is_valid"] == False].to_excel(writer, sheet_name="不合格", index=False)

print(f"\n完成：{len(all_data)} 个文件，共 {len(result)} 行")
```

---

## 七、常见坑

### 坑 1：`&` 和 `|` 的优先级

```python
# ❌ 错误：条件不加括号
df[df["subject"] == "math" & df["status"] == "qualified"]

# ✅ 正确：每个条件加括号
df[(df["subject"] == "math") & (df["status"] == "qualified")]
```

### 坑 2：修改 DataFrame 的警告

```python
# pandas 有时会报 SettingWithCopyWarning

# ✅ 用 .loc 避免
df.loc[df["status"] == "old", "status"] = "new"
#   └── 定位到行     └── 定位到列   └── 新值
```

### 坑 3：CSV 编码问题

```python
# 读进来乱码
df = pd.read_csv("file.csv", encoding="utf-8")   # 先试这个
df = pd.read_csv("file.csv", encoding="gbk")      # Windows 中文常用

# 写出去 Excel 打开乱码
df.to_csv("output.csv", encoding="utf-8-sig", index=False)
```

### 坑 4：合并后索引不连续

```python
# concat 之后行号可能是 0,1,2,0,1,2,0,1,2
result = pd.concat([df1, df2], ignore_index=True)  # 加这个参数，重新编号
```

### 坑 5：新增列时整列赋值 vs 条件赋值

```python
# ✅ 新增列——整列赋值
df["新列"] = df["旧列"] * 2

# ✅ 修改已有列——条件赋值，必须用 .loc
df.loc[df["status"] == "error", "status"] = "discarded"

# ❌ 条件赋值不加 .loc
df[df["status"] == "error"]["status"] = "discarded"   # 可能不生效，还会报警告
```

---

## 速查卡

```text
┌──────────────────────────────────────────────────────────┐
│              Pandas 结构化数据处理速查卡                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ 【一、读取列】                                            │
│   pd.read_csv("f.csv")               读 CSV              │
│   pd.read_csv("f.csv", usecols=["A"]) 只读指定列          │
│   pd.read_csv("f.csv", encoding="gbk")  中文 CSV         │
│   pd.read_excel("f.xlsx")            读 Excel            │
│   pd.read_excel("f.xlsx", sheet_name="S1") 指定 Sheet    │
│   df["col"]              取一列                          │
│   df[["c1","c2"]]        取多列                          │
│   df["col"].unique()     一列去重                        │
│   df["col"].value_counts() 一列分布                      │
│   df.columns.tolist()    列名列表                        │
│   df.dtypes              每列类型                        │
│   df.isnull().sum()      每列空值数                      │
│   "col" in df.columns    列是否存在                      │
│                                                          │
│ 【二、新增列】                                            │
│   df["新"] = df["旧"] * 2              计算新列          │
│   df["新"] = df["列"].str.len()        字符串长度        │
│   df["新"] = df["列"].str.contains("x") 包含判断         │
│   df["新"] = df["列"].apply(fn)        每行应用函数      │
│   np.select(conditions, choices, def)  高效多条件         │
│   df.apply(lambda row: ..., axis=1)    跨列计算           │
│   df.loc[条件, "列"] = 值              条件修改           │
│   df.drop("列", axis=1)                删除列            │
│   df.rename(columns={"旧":"新"})       重命名列           │
│                                                          │
│ 【三、保存文件】                                          │
│   df.to_csv("o.csv", index=False)          写 CSV        │
│   df.to_csv("o.csv", encoding="utf-8-sig") Excel不乱码   │
│   df.to_excel("o.xlsx", index=False)       写 Excel      │
│   df[["A","B"]].to_excel("o.xlsx")        只保存部分列   │
│   with pd.ExcelWriter("o.xlsx") as w:      多 Sheet      │
│       df1.to_excel(w, sheet_name="S1")                   │
│       df2.to_excel(w, sheet_name="S2")                   │
│   df[条件].to_excel("o.xlsx")             筛选→保存      │
│   for v,g in df.groupby("c"):             分组→保存      │
│       g.to_excel(f"{v}.xlsx")                            │
│                                                          │
│ 【四、批量处理】                                          │
│   Path("dir/").glob("*.csv")            遍历目录          │
│   pd.concat([df1,df2], ignore_index=True)  合并           │
│   df["来源"] = file.name                 加来源标签      │
│   for file in Path("dir/").glob("*"):    逐文件处理       │
│   pd.read_csv("f.csv", chunksize=10000)  大文件分块      │
│   ThreadPoolExecutor(max_workers=4)      并发加速         │
│   Path("out").mkdir(parents=True,        自动建目录       │
│       exist_ok=True)                                      │
│                                                          │
│ 【筛选】                                                  │
│   df[df["col"] == v]              等于                    │
│   df[df["col"] != v]              不等于                  │
│   df[df["col"] > n]               大于                    │
│   df[(A) & (B)]                   且（括号不能省）         │
│   df[(A) | (B)]                   或                      │
│   df[df["col"].isin([...])]       属于列表                │
│   df[df["col"].isnull()]          为空                    │
│   df[~df["col"].isin([...])]      取反                    │
│                                                          │
│ 【分组统计】                                              │
│   df.groupby("col").size()                分组计数        │
│   df.groupby("col")["n"].mean()           分组均值        │
│   df.groupby("col").agg({                 多指标          │
│       "n": ["mean","max","count"]                         │
│   })                                                     │
│                                                          │
│ 【排序】                                                  │
│   df.sort_values("col")                 升序              │
│   df.sort_values("col", ascending=False) 降序             │
│                                                          │
│ 【合并】                                                  │
│   pd.concat([df1,df2], ignore_index=True)  竖着拼         │
│   pd.merge(df1, df2, on="key", how="left") 横着拼         │
│                                                          │
│ 【去重】                                                  │
│   df.drop_duplicates()                  完全重复去重      │
│   df.drop_duplicates(subset=["id"])     按某列去重        │
└──────────────────────────────────────────────────────────┘
```
