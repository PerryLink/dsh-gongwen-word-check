# dsh-gongwen-word-check — 公文台账版头与主体要素核对

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-gongwen-word-check` 读取一份公文台账——每份已发出公文一行——按版本化的规则库核对这份台账登记的文字：`发文字号` 是否符合「机关代字〔年份〕序号」的形式、年份是否用六角括号〔〕括入，`成文日期` 是否可解析且不晚于核对日，`文种` 是否落在本机关自己配置的取值清单内，`主送机关` 是否填写，`标题` 是否在配置的长度上限内，`发文字号` 是否在台账内重复，以及标题里是否残留未替换的模板占位符。

## Install

```sh
dsh plugin --profile <name> add dsh-gongwen-word-check
dsh --profile <name> --dump-config | grep 'dsh-gongwen-word-check'
```

## 实际输出长什么样

![Terminal demo of dsh-gongwen-word-check: real output over its GW-006 fixture](https://raw.githubusercontent.com/PerryLink/dsh-gongwen-word-check/main/docs/assets/dsh-gongwen-word-check-hero.png)

![Animated terminal demo of dsh-gongwen-word-check](https://raw.githubusercontent.com/PerryLink/dsh-gongwen-word-check/main/docs/assets/dsh-gongwen-word-check-demo.gif)

本插件对自己 `GW-006` 测试夹具的**真实输出**，不是示意图。规则库不伪造引文，因此每条发现都会同时写明所引条款，以及该条款原文本次未取得。

## 它回答什么问题

| 你会问 | 它怎么答 |
|---|---|
| 发文字号写成了 `某政发[2026]15号`，用的是方括号。 | `GW-001` 会报出该行：本条配置的 pattern 要求年份用六角括号〔〕括入，应写成 `某政发〔2026〕15号`。本条**只核对发文字号的形式**——机关代字由各机关自行规定，它不判断代字是否正确，也不判断序号是否连续或是否重号。 |
| 成文日期按公文的习惯写成了汉字：二〇二六年三月十五日。 | `GW-002` 会报「无法解析」。它识别 `2026-03-15` 与 `2026-03-15 09:30` 两种写法，汉字日期需先统一为这两种写法，或停用本条。本条也**不核对成文日期与签发日期的关系**，那属于发文流程的内部一致性。 |
| 本机关没有配置文种清单，`GW-003` 会静默通过吗？ | 不会。`GW-003` 不内置任何清单，`values` 为空时它出现在报告的 `skipped` 中，而不是静默通过。《党政机关公文处理工作条例》列举了十五种主要文种，但本规则库**不硬编码**该清单——哪些文种可用取决于本机关口径。本条也不判断某份公文应当使用哪一种文种。 |
| 某行的主送机关栏是空的。 | `GW-004` 会报出该行：缺这一栏就无法确认这份公文发给了谁。它只核对是否填写，**不判断主送范围是否恰当**——主送谁、抄送谁属于拟稿与核稿的判断。 |
| 我们的标题比较长，这个长度上限是从哪儿来的？ | `GW-005` 在 `标题` 超过配置的 60 字时报出。**这个数字是本规则库的出厂配置，不是标准数值**：GB/T 9704-2012 对标题的量化要求只有「2 号小标宋体字」，未规定字数上限。本机关若习惯更长的标题，请调大 `maxLength` 或停用本条。本条只做字数核对，**不判断标题的文字表述是否规范**。 |
| 两行填了同一个发文字号。 | `GW-006` 会报出重复的文号；比较时忽略空白字符，命中通常意味着重号或抄错，需人工确认。它**不判断哪一份才应当使用该文号**。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
|---|---|---|
| 《党政机关公文格式》 | GB/T 9704-2012（现行，本次未取得条文） | GW-001, GW-002, GW-004, GW-005, GW-007 |
| 《党政机关公文处理工作条例》 | 中办发〔2012〕14号（自 2012 年 7 月 1 日起施行） | GW-003, GW-006 |

**边界（中文译文，以英文原文为准）：** 本插件核对一份**公文台账的版头与主体要素**，范围限于登记表可以机械判定的事项——发文字号是否符合「机关代字〔年份〕序号」的形态，签发日期是否可解析，公文种类是否取自你的取值口径，是否记录了主送机关，标题是否不过长，编号是否不重复，以及是否残留模板占位符。它核对的是**登记表所记录的文本，而不是版式**——字体、字号、页边距与印章位置只能就公文本身判断。

> ### ⚠️ 本插件报告中的引文究竟以什么为依据（以英文原文为准）
>
> **《党政机关公文处理工作条例》（中办发〔2012〕14号）已经取得并逐字阅读**，`rules/evidence/clause-verification.md` 记录了所引的条款——第八条（十五种公文种类）、第九条（格式要素，包括「发文字号。由发文机关代字、年份、发文顺序号组成」和「主送机关。公文的主要受理机关」）、第十条（把版式交由 GB/T 9704-2012 规定）和第四十二条（自 2012-07-01 起施行，取代此前两份文件，因此本规则库从不引用那两份文件）。
>
> **GB/T 9704-2012 本身本次未取得。** 这对一个值得直说的细节有影响：**`GW-001` 模式中的六角括号〔〕是版式标准的约定，而不是条例所规定的东西**——第九条第（五）项只要求「发文机关代字、年份、发文顺序号」。
>
> **各规则的 `excerpt` 字段仍写着“本次未取得”，每条规则也仍然是 `warn` 或 `info`。** 本插件核对的是*文本台账*所写的内容；条例规范的是*公文*本身，因此把空栏称为对“公文应当由……组成”的 `direct` 违反，会夸大这一发现。况且有一半规则本来就依据版式标准或你自己的约定。
>
> 有两个阈值是本地设定，规则库也这样写明。标题长度上限（`GW-005`，60 个字符）是**本规则库的默认值，不是标准数字**——第九条第（七）项只规定标题由发文机关、事由和文种构成，**两份文件中都没有出现任何字数**。而公文种类词表（`GW-003`）出厂为**空**，尽管第八条列出了十五种，因为该条说的是“主要有”，各单位也会使用清单之外的名称。
>
> 占位符检查有意**把「某」排除**在词表之外：模板标题常写作“关于某某工作的通知”，但“某”也会出现在正当标题中，用来代替涉密事由。

## Compatibility

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-rc.2`。**已声明 `engines.dsh`**：0.2.1 起由宿主单独裁决，范围为 `>=0.2.1-0 <0.3.0` |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/gongwen-word-check.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-gongwen-word-check
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-gongwen-word-check contributors.
