'use client'

import { useState } from 'react'
import Sidebar from './components/Sidebar'
import ChatPanel from './components/ChatPanel'
import PracticePanel from './components/PracticePanel'
import UploadPanel from './components/UploadPanel'
import { BookOpenIcon, CodeBracketIcon, ArrowUpTrayIcon } from '@heroicons/react/24/outline'

type ActivePanel = 'chat' | 'practice' | 'upload'

export default function Home() {
  const [activePanel, setActivePanel] = useState<ActivePanel>('chat')

  const renderActivePanel = () => {
    switch (activePanel) {
      case 'chat':
        return <ChatPanel />
      case 'practice':
        return <PracticePanel />
      case 'upload':
        return <UploadPanel />
      default:
        return <ChatPanel />
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="p-6">
          <h1 className="text-xl font-bold text-gray-900 mb-8">
            🎯 Coding Tutor
          </h1>
          
          <nav className="space-y-2">
            <button
              onClick={() => setActivePanel('chat')}
              className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                activePanel === 'chat'
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <BookOpenIcon className="w-5 h-5" />
              <span>Chat & Learn</span>
            </button>
            
            <button
              onClick={() => setActivePanel('practice')}
              className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                activePanel === 'practice'
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <CodeBracketIcon className="w-5 h-5" />
              <span>Practice Mode</span>
            </button>
            
            <button
              onClick={() => setActivePanel('upload')}
              className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                activePanel === 'upload'
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <ArrowUpTrayIcon className="w-5 h-5" />
              <span>Upload Notes</span>
            </button>
          </nav>
        </div>
        
        <Sidebar activePanel={activePanel} />
      </div>

      {/* Main Content */}
      <div className="main-content">
        {renderActivePanel()}
      </div>
    </div>
  )
}
