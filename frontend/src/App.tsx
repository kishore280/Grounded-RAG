import { ChatPanel } from './components/ChatPanel'
import { UploadPanel } from './components/UploadPanel'
import './App.css'

function App() {
  return (
    <div className="app">
      <h1>Grounded RAG</h1>
      <UploadPanel />
      <ChatPanel />
    </div>
  )
}

export default App
