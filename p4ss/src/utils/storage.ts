/**
 * @description web 存储
 */
import { isArray, isString } from './is'

/** web 存储对象 */
class StorageModel {
  /** 时间戳 */
  public readonly timestamp: number = Date.now()
  /** 数据 */
  public data: unknown = null

  constructor(data: unknown) {
    this.data = data
  }
}

/**
 * 获取 web 存储完整 key
 * @param key 数据 key
 * @returns 完整 key
 */
const getFullKey = (key: string) => `${import.meta.env.VITE_STORAGE}_${key}`

/**
 * 增、改 storage 指定 key
 * @param key 数据 key
 * @param value 数据
 * @returns 无
 */
export function storageSet(key: string, value: unknown): void {
  const data = JSON.stringify(new StorageModel(value))
  window.localStorage.setItem(getFullKey(key), data)
}

/**
 * 查 storage 指定 key
 * @param key 数据 key
 * @returns 查询结果
 */
export function storageGet<T = unknown>(key: string): T {
  try {
    const data = window.localStorage.getItem(getFullKey(key))
    const parseData = JSON.parse(data)
    return parseData.data
    /* eslint-disable-next-line */
  } catch (error) {
    return null
  }
}

/**
 * 删 storage 指定 key
 * @param key 数据 key
 * @returns 无
 */
export function storageRemove(key: string): void {
  window.localStorage.removeItem(getFullKey(key))
}

/**
 * 删 storage 所有 key
 * @param ignoreKeys 忽略删除的数据 key
 * @returns 无
 */
export function storageRemoveAll(ignoreKeys?: string[]): void {
  isArray(ignoreKeys)
    ? (ignoreKeys = ignoreKeys.map(key => getFullKey(key)))
    : (ignoreKeys = [])
  Object.keys(window.localStorage).forEach(key => {
    if (
      !isString(import.meta.env.VITE_STORAGE) ||
      (key.startsWith(import.meta.env.VITE_STORAGE) &&
        !ignoreKeys.includes(key))
    ) {
      window.localStorage.removeItem(key)
    }
  })
}
