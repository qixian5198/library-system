<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>📚 图书馆管理系统</h2>
        </div>
      </template>
      
      <!-- 登录表单 -->
      <el-form v-if="isLogin" :model="loginForm" :rules="loginRules" ref="loginFormRef" label-width="0">
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="用户名"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            size="large"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            :loading="loading"
            style="width: 100%"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
        
        <div class="switch-mode">
          <span>还没有账号？</span>
          <el-button type="primary" link @click="switchMode">立即注册</el-button>
        </div>
      </el-form>
      
      <!-- 注册表单 -->
      <el-form v-else :model="registerForm" :rules="registerRules" ref="registerFormRef" label-width="0">
        <el-form-item prop="username">
          <el-input 
            v-model="registerForm.username" 
            placeholder="用户名"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="registerForm.password" 
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password"
            placeholder="确认密码"
            prefix-icon="Lock"
            size="large"
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        
        <el-form-item prop="role">
          <el-select v-model="registerForm.role" placeholder="选择身份" size="large" style="width: 100%">
            <el-option label="读者" value="reader" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            :loading="loading"
            style="width: 100%"
            @click="handleRegister"
          >
            注册
          </el-button>
        </el-form-item>
        
        <div class="switch-mode">
          <span>已有账号？</span>
          <el-button type="primary" link @click="switchMode">立即登录</el-button>
        </div>
      </el-form>
      
      <div class="tips" v-if="isLogin">
        <p>默认账号: admin / admin123</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import { api } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isLogin = ref(true)
const loading = ref(false)
const loginFormRef = ref()
const registerFormRef = ref()

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  role: 'reader'
})

// 验证确认密码
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const registerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const switchMode = () => {
  isLogin.value = !isLogin.value
}

const handleLogin = async () => {
  try {
    await loginFormRef.value.validate()
    loading.value = true
    
    await authStore.login(loginForm.username, loginForm.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '登录失败')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  try {
    await registerFormRef.value.validate()
    loading.value = true
    
    await api.post('/auth/register', {
      username: registerForm.username,
      password: registerForm.password,
      role: registerForm.role
    })
    
    ElMessage.success('注册成功，请登录')
    isLogin.value = true
    loginForm.username = registerForm.username
    loginForm.password = ''
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.card-header h2 {
  text-align: center;
  color: #333;
  margin: 0;
}

.switch-mode {
  text-align: center;
  margin-top: 16px;
  color: #666;
}

.switch-mode span {
  margin-right: 8px;
}

.tips {
  text-align: center;
  color: #999;
  font-size: 12px;
  margin-top: 16px;
}
</style>
