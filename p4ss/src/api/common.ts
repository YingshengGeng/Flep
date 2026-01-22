import axios from 'axios'
// import { ElMessage } from 'element-plus'
import { ContentType } from '@/utils/enum'
import { isArray, isString } from '@/utils/is'

const instance = axios.create({
  withCredentials: false,
  timeout: 10000,
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': ContentType.Json
  },
  responseType: 'json'
})

instance.interceptors.response.use(
  response => response.data,
  error => {
    // ElMessage.error('服务器异常，请稍后重试')
    return Promise.reject(error)
  }
)

export async function loadJson(): Promise<CommonNode[]> {
  const res: CommonJson = await instance.get('./front_config.json')
  const { Router_List, SOUTHBOUND_SERVER_IP, SOUTHBOUND_SERVER_PORT } = res
  return Object.entries(Router_List).map(([key, value], index) => ({
    num: index + 1,
    key,
    localLabel: value.LOCAL_LABEL,
    type: value.TYPE === 'fz' ? '封装节点' : '转发节点',
    baseUrl: `http://${SOUTHBOUND_SERVER_IP[key]}:${SOUTHBOUND_SERVER_PORT[key]}`,
    ports: Object.entries(value.PORT_LIST)
      .map(([portKey, portValue]) => ({
        key: portKey,
        index: portValue,
        rate: value.PORT_LIMIT[portKey]
      }))
      .sort((a, b) => a.index - b.index),
    status: '否',
    topologies: [] as CommonTopology[]
  }))
}

export async function loadTopology(nodes: CommonNode[]): Promise<CommonEdge[]> {
  const responses = (await Promise.allSettled(
    nodes.map(({ baseUrl }) => instance.get(`${baseUrl}/topology`))
  )) as PromiseSettledResult<CommonTopology[]>[]
  
  const edges: CommonEdge[] = []

  responses.forEach((res, index) => {
    // 检查点 1: 确认接口请求是否成功
    if (res.status === 'rejected') {
      console.error(`[DEBUG] 节点 ${nodes[index].localLabel} 接口请求失败:`, res.reason);
      return
    }

    try {
      nodes[index].status = '是'
      const source = nodes[index].localLabel
      const ports = nodes[index].ports
      
      // 检查点 2: 打印后端返回的原始拓扑数据
      console.log(`[DEBUG] 节点 ${source} 返回的原始拓扑:`, res.value);

      if (!isString(source) || !isArray(res.value)) {
        console.warn(`[DEBUG] 节点 ${source} 数据格式不正确 (isArray: ${isArray(res.value)})`);
        return
      }

      res.value.forEach(topology => {
        // 检查点 3: 检查自环过滤逻辑
        if (source === topology.label) {
          console.warn(`[DEBUG] 过滤掉自环条目: ${topology.label}`);
          return
        }

        // 检查点 4: 核心查找逻辑深度对比
        const matchedPort = ports.find(item => String(item.key) === String(topology.port));
        
        console.log(`[DEBUG] 正在匹配端口 - 拓扑中的port: "${topology.port}", 节点可用端口Key:`, 
                    ports.map(p => p.key));
        
        if (!matchedPort) {
          console.error(`[DEBUG] 匹配失败！在端口列表里找不到 key 为 "${topology.port}" 的项`);
          return;
        }

        nodes[index].topologies.push({
          ...topology,
          // 如果这里 matchedPort 为空，index 就会是 null
          index: matchedPort?.index || null
        })

        edges.push({
          source,
          target: topology.label,
          label: isString(topology.port) ? `端口 ${topology.port}` : null
        })
      })
    } catch (error) {
      console.log(`[DEBUG] 处理索引 ${index} 时出错:`, error)
    }
  })

  // 检查点 5: 最终检查节点对象是否已被填充
  console.log('[DEBUG] 所有节点处理完成，最终 nodes 状态:', nodes);
  return edges
}

export async function loadGenerate(nodes: CommonNode[]): Promise<unknown[]> {
  const responses = (await Promise.allSettled(
    nodes.map(({ baseUrl }) => instance.post(`${baseUrl}/pkt_gen/start`))
  )) as PromiseSettledResult<CommonTopology[]>[]
  return responses.map(res => (res.status === 'rejected' ? null : res.value))
}

export async function loadStop(nodes: CommonNode[]): Promise<unknown[]> {
  const responses = (await Promise.allSettled(
    nodes.map(({ baseUrl }) => instance.post(`${baseUrl}/pkt_gen/stop`))
  )) as PromiseSettledResult<CommonTopology[]>[]
  return responses.map(res => (res.status === 'rejected' ? null : res.value))
}

export function loadForwardAdd(
  baseUrl: string,
  protocol: 'ipv4' | 'ipv6',
  data: unknown
): Promise<void> {
  return instance.post(`${baseUrl}/forward/${protocol}/add`, data)
}

export function loadForwardModify(
  baseUrl: string,
  protocol: 'ipv4' | 'ipv6',
  data: unknown
): Promise<void> {
  return instance.post(`${baseUrl}/forward/${protocol}/modify`, data)
}

export function loadForwardSearch(
  baseUrl: string,
  protocol: 'ipv4' | 'ipv6',
  data: unknown
): Promise<ForwardInfo[]> {
  return instance.post(`${baseUrl}/forward/${protocol}/inquire`, data)
}

export function loadForwardDelete(
  baseUrl: string,
  protocol: 'ipv4' | 'ipv6',
  data: unknown
): Promise<void> {
  return instance.post(`${baseUrl}/forward/${protocol}/delete`, data)
}

export function loadForwardReset(baseUrl: string): Promise<void> {
  return instance.post(`${baseUrl}/forward/reset`)
}

export function loadLabelAdd(baseUrl: string, data: unknown): Promise<void> {
  return instance.post(`${baseUrl}/label/add`, data)
}

export function loadLabelModify(baseUrl: string, data: unknown): Promise<void> {
  return instance.post(`${baseUrl}/label/modify`, data)
}

export function loadLabelSearch(
  baseUrl: string,
  data: unknown
): Promise<LabelInfo[]> {
  return instance.post(`${baseUrl}/label/inquire`, data)
}

export function loadLabelDelete(baseUrl: string, data: unknown): Promise<void> {
  return instance.post(`${baseUrl}/label/delete`, data)
}

export function loadLabelReset(baseUrl: string): Promise<void> {
  return instance.post(`${baseUrl}/label/clear`)
}
