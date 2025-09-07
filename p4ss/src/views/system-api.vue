<template>
  <div
    class="m-3 flex min-h-[calc(100vh-80px)] flex-col flex-nowrap items-stretch gap-3"
  >
    <common-title class="shrink-0 grow-0" title="系统调度接口列表" />
    <ul class="flex-auto">
      <li
        class="mb-2 select-none overflow-hidden rounded-lg bg-white"
        v-for="item of list"
        :key="item.id"
      >
        <div
          class="flex cursor-pointer flex-row flex-nowrap items-center justify-between p-3 transition-all"
          :class="{
            'bg-[#0059E5]': item.expanded,
            'text-white': item.expanded
          }"
          @click="item.expanded = !item.expanded"
        >
          <p>{{ item.name }}</p>
          <open-svg v-if="item.expanded" />
          <close-svg v-else />
        </div>
        <embed
          class="h-[800px] w-full"
          v-if="item.expanded"
          type="application/pdf"
          :src="item.src"
        />
      </li>
    </ul>
    <el-pagination
      class="flex shrink-0 grow-0 justify-end"
      layout="prev, pager, next"
      :total="query.total"
      :current-page="query.pageNum"
      @current-change="
        current => {
          query.pageNum = current
        }
      "
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import CommonTitle from '@/components/common-title.vue'
import OpenSvg from '@/assets/svg/open.svg'
import CloseSvg from '@/assets/svg/close.svg'

defineOptions({ name: 'SystemApi' })

const query = ref({ pageNum: 1, pageSize: 10, total: 10 })
const list = ref([
  {
    id: '1',
    name: '1.封装节点路径规则添加',
    src: './pdf/1_封装节点路径规则添加.pdf',
    expanded: false
  },
  {
    id: '2',
    name: '2.封装节点路径规则查询',
    src: './pdf/2_封装节点路径规则查询.pdf',
    expanded: false
  },
  {
    id: '3',
    name: '3.封装节点路径规则修改',
    src: './pdf/3_封装节点路径规则修改.pdf',
    expanded: false
  },
  {
    id: '4',
    name: '4.封装节点路径规则删除',
    src: './pdf/4_封装节点路径规则删除.pdf',
    expanded: false
  },
  {
    id: '5',
    name: '5.封装节点路径规则清除',
    src: './pdf/5_封装节点路径规则清除.pdf',
    expanded: false
  },
  {
    id: '6',
    name: '6.转发节点规则添加',
    src: './pdf/6_转发节点规则添加.pdf',
    expanded: false
  },
  {
    id: '7',
    name: '7.转发节点规则查询',
    src: './pdf/7_转发节点规则查询.pdf',
    expanded: false
  },
  {
    id: '8',
    name: '8.转发节点规则修改',
    src: './pdf/8_转发节点规则修改.pdf',
    expanded: false
  },
  {
    id: '9',
    name: '9.转发节点规则删除',
    src: './pdf/9_转发节点规则删除.pdf',
    expanded: false
  },
  {
    id: '10',
    name: '10.转发节点规则清空',
    src: './pdf/10_转发节点规则清空.pdf',
    expanded: false
  },
  {
    id: '11',
    name: '11.网络拓扑获取',
    src: './pdf/11_网络拓扑获取.pdf',
    expanded: false
  },
  {
    id: '12',
    name: '12.数据包生成',
    src: './pdf/12_数据包生成.pdf',
    expanded: false
  }
])
</script>
