/**
 * @description dayjs 辅助函数
 */
import dayjs from 'dayjs'
import { isString } from './is'

/**
 * 日期转 Date 对象
 * @param value 日期
 * @returns Date 对象
 */
export function dateToDate(value: string | number | Date | dayjs.Dayjs): Date {
  const instance = dayjs(value)
  return instance.isValid() ? instance.toDate() : null
}

/**
 * 日期转 day.js 对象
 * @param value 日期
 * @returns day.js 对象
 */
export function dateToDayjs(
  value: string | number | Date | dayjs.Dayjs
): dayjs.Dayjs {
  const instance = dayjs(value)
  return instance.isValid() ? instance : null
}

/**
 * 日期转 ISO-8601 规范日期字符串
 * @param value 日期
 * @returns ISO-8601 规范日期字符串
 */
export function dateToISO8601(
  value: string | number | Date | dayjs.Dayjs
): string {
  const instance = dayjs(value)
  return instance.isValid() ? instance.format() : null
}

/**
 * 日期转日期字符串
 * @param value 日期
 * @param template 格式化模板（默认 YYYY-MM-DD HH:mm:ss）
 * @returns 日期字符串
 */
export function dateToString(
  value: string | number | Date | dayjs.Dayjs,
  template?: string
): string {
  const instance = dayjs(value)
  if (!instance.isValid()) {
    return null
  }
  !isString(template) && (template = 'YYYY-MM-DD HH:mm:ss')
  return instance.format(template)
}
