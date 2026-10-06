<p align="center">
  <img src="assets/openintuition-banner.png" alt="OpenIntuition — 偏好变了，记忆也应该跟着变。" width="960">
</p>

# OpenIntuition

**一个在本地运行的偏好记忆测试工具。**

用户会改主意，有些要求只对当前会话有效，也可能要求撤销之前的偏好。OpenIntuition 把这些变化写成明确的事件序列，运行不同记忆策略，再告诉你：它们在哪里答对了，在哪里还在使用不适用的旧设置。

[English](README.md) · [中文上手教程](docs/GETTING_STARTED.zh-CN.md) · [示例结果报告](docs/example_results.md) · [事件规则](docs/policy_spec.md) · [参与开发](CONTRIBUTING.md)

**当前版本：** `0.1.0.dev2` · Python 3.12 · MIT 开源 · 无运行时依赖 · 不需要 API key

## 为什么要做这个项目？

想象这段历史：

> “我平时用深色主题。”
>
> “这次 S1 会议，临时改用浅色主题。”
>
> 到了另一场 S2 会话：“现在应该用什么主题？”

如果记忆程序只保留最后一次设置，它会回答 `light`。但临时要求只属于 S1，S2 的答案应该还是 `dark`。

另一个容易出错的情况是撤销。用户说“忘掉我的主题偏好”之后，程序不应该继续返回旧设置。按照本项目的规则，此时应回答 `ASK`：没有已知的适用偏好，需要询问用户。

OpenIntuition 从这些小而具体的问题开始，让错误可以被复现、定位和讨论。

## 现在已经能做什么？

- 校验 UTF-8 JSONL 场景数据，发现错误时给出文件、行号和字段。
- 运行两种本地策略：只记最后一个值，以及区分会话并处理撤销。
- 计算整体分数和各类场景的分数。
- 统计多少个完整场景的所有检查点都答对了。
- 保存每条预测，并生成列出错误的 Markdown 报告。
- 让策略只看到查询时刻之前的事件，不把参考答案传进去。

自带数据包含 **8 个虚构场景、24 个检查点**，覆盖长期更新、临时例外、撤销和无关事件。当前输入是结构化事件；项目还没有从自然语言聊天中提取偏好，也没有调用真实模型。

## 几分钟跑起来

请使用 **Python 3.12**；当前支持范围是 `>=3.12,<3.13`。先用 `python3 --version` 确认版本。以下命令适用于 macOS 或 Linux。

```bash
git clone https://github.com/taobuilds/OpenIntuition.git
cd OpenIntuition

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'

python -m openintuition_memory_check validate --data data/scenarios.jsonl
python -m openintuition_memory_check run --data data/scenarios.jsonl --policy both --output results/first-run
```

预期终端输出：

```text
naive_last_value: 19/24 checkpoints (79.2%); 4/8 scenarios fully correct
scoped_state: 24/24 checkpoints (100.0%); 8/8 scenarios fully correct
Results: results/first-run/report.md
```

打开 `results/first-run/report.md` 看结果。每次运行请使用**新的输出目录**，例如 `results/second-run`。程序会拒绝覆盖已有目录，避免丢失之前的结果。

安装时需要下载开发工具；评估本身在本地完成，不需要联网、API key 或模型服务。`dev` 额外安装 pytest；如果只想使用工具，可以运行 `python -m pip install -e .`。

项目更名后，Python 模块仍叫 `openintuition_memory_check`，所以之前的命令仍然可用。

## 两种策略有什么区别？

| 策略 | 如何回答 | 当前边界 |
| --- | --- | --- |
| `naive_last_value` | 返回这个偏好最后一次 set 或 temporary 的值 | 故意忽略会话范围和撤销 |
| `scoped_state` | 按规则处理长期设置、会话例外和撤销 | 只处理明确事件，不理解自然语言 |

两种策略都忽略 note 和不相关的偏好键。简单策略是用来突出范围与撤销问题的对照程序，并不代表其他记忆产品的实现。

只运行一种策略：

```bash
python -m openintuition_memory_check run --data data/scenarios.jsonl --policy scoped_state --output results/scoped-only
```

## 怎么读懂分数？

在自带的 `pilot-0.1` 数据上：

| 场景类型 | 检查点数量 | 只记最后一个值 | 区分会话、处理撤销 |
| --- | ---: | ---: | ---: |
| 长期偏好更新 | 6 | 6/6 | 6/6 |
| 临时例外 | 6 | 4/6 | 6/6 |
| 撤销偏好 | 6 | 3/6 | 6/6 |
| 无关事件 | 6 | 6/6 | 6/6 |
| **合计** | **24** | **19/24（79.2%）** | **24/24（100.0%）** |

简单策略错了 5 次：2 次把一个会话的临时偏好带到了其他会话，3 次在撤销后仍返回旧设置。它在 8 个场景中的 4 个场景里全部答对；按范围处理的策略在 8 个场景里全部答对。

**100% 表示符合当前定义的规则。** 参考答案也是按这些规则写的，所以这个分数还不能证明真实 AI 的记忆能力、更复杂历史上的泛化能力，或比其他产品更好。同一场景的 3 个检查点共享历史，24 个检查点也不等于 24 个独立实验。

### 三份结果文件

| 文件 | 内容 | 什么时候看 |
| --- | --- | --- |
| `report.md` | 总分、分类分数、逐条错误 | 想直接读懂结果、定位错误 |
| `predictions.jsonl` | 每种策略在每个检查点的答案 | 想筛选错误或写分析脚本 |
| `summary.json` | 每种策略的汇总指标 | 想让另一个程序读取分数 |

同时运行两种策略会产生 **48 条预测记录**。每条记录包含策略、场景、类别、检查点、查询步骤、偏好键、会话、参考答案、预测和是否答对。

例如：

```json
{"policy":"naive_last_value","scenario":"temporary_01","category":"temporary","checkpoint":"q3","as_of_step":3,"key":"theme","session_id":"S2","expected":"dark","predicted":"light","correct":false}
```

`expected` 是预先写好的标签，`predicted` 才是程序计算的结果。两个字符串完全一致才算答对。完整示例见[结果报告](docs/example_results.md)。

策略答错属于正常的比较结果，运行完成后退出码仍是 `0`；输入错误或输出目录错误返回 `2`。

## 场景数据怎么写？

JSONL 文件的一行就是一个独立场景。events 记录发生的事情，checkpoints 指定在某一步询问哪个会话的哪个偏好。

| 操作 | 含义 |
| --- | --- |
| `set` | 替换长期偏好，并清除该键之前的临时例外 |
| `temporary` | 仅为一个指定会话设置例外 |
| `revoke` | 清除这个键的长期偏好和所有临时例外 |
| `note` | 记录信息，不改变偏好 |

在对应会话中，临时值优先于长期值。没有适用值时返回 `ASK`。新的长期设置清除旧临时设置，是本原型的明确约定；当前还没有时间过期或会话结束事件。

下面是一条完整的最小场景：

```json
{"schema_version":"0.1","id":"theme_example","category":"update","events":[{"id":"e1","step":1,"op":"set","key":"theme","value":"dark","session_id":null}],"checkpoints":[{"id":"q1","as_of_step":1,"key":"theme","session_id":"S1","expected":"dark"}]}
```

事件步骤从 1 开始连续编号。检查点不能超出场景最后一步。字段必须符合定义；重复 ID、重复 JSON 字段、空行和格式错误都会被拒绝。校验器检查格式，不会替你判断参考答案是否合理。

阅读现有标签：

```bash
python -m openintuition_memory_check validate --data data/scenarios.jsonl --review
```

完整字段规则见[事件说明](docs/policy_spec.md)，数据来源和限制见[数据说明](data/DATASET_CARD.md)。这些案例由 AI 辅助起草并对照规则检查，都是虚构的，不含真实聊天记录。

## 怎么避免“把答案给了程序”？

每次查询时，评估器截取截至 `as_of_step` 的事件历史。策略只接收三个参数：这段事件、偏好键、会话 ID。它不会接收参考答案、场景类别、检查点对象或未来事件。

每个问题都从自己的事件历史计算，不同场景之间不共享状态。测试覆盖了这条输入边界。不过它是同一个 Python 进程中的接口约定，不是运行不可信代码的安全沙箱。

## 从哪里读代码？

```text
assets/                            标志、横幅和设计说明
data/
  scenarios.jsonl                  八个虚构场景
  DATASET_CARD.md                  数据来源与限制
docs/
  policy_spec.md                   事件和查询规则
  example_results.md               已生成的示例报告
  GETTING_STARTED.zh-CN.md          中文上手教程
src/openintuition_memory_check/
  schema.py                        数据类型和字段校验
  dataset.py                       读取 JSONL 和报告文件错误
  policies.py                      两种偏好策略
  evaluation.py                    预测、评分和报告
  cli.py                           终端命令入口
tests/                             格式、策略和输入边界测试
```

建议先读 `policies.py`，再读 `evaluation.py`，最后看 `cli.py`。开发检查：

```bash
python -m pytest -q
```

修改规则或增加场景前，请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。新增参考答案应先手工推导，不能直接抄被测策略的输出。

## 常见问题

| 问题 | 处理方式 |
| --- | --- |
| 提示找不到 openintuition_memory_check 模块 | 激活 `.venv`，并在该环境安装项目 |
| 提示 Python 版本不支持 | 使用 Python 3.12，重新创建对应虚拟环境 |
| 输出目录已存在 | 换一个新目录，保留旧结果 |
| 找不到场景文件 | 在项目根目录运行，或传文件的完整路径 |
| 某条数据校验失败 | 根据错误给出的行号和字段修改 |
| 策略答案与参考标签不同 | 先复查事件规则和标签，再判断是哪一方有问题 |

## 接下来做什么？

- [x] 结构化场景和严格校验
- [x] 两种本地策略比较，按检查点和完整场景评分
- [x] 逐条预测文件和可阅读的错误报告
- [ ] 更长的历史、重复临时更新、更多偏好键组合
- [ ] 独立审查的评估场景
- [ ] 在相同输入接口下增加其他策略
- [ ] 自然语言提取和可选模型接入

目前优先增加明确偏好变化的测试覆盖，再考虑模型调用。

## 项目的小猫头鹰

青绿色小猫头鹰采用不规则手绘线条和不对称的表情。眼睛里的环代表观察与记忆，旁边的橙色光点代表直觉。它是 OpenIntuition 当前的项目形象。

[透明背景标志](assets/openintuition-logo.png) · [首页横幅](assets/openintuition-banner.png) · [设计说明与生成提示词](assets/README.md)

## 开源许可

代码、虚构案例和项目图片均使用 [MIT 许可](LICENSE)。
