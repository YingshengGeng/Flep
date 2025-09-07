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
    if (res.status === 'rejected') {
      return
    }
    try {
      nodes[index].status = '是'
      const source = nodes[index].localLabel
      const ports = nodes[index].ports
      if (!isString(source) || !isArray(res.value)) {
        return
      }
      res.value.forEach(topology => {
        if (!isString(topology.label) || source === topology.label) {
          return
        }
        nodes[index].topologies.push({
          ...topology,
          index: ports.find(item => item.key === topology.port)?.index || null
        })
        edges.push({
          source,
          target: topology.label,
          label: isString(topology.port) ? `端口 ${topology.port}` : null
        })
      })
    } catch (error) {
      console.log(index, error)
    }
  })

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
