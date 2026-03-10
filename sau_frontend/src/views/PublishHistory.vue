<template>
  <div class="publish-history">
    <div class="page-header">
      <h1>发布历史</h1>
    </div>

    <!-- 筛选栏 -->
    <el-card style="margin-bottom:16px">
      <el-form inline>
        <el-form-item label="平台">
          <el-select v-model="filterPlatform" placeholder="全部" clearable style="width:120px" @change="fetchHistory">
            <el-option label="小红书" :value="1" />
            <el-option label="视频号" :value="2" />
            <el-option label="抖音" :value="3" />
            <el-option label="快手" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterStatus" placeholder="全部" clearable style="width:100px" @change="fetchHistory">
            <el-option label="成功" :value="1" />
            <el-option label="失败" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchHistory" :loading="loading">刷新</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 历史列表 -->
    <el-card>
      <el-table :data="historyList" style="width:100%" v-loading="loading" empty-text="暂无发布记录">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="platform" label="平台" width="100">
          <template #default="scope">
            <el-tag :type="getPlatformTagType(scope.row.platformType)" effect="plain">
              {{ scope.row.platform }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column label="账号" width="160" show-overflow-tooltip>
          <template #default="scope">
            <span v-if="scope.row.accountName && scope.row.accountName.length">
              {{ scope.row.accountName.join(', ') }}
            </span>
            <span v-else style="color:#c0c4cc">默认账号</span>
          </template>
        </el-table-column>
        <el-table-column label="文件数" width="80" align="center">
          <template #default="scope">
            {{ scope.row.fileList ? scope.row.fileList.length : 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="statusText" label="状态" width="80" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'" effect="plain">
              {{ scope.row.statusText }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="errorMsg" label="错误信息" min-width="180" show-overflow-tooltip>
          <template #default="scope">
            <span v-if="scope.row.errorMsg" style="color:#f56c6c;font-size:12px">{{ scope.row.errorMsg }}</span>
            <span v-else style="color:#c0c4cc">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="发布时间" width="180" />
      </el-table>

      <!-- 分页 -->
      <div style="margin-top:16px;display:flex;justify-content:flex-end">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchHistory"
          @current-change="fetchHistory"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5409'

const loading = ref(false)
const historyList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const filterPlatform = ref(null)
const filterStatus = ref(null)

const fetchHistory = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value,
      pageSize: pageSize.value
    })
    if (filterPlatform.value !== null && filterPlatform.value !== '') {
      params.append('platform', filterPlatform.value)
    }
    if (filterStatus.value !== null && filterStatus.value !== '') {
      params.append('status', filterStatus.value)
    }

    const res = await fetch(`${apiBaseUrl}/publishHistory?${params}`).then(r => r.json())
    if (res.code === 200) {
      historyList.value = res.data.list
      total.value = res.data.total
    }
  } catch (e) {
    console.error('获取发布历史失败:', e)
  } finally {
    loading.value = false
  }
}

const getPlatformTagType = (type) => {
  return { 1: 'danger', 2: 'warning', 3: '', 4: 'success' }[type] || 'info'
}

onMounted(fetchHistory)
</script>

<style lang="scss" scoped>
.publish-history {
  .page-header {
    margin-bottom: 20px;
    h1 { font-size: 24px; margin: 0; }
  }
}
</style>
