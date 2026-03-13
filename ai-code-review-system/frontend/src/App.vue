<template>
  <div id="app">
    <el-container class="app-container">
      <el-header class="app-header">
        <div class="header-left">
          <h1>AI Code Review System</h1>
        </div>
        <div class="header-right">
          <el-button type="primary" @click="showUploadDialog = true">
            <el-icon><Upload /></el-icon>
            Upload Code
          </el-button>
        </div>
      </el-header>
      <el-container>
        <el-aside width="200px" class="app-sidebar">
          <el-menu
            :default-active="currentRoute"
            router
            class="sidebar-menu"
          >
            <el-menu-item index="/">
              <el-icon><Document /></el-icon>
              <span>Code Editor</span>
            </el-menu-item>
            <el-menu-item index="/analysis">
              <el-icon><DataAnalysis /></el-icon>
              <span>Analysis</span>
            </el-menu-item>
            <el-menu-item index="/collaboration">
              <el-icon><Connection /></el-icon>
              <span>Collaboration</span>
            </el-menu-item>
            <el-menu-item index="/statistics">
              <el-icon><PieChart /></el-icon>
              <span>Statistics</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main class="app-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>

    <el-dialog v-model="showUploadDialog" title="Upload Code File" width="500px">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        drag
      >
        <el-icon class="el-icon--upload"><Upload /></el-icon>
        <div class="el-upload__text">
          Drop file here or <em>click to upload</em>
        </div>
      </el-upload>
      <el-select v-model="selectedLanguage" placeholder="Select Language" class="language-select">
        <el-option label="Python" value="python" />
        <el-option label="JavaScript" value="javascript" />
        <el-option label="Java" value="java" />
        <el-option label="C/C++" value="cpp" />
        <el-option label="Go" value="go" />
        <el-option label="Rust" value="rust" />
      </el-select>
      <template #footer>
        <el-button @click="showUploadDialog = false">Cancel</el-button>
        <el-button type="primary" @click="handleUpload">Upload</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { Upload, Document, DataAnalysis, Connection, PieChart } from '@element-plus/icons-vue'

const route = useRoute()
const currentRoute = computed(() => route.path)

const showUploadDialog = ref(false)
const selectedLanguage = ref('python')
const uploadRef = ref()
const currentFile = ref<File | null>(null)

const handleFileChange = (file: any) => {
  currentFile.value = file.raw
}

const handleUpload = async () => {
  if (!currentFile.value) {
    ElMessage.warning('Please select a file')
    return
  }

  const formData = new FormData()
  formData.append('file', currentFile.value)
  formData.append('language', selectedLanguage.value)

  try {
    const response = await axios.post('/api/code/upload', formData)
    ElMessage.success('File uploaded successfully')
    showUploadDialog.value = false
  } catch (error) {
    ElMessage.error('Upload failed')
  }
}
</script>

<style scoped>
.app-container {
  height: 100vh;
}

.app-header {
  background: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left h1 {
  margin: 0;
  font-size: 20px;
}

.app-sidebar {
  background: #f5f7fa;
}

.sidebar-menu {
  border-right: none;
  background: transparent;
}

.app-main {
  background: #fff;
  overflow-y: auto;
  padding: 0;
}

.language-select {
  width: 100%;
  margin-top: 20px;
}
</style>
