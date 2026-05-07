<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon books">
            <el-icon size="32"><Reading /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_books }}</div>
            <div class="stat-label">图书总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon readers">
            <el-icon size="32"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_readers }}</div>
            <div class="stat-label">读者总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon borrowed">
            <el-icon size="32"><Tickets /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.borrowed_count }}</div>
            <div class="stat-label">在借数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon overdue">
            <el-icon size="32"><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.overdue_count }}</div>
            <div class="stat-label">逾期数量</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快捷操作 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>📌 快捷操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/books')">
              <el-icon><Plus /></el-icon>
              添加图书
            </el-button>
            <el-button type="success" @click="$router.push('/readers')">
              <el-icon><Plus /></el-icon>
              添加读者
            </el-button>
            <el-button type="warning" @click="$router.push('/borrowings')">
              <el-icon><Tickets /></el-icon>
              借书还书
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { statsApi } from '../api'

const stats = ref({
  total_books: 0,
  total_readers: 0,
  today_borrowings: 0,
  borrowed_count: 0,
  overdue_count: 0
})

const fetchStats = async () => {
  try {
    const { data } = await statsApi.getStats()
    stats.value = data
  } catch (error) {
    console.error('获取统计数据失败', error)
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 16px;
}

.stat-icon.books { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.stat-icon.readers { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat-icon.borrowed { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.stat-icon.overdue { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 4px;
}

.quick-actions {
  display: flex;
  gap: 12px;
}
</style>
