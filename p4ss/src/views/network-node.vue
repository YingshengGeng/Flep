<template>
  <div
    class="m-3 flex min-h-[calc(100vh-80px)] flex-col flex-nowrap items-stretch gap-3"
  >
    <common-title class="shrink-0 grow-0" title="网络节点列表" />
    <section class="flex-auto bg-white p-3" v-loading="loading">
      <el-table
        :header-cell-style="{ backgroundColor: '#eff1f4', color: '#9097a2' }"
        :data="list"
        stripe
      >
        <el-table-column label="序号" prop="num" />
        <el-table-column label="节点 local label" prop="localLabel" />
        <el-table-column label="节点类型" prop="type" />
        <el-table-column label="节点启动端口数" prop="ports">
          <template #default="{ row }">
            {{ row.ports.length }}
          </template>
        </el-table-column>
        <el-table-column label="节点服务器是否连接" prop="status" />
      </el-table>
    </section>
    <el-pagination
      class="flex shrink-0 grow-0 justify-end"
      layout="prev, pager, next"
      :total="query.total"
      :current-page="query.pageNum"
      @current-change="
        current => {
          query.pageNum = current
          loadDataList(false)
        }
      "
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '@/api'
import CommonTitle from '@/components/common-title.vue'

defineOptions({ name: 'NetworkNode' })

const loading = ref(true)
const query = ref({ pageNum: 1, pageSize: 10, total: 0 })
const baseList = ref<CommonNode[]>([])
const list = ref<CommonNode[]>([])

async function loadDataList(reset: boolean) {
  try {
    if (reset) {
      loading.value = true
      query.value = { pageNum: 1, pageSize: 10, total: 0 }
      baseList.value = []
      list.value = []
      const nodes = await api.loadJson()
      await api.loadTopology(nodes)
      baseList.value = nodes
      query.value.total = nodes.length
    }
    list.value = baseList.value.slice(
      (query.value.pageNum - 1) * query.value.pageSize,
      query.value.pageNum * query.value.pageSize
    )
  } catch (error) {
  } finally {
    loading.value = false
  }
}

loadDataList(true)
</script>
