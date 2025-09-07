/**
 * @description 类型判断
 */

/** 参数类型 */
export type IsType =
  | 'null'
  | 'undefined'
  | 'string'
  | 'number'
  | 'bigint'
  | 'boolean'
  | 'symbol'
  | 'function'
  | 'generatorfunction'
  | 'asyncfunction'
  | 'array'
  | 'uint8array'
  | 'uint16array'
  | 'uint32array'
  | 'float32array'
  | 'float64array'
  | 'object'
  | 'reflect'
  | 'date'
  | 'formdata'
  | 'blob'
  | 'promise'
  | 'regexp'
  | 'set'
  | 'weakset'
  | 'map'
  | 'weakmap'
  | 'file'

/**
 * 判断传入参数是否为具体类型
 * - asyncfunction | function 取决于 babel target 设置
 * @param val 校验对象
 * @returns 参数具体类型
 */
export function isTypeOf(val: unknown): IsType {
  return Object.prototype.toString
    .call(val)
    .slice(8, -1)
    .toLowerCase() as IsType
}

/**
 * 判断传入参数是否为有效字符串
 * @param val 校验对象
 * @returns 校验结果
 */
export function isString(val: unknown): val is string {
  return typeof val === 'string' && val.trim() !== ''
}

/**
 * 判断传入参数是否为有效数字
 * @param val 校验对象
 * @returns 校验结果
 */
export function isNumber(val: unknown): val is number {
  return (
    typeof val === 'number' &&
    !isNaN(val) &&
    val !== Infinity &&
    val !== -Infinity
  )
}

/**
 * 判断传入参数是否为函数
 * @param val 校验对象
 * @returns 校验结果
 */
export function isFunction(val: unknown): val is (...rest: unknown[]) => void {
  return typeof val === 'function'
}

/**
 * 判断传入参数是否为普通对象
 * @param val 校验对象
 * @returns 校验结果
 */
export function isObject(val: unknown): boolean {
  return isTypeOf(val) === 'object'
}

/**
 * 判断传入参数是否为存在数据的普通数组
 * @param val 校验对象
 * @returns 校验结果
 */
export function isArray(val: unknown): boolean {
  return isTypeOf(val) === 'array' && (val as unknown[]).length > 0
}

/**
 * 判断传入参数是否为日期对象
 * @param val 校验对象
 * @returns 校验结果
 */
export function isDate(val: unknown): val is Date {
  return isTypeOf(val) === 'date'
}

/**
 * 判断传入参数是否为正则表达式
 * @param val 校验对象
 * @returns 校验结果
 */
export function isRegExp(val: unknown): val is RegExp {
  return isTypeOf(val) === 'regexp'
}

/**
 * 判断传入参数是否为 Form 对象
 * @param val 校验对象
 * @returns 校验结果
 */
export function isFormData(val: unknown): val is FormData {
  return isTypeOf(val) === 'formdata'
}

/**
 * 判断传入参数是否为 Blob 对象
 * @param val 校验对象
 * @returns 校验结果
 */
export function isBlob(val: unknown): val is Blob {
  return isTypeOf(val) === 'blob'
}

/**
 * 判断传入参数是否为 Promise 对象
 * @param val 校验对象
 * @returns 校验结果
 */
export function isPromise(val: unknown): val is Promise<unknown> {
  return isTypeOf(val) === 'promise'
}

/**
 * 判断传入参数是否为文件对象
 * @param val 校验对象
 * @returns 校验结果
 */
export function isFile(val: unknown): val is File {
  return isTypeOf(val) === 'file'
}
