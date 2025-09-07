interface CommonJson {
  /** 接口地址拼接：ip */
  SOUTHBOUND_SERVER_IP: { [key: string]: string }
  /** 接口地址拼接：port */
  SOUTHBOUND_SERVER_PORT: { [key: string]: string }
  /** 网络节点信息：key-关联 index */
  Router_List: {
    [key: string]: {
      /** 节点 id */
      LOCAL_LABEL: string
      /** 节点类型：fz-封装、zf-转发 */
      TYPE: 'fz' | 'zf'
      /** 节点编号映射 */
      PORT_LIST: { [key: string]: number }
      /** 节点编号速率 */
      PORT_LIMIT: { [key: string]: string }
    }
  }
}

interface CommonTopology {
  /** 当前节点端口 */
  port: string
  /** 目标节点 id（标签） */
  label: string
  /** 延迟 */
  latency: string
  /** 当前节点端口对应 PORT_LIST 映射 */
  index: number
}

interface CommonNode {
  /** 节点序号 */
  num: number
  /** 节点 key */
  key: string
  /** 节点 id（标签） */
  localLabel: string
  /** 节点类型 */
  type: '封装节点' | '转发节点'
  /** 节点接口 baseURL */
  baseUrl: string
  /** 节点端口信息 */
  ports: { key: string; index: number; rate: string }[]
  /** 节点是否在线 */
  status: '是' | '否'
  /** 节点邻接拓扑 */
  topologies: CommonTopology[]
}

interface CommonEdge {
  /** 源节点 id（标签） */
  source: string
  /** 目标节点 id（标签） */
  target: string
  /** 连线文本 */
  label: string
}

interface CommonOperation {
  /** 操作内容 */
  content: string
  /** 查询结果（封装节点） */
  forwards: ForwardInfo[]
  /** 查询结果（转发节点） */
  labels: LabelInfo[]
}

interface ForwardInfo {
  /** 网络层协议 */
  ip: 'ipv4' | 'ipv6'
  /** 传输层协议 */
  tp: 'tcp' | 'udp'
  /** ipv4 源地址 */
  ipv4_src: string
  /** ipv4 目的地址 */
  ipv4_dst: string
  /** ipv6 源地址 */
  ipv6_src: string
  /** ipv6 目的地址 */
  ipv6_dst: string
  /** 源端口 */
  tp_src: string
  /** 目的端口 */
  tp_dst: string
  /** 标签 */
  label_list: string[]
}

interface LabelInfo {
  /** 匹配标签 */
  label: string
  /** 出端口 */
  port: string | number
}
