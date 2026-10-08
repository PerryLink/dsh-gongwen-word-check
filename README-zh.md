# dsh-gongwen-word-check — 公文台账版头与主体要素核对

`dsh-gongwen-word-check` 读取一份公文台账——每份已发出公文一行——按版本化的规则库核对这份台账登记的文字：`发文字号` 是否符合「机关代字〔年份〕序号」的形式、年份是否用六角括号〔〕括入，`成文日期` 是否可解析且不晚于核对日，`文种` 是否落在本机关自己配置的取值清单内，`主送机关` 是否填写，`标题` 是否在配置的长度上限内，`发文字号` 是否在台账内重复，以及标题里是否残留未替换的模板占位符。

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

**Boundary:** this plugin checks a **公文台账的版头与主体要素** for what a register can be held to
mechanically — that the document number follows its 「机关代字〔年份〕序号」 shape, that the signing date
parses, that the document kind comes from your vocabulary, that a main recipient is recorded, that the
title is not over-long, that numbers do not repeat, and that no template placeholder survives. It checks
**the text a register records, not the layout** — typeface, size, margins and seal placement can only be
judged from the document itself.

> ### ⚠️ What the citations in this plugin's report actually rest on
>
> **《党政机关公文处理工作条例》(中办发〔2012〕14号) was obtained and read verbatim**, and
> `rules/evidence/clause-verification.md` records which articles were quoted — article 8 (the fifteen document
> kinds), article 9 (the format elements, including 「发文字号。由发文机关代字、年份、发文顺序号组成」 and
> 「主送机关。公文的主要受理机关」), article 10 (which delegates layout to GB/T 9704-2012) and article 42
> (in force from 2012-07-01, superseding two earlier documents this pack therefore never cites).
>
> **GB/T 9704-2012 itself was not obtained.** That matters for one detail worth stating plainly: **the
> 六角括号〔〕 in `GW-001`'s pattern is the layout standard's convention, not something the regulation
> fixes** — article 9(5) requires only 「发文机关代字、年份、发文顺序号」.
>
> **The rule `excerpt` fields still say "本次未取得", and every rule remains `warn` or `info`.** What this
> plugin checks is what a *register of text* says; the regulation governs the *document*, so calling a blank
> column a `direct` breach of "a document shall consist of …" would overstate the finding. Half the rules rest
> on the layout standard or on your own convention in any case.
>
> Two thresholds are local, and the pack says so. The title-length ceiling (`GW-005`, 60 characters) is
> **this rule pack's default, not a standard figure** — article 9(7) fixes only that the title consists of the
> issuing body, the subject and the kind, and **no character count appears in either document**. And the
> document-kind vocabulary (`GW-003`) ships **empty** despite article 8 listing fifteen kinds, because the
> article says "主要有" and units also use names outside the list.
>
> The placeholder check deliberately **omits 「某」** from its term list: template titles often read
> "关于某某工作的通知", but 某 also appears in legitimate titles as a stand-in for a confidential subject.

## Compatibility

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-alpha.1`。**刻意不声明 `engines.dsh`**：它没有任何读取者，也无法拒装任何宿主 |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` / `both` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Install

```sh
dsh plugin --profile <name> add dsh-gongwen-word-check
dsh --profile <name> --dump-config | grep 'dsh-gongwen-word-check'
```

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
