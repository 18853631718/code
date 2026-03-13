<template>
  <div class="code-editor-page">
    <div class="editor-section">
      <CodeEditor
        ref="editorRef"
        v-model="codeContent"
        :language="currentLanguage"
        @analyze="handleAnalyze"
        @languageChange="handleLanguageChange"
      />
    </div>
    <div class="result-section">
      <el-card v-if="analysisResult" class="result-card">
        <template #header>
          <div class="result-header">
            <span>Analysis Result</span>
            <el-tag :type="getSeverityType(analysisResult.severity)">
              {{ analysisResult.severity?.toUpperCase() || 'NONE' }}
            </el-tag>
          </div>
        </template>
        <div class="result-content">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Defect Type">
              {{ analysisResult.defect_type || 'None' }}
            </el-descriptions-item>
            <el-descriptions-item label="Confidence">
              {{ analysisResult.confidence ? (analysisResult.confidence * 100).toFixed(2) + '%' : 'N/A' }}
            </el-descriptions-item>
            <el-descriptions-item label="Line Number">
              {{ analysisResult.line_number || 'N/A' }}
            </el-descriptions-item>
            <el-descriptions-item label="Severity">
              {{ analysisResult.severity || 'medium' }}
            </el-descriptions-item>
          </el-descriptions>
          <div v-if="analysisResult.suggestion" class="suggestion">
            <h4>Suggestion:</h4>
            <p>{{ analysisResult.suggestion }}</p>
          </div>
          <div v-if="analysisResult.issues && analysisResult.issues.length > 0" class="issues">
            <h4>Issues Found:</h4>
            <el-alert
              v-for="(issue, index) in analysisResult.issues"
              :key="index"
              :title="issue.message"
              :type="getIssueType(issue.severity)"
              :closable="false"
              show-icon
            >
              <template #title>
                <span>Line {{ issue.line }}: {{ issue.message }}</span>
              </template>
            </el-alert>
          </div>
          <div v-if="analysisResult.features" class="metrics">
            <h4>Code Metrics:</h4>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="Line Count">
                {{ analysisResult.features.line_count }}
              </el-descriptions-item>
              <el-descriptions-item label="Function Count">
                {{ analysisResult.features.function_count }}
              </el-descriptions-item>
              <el-descriptions-item label="Class Count">
                {{ analysisResult.features.class_count }}
              </el-descriptions-item>
              <el-descriptions-item label="Complexity">
                {{ analysisResult.features.complexity }}
              </el-descriptions-item>
              <el-descriptions-item label="Cyclomatic Complexity">
                {{ analysisResult.features.cyclomatic_complexity }}
              </el-descriptions-item>
              <el-descriptions-item label="Maintainability Index">
                {{ analysisResult.features.maintainability_index }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </el-card>
      <el-empty v-else description="Click 'Analyze Code' to analyze your code" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import CodeEditor from '@/components/CodeEditor.vue'
import { analyzeApi } from '@/utils/api'

const editorRef = ref()

// 默认代码 - 按语言分类
const defaultCodeByLanguage = {
  python: `# Example Python code
def hello_world():
    print("Hello, World!")
    return None

if __name__ == "__main__":
    hello_world()
`,
  javascript: `// Example JavaScript code
function helloWorld() {
    console.log("Hello, World!");
    return null;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = helloWorld;
} else {
    helloWorld();
}
`,
  java: `// Example Java code
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
    
    public static String helloWorld() {
        return "Hello, World!";
    }
}
`,
  cpp: `// Example C++ code
#include <iostream>

std::string helloWorld() {
    return "Hello, World!";
}

int main() {
    std::cout << helloWorld() << std::endl;
    return 0;
}
`,
  go: `// Example Go code
package main

import "fmt"

func helloWorld() string {
    return "Hello, World!"
}

func main() {
    fmt.Println(helloWorld())
}
`,
  rust: `// Example Rust code
fn hello_world() -> &'static str {
    "Hello, World!"
}

fn main() {
    println!("{}", hello_world());
}
`
};

const currentLanguage = ref('python')
const codeContent = ref(defaultCodeByLanguage[currentLanguage.value])
const analysisResult = ref<any>(null)

// 监听语言变化，更新默认代码
watch(currentLanguage, (newLang) => {
  codeContent.value = defaultCodeByLanguage[newLang as keyof typeof defaultCodeByLanguage] || defaultCodeByLanguage.python
})

const getIssueType = (severity?: string) => {
  const types: Record<string, any> = {
    high: 'error',
    warning: 'warning',
    medium: 'warning',
    low: 'info',
    none: 'success'
  }
  return types[severity || 'none'] || 'info'
}

const getSeverityType = (severity?: string) => {
  const types: Record<string, any> = {
    high: 'danger',
    medium: 'warning',
    low: 'info',
    none: 'success'
  }
  return types[severity || 'none'] || 'info'
}

const handleAnalyze = async (code: string) => {
  try {
    console.log('Analyzing code:', code)
    const result = await analyzeApi.analyze(code, currentLanguage.value)
    console.log('Analysis result:', result)
    
    analysisResult.value = result
    
    if (result && result.line_number) {
      editorRef.value?.setMarkers([{
        line: result.line_number,
        message: result.suggestion || result.defect_type,
        severity: result.severity || 'medium'
      }])
    }
  } catch (error) {
    console.error('Analysis failed:', error)
  }
}

const handleLanguageChange = (lang: string) => {
  currentLanguage.value = lang
  const newCode = defaultCodeByLanguage[lang as keyof typeof defaultCodeByLanguage]
  if (newCode) {
    codeContent.value = newCode
  } else {
    codeContent.value = defaultCodeByLanguage.python
  }
  console.log('Language changed to:', lang, 'Code updated:', codeContent.value)
}
</script>

<style scoped>
.code-editor-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  padding: 20px;
  overflow-y: auto;
  gap: 20px;
}

.editor-section {
  flex: 1;
  min-height: 300px;
  overflow: hidden;
}

.result-section {
  flex-shrink: 0;
}

.result-card {
  width: 100%;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-content {
  padding: 10px 0;
}

.suggestion {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.suggestion h4 {
  margin-bottom: 10px;
  color: #409eff;
}

.metrics {
  margin-top: 20px;
}

.metrics h4 {
  margin-bottom: 10px;
  color: #409eff;
}
</style>
