# dsh-gongwen-word-check

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

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for a year's register use `ptc` |

## What it does

Registers the `gongwen_word_check` tool. It reads one document register — one row per issued document — applies
a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `GW-001` | the document number follows 「代字〔年份〕序号」 | warn | principle |
| `GW-002` | the signing date parses and is not in the future | warn | principle |
| `GW-003` | the document kind comes from your vocabulary (off by default) | info | local |
| `GW-004` | a main recipient is recorded | warn | principle |
| `GW-005` | the title is not over the configured length | warn | principle |
| `GW-006` | document numbers are unique in the register | warn | principle |
| `GW-007` | the title holds no unreplaced placeholder | warn | principle |

## Install

```sh
pnpm pack
dsh plugin --profile <name> add ./dsh-gongwen-word-check-0.1.0.tgz
dsh --profile <name> --dump-config | grep 'dsh-gongwen-word-check'
```

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/gongwen-word-check.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `GW-001` `pattern` — the document-number shape. Widen it for joint issuances or minutes that carry no
  number, or disable the rule.
- `GW-003` `values` — your document kinds, e.g.
  `[决议, 决定, 命令, 公报, 公告, 通告, 意见, 通知, 通报, 报告, 请示, 批复, 议案, 函, 纪要]`.
- `GW-005` `maxLength` / `minLength` — **your** title-length bounds. The default ceiling of 60 is a local
  convention, not a standard figure.
- `GW-007` `terms` — the placeholders to look for; 「某」 is deliberately absent.

## Material format

The tool accepts JSON or YAML:

```yaml
issuer: 某某机关
year: 2026
rows:
  - { 发文字号: 某政发〔2026〕15号, 标题: 某某机关关于印发某某管理办法的通知, 文种: 通知,
      发文机关: 某某机关, 成文日期: 2026-03-10, 主送机关: 各直属单位,
      抄送机关: 某某办公室, 密级: 公开, 紧急程度: 平件 }
```

Column names are matched case-insensitively and ignoring spaces, underscores and hyphens; the register's own
column names are kept, so a finding names the column it read. Dates may be `2026-03-10` or
`2026-03-10 09:30` — a Chinese-numeral date is reported as unparseable on purpose.

## Rule sources

Rule data lives in `rules/gongwen-word-check.yaml`. The pack's header states the citation gap in full, and
each rule's `note` repeats the part that matters for that rule. The load-time guard that normally enforces
"an excerpt must be a real quotation of at least eight characters" cannot tell a quotation from a
description — so this pack leans on the header, the per-rule notes and a test that asserts every `excerpt`
admits the gap.

## Troubleshooting

- **`GW-001` fires on a number I consider correct.** The pattern requires the year in **六角括号〔〕**; a
  number written with `[]`, `（）` or a hyphen fails. Adjust `pattern` for your house style.
- **`GW-002` fires on a Chinese-numeral date.** The reader accepts `2026-03-10`; `二〇二六年三月十日` is
  reported as unparseable on purpose so you can decide whether to normalise the export.
- **`GW-003` never runs.** Its vocabulary is empty. Which document names count as kinds is your
  institution's call, and the plugin will not guess.
- **`GW-005` fires on a title that fits on the page.** The ceiling is 60 characters by default and is a
  local convention. Raise it, or disable the rule.
- **`GW-007` does not fire on a title containing 某.** That is deliberate; add the character to `terms` if
  your templates really use it as a placeholder.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`; if
  your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-gongwen-word-check@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, the shared table-plugin suite plus paired fixtures
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-gongwen-word-check   # refresh src/shared from ../_shared
```

The plugin is **data-only**: `src/model.ts` declares the table shape, the shared kit supplies the reader and
the check engine, and the rule pack declares every check.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-gongwen-word-check contributors.
