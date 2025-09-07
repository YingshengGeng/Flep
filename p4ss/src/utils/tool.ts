/**
 * @description 工具
 */
import { ElMessage } from 'element-plus'
import { MimeType } from './enum'
import {
  isArray,
  isBlob,
  isDate,
  isFile,
  isFunction,
  isNumber,
  isObject,
  isRegExp,
  isString
} from './is'

/**
 * 防抖
 * @param fn 目标函数
 * @param delay 延迟时间
 * @returns 包装函数
 */
export function toolDebounce(
  fn: unknown,
  delay?: number
): (...rest: unknown[]) => void {
  !isNumber(delay) && (delay = 200)
  let timer: number = null
  return function (...rest: unknown[]) {
    if (timer) {
      clearTimeout(timer)
    }
    timer = setTimeout(() => {
      isFunction(fn) && Reflect.apply(fn, fn, rest)
    }, delay)
  }
}

/**
 * 节流
 * @param fn 目标函数
 * @param delay 间隔时间
 * @returns 包装函数
 */
export function toolThrottle(
  fn: unknown,
  delay?: number
): (...rest: unknown[]) => void {
  !isNumber(delay) && (delay = 200)
  let lastTime = new Date().getTime()
  return function (...rest: unknown[]) {
    const nowTime = new Date().getTime()
    if (nowTime - lastTime >= delay) {
      isFunction(fn) && Reflect.apply(fn, fn, rest)
      lastTime = nowTime
    }
  }
}

/**
 * 生成 uuid
 * @returns uuid 字符串
 */
export function toolGenerateUuid(): string {
  let uuid = ''
  for (let i = 1; i <= 32; i++) {
    const num = Math.floor(Math.random() * 16.0).toString(16)
    uuid += num
    if (i === 8 || i === 12 || i === 16 || i === 20) {
      uuid += '-'
    }
  }
  return uuid
}

/**
 * 生成 dataId
 * @returns dataId 字符串
 */
export function toolGenerateDataId(): string {
  let dataId = ''
  for (let i = 1; i <= 16; i++) {
    const num = Math.floor(Math.random() * 16.0).toString(16)
    dataId += num
  }
  return dataId
}

/**
 * 异步休眠
 * @param time 休眠时长
 * @returns 休眠 promise
 */
export function toolSleep(time?: number): Promise<void> {
  if (!isNumber(time) || time < 1000) {
    time = 1000
  }
  return new Promise(resolve => setTimeout(resolve, time))
}

/**
 * 深拷贝
 * @param source 原始对象
 * @returns 深拷贝对象
 */
export function toolDeepCopy<T>(source: T): T {
  /**
   * 1.基本类型：直接返回
   * 2.日期：构建新的日期对象返回
   * 3.正则表达式：构建新的正则对象返回
   * 4.数组：递归遍历数组元素深拷贝
   * 5.对象：递归遍历对象属性深拷贝
   */
  if (source == null || typeof source !== 'object') {
    return source
  }
  if (isDate(source)) {
    /* eslint-disable-next-line */
    // @ts-ignore
    return new Date(source) as T
  }
  if (isRegExp(source)) {
    /* eslint-disable-next-line */
    // @ts-ignore
    return new RegExp(source) as T
  }
  if (Array.isArray(source)) {
    const copy: unknown[] = []
    source.forEach(item => copy.push(toolDeepCopy(item)))
    /* eslint-disable-next-line */
    // @ts-ignore
    return copy as T
  }
  if (isObject(source)) {
    const copy = {} as { [key: string]: unknown }
    for (const [key, value] of Object.entries(source)) {
      copy[key] = toolDeepCopy(value)
    }
    /* eslint-disable-next-line */
    // @ts-ignore
    return copy as T
  }
  return source
}

/**
 * 按换行符拆分字符串为数组
 * @param value 字符串
 * @returns 字符串数组
 */
export function toolStringToArray(value: unknown): string[] {
  const set = new Set<string>()
  if (isString(value)) {
    value.split(/[\r\n]+/g).forEach(item => {
      const newItem = item.replace(/^\s+|\s+$/g, '')
      isString(newItem) && set.add(newItem)
    })
  }
  return Array.from(set)
}

/**
 * 过滤对象
 * @param source 原始对象
 * @param ignoreKeys 忽略提取 key
 * @returns 过滤后对象
 */
export function toolFilterObject<T = unknown>(
  source: T,
  ignoreKeys?: string[]
): T {
  !isObject(source) && (source = {} as T)
  !isArray(ignoreKeys) && (ignoreKeys = [])
  const target = {}
  for (const [key, value] of Object.entries(source)) {
    if (
      key.startsWith('ui_') ||
      ignoreKeys.includes(key) ||
      value == null ||
      value === ''
    ) {
      continue
    }
    Reflect.set(target, key, value)
  }
  return target as T
}

/**
 * 转换 FormData
 * @param data 原始对象
 * @returns 表单对象
 */
export function toolTransformForm(data: unknown): FormData {
  const form = new FormData()
  if (!isObject(data)) {
    return form
  }
  for (const [key, value] of Object.entries(data)) {
    if (Array.isArray(value)) {
      // 数组：form-data 额外追加 key-value
      value.forEach(item => form.append(key, toolTransformFile(item)))
    } else {
      // 其他：直接设置 key-value
      form.append(key, toolTransformFile(value))
    }
  }
  return form
}

/**
 * 转换 File
 * @param data 原始对象
 * @returns 文件对象
 */
export function toolTransformFile(data: File): File {
  if (!isFile(data)) {
    return data
  }
  // 转换原始文件对象：utf-8 编码文件名解决后端乱码问题
  return new File([data], encodeURIComponent(data.name), { type: data.type })
}

/**
 * 导入文件
 * @param exts 文件扩展名
 * @param size 文件最大尺寸：0-不限制、其他-单位 b（1M = 1024kb = 1024 * 1024b）
 * @returns 文件对象
 */
export function toolImportFile(exts: string[], size?: number): Promise<File> {
  !isArray(exts) && (exts = ['xls', 'xlsx', 'xlsm', 'xlsb'])
  ;(!isNumber(size) || size < 0) && (size = 0)
  return new Promise((resolve, reject) => {
    // 1.创建 input 元素
    const input = document.createElement('input')
    input.type = 'file'
    input.multiple = false
    // 2.设置默认勾选文件类型
    let accept = ''
    exts.forEach(ext => {
      ext = `${ext.charAt(0).toUpperCase()}${ext.slice(1)}`
      const mimetype = MimeType[ext as keyof typeof MimeType]
      if (!mimetype) {
        return
      }
      accept = isString(accept) ? `${accept}, ${mimetype}` : `${mimetype}`
    })
    input.accept = accept
    // 3.取消选择文件
    /* eslint-disable-next-line */
    // @ts-ignore
    input.oncancel = () => reject()
    // 4.确认选择文件
    input.onchange = e => {
      // 4-1.获取提交文件对象
      const file = (e.target as HTMLInputElement).files[0]
      if (!file) {
        reject()
        return
      }
      // 4-2.获取提交文件扩展名
      const fileNames = file.name.split('.')
      let extension = fileNames[fileNames.length - 1]
      extension = isString(extension) ? extension.toLowerCase() : null
      // 4-3.文件扩展名校验
      if (!exts.includes(extension)) {
        ElMessage.warning('导入文件类型不符合要求')
        reject()
        return
      }
      // 4-4.文件大小校验
      if (size > 0 && file.size > size) {
        ElMessage.warning(
          `导入文件大小超过 ${(size / 1024 / 1024).toFixed(0)} M`
        )
        return
      }
      resolve(file)
    }
    // 5.触发选择文件
    input.click()
  })
}

/**
 * 导出文件
 * @param blob 二进制数据
 * @param name 文件名
 * @returns 无
 */
export function toolDownloadFile(blob: unknown, name: string): void {
  if (!isBlob(blob) || !isString(name)) {
    ElMessage.error('导出数据失败，请稍后再试')
    return
  }
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `${name}`
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(a.href)
}

/**
 * 字符串 base64 编码
 * @param data 原始字符串
 * @returns 编码字符串
 */
export function toolEncodeBase64(data: string): string {
  try {
    if (!isString(data)) {
      throw new Error()
    }
    const encodeString = window.encodeURIComponent(data)
    const encodeData = window.btoa(encodeString)
    return encodeData
    /* eslint-disable-next-line */
  } catch (error) {
    return data
  }
}

/**
 * 字符串 base64 解码
 * @param data 编码字符串
 * @returns 原始字符串
 */
export function toolDecodeBase64(data: string): string {
  try {
    if (!isString(data)) {
      throw new Error()
    }
    const decodeData = window.atob(data)
    const decodeString = window.decodeURIComponent(decodeData)
    return decodeString
    /* eslint-disable-next-line */
  } catch (error) {
    return data
  }
}

/**
 * 格式化文件大小单位
 * @param size 文件大小（单位 b）
 * @returns 格式后带单位文件大小
 */
export function toolFormatFileSize(size: number): string {
  const units = ['b', 'kb', 'mb', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(2)} ${units[unitIndex]}`
}

/**
 * 转换文件大小单位
 * @param size 文件大小
 * @param fromUnit 初始单位
 * @param toUnit 目标单位
 * @param decimalPoint 结果保留的小数位数（默认 2）
 * @return 转换后带单位文件大小
 */
export function toolConvertFileSize(
  size: number,
  fromUnit: string,
  toUnit: string,
  decimalPoint?: number
): string {
  !isNumber(decimalPoint) && (decimalPoint = 2)
  // 定义单位与字节之间的转换关系
  const units = ['b', 'kb', 'mb', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
  // 获取初始单位和目标单位的索引
  const fromIndex = units.indexOf(fromUnit)
  const toIndex = units.indexOf(toUnit)
  // 若 指定单位不在转换关系中 则 直接返回
  if (fromIndex === -1 || toIndex === -1) {
    return null
  }
  // 计算初始单位与目标单位之间的转换系数
  const exponent = toIndex - fromIndex
  // 计算结果大小
  const resultSize = size / Math.pow(1024, exponent)
  // 返回格式化后的结果
  return `${resultSize.toFixed(decimalPoint)} ${toUnit}`
}

/**
 * url 参数解析
 * @returns 解析对象
 */
export function toolParseUrl(): { [key: string]: unknown } {
  try {
    const result: { [key: string]: unknown } = {}
    window.location.href.replace(
      /[?&]{1}([^?&=]+)=([^&#]+)/g,
      (_match, key, value) => (result[key] = decodeURIComponent(value))
    )
    return result
    /* eslint-disable-next-line */
  } catch (error) {
    return {}
  }
}
