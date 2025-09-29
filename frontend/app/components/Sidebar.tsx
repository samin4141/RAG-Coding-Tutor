'use client'

import { useState, useEffect } from 'react'
import { ChartBarIcon, DocumentTextIcon, CpuChipIcon } from '@heroicons/react/24/outline'

interface SidebarProps {
  activePanel: string
}

interface Stats {
  total_documents: number
  total_chunks: number
  total_vectors: number
  total_problems: number
  total_attempts: number
  success_rate: number
}

export default function Sidebar({ activePanel }: SidebarProps) {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [activePanel])

  const fetchStats = async () => {
    try {
      setLoading(true)
      
      // Get different stats depending on what tab we're on
      if (activePanel === 'chat' || activePanel === 'upload') {
        const response = await fetch('/api/ingest/status')
        const ingestStats = await response.json()
        
        const searchResponse = await fetch('/api/search/stats')
        const searchStats = await searchResponse.json()
        
        setStats({
          total_documents: ingestStats.total_documents,
          total_chunks: ingestStats.total_chunks,
          total_vectors: searchStats.vector_store.total_vectors,
          total_problems: 0,
          total_attempts: 0,
          success_rate: 0
        })
      } else if (activePanel === 'practice') {
        const response = await fetch('/api/practice/stats')
        const practiceStats = await response.json()
        
        setStats({
          total_documents: 0,
          total_chunks: 0,
          total_vectors: 0,
          total_problems: practiceStats.total_problems,
          total_attempts: practiceStats.total_attempts,
          success_rate: practiceStats.success_rate
        })
      }
    } catch (error) {
      console.error('Could not load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const renderChatStats = () => (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-gray-700 flex items-center">
        <DocumentTextIcon className="w-4 h-4 mr-2" />
        Knowledge Base
      </h3>
      
      <div className="space-y-3">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Documents</span>
          <span className="font-medium">{stats?.total_documents || 0}</span>
        </div>
        
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Chunks</span>
          <span className="font-medium">{stats?.total_chunks || 0}</span>
        </div>
        
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Vectors</span>
          <span className="font-medium">{stats?.total_vectors || 0}</span>
        </div>
      </div>
      
      {stats?.total_documents === 0 && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-xs text-yellow-700">
            📚 Upload some notes first to start chatting with your knowledge base!
          </p>
        </div>
      )}
    </div>
  )

  const renderPracticeStats = () => (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-gray-700 flex items-center">
        <ChartBarIcon className="w-4 h-4 mr-2" />
        Practice Stats
      </h3>
      
      <div className="space-y-3">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Problems</span>
          <span className="font-medium">{stats?.total_problems || 0}</span>
        </div>
        
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Attempts</span>
          <span className="font-medium">{stats?.total_attempts || 0}</span>
        </div>
        
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Success Rate</span>
          <span className="font-medium">
            {stats?.success_rate ? `${(stats.success_rate * 100).toFixed(1)}%` : '0%'}
          </span>
        </div>
      </div>
      
      {stats?.total_problems === 0 && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-xs text-blue-700">
            🚀 Practice problems will show up automatically when you start coding!
          </p>
        </div>
      )}
    </div>
  )

  const renderUploadStats = () => renderChatStats()

  return (
    <div className="px-6 pb-6">
      <div className="border-t border-gray-200 pt-6">
        {loading ? (
          <div className="animate-pulse space-y-3">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            <div className="h-3 bg-gray-200 rounded w-2/3"></div>
          </div>
        ) : (
          <>
            {activePanel === 'chat' && renderChatStats()}
            {activePanel === 'practice' && renderPracticeStats()}
            {activePanel === 'upload' && renderUploadStats()}
          </>
        )}
      </div>
      
      {/* System Status */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <h3 className="text-sm font-semibold text-gray-700 flex items-center mb-3">
          <CpuChipIcon className="w-4 h-4 mr-2" />
          System Status
        </h3>
        
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-600">LLM</span>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
              <span className="text-green-600">Local</span>
            </div>
          </div>
          
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-600">Vector DB</span>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
              <span className="text-green-600">FAISS</span>
            </div>
          </div>
          
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-600">Database</span>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
              <span className="text-green-600">SQLite</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
