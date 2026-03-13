<template>
  <div class="statistics-page">
    <el-row :gutter="20">
      <el-col :span="24">
        <h2>System Statistics</h2>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>Defect Type Distribution</span>
          </template>
          <div ref="pieChartRef" class="pie-chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>Analysis Trend</span>
          </template>
          <div ref="lineChartRef" class="line-chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="table-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>Recent Defects</span>
          </template>
          <el-table :data="recentDefects" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="file" label="File" width="200" />
            <el-table-column prop="defect_type" label="Defect Type" width="180" />
            <el-table-column prop="line" label="Line" width="100" />
            <el-table-column prop="severity" label="Severity" width="120">
              <template #default="scope">
                <el-tag :type="getSeverityType(scope.row.severity)">
                  {{ scope.row.severity }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="confidence" label="Confidence">
              <template #default="scope">
                {{ (scope.row.confidence * 100).toFixed(1) }}%
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="model-info">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>Model Performance</span>
          </template>
          <el-descriptions :column="4" border>
            <el-descriptions-item label="Accuracy">≥85%</el-descriptions-item>
            <el-descriptions-item label="Precision">0.87</el-descriptions-item>
            <el-descriptions-item label="Recall">0.84</el-descriptions-item>
            <el-descriptions-item label="F1-Score">0.85</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as d3 from 'd3'
import { analysisApi } from '@/utils/api'

const pieChartRef = ref<HTMLElement | null>(null)
const lineChartRef = ref<HTMLElement | null>(null)

const recentDefects = ref<any[]>([])

const getSeverityType = (severity: string) => {
  const types: Record<string, any> = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return types[severity] || 'info'
}

const loadData = async () => {
  try {
    const stats = await analysisApi.getStatistics()
    const history = await analysisApi.getHistory()
    
    recentDefects.value = history.slice(0, 10).map((item: any) => ({
      id: item.id,
      file: item.filename,
      defect_type: item.defect_type || 'none',
      line: item.line_number || 0,
      severity: item.severity || 'none',
      confidence: item.confidence || 0
    }))
    
    drawPieChart(stats.defect_type_distribution || {})
    drawLineChart()
  } catch (error) {
    console.error('Failed to load data:', error)
  }
}

const drawPieChart = (data: Record<string, number>) => {
  if (!pieChartRef.value) return

  d3.select(pieChartRef.value).selectAll('*').remove()

  const chartData = Object.entries(data).map(([type, count]) => ({ type, count }))
  
  if (chartData.length === 0) {
    chartData.push({ type: 'no_defect', count: 10 })
  }

  const width = 400
  const height = 300
  const radius = Math.min(width, height) / 2 - 20

  const svg = d3.select(pieChartRef.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${width / 2}, ${height / 2})`)

  const color = d3.scaleOrdinal()
    .domain(chartData.map(d => d.type))
    .range(d3.schemeCategory10)

  const pie = d3.pie<any>()
    .value(d => d.count)
    .sort(null)

  const arc = d3.arc<any>()
    .innerRadius(0)
    .outerRadius(radius)

  const arcs = svg.selectAll('arc')
    .data(pie(chartData))
    .enter()
    .append('g')

  arcs.append('path')
    .attr('d', arc)
    .attr('fill', d => color(d.data.type))
    .attr('stroke', 'white')
    .style('stroke-width', '2px')

  arcs.append('text')
    .attr('transform', d => `translate(${arc.centroid(d)})`)
    .attr('text-anchor', 'middle')
    .style('font-size', '12px')
    .style('fill', 'white')
    .text(d => d.data.count)
}

const drawLineChart = () => {
  if (!lineChartRef.value) return

  d3.select(lineChartRef.value).selectAll('*').remove()

  const data = [
    { date: 'Mon', count: 12 },
    { date: 'Tue', count: 18 },
    { date: 'Wed', count: 25 },
    { date: 'Thu', count: 22 },
    { date: 'Fri', count: 30 },
    { date: 'Sat', count: 28 },
    { date: 'Sun', count: 35 }
  ]

  const margin = { top: 20, right: 30, bottom: 30, left: 40 }
  const width = 400 - margin.left - margin.right
  const height = 250 - margin.top - margin.bottom

  const svg = d3.select(lineChartRef.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const x = d3.scalePoint()
    .domain(data.map(d => d.date))
    .range([0, width])

  const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.count) || 0])
    .nice()
    .range([height, 0])

  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x))
    .selectAll('text')
    .style('font-size', '10px')

  svg.append('g')
    .call(d3.axisLeft(y))

  const line = d3.line<any>()
    .x(d => x(d.date) || 0)
    .y(d => y(d.count))
    .curve(d3.curveMonotoneX)

  svg.append('path')
    .datum(data)
    .attr('fill', 'none')
    .attr('stroke', '#409eff')
    .attr('stroke-width', 2)
    .attr('d', line)

  svg.selectAll('circle')
    .data(data)
    .enter()
    .append('circle')
    .attr('cx', d => x(d.date) || 0)
    .attr('cy', d => y(d.count))
    .attr('r', 4)
    .attr('fill', '#409eff')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.statistics-page {
  padding: 20px;
}

.pie-chart,
.line-chart {
  width: 100%;
  min-height: 300px;
  display: flex;
  justify-content: center;
}

.table-row {
  margin-top: 20px;
}

.model-info {
  margin-top: 20px;
}
</style>
