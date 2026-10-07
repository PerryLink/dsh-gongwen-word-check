/**
 * dsh-gongwen-word-check — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'gongwen_word_check'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  docNo: ['发文字号', '文号', '文件编号', 'docNo'],
  title: ['标题', '公文标题', '文件标题', 'title'],
  docKind: ['文种', '公文种类', '文件种类', 'docKind'],
  issuer: ['发文机关', '制发机关', '发文单位', 'issuer'],
  signedAt: ['成文日期', '签发日期', '发文日期', 'signedAt'],
  recipient: ['主送机关', '主送单位', '受文机关', 'recipient'],
  cc: ['抄送机关', '抄送单位', 'cc'],
  drafter: ['拟稿人', '起草人', '承办人', 'drafter'],
  securityLevel: ['密级', '秘密等级', 'securityLevel'],
  urgent: ['紧急程度', '缓急程度', 'urgent'],
  note: ['备注', '说明', 'note', 'remark'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'documents', 'items', '文书'],
  columns: COLUMNS,
  header: {
  issuer: ['issuer', '发文机关', '制发机关'],
  year: ['year', '年度'],
  checkedAt: ['checkedAt', '核对日期'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '发文字号',
  'docNo',
  '标题',
  'title',
  '文种',
  'docKind',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
