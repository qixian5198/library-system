<template>
  <div class="borrowings-page">
    <!-- 工具栏 -->
    <el-card class="toolbar">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-select v-model="filterStatus" placeholder="借阅状态" clearable @change="fetchBorrowings">
            <el-option label="全部" value="" />
            <el-option label="借阅中" value="borrowed" />
            <el-option label="已归还" value="returned" />
            <el-option label="已逾期" value="overdue" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="openBorrowDialog">
            <el-icon><Plus /></el-icon>
            借书
          </el-button>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 借阅列表 -->
    <el-card style="margin-top: 16px">
      <el-table :data="borrowings" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="book_title" label="书名" min-width="150" />
        <el-table-column prop="reader_name" label="读者" width="100" />
        <el-table-column prop="borrow_date" label="借阅日期" width="160">
          <template #default="{ row }">
            {{ formatDate(row.borrow_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="due_date" label="应还日期" width="160">
          <template #default="{ row }">
            {{ formatDate(row.due_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="return_date" label="归还日期" width="160">
          <template #default="{ row }">
            {{ row.return_date ? formatDate(row.return_date) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'borrowed' || row.status === 'overdue'"
              type="success" 
              size="small" 
              @click="handleReturn(row)"
            >
              还书
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchBorrowings"
          @current-change="fetchBorrowings"
        />
      </div>
    </el-card>
    
    <!-- 借书对话框 -->
    <el-dialog v-model="borrowDialogVisible" title="借书" width="450px">
      <el-form :model="borrowForm" :rules="borrowRules" ref="borrowFormRef" label-width="80px">
        <el-form-item label="选择图书" prop="book_id">
          <el-select 
            v-model="borrowForm.book_id" 
            placeholder="请选择图书"
            filterable
            style="width: 100%"
            @focus="loadBooks"
          >
            <el-option
              v-for="book in bookList"
              :key="book.id"
              :label="`${book.title} (可借: ${book.available})`"
              :value="book.id"
              :disabled="book.available <= 0"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="选择读者" prop="reader_id">
          <el-select 
            v-model="borrowForm.reader_id" 
            placeholder="请选择读者"
            filterable
            style="width: 100%"
            @focus="loadReaders"
          >
            <el-option
              v-for="reader in readerList"
              :key="reader.id"
              :label="`${reader.name} (在借: ${reader.borrowed_count})`"
              :value="reader.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="借阅天数" prop="days">
          <el-input-number v-model="borrowForm.days" :min="1" :max="90" style="width: 100%" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="borrowDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBorrow" :loading="submitting">
          确认借书
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { borrowingApi, bookApi, readerApi } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const borrowings = ref([])
const loading = ref(false)
const filterStatus = ref('')
const borrowDialogVisible = ref(false)
const submitting = ref(false)
const bookList = ref([])
const readerList = ref([])
const borrowFormRef = ref()

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const borrowForm = reactive({
  book_id: null,
  reader_id: null,
  days: 30
})

const borrowRules = {
  book_id: [{ required: true, message: '请选择图书', trigger: 'change' }],
  reader_id: [{ required: true, message: '请选择读者', trigger: 'change' }]
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return dateStr.replace('T', ' ').substring(0, 19)
}

const getStatusType = (status) => {
  const types = {
    borrowed: 'primary',
    returned: 'success',
    overdue: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    borrowed: '借阅中',
    returned: '已归还',
    overdue: '已逾期'
  }
  return texts[status] || status
}

const fetchBorrowings = async () => {
  loading.value = true
  try {
    const { data } = await borrowingApi.getBorrowings({
      page: pagination.page,
      per_page: pagination.per_page,
      status: filterStatus.value
    })
    borrowings.value = data.borrowings
    pagination.total = data.total
  } catch (error) {
    ElMessage.error('获取借阅记录失败')
  } finally {
    loading.value = false
  }
}

const loadBooks = async () => {
  if (bookList.value.length === 0) {
    const { data } = await bookApi.getBooks({ per_page: 100 })
    bookList.value = data.books
  }
}

const loadReaders = async () => {
  if (readerList.value.length === 0) {
    const { data } = await readerApi.getReaders({ per_page: 100 })
    readerList.value = data.readers
  }
}

const openBorrowDialog = () => {
  borrowForm.book_id = null
  borrowForm.reader_id = null
  borrowForm.days = 30
  bookList.value = []
  readerList.value = []
  borrowDialogVisible.value = true
}

const handleBorrow = async () => {
  try {
    await borrowFormRef.value.validate()
    submitting.value = true
    
    await borrowingApi.borrowBook(borrowForm)
    ElMessage.success('借书成功')
    borrowDialogVisible.value = false
    fetchBorrowings()
  } catch (error) {
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)
    } else if (error !== 'cancel') {
      ElMessage.error('借书失败')
    }
  } finally {
    submitting.value = false
  }
}

const handleReturn = (row) => {
  ElMessageBox.confirm(`确定要归还《${row.book_title}》吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(async () => {
    try {
      await borrowingApi.returnBook(row.id)
      ElMessage.success('还书成功')
      fetchBorrowings()
    } catch (error) {
      ElMessage.error(error.response?.data?.error || '还书失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchBorrowings()
})
</script>

<style scoped>
.borrowings-page {
  padding: 20px;
}

.toolbar {
  margin-bottom: 16px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
