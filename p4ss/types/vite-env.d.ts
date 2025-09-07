/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** 页面标题 */
  VITE_TITLE: string
  /** 浏览器存储命名空间 */
  VITE_STORAGE: string
  /** 配置变量 */
  VITE_ENV: 'development' | 'production'
  /** 业务接口 */
  VITE_BASE_API: string
  /** 静态资源路径 */
  VITE_PUBLIC_PATH: string
  /** 最后编译时间 */
  VITE_BUILDTIME: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

declare interface Window {}
