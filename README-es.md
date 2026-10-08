# dsh-gongwen-word-check — Verificación de los elementos de formato del registro de documentos oficiales

`dsh-gongwen-word-check` lee un registro de documentos oficiales —una fila por documento emitido— y contrasta el texto que ese registro anota con un paquete de reglas versionado: si `发文字号` respeta la forma 「机关代字〔年份〕序号」 con el año entre corchetes hexagonales 〔〕, si `成文日期` se puede analizar como fecha y no es posterior al día de la comprobación, si `文种` procede del vocabulario que configura su propia unidad, si `主送机关` está rellenado, si `标题` se mantiene dentro de la longitud configurada, si un `发文字号` se repite en el registro y si un título conserva algún marcador de plantilla sin sustituir.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| El número de documento se escribió `某政发[2026]15号`, con corchetes cuadrados. | `GW-001` señala esa fila: el patrón con el que se configuró exige corchetes hexagonales 〔〕 alrededor del año, de modo que la forma que corresponde escribir es `某政发〔2026〕15号`. La regla solo comprueba la forma del número — la sigla 机关代字 la fija su unidad, así que no juzga si la sigla es la correcta ni si los números de orden son consecutivos o se repiten. |
| La fecha de firma está escrita como suele llevarla el documento: 二〇二六年三月十五日. | `GW-002` informa de que no puede analizar ese valor. Reconoce `2026-03-15` y `2026-03-15 09:30`; una fecha en caracteres chinos debe escribirse de una de esas dos maneras, o bien desactivar la regla. La regla tampoco contrasta la fecha de firma con la fecha de expedición: eso es interno al flujo de emisión. |
| Nunca configuramos la lista de 文种 de nuestra unidad. ¿`GW-003` pasa en silencio? | No. `GW-003` no lleva ninguna lista incorporada, así que con `values` sin definir aparece en el apartado `skipped` del informe en lugar de pasar en silencio. 《党政机关公文处理工作条例》 enumera quince clases principales, pero el paquete no las fija en el código: qué clases puede usar su unidad es decisión suya. La regla tampoco juzga qué clase debería haber empleado un documento concreto. |
| Una fila deja 主送机关 en blanco. | `GW-004` señala esa fila, porque sin destinatario principal no hay con qué confirmar a quién se envió el documento. Comprueba que la columna esté rellenada, no que el alcance de los destinatarios sea el adecuado: a quién se dirige y a quién se copia es una decisión de redacción. |
| Nuestro título es largo. ¿De dónde sale el límite de longitud? | `GW-005` señala un `标题` que supera el límite configurado de 60 caracteres. Esa cifra es el valor por defecto de este paquete de reglas, no un número de la norma: GB/T 9704-2012 fija para el título 「2 号小标宋体字」 y no da ningún límite de caracteres, así que si su unidad redacta títulos más largos, aumente `maxLength` o desactive la regla. La regla solo cuenta caracteres: no juzga la redacción del título. |
| Dos filas llevan el mismo 发文字号. | `GW-006` señala el número repetido; compara los valores ignorando los espacios y un acierto suele significar un número reutilizado o mal copiado que una persona debe confirmar. No decide cuál de los dos documentos debería llevar ese número. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-gongwen-word-check
dsh --profile <name> --dump-config | grep 'dsh-gongwen-word-check'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/gongwen-word-check.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-gongwen-word-check
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-gongwen-word-check contributors.
