<template>
  <div class="analysis-page">
    <el-row :gutter="20">
      <el-col :span="24">
        <h2>Code Analysis</h2>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#409eff"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.total_files || 0 }}</div>
              <div class="stat-label">Total Files</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#e6a23c"><DataAnalysis /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.total_analysis || 0 }}</div>
              <div class="stat-label">Total Analysis</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#f56c6c"><Warning /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.severity_distribution?.high || 0 }}</div>
              <div class="stat-label">High Severity</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#67c23a"><Success /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.accuracy || 'N/A' }}</div>
              <div class="stat-label">Accuracy</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <span>Defect Distribution</span>
          </template>
          <DefectVisualization :defects="recentDefects" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="history-card">
          <template #header>
            <span>Recent Analysis</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="item in analysisHistory"
              :key="item.id"
              :timestamp="item.created_at"
              placement="top"
            >
              <el-card>
                <h4>{{ item.filename }}</h4>
                <p>{{ item.defect_type || 'No defect' }}</p>
                <el-tag :type="getSeverityType(item.severity)" size="small">
                  {{ item.severity }}
                </el-tag>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { analysisApi } from '@/utils/api'
import DefectVisualization from '@/components/DefectVisualization.vue'
import { ElMessage } from 'element-plus'

const statistics = ref<any>({
  total_files: 0,
  total_analysis: 0,
  accuracy: '≥85%',
  severity_distribution: {},
  defect_type_distribution: {}
})

const recentDefects = ref<any[]>([])
const analysisHistory = ref<any[]>([])

const getSeverityType = (severity?: string) => {
  const types: Record<string, any> = {
    high: 'danger',
    medium: 'warning',
    low: 'info',
    none: 'success'
  }
  return types[severity || 'none'] || 'info'
}

const loadStatistics = async () => {
  try {
    const data = await analysisApi.getStatistics()
    statistics.value = data
    
    if (data.defect_type_distribution) {
      recentDefects.value = Object.entries(data.defect_type_distribution).map(([defectType, count]: [string, any]) => ({
        defectType,
        line: 1,
        severity: getSeverityFromType(defectType),
        confidence: 0.85
      }))
    }
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

const loadHistory = async () => {
  try {
    const data = await analysisApi.getHistory()
    analysisHistory.value = data || []
  } catch (error) {
    console.error('Failed to load history:', error)
  }
}

const getSeverityFromType = (defectType: string) => {
  const types: Record<string, string> = {
    null_pointer: 'high',
    buffer_overflow: 'high',
    memory_leak: 'medium',
    sql_injection: 'high',
    race_condition: 'medium',
    no_defect: 'none'
  }
  return types[defectType] || 'medium'
}

onMounted(() => {
  loadStatistics()
  loadHistory()
})
</script>

<style scoped>
.analysis-page {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  font-size: 36px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.chart-card {
  margin-bottom: 20px;
}

.history-card {
  height: 400px;
  overflow-y: auto;
}
</style>
