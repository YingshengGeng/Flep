/**
 * 生成列表
 * @returns 列表
 */
export function generateList(): number[] {
  return Array(10)
    .fill({})
    .map((_item, index) => index + 1)
}
