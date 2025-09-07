<template>
  <div class="flex h-full flex-nowrap items-stretch overflow-hidden">
    <!-- 1.左侧拓扑图 -->
    <section class="relative flex-auto">
      <!-- 控制按钮 -->
      <button
        class="btn absolute right-[210px] top-4 z-10 h-9 min-h-9 rounded-[18px] bg-[#0059E5] text-white hover:bg-blue-500"
        @click="loadDataList"
      >
        <span class="loading loading-spinner" v-if="loading"></span>
        拓扑信息查询
      </button>
      <button
        class="btn absolute right-4 top-4 z-10 h-9 min-h-9 cursor-pointer rounded-[18px] bg-gray-300 text-gray-500 hover:bg-gray-200"
        @click="loadDataGenerate"
      >
        <div class="relative">
          <div
            class="absolute z-10 size-4 animate-ping rounded-full bg-lime-500"
            v-if="generating"
          ></div>
          <div
            class="relative size-4 rounded-full bg-gray-500"
            :class="{ 'bg-lime-500': generating }"
          ></div>
        </div>
        {{
          generateStatus === 'stop'
            ? '拓扑数据包开启生成'
            : '拓扑数据包关闭生成'
        }}
      </button>
      <!-- 节点信息面板 -->
      <common-pannel ref="pannelRef" />
      <!-- 画布 -->
      <div id="graph" class="h-full w-full"></div>
    </section>

    <!-- 2.右侧数据面板 -->
    <section
      class="flex w-80 shrink-0 grow-0 flex-col overflow-auto border-l border-gray-300 bg-white p-3"
    >
      <!-- 节点信息 -->
      <div class="rounded-lg bg-[#EEF1FA] p-3">
        <div class="flex flex-row flex-nowrap items-center gap-2">
          <info-svg class="shrink-0 grow-0" />
          <p class="font-bold text-[#0059E5]">节点信息</p>
        </div>
        <div
          class="mt-3 flex flex-row flex-nowrap items-center justify-between text-xs"
        >
          <p class="text-[#9097a2]">节点local label</p>
          <p>{{ currentNode?.localLabel || '--' }}</p>
        </div>
        <div
          class="mt-2 flex flex-row flex-nowrap items-center justify-between text-xs"
        >
          <p class="text-[#9097a2]">节点类型</p>
          <p>{{ currentNode?.type || '--' }}</p>
        </div>
      </div>
      <!-- 节点端口信息 -->
      <common-title class="mt-5" title="节点端口信息" />
      <table class="mt-3">
        <thead>
          <tr class="h-8 bg-[#eff1f4] text-[#9097a2]">
            <th class="w-1/2 px-3 text-left">编号</th>
            <th class="w-1/2 px-3 text-left">速率</th>
          </tr>
        </thead>
        <tbody>
          <tr
            class="h-8 transition hover:bg-[#f7fafd]"
            :class="{ 'bg-[#FAF8F8]': index % 2 === 1 }"
            v-for="(item, index) of currentNode?.ports"
            :key="item.key"
          >
            <td class="w-1/2 px-3">{{ item.index }}</td>
            <td class="w-1/2 px-3">{{ item.rate }}</td>
          </tr>
        </tbody>
      </table>
      <!-- 邻接节点信息 -->
      <common-title class="mt-5" title="邻接节点信息" />
      <ul class="mt-3">
        <li
          class="mb-2 rounded-lg bg-[#FAF8F8] px-3 py-2 text-xs"
          v-for="(item, index) of currentNode?.topologies"
          :key="index"
        >
          <p>{{ item.label }}</p>
          <div
            class="mt-2 flex flex-row flex-nowrap items-center justify-between"
          >
            <p class="text-[#9097a2]">邻接节点信息</p>
            <p>{{ item.index }}</p>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Graph, Model, Node } from '@antv/x6'
import { CircularLayout } from '@antv/layout'
import { toolDebounce } from '@/utils/tool'
import { storageGet, storageSet } from '@/utils/storage'
import api from '@/api'
import CommonTitle from '@/components/common-title.vue'
import commonPannel from '@/components/common-pannel.vue'
import InfoSvg from '@/assets/svg/info.svg'
import forwardPng from '@/assets/image/forward.png'
import labelPng from '@/assets/image/label.png'

defineOptions({ name: 'ReliableCommunication' })

const loading = ref(false)
const generating = ref(false)
const generateStatus = ref(storageGet('generateStatus') || 'stop')
const nodes = ref<CommonNode[]>([])
const currentNode = ref<CommonNode>(null)
const currentCount = ref(0)
const pannelRef = ref()

async function loadDataList() {
  if (loading.value || generating.value) {
    return
  }

  try {
    loading.value = true
    nodes.value = await api.loadJson()
    const edges = await api.loadTopology(nodes.value)

    const json: Model.FromJSONData = {
      nodes: [],
      edges: []
    }

    nodes.value.forEach(node => {
      json.nodes.push({
        id: node.localLabel,
        shape: node.type === '转发节点' ? 'topology-node2' : 'topology-node1',
        label: node.localLabel,
        data: node
      })
    })

    edges.forEach(edge => {
      json.edges.push({ ...edge, shape: 'topology-edge', label: '' })
    })

    const circularLayout = new CircularLayout({
      type: 'circular',
      center: [500, 500],
      radius: 350
    })
    // @ts-ignore
    const model = circularLayout.layout(json)

    ;(model.nodes as Node.Metadata[]).forEach(node => {
      const position = storageGet(node.id) as { x: number; y: number }
      if (!position) {
        return
      }
      node.x = position.x
      node.y = position.y
    })

    graph.fromJSON(model)
    graph.centerContent()
  } catch (error) {
  } finally {
    loading.value = false
  }
}

async function loadDataGenerate() {
  if (loading.value || generating.value) {
    return
  }

  try {
    generating.value = true
    if (generateStatus.value === 'stop') {
      await api.loadGenerate(nodes.value)
      ElMessage.success('拓扑数据包已开启生成')
    } else {
      await api.loadStop(nodes.value)
      ElMessage.success('拓扑数据包已关闭生成')
    }
  } catch (error) {
  } finally {
    generateStatus.value = generateStatus.value === 'stop' ? 'start' : 'stop'
    storageSet('generateStatus', generateStatus.value)
    generating.value = false
  }
}

/*************************** antv x6 ***************************/

let graph: Graph = null

Graph.registerNode(
  'topology-node1',
  {
    inherit: 'image',
    width: 60,
    height: 60,
    angle: 0,
    imageUrl: labelPng,
    attrs: {
      text: { refY: 0 }
    }
  },
  true
)

Graph.registerNode(
  'topology-node2',
  {
    inherit: 'image',
    width: 60,
    height: 60,
    angle: 0,
    imageUrl: forwardPng,
    attrs: {
      text: { refY: 0 }
    }
  },
  true
)

Graph.registerEdge(
  'topology-edge',
  {
    inherit: 'edge',
    attrs: {
      line: { stroke: '#8f8f8f', strokeWidth: 1, targetMarker: 'block' }
    }
  },
  true
)

function onClickNode(node: Node) {
  graph
    .getNodes()
    .forEach(item => graph.getCellById(item.id)?.attr('image/filter', 'none'))
  node.attr('image/filter', 'drop-shadow(0 0 10px rgb(33, 150, 243))')

  const data = node.getData()
  currentNode.value = data
  currentCount.value++
  setTimeout(() => (currentCount.value = 0), 350)
  currentCount.value > 1 && pannelRef.value?.open(data)
}

function onMoveNode(node: Node) {
  const { x, y } = node.getPosition()
  storageSet(node.id, { x, y })
}

function onClickBlank() {
  graph
    .getNodes()
    .forEach(item => graph.getCellById(item.id)?.attr('image/filter', 'none'))

  currentNode.value = null
  currentCount.value = 0
  pannelRef.value?.close()
}

const onResize = toolDebounce(() => {
  const graphContainer = document.querySelector<HTMLDivElement>('#graph')
  const { width, height } = graphContainer.getBoundingClientRect()

  graph?.resize(width, height)
  graph?.centerContent()
})

function initGraph() {
  const graphContainer = document.querySelector<HTMLDivElement>('#graph')
  const { width, height } = graphContainer.getBoundingClientRect()

  graph = new Graph({
    container: graphContainer,
    width,
    height,
    autoResize: true,
    background: {
      color: '#eef1fa'
    },
    grid: {
      visible: true,
      type: 'doubleMesh',
      size: 20,
      args: [
        { color: '#e1e1e1', thickness: 1 },
        { color: '#e1e1e1', thickness: 1, factor: 4 }
      ]
    },
    panning: {
      enabled: true
    },
    mousewheel: {
      enabled: true
    },
    connecting: {
      allowBlank: false,
      allowLoop: true,
      allowNode: true,
      allowEdge: false,
      allowPort: false,
      allowMulti: true
    }
  })

  graph.on('node:click', ({ node }) => onClickNode(node))
  graph.on('node:moved', ({ node }) => onMoveNode(node))
  graph.on('blank:click', () => onClickBlank())
}

onMounted(() => {
  window.addEventListener('resize', onResize, false)

  initGraph()
  onResize()
  loadDataList()
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize, false)

  graph.off()
  graph.dispose()
})
</script>
