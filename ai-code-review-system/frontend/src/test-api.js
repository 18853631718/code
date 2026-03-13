import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 30000
})

// 测试统计接口
apiClient.get('/api/analysis/statistics')
  .then(res => {
    console.log('Statistics success:', res.data)
  })
  .catch(err => {
    console.log('Statistics error:', err.message, err.response?.status)
  })
