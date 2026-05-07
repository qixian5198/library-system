<template>
  <div class="readers-page">
    <!-- 工具栏 -->
    <el-card class="toolbar">
      <el-row :gutter="16">
        <el-col :span="8">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索姓名、电话"
            clearable
            @clear="fetchReaders"
            @keyup.enter="fetchReaders"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="fetchReaders">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </el-col>
        <el-col :span="12" style="text-align: right">
          <el-button type="success" @click="openAddDialog">
            <el-icon><Plus /></el-icon>
            添加读者
          </el-button>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 读者列表 -->
    <el-card style="margin-top: 16px">
      <el-table :data="readers" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="60" />
        <el-table-column prop="age" label="年龄" width="60" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="register_date" label="注册日期" width="120">
          <template #default="{ row }">
            {{ row.register_date?.split('T')[0] }}
          </template>
        </el-table-column>
        <el-table-column prop="borrowed_count" label="在借" width="80">
          <template #default="{ row }">
            <el-tag :type="row.borrowed_count > 0 ? 'warning' : 'success'">
              {{ row.borrowed_count }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
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
          @size-change="fetchReaders"
          @current-change="fetchReaders"
        />
      </div>
    </el-card>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑读者' : '添加读者'"
      width="450px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="form.gender" placeholder="请选择性别" style="width: 100%">
            <el-option label="男" value="男" />
            <el-option label="女" value="女" />
          </el-select>
        </el-form-item>
        <el-form-item label="年龄" prop="age">
          <el-input-number v-model="form.age" :min="1" :max="150" style="width: 100%" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入电话" />
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
import { readerApi } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const readers = ref([])
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
  name: '',
  gender: '',
  age: null,
  phone: ''
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }]
}

const fetchReaders = async () => {
  loading.value = true
  try {
    const { data } = await readerApi.getReaders({
      page: pagination.page,
      per_page: pagination.per_page,
      search: searchKeyword.value
    })
    readers.value = data.readers
    pagination.total = data.total
  } catch (error) {
    ElMessage.error('获取读者列表失败')
  } finally {
    loading.value = false
  }
}

const openAddDialog = () => {
  isEdit.value = false
  Object.assign(form, {
    id: null,
    name: '',
    gender: '',
    age: null,
    phone: ''
  })
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    name: row.name,
    gender: row.gender,
    age: row.age,
    phone: row.phone
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      await readerApi.updateReader(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await readerApi.createReader(form)
      ElMessage.success('添加成功')
    }
    
    dialogVisible.value = false
    fetchReaders()
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
  ElMessageBox.confirm(`确定要删除读者 ${row.name} 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await readerApi.deleteReader(row.id)
      ElMessage.success('删除成功')
      fetchReaders()
    } catch (error) {
      ElMessage.error(error.response?.data?.error || '删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchReaders()
})
</script>

<style scoped>
.readers-page {
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
