<template>
  <div class="code-editor-container">
    <div class="editor-toolbar">
      <el-select v-model="localLanguage" placeholder="Language" @change="handleLanguageChange" class="language-selector">
        <el-option label="Python" value="python" />
        <el-option label="JavaScript" value="javascript" />
        <el-option label="Java" value="java" />
        <el-option label="C/C++" value="cpp" />
        <el-option label="Go" value="go" />
        <el-option label="Rust" value="rust" />
      </el-select>
      <el-button type="primary" @click="handleAnalyze" :loading="analyzing">
        <el-icon><Search /></el-icon>
        Analyze Code
      </el-button>
      <el-button @click="handleFormat">
        <el-icon><Document /></el-icon>
        Format
      </el-button>
    </div>
    <div ref="editorContainer" class="editor-wrapper"></div>
    <div v-if="defectMarkers.length > 0" class="defect-panel">
      <h4>Defects Detected</h4>
      <el-tag
        v-for="(defect, index) in defectMarkers"
        :key="index"
        :type="getSeverityType(defect.severity)"
        class="defect-tag"
        @click="jumpToLine(defect.line)"
      >
        Line {{ defect.line }}: {{ defect.message }}
      </el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import * as monaco from 'monaco-editor'
import { ElMessage } from 'element-plus'
import { Search, Document } from '@element-plus/icons-vue'

interface DefectMarker {
  line: number
  message: string
  severity: string
}

const props = defineProps<{
  modelValue?: string
  language?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'analyze', code: string): void
  (e: 'languageChange', language: string): void
}>()

const editorContainer = ref<HTMLElement | null>(null)
const analyzing = ref(false)
const defectMarkers = ref<DefectMarker[]>([])
let editor: monaco.editor.IStandaloneCodeEditor | null = null

// 本地language状态
const localLanguage = ref(props.language || 'python')

const languageMap: Record<string, string> = {
  python: 'python',
  javascript: 'javascript',
  java: 'java',
  cpp: 'cpp',
  go: 'go',
  rust: 'rust'
}

// 监听props.language的变化，同步语言切换并更新编辑器
watch(() => props.language, (newLang) => {
  if (newLang && newLang !== localLanguage.value) {
    localLanguage.value = newLang
    if (editor) {
      const model = editor.getModel()
      if (model) {
        monaco.editor.setModelLanguage(model, languageMap[newLang] || 'plaintext')
      }
    }
    // 触发languageChange事件，让父组件更新代码
    emit('languageChange', newLang)
  }
})

// 监听props.modelValue的变化，更新编辑器内容
watch(() => props.modelValue, (newValue) => {
  if (editor && newValue !== undefined && newValue !== editor.getValue()) {
    editor.setValue(newValue)
  }
})

onMounted(() => {
  if (editorContainer.value) {
    editor = monaco.editor.create(editorContainer.value, {
      value: props.modelValue || '',
      language: languageMap[localLanguage.value] || 'plaintext',
      theme: 'vs-dark',
      automaticLayout: true,
      minimap: { enabled: true },
      fontSize: 14,
      lineNumbers: 'on',
      renderWhitespace: 'selection',
      tabSize: 4,
      insertSpaces: true,
      wordWrap: 'on',
      scrollBeyondLastLine: false,
      folding: true,
      glyphMargin: true,
      fixedOverflowWidgets: true
    })

    editor.onDidChangeModelContent(() => {
      const value = editor?.getValue() || ''
      emit('update:modelValue', value)
    })
  }
})

onBeforeUnmount(() => {
  editor?.dispose()
})

const handleLanguageChange = (lang: string) => {
  localLanguage.value = lang
  if (editor) {
    const model = editor.getModel()
    if (model) {
      const newLang = languageMap[lang] || 'plaintext'
      monaco.editor.setModelLanguage(model, newLang)
    }
  }
  emit('languageChange', lang)
}

const handleAnalyze = async () => {
  if (!editor) return
  
  analyzing.value = true
  const code = editor.getValue()
  
  try {
    emit('analyze', code)
  } catch (error) {
    ElMessage.error('Analysis failed')
  } finally {
    analyzing.value = false
  }
}

const handleFormat = () => {
  editor?.getAction('editor.action.formatDocument')?.run()
}

const jumpToLine = (line: number) => {
  editor?.revealLineInCenter(line)
  editor?.setPosition({ lineNumber: line, column: 1 })
}

const getSeverityType = (severity: string) => {
  const types: Record<string, any> = {
    high: 'danger',
    medium: 'warning',
    low: 'info',
    none: 'success'
  }
  return types[severity] || 'info'
}

const setValue = (code: string) => {
  editor?.setValue(code)
}

const setMarkers = (markers: DefectMarker[]) => {
  defectMarkers.value = markers
  
  if (!editor) return
  
  const model = editor.getModel()
  if (!model) return
  
  const monacoMarkers: monaco.editor.IMarkerData[] = markers.map(marker => ({
    severity: marker.severity === 'high' 
      ? monaco.MarkerSeverity.Error 
      : marker.severity === 'medium'
        ? monaco.MarkerSeverity.Warning
        : monaco.MarkerSeverity.Info,
    message: marker.message,
    startLineNumber: marker.line,
    startColumn: 1,
    endLineNumber: marker.line,
    endColumn: 1000
  }))
  
  monaco.editor.setModelMarkers(model, 'defect-detection', monacoMarkers)
}

defineExpose({
  setValue,
  setMarkers
})
</script>

<style scoped>
.code-editor-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-toolbar {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: #1e1e1e;
  border-bottom: 1px solid #333;
}

.language-selector {
  width: 150px;
}

.editor-wrapper {
  flex: 1;
  min-height: 400px;
}

.defect-panel {
  padding: 15px;
  background: #2d2d2d;
  border-top: 1px solid #333;
}

.defect-panel h4 {
  color: #fff;
  margin-bottom: 10px;
}

.defect-tag {
  margin: 5px;
  cursor: pointer;
}
</style>
