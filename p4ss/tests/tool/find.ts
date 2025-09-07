/**
 * 获取指定测试 id 标识
 * @param id 测试 id
 * @returns 测试 id 标识
 */
export function testid(id: string): string {
  return `[data-testid="${id}"]`
}
