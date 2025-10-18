'use client'

import { useState, useRef, useEffect } from 'react'
import { PaperAirplaneIcon, DocumentTextIcon } from '@heroicons/react/24/outline'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  sources?: Source[]
  timestamp: Date
}

interface Source {
  title: string
  path: string
  section: string
  score: number
}

export default function ChatPanel() {
  const [chatHistory, setChatHistory] = useState<Message[]>([])
  const [userInput, setUserInput] = useState('')
  const [isThinking, setIsThinking] = useState(false)
  const bottomOfChatRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    bottomOfChatRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [chatHistory])

  const askQuestion = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!userInput.trim() || isThinking) return

    const userQuestion: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: userInput.trim(),
      timestamp: new Date()
    }

    setChatHistory(prev => [...prev, userQuestion])
    setUserInput('')
    setIsThinking(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userQuestion.content,
          stream: false
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const responseData = await response.json()

      const aiAnswer: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: responseData.response,
        sources: responseData.sources,
        timestamp: new Date()
      }

      setChatHistory(prev => [...prev, aiAnswer])
    } catch (error) {
        console.error('Oops, chat broke:', error)
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Hmm, something went wrong. Is the backend actually running?',
        timestamp: new Date()
      }
      setChatHistory(prev => [...prev, errorResponse])
    } finally {
      setIsThinking(false)
    }
  }

  const showMessage = (message: Message) => (
    <div
      key={message.id}
      className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} mb-6`}
    >
      <div
        className={`max-w-3xl ${
          message.type === 'user'
            ? 'bg-primary-600 text-white'
            : 'bg-white border border-gray-200'
        } rounded-lg p-4 shadow-sm`}
      >
        {message.type === 'user' ? (
          <p className="text-white">{message.content}</p>
        ) : (
          <div>
            <div className="markdown-content">
              <ReactMarkdown
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '')
                    return !inline && match ? (
                      <SyntaxHighlighter
                        style={tomorrow}
                        language={match[1]}
                        PreTag="div"
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    )
                  }
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
            
            {message.sources && message.sources.length > 0 && (
              <div className="mt-4 pt-3 border-t border-gray-100">
                <p className="text-xs text-gray-500 mb-2 flex items-center">
                  <DocumentTextIcon className="w-3 h-3 mr-1" />
                  Sources from your notes:
                </p>
                <div className="flex flex-wrap gap-2">
                  {message.sources.map((source, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-primary-50 text-primary-700 border border-primary-200"
                    >
                      {source.path}
                      {source.section && `#${source.section}`}
                      <span className="ml-1 text-primary-500">
                        ({(source.score * 100).toFixed(0)}%)
                      </span>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
        
        <p className={`text-xs mt-2 ${
          message.type === 'user' ? 'text-primary-100' : 'text-gray-400'
        }`}>
          {message.timestamp.toLocaleTimeString()}
        </p>
      </div>
    </div>
  )

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900">Chat & Learn</h2>
        <p className="text-gray-600 mt-1">
          Ask questions about your coding interview notes and get personalized explanations
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
        {chatHistory.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <DocumentTextIcon className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Start a conversation
              </h3>
              <p className="text-gray-600 mb-6 max-w-md">
                Ask me anything about your coding interview notes. I'll dig through your uploaded stuff and explain things in detail.
              </p>
              <div className="space-y-2 text-sm text-gray-500">
                <p>💡 Try asking:</p>
                <ul className="space-y-1">
                  <li>"Explain Union-Find with an example"</li>
                  <li>"How does Dijkstra's algorithm work?"</li>
                  <li>"What's the difference between DFS and BFS?"</li>
                  <li>"Show me dynamic programming patterns"</li>
                </ul>
              </div>
            </div>
          </div>
        ) : (
          <>
            {chatHistory.map(showMessage)}
            {isThinking && (
              <div className="flex justify-start mb-6">
                <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
                    <span className="text-gray-600">Let me think about this...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomOfChatRef} />
          </>
        )}
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 p-6">
        <form onSubmit={askQuestion} className="flex space-x-4">
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="What do you want to know about your coding notes?"
            className="flex-1 input-field"
            disabled={isThinking}
          />
          <button
            type="submit"
            disabled={isThinking || !userInput.trim()}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <PaperAirplaneIcon className="w-4 h-4" />
            <span>Send</span>
          </button>
        </form>
      </div>
    </div>
  )
}
