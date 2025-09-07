/**
 * @description cz-customizable 配置文件
 * @extends https://github.com/leoforfree/cz-customizable
 */

module.exports = {
  types: [
    { value: 'feat', name: 'feat:         一项新功能' },
    { value: 'fix', name: 'fix:          一个 Bug 修复' },
    { value: 'test', name: 'test:         单元、集成测试变更' },
    { value: 'refactor', name: 'refactor:     已有功能重构' },
    { value: 'style', name: 'style:        代码风格变更（格式、分号等）' },
    { value: 'build', name: 'build:        webpack、rollup 变更' },
    { value: 'chore', name: 'chore:        构建过程、辅助工具变更' },
    { value: 'ci', name: 'ci:           持续集成变更' },
    { value: 'perf', name: 'perf:         性能、体验提升' },
    { value: 'revert', name: 'revert:       回滚先前提交' },
    { value: 'docs', name: 'docs:         文档变更' }
  ],
  scopes: [{ name: 'src' }, { name: 'all' }],
  messages: {
    type: '请选择一种提交类型:',
    scope: '请选择一个修改范围(可选):',
    subject: '短提交说明:\n',
    body: '长提交说明, 使用 "|" 换行(可选):\n',
    breaking: '非兼容性说明(可选):\n',
    footer: '关闭关联 issue, 例如: #31, #34 (可选):\n',
    confirmCommit: '确定提交本次 git message?'
  },
  allowBreakingChanges: ['feat', 'fix'],
  allowCustomScopes: false,
  skipQuestions: ['body', 'footer'],
  subjectLimit: 80
}
