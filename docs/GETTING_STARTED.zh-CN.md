# 跑一次 OpenIntuition，读懂它的结果

OpenIntuition 目前回答一个具体问题：当用户更新、临时改变或撤销偏好时，记忆程序会不会继续返回错误的旧设置？

它已经能读取测试场景、运行两种策略、比较答案并输出报告。整个过程在本地运行，不需要 API key，也不会产生模型调用费用。

## 1. 打开项目，激活环境

如果你已经在项目文件夹里完成过安装，直接运行：

```bash
source .venv/bin/activate
```

如果你第一次下载这个项目，请使用 Python 3.12：

```bash
git clone https://github.com/taobuilds/OpenIntuition.git
cd OpenIntuition
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

后面的命令都要在项目根目录运行，也就是包含 README.md、data 和 src 的文件夹。

## 2. 运行比较

```bash
python -m openintuition_memory_check run --data data/scenarios.jsonl --policy both --output results/first-run
```

参数的意思：

- `run`：运行测试并评分。
- `--data`：使用哪份场景数据。
- `--policy both`：把两种策略都跑一遍。
- `--output`：把结果放进这个新文件夹。

你会看到：

```text
naive_last_value: 19/24 checkpoints (79.2%); 4/8 scenarios fully correct
scoped_state: 24/24 checkpoints (100.0%); 8/8 scenarios fully correct
Results: results/first-run/report.md
```

重复运行时，请把输出目录换成 `results/second-run` 等新名字。程序会拒绝覆盖已有目录。策略答错属于比较结果，程序仍然正常完成；输入或写文件失败才算运行错误。

## 3. 两种策略到底有什么区别？

`naive_last_value` 是简单对照程序：同一个偏好，只保留最后一次设置的值。它会忽略“仅这次会话有效”和“已经撤销”。它会过滤 note，因此它也不是把每条文字都直接存成偏好。

`scoped_state` 则区分长期设置和特定会话的临时设置。撤销时，它清除对应设置；没有适用设置时返回 `ASK`，意思是需要询问用户。

例如：

1. 用户长期喜欢深色主题。
2. 用户只在 S1 会话临时使用浅色主题。
3. 现在询问 S2 会话该用什么主题。

简单策略回答 `light`，因为浅色是最后设置的值。按会话处理的策略回答 `dark`，因为 S1 的临时要求不应影响 S2。

## 4. 看报告，而不只看百分比

打开 `results/first-run/report.md`，里面有总分、每类场景的分数，以及所有答错的检查点。

这份数据上，简单策略有 5 个错误：2 个是把临时设置带到了其他会话，3 个是撤销之后仍然返回旧设置。它在 4 个完整场景里答对了所有问题；另一个策略在 8 个完整场景里都答对了。

另外两份文件方便后续分析：

- `predictions.jsonl`：逐条保存预测、预期答案和是否答对，两个策略总共 48 条记录。
- `summary.json`：保存机器可以读取的汇总分数。

这里的 `expected` 是预先写好的参考答案，`predicted` 才是程序实际计算出来的答案。评分是字符串完全一致才算正确。程序不会把 expected 传给策略，也不会把查询时刻之后的事件传进去。

## 5. 这个结果能说明什么？

它说明这两段程序在这 8 个人工场景上的行为不同。100% 表示 scoped_state 符合当前定义的规则。这些规则也是参考答案的依据，所以还不能说它证明了 AI 记忆更强，更不能拿这个分数去声称超过其他产品。

同一个场景的 3 个问题共享一段历史，所以 24 个检查点不等于 24 个独立实验。后续应先增加更复杂、独立设计的场景，再考虑真实模型。

## 6. 你可以从哪里开始理解代码？

先读 `src/openintuition_memory_check/policies.py`，它包含两种策略，代码最短，也是项目的核心。然后读 `evaluation.py`：它负责截取事件历史、调用策略、比较答案和写报告。最后再读 `cli.py`，理解终端命令如何调用这些功能。

你可以先动手做一个小实验：复制一个 temporary 场景，给它一个新的 id，把临时设置的会话改成 S2，并手工重新推导每个 expected。然后验证数据并重新运行比较。不要用策略输出反过来填参考答案，否则测试失去了独立判断的作用。

开发检查：

```bash
python -m pytest -q
```

接下来值得增加的场景是：连续两次临时更新、临时设置后撤销、重新设置长期偏好清除旧例外，以及多个偏好互不干扰。保留现有例子，有助于发现后来改代码时是否破坏了已有行为。
