# dsh-gongwen-word-check — Verificação dos elementos de formato do registo de documentos oficiais

`dsh-gongwen-word-check` lê um registo de documentos oficiais —uma linha por documento emitido— e confronta o texto que esse registo anota com um pacote de regras versionado: se `发文字号` segue a forma 「机关代字〔年份〕序号」 com o ano entre parênteses hexagonais 〔〕, se `成文日期` é analisável como data e não é posterior ao dia da verificação, se `文种` vem do vocabulário que a sua própria unidade configura, se `主送机关` está preenchido, se `标题` se mantém dentro do comprimento configurado, se um `发文字号` se repete no registo e se um título conserva algum marcador de modelo por substituir.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| O número do documento foi escrito `某政发[2026]15号`, com parênteses retos. | `GW-001` assinala essa linha: o padrão com que foi configurada exige parênteses hexagonais 〔〕 em torno do ano, portanto a forma a escrever é `某政发〔2026〕15号`. A regra verifica apenas a forma do número — a sigla 机关代字 é fixada pela sua unidade, pelo que não julga se a sigla é a correta nem se os números de ordem são consecutivos ou repetidos. |
| A data de assinatura está escrita como o documento costuma trazê-la: 二〇二六年三月十五日. | `GW-002` informa que não consegue analisar esse valor. Reconhece `2026-03-15` e `2026-03-15 09:30`; uma data em caracteres chineses tem de ser escrita numa dessas duas formas, ou a regra ser desativada. A regra também não confronta a data de assinatura com a data de expedição: isso é interno ao fluxo de emissão. |
| Nunca configurámos a lista de 文种 da nossa unidade. O `GW-003` passa em silêncio? | Não. O `GW-003` não traz qualquer lista incorporada, pelo que com `values` por definir aparece na secção `skipped` do relatório em vez de passar em silêncio. 《党政机关公文处理工作条例》 enumera quinze tipos principais, mas o pacote não os fixa no código: que tipos a sua unidade pode usar é uma decisão sua. A regra também não julga que tipo um determinado documento deveria ter usado. |
| Uma linha deixa 主送机关 em branco. | `GW-004` assinala essa linha, porque sem destinatário principal não há como confirmar a quem foi enviado o documento. Verifica que a coluna está preenchida, não que o âmbito dos destinatários seja o adequado: a quem se dirige e a quem se envia cópia é uma decisão de redação. |
| O nosso título é comprido. De onde vem o limite de comprimento? | `GW-005` assinala um `标题` acima do limite configurado de 60 caracteres. Esse valor é a predefinição deste pacote de regras, não um número da norma: a GB/T 9704-2012 fixa para o título 「2 号小标宋体字」 e não indica qualquer limite de caracteres, pelo que, se a sua unidade redige títulos mais longos, aumente `maxLength` ou desative a regra. A regra conta apenas caracteres: não julga a redação do título. |
| Duas linhas trazem o mesmo 发文字号. | `GW-006` assinala o número repetido; compara os valores ignorando espaços e uma ocorrência costuma significar um número reutilizado ou mal copiado que uma pessoa tem de confirmar. Não decide qual dos dois documentos deve usar esse número. |

## Normas que segue

| Documento | Número | Regras que o citam |
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

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-gongwen-word-check
dsh --profile <name> --dump-config | grep 'dsh-gongwen-word-check'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/gongwen-word-check.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-gongwen-word-check
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-gongwen-word-check contributors.
