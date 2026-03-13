import { io, Socket } from 'socket.io-client'
import { ref, reactive } from 'vue'

class WebSocketClient {
  private socket: Socket | null = null
  public connected = ref(false)
  public users = ref<string[]>([])
  public codeUpdates = ref<string>('')
  public analysisResults = ref<any>(null)

  private callbacks: Map<string, Function[]> = new Map()

  connect(url: string = 'http://localhost:5000') {
    this.socket = io(url, {
      transports: ['websocket', 'polling']
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.connected.value = true
    })

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected')
      this.connected.value = false
    })

    this.socket.on('connected', (data) => {
      console.log('Server message:', data)
    })

    this.socket.on('user_list', (data) => {
      this.users.value = data.users || []
    })

    this.socket.on('code_updated', (data) => {
      this.codeUpdates.value = data.code
      this.emit('codeUpdated', data)
    })

    this.socket.on('cursor_moved', (data) => {
      this.emit('cursorMoved', data)
    })

    this.socket.on('comment_added', (data) => {
      this.emit('commentAdded', data)
    })

    this.socket.on('analysis_updated', (data) => {
      this.analysisResults.value = data
      this.emit('analysisUpdated', data)
    })
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  joinSession(sessionId: string, username: string) {
    this.socket?.emit('join_session', { session_id: sessionId, username })
  }

  leaveSession(sessionId: string, username: string) {
    this.socket?.emit('leave_session', { session_id: sessionId, username })
  }

  sendCodeChange(sessionId: string, code: string, username: string) {
    this.socket?.emit('code_change', { session_id: sessionId, code, username })
  }

  sendCursorPosition(sessionId: string, position: any, username: string) {
    this.socket?.emit('cursor_position', { session_id: sessionId, position, username })
  }

  sendComment(sessionId: string, comment: any) {
    this.socket?.emit('comment_added', { session_id: session_id, comment })
  }

  sendAnalysisUpdate(sessionId: string, result: any) {
    this.socket?.emit('analysis_update', { session_id: sessionId, result })
  }

  on(event: string, callback: Function) {
    if (!this.callbacks.has(event)) {
      this.callbacks.set(event, [])
    }
    this.callbacks.get(event)?.push(callback)
  }

  off(event: string, callback?: Function) {
    if (!callback) {
      this.callbacks.delete(event)
    } else {
      const callbacks = this.callbacks.get(event)
      if (callbacks) {
        const index = callbacks.indexOf(callback)
        if (index > -1) {
          callbacks.splice(index, 1)
        }
      }
    }
  }

  private emit(event: string, data: any) {
    const callbacks = this.callbacks.get(event)
    if (callbacks) {
      callbacks.forEach(cb => cb(data))
    }
  }
}

export const websocketClient = new WebSocketClient()

export function useWebSocket() {
  return websocketClient
}
