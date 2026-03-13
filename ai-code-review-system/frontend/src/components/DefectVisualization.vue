<template>
  <div class="defect-visualization">
    <div ref="chartContainer" class="chart-container"></div>
    <div class="legend">
      <div class="legend-item">
        <span class="legend-color high"></span>
        <span>High Severity</span>
      </div>
      <div class="legend-item">
        <span class="legend-color medium"></span>
        <span>Medium Severity</span>
      </div>
      <div class="legend-item">
        <span class="legend-color low"></span>
        <span>Low Severity</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'

interface DefectData {
  defectType: string
  line: number
  severity: string
  confidence: number
}

const props = defineProps<{
  defects: DefectData[]
}>()

const chartContainer = ref<HTMLElement | null>(null)

const severityColors: Record<string, string> = {
  high: '#f56c6c',
  medium: '#e6a23c',
  low: '#909399',
  none: '#67c23a'
}

const drawChart = () => {
  if (!chartContainer.value || props.defects.length === 0) return
  
  d3.select(chartContainer.value).selectAll('*').remove()
  
  const margin = { top: 20, right: 30, bottom: 40, left: 60 }
  const width = chartContainer.value.clientWidth - margin.left - margin.right
  const height = 300 - margin.top - margin.bottom
  
  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)
  
  const severityCounts = d3.rollup(
    props.defects,
    v => v.length,
    d => d.severity
  )
  
  const data = Array.from(severityCounts, ([severity, count]) => ({
    severity,
    count
  }))
  
  const x = d3.scaleBand()
    .domain(data.map(d => d.severity))
    .range([0, width])
    .padding(0.3)
  
  const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.count) || 0])
    .nice()
    .range([height, 0])
  
  svg.append('g')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x))
    .selectAll('text')
    .style('font-size', '12px')
  
  svg.append('g')
    .call(d3.axisLeft(y))
    .selectAll('text')
    .style('font-size', '12px')
  
  svg.selectAll('.bar')
    .data(data)
    .join('rect')
    .attr('class', 'bar')
    .attr('x', d => x(d.severity) || 0)
    .attr('y', d => y(d.count))
    .attr('width', x.bandwidth())
    .attr('height', d => height - y(d.count))
    .attr('fill', d => severityColors[d.severity] || '#409eff')
    .attr('rx', 4)
  
  svg.selectAll('.label')
    .data(data)
    .join('text')
    .attr('class', 'label')
    .attr('x', d => (x(d.severity) || 0) + x.bandwidth() / 2)
    .attr('y', d => y(d.count) - 5)
    .attr('text-anchor', 'middle')
    .style('font-size', '14px')
    .style('font-weight', 'bold')
    .style('fill', '#333')
    .text(d => d.count)
}

onMounted(() => {
  drawChart()
})

watch(() => props.defects, () => {
  drawChart()
}, { deep: true })
</script>

<style scoped>
.defect-visualization {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
}

.chart-container {
  width: 100%;
  min-height: 300px;
}

.legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.legend-color.high {
  background: #f56c6c;
}

.legend-color.medium {
  background: #e6a23c;
}

.legend-color.low {
  background: #909399;
}
</style>
