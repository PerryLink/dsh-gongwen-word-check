import { describeTablePlugin } from './table-plugin-suite.ts'
import { Config } from '../src/config.ts'
import { parseMaterial, runCheck, SPEC } from '../src/model.ts'
import { buildView } from '../src/view.ts'
import { inject, name, resolvePackageFile, TOOL_NAME } from '../src/index.ts'

describeTablePlugin({
  name,
  inject,
  TOOL_NAME,
  resolvePackageFile,
  Config,
  rulesFile: 'rules/gongwen-word-check.yaml',
  parseMaterial,
  runCheck,
  buildView,
  columnNames: SPEC.columns,
  samples: {
    good: {
      issuer: '某某机关',
      year: 2026,
      rows: [
        {
          发文字号: '某政发〔2026〕15号',
          标题: '某某机关关于印发某某管理办法的通知',
          文种: '通知',
          发文机关: '某某机关',
          成文日期: '2026-03-10',
          主送机关: '各直属单位',
          密级: '公开',
          紧急程度: '平件',
        },
      ],
    },
    unknownColumn: { rows: [{ 备注: '甲' }] },
  },
})
