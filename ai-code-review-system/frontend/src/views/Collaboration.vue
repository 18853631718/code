<template>
  <div class="collaboration-page">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="session-panel">
          <template #header>
            <div class="panel-header">
              <span>Review Sessions</span>
              <el-button type="primary" size="small" @click="showCreateDialog = true">
                New Session
              </el-button>
            </div>
          </template>
          <el-list>
            <el-list-item
              v-for="session in sessions"
              :key="session.id"
              :class="{ active: currentSession?.id === session.id }"
              @click="selectSession(session)"
            >
              <div class="session-item">
                <div class="session-name">{{ session.name }}</div>
                <div class="session-info">
                  <el-tag size="small">{{ session.status }}</el-tag>
                  <span class="participant-count">
                    {{ session.participants?.length || 0 }} participants
                  </span>
                </div>
              </div>
            </el-list-item>
          </el-list>
        </el-card>

        <el-card class="users-panel">
          <template #header>
            <span>Online Users</span>
          </template>
          <el-tag
            v-for="user in onlineUsers"
            :key="user"
            class="user-tag"
          >
            {{ user }}
          </el-tag>
          <div v-if="onlineUsers.length === 0" class="no-users">
            No users online
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card v-if="currentSession" class="editor-panel">
          <template #header>
            <div class="panel-header">
              <span>{{ currentSession.name }}</span>
              <el-button type="success" size="small" @click="startAnalysis">
                Run Analysis
              </el-button>
            </div>
          </template>
          <CodeEditor
            v-model="sessionCode"
            :language="currentLanguage"
            @analyze="handleAnalyze"
          />
        </el-card>

        <el-card v-else class="empty-panel">
          <el-empty description="Select a session to start collaborating" />
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showCreateDialog" title="Create New Session" width="400px">
      <el-form :model="newSession" label-width="80px">
        <el-form-item label="Session Name">
          <el-input v-model="newSession.name" placeholder="Enter session name" />
        </el-form-item>
        <el-form-item label="Your Name">
          <el-input v-model="newSession.owner" placeholder="Enter your name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="createSession">Create</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { collaborationApi } from '@/utils/api'
import { useWebSocket } from '@/websocket/client'
import CodeEditor from '@/components/CodeEditor.vue'
import { ElMessage } from 'element-plus'

const ws = useWebSocket()

const sessions = ref<any[]>([])
const currentSession = ref<any>(null)
const onlineUsers = ref<string[]>([])
const sessionCode = ref('')
const currentLanguage = ref('python')
const showCreateDialog = ref(false)
const newSession = ref({
  name: '',
  owner: ''
})

const loadSessions = async () => {
  try {
    const data = await collaborationApi.getSessions()
    sessions.value = data || []
  } catch (error) {
    console.error('Failed to load sessions:', error)
  }
}

const selectSession = async (session: any) => {
  currentSession.value = session
  ws.joinSession(session.id.toString(), newSession.value.owner || 'User')
  
  try {
    const sessionData = await collaborationApi.getSession(session.id)
    sessionCode.value = sessionData.code_content || ''
  } catch (error) {
    console.error('Failed to load session details:', error)
  }
}

const createSession = async () => {
  try {
    const session = await collaborationApi.createSession(
      newSession.value.name,
      newSession.value.owner
    )
    sessions.value.push(session)
    showCreateDialog.value = false
    newSession.value = { name: '', owner: '' }
    ElMessage.success('Session created successfully')
    loadSessions()
  } catch (error) {
    ElMessage.error('Failed to create session')
  }
}

const startAnalysis = () => {
  ws.sendAnalysisUpdate(currentSession.value.id.toString(), {
    code: sessionCode.value,
    language: currentLanguage.value
  })
}

const handleAnalyze = async (code: string) => {
  console.log('Analyzing code:', code)
}

onMounted(() => {
  ws.connect()
  loadSessions()
  
  ws.on('userList', (data: any) => {
    onlineUsers.value = data.users || []
  })
  
  ws.on('codeUpdated', (data: any) => {
    sessionCode.value = data.code
  })
})

onUnmounted(() => {
  ws.disconnect()
})
</script>

<style scoped>
.collaboration-page {
  padding: 20px;
}

.session-panel,
.users-panel {
  margin-bottom: 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-item {
  width: 100%;
  cursor: pointer;
}

.session-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.session-info {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #909399;
}

.active {
  background-color: #ecf5ff;
}

.user-tag {
  margin: 5px;
}

.no-users {
  color: #909399;
  text-align: center;
  padding: 20px;
}

.editor-panel {
  min-height: 600px;
}

.empty-panel {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
