/**
 * @description 枚举
 */

/** 编码类型 content-type */
export enum ContentType {
  /** json 请求 */
  Json = 'application/json;charset=UTF-8',
  /**  */
  UrlEncoded = 'application/x-www-form-urlencoded;charset:UTF-8',
  /** form 表单请求 */
  Form = 'multipart/form-data'
}

/** 内容类型枚举 mimetype */
export enum MimeType {
  /** 图片：jpg、jpeg、jpe */
  Jpg = 'image/jpeg',
  /** 图片：png */
  Png = 'image/png',
  /** 图片：gif */
  Gif = 'image/gif',
  /** 图片：bmp */
  Bmp = 'image/bmp',
  /** 视频：mp4 */
  Mp4 = 'video/mp4',
  /** 视频：mov */
  Mov = 'video/quicktime',
  /** 文件：pdf */
  Pdf = 'application/pdf',
  /** 文件：doc、dot */
  Doc = 'application/msword',
  /** 文件：docx */
  Docx = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  /** 文件：xls */
  Xls = 'application/vnd.ms-excel',
  /** 文件：xlsx */
  Xlsx = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  /** 文件：xlsm */
  Xlsm = 'application/vnd.ms-excel.addin.macroEnabled.12',
  /** 文件：xlsb */
  Xlsb = 'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
  /** 文件：ppt、pot、pps、ppa */
  Ppt = 'application/vnd.ms-powerpoint',
  /** 文件：pptx */
  Pptx = 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  /** 文件：txt */
  Txt = 'text/plain',
  /** 压缩包：rar */
  Rar = 'application/x-rar-compressed',
  /** 压缩包：zip */
  Zip = 'application/zip'
}
