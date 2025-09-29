'use client'

import { useState, useEffect } from 'react'
import { PlayIcon, LightBulbIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline'
import Editor from '@monaco-editor/react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism'
import toast from 'react-hot-toast'

interface Problem {
  problem_id: string
  title: string
  difficulty: string
  prompt_md: string
  sample_tests: TestCase[]
  tags: string[]
  skills: string[]
}

interface TestCase {
  input: string
  expected_output: string
}

interface TestResult {
  input_data: string
  expected_output: string
  actual_output: string
  passed: boolean
  error?: string
}

interface SubmissionResult {
  passed: boolean
  score: number
  test_results: TestResult[]
  feedback_md: string
  attempt_id: string
}

export default function PracticePanel() {
  const [problem, setProblem] = useState<Problem | null>(null)
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState<SubmissionResult | null>(null)
  const [showHint, setShowHint] = useState(false)
  const [hint, setHint] = useState('')
  const [hintLevel, setHintLevel] = useState(1)

  const startPractice = async (difficulty?: string) => {
    setLoading(true)
    setResult(null)
    setShowHint(false)
    setHint('')
    setHintLevel(1)
    
    try {
      const params = new URLSearchParams()
      if (difficulty) params.append('difficulty', difficulty)
      
      const response = await fetch(`/api/practice/start?${params}`)
      if (!response.ok) {
        throw new Error('Failed to start practice')
      }
      
      const data: Problem = await response.json()
      setProblem(data)
      setCode('# Write your solution here\n\n')
      toast.success(`Started: ${data.title}`)
    } catch (error) {
      console.error('Whoops, failed to start practice:', error)
      toast.error('Could not start practice - something went wrong!')
    } finally {
      setLoading(false)
    }
  }

  const submitCode = async () => {
    if (!problem || !code.trim()) return
    
    setSubmitting(true)
    
    try {
      const response = await fetch('/api/practice/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          problem_id: problem.problem_id,
          code: code,
          language: 'python'
        }),
      })
      
      if (!response.ok) {
        throw new Error('Failed to submit code')
      }
      
      const data: SubmissionResult = await response.json()
      setResult(data)
      
      if (data.passed) {
        toast.success('Nailed it! All tests passed! 🎉')
      } else {
        toast.error('Not quite there yet - check the results below')
      }
    } catch (error) {
      console.error('Submit failed:', error)
      toast.error('Could not submit your code - try again!')
    } finally {
      setSubmitting(false)
    }
  }

  const getHint = async () => {
    if (!problem) return
    
    try {
      const response = await fetch('/api/practice/hint', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          problem_id: problem.problem_id,
          hint_level: hintLevel
        }),
      })
      
      if (!response.ok) {
        throw new Error('Failed to get hint')
      }
      
      const data = await response.json()
      setHint(data.hint)
      setShowHint(true)
      toast.success(`Here's hint #${hintLevel} for you!`)
    } catch (error) {
      console.error('Hint request failed:', error)
      toast.error('Could not get a hint right now')
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy': return 'text-green-600 bg-green-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'hard': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  if (!problem) {
    return (
      <div className="flex flex-col h-screen">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-6">
          <h2 className="text-2xl font-bold text-gray-900">Practice Mode</h2>
          <p className="text-gray-600 mt-1">
            Solve coding problems and get AI-powered feedback
          </p>
        </div>

        {/* Start Practice */}
        <div className="flex-1 flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <PlayIcon className="w-8 h-8 text-primary-600" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Ready to practice?
            </h3>
            <p className="text-gray-600 mb-8 max-w-md">
              Pick a difficulty and let's start coding! You'll get personalized feedback on your solutions.
            </p>
            
            <div className="space-y-3">
              <button
                onClick={() => startPractice('easy')}
                disabled={loading}
                className="w-48 btn-primary disabled:opacity-50"
              >
                {loading ? 'Loading...' : 'Start Easy Problem'}
              </button>
              
              <button
                onClick={() => startPractice('medium')}
                disabled={loading}
                className="w-48 btn-primary disabled:opacity-50"
              >
                {loading ? 'Loading...' : 'Start Medium Problem'}
              </button>
              
              <button
                onClick={() => startPractice('hard')}
                disabled={loading}
                className="w-48 btn-primary disabled:opacity-50"
              >
                {loading ? 'Loading...' : 'Start Hard Problem'}
              </button>
              
              <button
                onClick={() => startPractice()}
                disabled={loading}
                className="w-48 btn-secondary disabled:opacity-50"
              >
                {loading ? 'Loading...' : 'Random Problem'}
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900">{problem.title}</h2>
            <div className="flex items-center space-x-3 mt-2">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(problem.difficulty)}`}>
                {problem.difficulty}
              </span>
              {problem.tags.map((tag, index) => (
                <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs">
                  {tag}
                </span>
              ))}
            </div>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={getHint}
              className="btn-secondary flex items-center space-x-2"
            >
              <LightBulbIcon className="w-4 h-4" />
              <span>Hint {hintLevel}</span>
            </button>
            
            <button
              onClick={() => startPractice()}
              className="btn-secondary"
            >
              New Problem
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Problem Description */}
        <div className="w-1/2 border-r border-gray-200 overflow-y-auto">
          <div className="p-6">
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
                {problem.prompt_md}
              </ReactMarkdown>
            </div>
            
            {/* Sample Tests */}
            {problem.sample_tests.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-3">Sample Tests</h3>
                {problem.sample_tests.map((test, index) => (
                  <div key={index} className="mb-4 p-3 bg-gray-50 rounded-lg">
                    <div className="mb-2">
                      <strong>Input:</strong>
                      <pre className="mt-1 text-sm bg-gray-100 p-2 rounded">{test.input}</pre>
                    </div>
                    <div>
                      <strong>Expected Output:</strong>
                      <pre className="mt-1 text-sm bg-gray-100 p-2 rounded">{test.expected_output}</pre>
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {/* Hint */}
            {showHint && hint && (
              <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h3 className="text-lg font-semibold mb-2 flex items-center">
                  <LightBulbIcon className="w-5 h-5 mr-2 text-yellow-600" />
                  Hint (Level {hintLevel})
                </h3>
                <div className="markdown-content">
                  <ReactMarkdown>{hint}</ReactMarkdown>
                </div>
                <button
                  onClick={() => {
                    setHintLevel(prev => prev + 1)
                    getHint()
                  }}
                  className="mt-3 text-sm text-yellow-700 hover:text-yellow-800"
                >
                  Need an even bigger hint? →
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Code Editor and Results */}
        <div className="w-1/2 flex flex-col">
          {/* Editor */}
          <div className="flex-1 border-b border-gray-200">
            <div className="h-full">
              <Editor
                height="100%"
                defaultLanguage="python"
                value={code}
                onChange={(value) => setCode(value || '')}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  roundedSelection: false,
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                }}
              />
            </div>
          </div>

          {/* Submit Button */}
          <div className="p-4 bg-white border-b border-gray-200">
            <button
              onClick={submitCode}
              disabled={submitting || !code.trim()}
              className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              <PlayIcon className="w-4 h-4" />
              <span>{submitting ? 'Running Tests...' : 'Submit & Test'}</span>
            </button>
          </div>

          {/* Results */}
          {result && (
            <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
              <div className="space-y-4">
                {/* Overall Result */}
                <div className={`p-4 rounded-lg ${
                  result.passed ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                }`}>
                  <div className="flex items-center space-x-2">
                    {result.passed ? (
                      <CheckCircleIcon className="w-5 h-5 text-green-600" />
                    ) : (
                      <XCircleIcon className="w-5 h-5 text-red-600" />
                    )}
                    <span className={`font-semibold ${
                      result.passed ? 'text-green-800' : 'text-red-800'
                    }`}>
                      {result.passed ? 'All Tests Passed!' : 'Some Tests Failed'}
                    </span>
                  </div>
                  <p className={`mt-1 text-sm ${
                    result.passed ? 'text-green-700' : 'text-red-700'
                  }`}>
                    Score: {(result.score * 100).toFixed(1)}%
                  </p>
                </div>

                {/* Test Results */}
                <div>
                  <h3 className="font-semibold mb-2">Test Results</h3>
                  {result.test_results.map((test, index) => (
                    <div key={index} className={`mb-3 p-3 rounded-lg border ${
                      test.passed ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                    }`}>
                      <div className="flex items-center space-x-2 mb-2">
                        {test.passed ? (
                          <CheckCircleIcon className="w-4 h-4 text-green-600" />
                        ) : (
                          <XCircleIcon className="w-4 h-4 text-red-600" />
                        )}
                        <span className="font-medium">Test {index + 1}</span>
                      </div>
                      
                      <div className="text-sm space-y-1">
                        <div>
                          <strong>Input:</strong> <code>{test.input_data}</code>
                        </div>
                        <div>
                          <strong>Expected:</strong> <code>{test.expected_output}</code>
                        </div>
                        <div>
                          <strong>Your Output:</strong> <code>{test.actual_output}</code>
                        </div>
                        {test.error && (
                          <div className="text-red-600">
                            <strong>Error:</strong> {test.error}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {/* AI Feedback */}
                {result.feedback_md && (
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h3 className="font-semibold mb-2">AI Feedback</h3>
                    <div className="markdown-content text-sm">
                      <ReactMarkdown>{result.feedback_md}</ReactMarkdown>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
