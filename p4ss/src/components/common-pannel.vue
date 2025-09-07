<template>
  <div
    class="absolute bottom-3 left-3 right-3 z-10 flex h-[422px] flex-nowrap items-stretch gap-3 rounded-xl bg-white p-4 shadow-2xl transition ease-linear"
    :class="{ 'translate-y-[450px]': !visible }"
  >
    <!-- 1.表单区 -->
    <section class="w-[300px] shrink-0 grow-0">
      <!-- 标题 -->
      <div class="flex flex-nowrap items-center gap-2">
        <div class="size-2 rounded-full bg-[#0059E5]"></div>
        <p class="flex-auto text-base font-bold text-black">{{ title }}</p>
      </div>
      <!-- 转发节点表单 -->
      <div v-if="currentNode?.type === '转发节点'">
        <!-- 匹配标签 -->
        <div class="mt-4 flex flex-row flex-nowrap items-center gap-3">
          <p class="w-16 shrink-0 grow-0 text-xs text-gray-500">匹配标签</p>
          <input
            class="input input-sm flex-auto bg-gray-100"
            type="text"
            v-model.trim="info.label"
          />
        </div>
        <!-- 出端口 -->
        <div class="mt-3 flex flex-row flex-nowrap items-center gap-3">
          <p class="w-16 shrink-0 grow-0 text-xs text-gray-500">出端口</p>
          <input
            class="input input-sm flex-auto bg-gray-100"
            type="text"
            v-model.trim="info.port"
          />
        </div>
      </div>
      <!-- 封装节点表单 -->
      <div v-else>
        <!-- 网络层协议 -->
        <div class="mt-4 flex flex-row flex-nowrap items-center gap-3">
          <p class="w-16 shrink-0 grow-0 text-xs text-gray-500">网络层协议</p>
          <select
            class="select select-sm flex-auto bg-gray-100"
            v-model.trim="info.ip"
          >
            <option>ipv4</option>
            <option>ipv6</option>
          </select>
        </div>
        <!-- 源地址 -->
        <div class="mt-3 flex flex-row flex-nowrap items-center gap-3">
          <p class="w-16 shrink-0 grow-0 text-xs text-gray-500">源地址</p>
          <input
            class="input input-sm flex-auto bg-gray-100"
            type="text"
            v-if="info.ip === 'ipv6'"
            v-model.trim="info.ipv6_src"
          />
          <input
            class="input input-sm flex-auto bg-gray-100"
            type="text"
            v-else
            v-model.trim="info.ipv4_src"
          />
        </div>
        <!-- 目的地址 -->
        <div class="mt-3 flex flex-row flex-nowrap items-center gap-3">
          <p class="w-16 shrink-0 grow-0 text-xs text-gray-500">目的地址</p>
          <input
            class="input input-sm flex-auto bg-gray-100"
            type="text"
            v-if="info.ip === 'ipv6'"
            v-model.trim="info.ipv6_dst"
          />
          <input
            class="input input-sm flex-auto bg-gray-100"
            type="text"
            v-else
            v-model.trim="info.ipv4_dst"
          />
        </div>
        <!-- 传输层协议 -->
        <div class="mt-3 flex flex-row flex-nowrap items-center gap-3">
          <p class="w-16 shrink-0 grow-0 text-xs text-gray-500">传输层协议</p>
          <select
            class="select select-sm flex-auto bg-gray-100"
            v-model.trim="info.tp"
          >
            <option>tcp</option>
            <option>udp</option>
          </select>
        </div>
        <!-- 源端口 -->
        <div class="mt-3 flex flex-row flex-nowrap items-center gap-3">
          <p class="w-16 shrink-0 grow-0 text-xs text-gray-500">源端口</p>
          <input
            class="input input-sm flex-auto bg-gray-100"
            type="text"
            v-model.trim="info.tp_src"
          />
        </div>
        <!-- 目的端口 -->
        <div class="mt-3 flex flex-row flex-nowrap items-center gap-3">
          <p class="w-16 shrink-0 grow-0 text-xs text-gray-500">目的端口</p>
          <input
            class="input input-sm flex-auto bg-gray-100"
            type="text"
            v-model.trim="info.tp_dst"
          />
        </div>
        <!-- 标签 -->
        <div class="mt-3 flex flex-row flex-nowrap items-center gap-3">
          <p class="w-16 shrink-0 grow-0 text-xs text-gray-500">标签</p>
          <el-input-tag
            class="flex-auto !rounded-lg !bg-gray-100 !shadow-none"
            tag-type="primary"
            tag-effect="dark"
            v-model="info.label_list"
          />
        </div>
      </div>
    </section>
    <!-- 2.按钮区 -->
    <section
      class="flex shrink-0 grow-0 flex-col flex-nowrap justify-center gap-6"
    >
      <button
        class="btn h-9 min-h-9 rounded-[18px] bg-white shadow-lg"
        :class="{
          '!hover:bg-blue-500 !bg-[#0059E5] !text-white': operation === item.key
        }"
        v-for="item of operationConfig"
        @click="onClickItems(item.key)"
      >
        <component :is="item.svg" />
        {{ item.key }}
      </button>
    </section>
    <!-- 3.日志区 -->
    <ul class="flex-auto overflow-y-auto rounded-lg bg-gray-100 p-2">
      <li
        class="text-xs text-[#222]"
        :class="{ 'mt-2': index > 0 }"
        v-for="(item, index) of operations"
        :key="index"
      >
        <p>{{ item.content }}</p>
        <!-- 转发节点数据 -->
        <div v-if="currentNode?.type === '转发节点'">
          <div
            class="list-disc pl-1 text-gray-500"
            v-for="(subItem, subIndex) of item.labels"
            :key="`${index}_${subIndex}`"
          >
            <span>{{ subIndex + 1 }}.&nbsp;&nbsp;</span>
            <span>匹配标签: {{ subItem.label }}&nbsp;&nbsp;\&nbsp;&nbsp;</span>
            <span>出端口: {{ subItem.port }}</span>
          </div>
        </div>
        <!-- 封装节点数据 -->
        <div v-else>
          <div
            class="list-disc pl-1 text-gray-500"
            v-for="(subItem, subIndex) of item.forwards"
            :key="`${index}_${subIndex}`"
          >
            <span>{{ subIndex + 1 }}.&nbsp;&nbsp;</span>
            <span>传输层协议: {{ subItem.tp }}&nbsp;&nbsp;\&nbsp;&nbsp;</span>
            <span v-if="subItem.ip === 'ipv6'">
              ipv6源地址: {{ subItem.ipv6_src }}&nbsp;&nbsp;\&nbsp;&nbsp;
            </span>
            <span v-else>
              ipv4源地址: {{ subItem.ipv4_src }}&nbsp;&nbsp;\&nbsp;&nbsp;
            </span>
            <span v-if="subItem.ip === 'ipv6'">
              ipv6目的地址: {{ subItem.ipv6_dst }}&nbsp;&nbsp;\&nbsp;&nbsp;
            </span>
            <span v-else>
              ipv4目的地址: {{ subItem.ipv4_dst }}&nbsp;&nbsp;\&nbsp;&nbsp;
            </span>
            <span>源端口: {{ subItem.tp_src }}&nbsp;&nbsp;\&nbsp;&nbsp;</span>
            <span>目的端口: {{ subItem.tp_dst }}&nbsp;&nbsp;\&nbsp;&nbsp;</span>
            <span>标签: {{ subItem.label_list }}</span>
          </div>
        </div>
      </li>
      <li class="mt-4" ref="operationRef"></li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import type { AxiosError } from 'axios'
import { isArray, isString } from '@/utils/is'
import api from '@/api'
import AddSvg from '@/assets/svg/add.svg'
import SearchSvg from '@/assets/svg/search.svg'
import DeleteSvg from '@/assets/svg/delete.svg'
import ClearSvg from '@/assets/svg/clear.svg'

defineExpose({ open, close })

const visible = ref(false)
const currentNode = ref<CommonNode>(null)
const operationConfig = [
  { key: '添加', svg: AddSvg },
  { key: '修改', svg: AddSvg },
  { key: '查询', svg: SearchSvg },
  { key: '删除', svg: DeleteSvg },
  { key: '重置', svg: ClearSvg }
]
const operation = ref('添加')
const operations = ref<CommonOperation[]>([])
const operationRef = ref<HTMLLIElement>()
const info = ref<ForwardInfo & LabelInfo>({
  // 1.封装节点
  ip: 'ipv4', // 网络层协议（增删查）
  tp: 'tcp', // 传输层协议（增删查）
  ipv4_src: '', // ipv4 源地址（增删查）
  ipv4_dst: '', // ipv4 目的地址（增删查）
  ipv6_src: '', // ipv6 源地址（增删查）
  ipv6_dst: '', // ipv6 目的地址（增删查）
  tp_src: '', // 源端口（增删查）
  tp_dst: '', // 目的端口（增删查）
  label_list: [], // 标签（增）
  // 2.转发节点
  label: '', // 匹配标签（增删查）
  port: '' // 出端口（增）
})

const title = computed(() =>
  currentNode.value?.type === '转发节点'
    ? '转发节点端口信息'
    : '封装节点端口信息'
)

function open(node: CommonNode) {
  visible.value = true
  currentNode.value = node
  operation.value = '添加'
  operations.value = []
  handleInfoReset()
}

function close() {
  visible.value = false
}

function handleInfoReset() {
  info.value = {
    ip: 'ipv4',
    tp: 'tcp',
    ipv4_src: '',
    ipv4_dst: '',
    ipv6_src: '',
    ipv6_dst: '',
    tp_src: '',
    tp_dst: '',
    label_list: [],
    label: '',
    port: ''
  }
}

function onClickItems(type: string) {
  operation.value = type

  switch (type) {
    case '添加':
      ;(async () => {
        try {
          const baseUrl = currentNode.value.baseUrl
          const body = {} as Partial<ForwardInfo & LabelInfo>
          if (currentNode.value.type === '转发节点') {
            isString(info.value.label) && (body.label = info.value.label)
            isString(info.value.port) && (body.port = info.value.port)
            await api.loadLabelAdd(baseUrl, body)
          } else {
            body.tp = info.value.tp
            if (info.value.ip === 'ipv6') {
              isString(info.value.ipv6_src) &&
                (body.ipv6_src = info.value.ipv6_src)
              isString(info.value.ipv6_dst) &&
                (body.ipv6_dst = info.value.ipv6_dst)
            } else {
              isString(info.value.ipv4_src) &&
                (body.ipv4_src = info.value.ipv4_src)
              isString(info.value.ipv4_dst) &&
                (body.ipv4_dst = info.value.ipv4_dst)
            }
            isString(info.value.tp_src) && (body.tp_src = info.value.tp_src)
            isString(info.value.tp_dst) && (body.tp_dst = info.value.tp_dst)
            isArray(info.value.label_list) &&
              // @ts-ignore
              (body.label_list = info.value.label_list.join(','))
            await api.loadForwardAdd(baseUrl, info.value.ip, body)
          }
          operations.value.push({
            content: '添加成功！',
            forwards: [],
            labels: []
          })
        } catch (error) {
          operations.value.push({
            content: '添加失败！',
            forwards: [],
            labels: []
          })
        } finally {
          nextTick(() => {
            handleInfoReset()
            operationRef.value?.scrollIntoView({ behavior: 'smooth' })
          })
        }
      })()
      break

    case '修改':
      ;(async () => {
        try {
          const baseUrl = currentNode.value.baseUrl
          const body = {} as Partial<ForwardInfo & LabelInfo>
          if (currentNode.value.type === '转发节点') {
            isString(info.value.label) && (body.label = info.value.label)
            isString(info.value.port) && (body.port = info.value.port)
            await api.loadLabelModify(baseUrl, body)
          } else {
            body.tp = info.value.tp
            if (info.value.ip === 'ipv6') {
              isString(info.value.ipv6_src) &&
                (body.ipv6_src = info.value.ipv6_src)
              isString(info.value.ipv6_dst) &&
                (body.ipv6_dst = info.value.ipv6_dst)
            } else {
              isString(info.value.ipv4_src) &&
                (body.ipv4_src = info.value.ipv4_src)
              isString(info.value.ipv4_dst) &&
                (body.ipv4_dst = info.value.ipv4_dst)
            }
            isString(info.value.tp_src) && (body.tp_src = info.value.tp_src)
            isString(info.value.tp_dst) && (body.tp_dst = info.value.tp_dst)
            isArray(info.value.label_list) &&
              // @ts-ignore
              (body.label_list = info.value.label_list.join(','))
            await api.loadForwardModify(baseUrl, info.value.ip, body)
          }
          operations.value.push({
            content: '修改成功！',
            forwards: [],
            labels: []
          })
        } catch (error) {
          operations.value.push({
            content: `修改失败！${(error as AxiosError).response?.data}`,
            forwards: [],
            labels: []
          })
        } finally {
          nextTick(() => {
            handleInfoReset()
            operationRef.value?.scrollIntoView({ behavior: 'smooth' })
          })
        }
      })()
      break

    case '查询':
      ;(async () => {
        try {
          const baseUrl = currentNode.value.baseUrl
          const body = {} as Partial<ForwardInfo & LabelInfo>
          if (currentNode.value.type === '转发节点') {
            isString(info.value.label) && (body.label = info.value.label)
            const res = await api.loadLabelSearch(baseUrl, body)
            operations.value.push({
              content: '查询结果显示：',
              forwards: [],
              labels: isArray(res) ? res : []
            })
          } else {
            body.tp = info.value.tp
            if (info.value.ip === 'ipv6') {
              isString(info.value.ipv6_src) &&
                (body.ipv6_src = info.value.ipv6_src)
              isString(info.value.ipv6_dst) &&
                (body.ipv6_dst = info.value.ipv6_dst)
            } else {
              isString(info.value.ipv4_src) &&
                (body.ipv4_src = info.value.ipv4_src)
              isString(info.value.ipv4_dst) &&
                (body.ipv4_dst = info.value.ipv4_dst)
            }
            isString(info.value.tp_src) && (body.tp_src = info.value.tp_src)
            isString(info.value.tp_dst) && (body.tp_dst = info.value.tp_dst)
            const res = await api.loadForwardSearch(
              baseUrl,
              info.value.ip,
              body
            )
            operations.value.push({
              content: '查询结果显示：',
              forwards: isArray(res)
                ? res.map(item => ({ ...item, ip: info.value.ip }))
                : [],
              labels: []
            })
          }
        } catch (error) {
          operations.value.push({
            content: '查询失败！',
            forwards: [],
            labels: []
          })
        } finally {
          nextTick(() => {
            handleInfoReset()
            operationRef.value?.scrollIntoView({ behavior: 'smooth' })
          })
        }
      })()
      break

    case '删除':
      ;(async () => {
        try {
          const baseUrl = currentNode.value.baseUrl
          const body = {} as Partial<ForwardInfo & LabelInfo>
          if (currentNode.value.type === '转发节点') {
            isString(info.value.label) && (body.label = info.value.label)
            await api.loadLabelDelete(baseUrl, body)
          } else {
            body.tp = info.value.tp
            if (info.value.ip === 'ipv6') {
              isString(info.value.ipv6_src) &&
                (body.ipv6_src = info.value.ipv6_src)
              isString(info.value.ipv6_dst) &&
                (body.ipv6_dst = info.value.ipv6_dst)
            } else {
              isString(info.value.ipv4_src) &&
                (body.ipv4_src = info.value.ipv4_src)
              isString(info.value.ipv4_dst) &&
                (body.ipv4_dst = info.value.ipv4_dst)
            }
            isString(info.value.tp_src) && (body.tp_src = info.value.tp_src)
            isString(info.value.tp_dst) && (body.tp_dst = info.value.tp_dst)
            await api.loadForwardDelete(baseUrl, info.value.ip, body)
          }
          operations.value.push({
            content: '删除成功！',
            forwards: [],
            labels: []
          })
        } catch (error) {
          operations.value.push({
            content: '删除失败！',
            forwards: [],
            labels: []
          })
        } finally {
          nextTick(() => {
            handleInfoReset()
            operationRef.value?.scrollIntoView({ behavior: 'smooth' })
          })
        }
      })()
      break

    case '重置':
      ;(async () => {
        try {
          const baseUrl = currentNode.value.baseUrl
          if (currentNode.value.type === '转发节点') {
            await api.loadLabelReset(baseUrl)
          } else {
            await api.loadForwardReset(baseUrl)
          }
          operations.value.push({
            content: '重置成功！',
            forwards: [],
            labels: []
          })
        } catch (error) {
          operations.value.push({
            content: '重置失败！',
            forwards: [],
            labels: []
          })
        } finally {
          nextTick(() => {
            handleInfoReset()
            operationRef.value?.scrollIntoView({ behavior: 'smooth' })
          })
        }
      })()
      break
  }
}
</script>
