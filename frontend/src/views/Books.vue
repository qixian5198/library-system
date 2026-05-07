<template>
  <div class="books-page">
    <!-- 工具栏 -->
    <el-card class="toolbar">
      <el-row :gutter="16">
        <el-col :span="8">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索书名、作者、ISBN"
            clearable
            @clear="fetchBooks"
            @keyup.enter="fetchBooks"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="fetchBooks">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </el-col>
        <el-col :span="12" style="text-align: right">
          <el-button type="success" @click="openAddDialog">
            <el-icon><Plus /></el-icon>
            添加图书
          </el-button>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 图书列表 -->
    <el-card style="margin-top: 16px">
      <el-table :data="books" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="50" />
        <el-table-column prop="title" label="书名" min-width="150" />
        <el-table-column prop="author" label="作者" width="100" />
        <el-table-column prop="publisher" label="出版社" width="120" />
        <el-table-column prop="category" label="分类" width="80" />
        <el-table-column prop="price" label="价格" width="70">
          <template #default="{ row }">
            ¥{{ row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="60" />
        <el-table-column prop="available" label="可借" width="60">
          <template #default="{ row }">
            <el-tag :type="row.available > 0 ? 'success' : 'danger'" size="small">
              {{ row.available }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openEditDialog(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
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
          @size-change="fetchBooks"
          @current-change="fetchBooks"
        />
      </div>
    </el-card>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑图书' : '添加图书'"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="书名" prop="title">
          <el-input v-model="form.title" placeholder="请输入书名" />
        </el-form-item>
        <el-form-item label="作者" prop="author">
          <el-input v-model="form.author" placeholder="请输入作者" />
        </el-form-item>
        <el-form-item label="ISBN" prop="isbn">
          <el-input v-model="form.isbn" placeholder="请输入ISBN" />
        </el-form-item>
        <el-form-item label="出版社" prop="publisher">
          <el-input v-model="form.publisher" placeholder="请输入出版社" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
            <el-option label="小说" value="小说" />
            <el-option label="文学" value="文学" />
            <el-option label="科幻" value="科幻" />
            <el-option label="技术" value="技术" />
            <el-option label="历史" value="历史" />
            <el-option label="心理学" value="心理学" />
            <el-option label="悬疑" value="悬疑" />
            <el-option label="古典文学" value="古典文学" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="form.price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="form.stock" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="简介" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入简介"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { bookApi } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const books = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const formRef = ref()

const searchKeyword = ref('')

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const form = reactive({
  id: null,
  title: '',
  author: '',
  isbn: '',
  publisher: '',
  category: '',
  price: 0,
  stock: 1,
  description: '',
  cover: ''
})

const rules = {
  title: [{ required: true, message: '请输入书名', trigger: 'blur' }],
  author: [{ required: true, message: '请输入作者', trigger: 'blur' }]
}

const fetchBooks = async () => {
  loading.value = true
  try {
    const { data } = await bookApi.getBooks({
      page: pagination.page,
      per_page: pagination.per_page,
      search: searchKeyword.value
    })
    books.value = data.books
    pagination.total = data.total
  } catch (error) {
    ElMessage.error('获取图书列表失败')
  } finally {
    loading.value = false
  }
}

const openAddDialog = () => {
  isEdit.value = false
  Object.assign(form, {
    id: null,
    title: '',
    author: '',
    isbn: '',
    publisher: '',
    category: '',
    price: 0,
    stock: 1,
    description: '',
    cover: ''
  })
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    title: row.title,
    author: row.author,
    isbn: row.isbn,
    publisher: row.publisher || '',
    category: row.category,
    price: row.price || 0,
    stock: row.stock,
    description: row.description || '',
    cover: row.cover || ''
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      await bookApi.updateBook(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await bookApi.createBook(form)
      ElMessage.success('添加成功')
    }
    
    dialogVisible.value = false
    fetchBooks()
  } catch (error) {
    if (error.response?.data?.error) {
      ElMessage.error(error.response.data.error)
    } else if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  } finally {
    submitting.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除图书《${row.title}》吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await bookApi.deleteBook(row.id)
      ElMessage.success('删除成功')
      fetchBooks()
    } catch (error) {
      ElMessage.error(error.response?.data?.error || '删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchBooks()
})
</script>

<style scoped>
.books-page {
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
