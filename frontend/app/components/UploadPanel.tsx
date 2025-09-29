'use client'

import { useState, useCallback } from 'react'
import { ArrowUpTrayIcon, DocumentTextIcon, TrashIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface Document {
  id: string
  title: string
  source: string
  path: string
  created_at: string
  chunk_count: number
}

export default function UploadPanel() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [uploading, setUploading] = useState(false)
  const [loading, setLoading] = useState(false)
  const [dragActive, setDragActive] = useState(false)

  const fetchDocuments = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/ingest/documents')
      if (response.ok) {
        const data = await response.json()
        setDocuments(data)
      }
    } catch (error) {
      console.error('Error fetching documents:', error)
    } finally {
      setLoading(false)
    }
  }

  React.useEffect(() => {
    fetchDocuments()
  }, [])

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files)
    }
  }, [])

  const handleFiles = async (files: FileList) => {
    const file = files[0]
    if (!file) return

    // Check file type
    const allowedTypes = ['.md', '.txt', '.py', '.cpp', '.java', '.js', '.ts']
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase()
    
    if (!allowedTypes.includes(fileExt)) {
      toast.error('Unsupported file type. Please upload .md, .txt, or code files.')
      return
    }

    setUploading(true)
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('title', file.name)

      const response = await fetch('/api/ingest/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const result = await response.json()
      toast.success(`Successfully uploaded ${file.name} (${result.chunks_created} chunks created)`)
      
      // Refresh documents list
      fetchDocuments()
    } catch (error) {
      console.error('Upload error:', error)
      toast.error('Failed to upload file')
    } finally {
      setUploading(false)
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(e.target.files)
    }
  }

  const deleteDocument = async (documentId: string, title: string) => {
    if (!confirm(`Are you sure you want to delete "${title}"?`)) {
      return
    }

    try {
      const response = await fetch(`/api/ingest/documents/${documentId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('Delete failed')
      }

      toast.success(`Deleted ${title}`)
      fetchDocuments()
    } catch (error) {
      console.error('Delete error:', error)
      toast.error('Failed to delete document')
    }
  }

  const addTextNote = async () => {
    const title = prompt('Enter a title for your note:')
    if (!title) return

    const content = prompt('Enter your note content (markdown supported):')
    if (!content) return

    try {
      const response = await fetch('/api/ingest/text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title,
          content,
          source: 'manual'
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to add note')
      }

      const result = await response.json()
      toast.success(`Added note "${title}" (${result.chunks_created} chunks created)`)
      fetchDocuments()
    } catch (error) {
      console.error('Add note error:', error)
      toast.error('Failed to add note')
    }
  }

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900">Upload Notes</h2>
        <p className="text-gray-600 mt-1">
          Upload your coding interview notes, solutions, and study materials
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Upload Area */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 bg-white hover:border-gray-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <ArrowUpTrayIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Upload your files
            </h3>
            <p className="text-gray-600 mb-4">
              Drag and drop files here, or click to browse
            </p>
            <p className="text-sm text-gray-500 mb-6">
              Supported: .md, .txt, .py, .cpp, .java, .js, .ts
            </p>
            
            <div className="flex justify-center space-x-4">
              <label className="btn-primary cursor-pointer">
                <input
                  type="file"
                  className="hidden"
                  onChange={handleFileInput}
                  accept=".md,.txt,.py,.cpp,.java,.js,.ts"
                  disabled={uploading}
                />
                {uploading ? 'Uploading...' : 'Choose File'}
              </label>
              
              <button
                onClick={addTextNote}
                className="btn-secondary"
                disabled={uploading}
              >
                Add Text Note
              </button>
            </div>
          </div>

          {/* Documents List */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  Your Documents
                </h3>
                <button
                  onClick={fetchDocuments}
                  disabled={loading}
                  className="btn-secondary text-sm"
                >
                  {loading ? 'Loading...' : 'Refresh'}
                </button>
              </div>
            </div>

            {loading ? (
              <div className="p-6">
                <div className="animate-pulse space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="flex items-center space-x-4">
                      <div className="w-8 h-8 bg-gray-200 rounded"></div>
                      <div className="flex-1 space-y-2">
                        <div className="h-4 bg-gray-200 rounded w-1/3"></div>
                        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : documents.length === 0 ? (
              <div className="p-6 text-center">
                <DocumentTextIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No documents uploaded yet</p>
                <p className="text-sm text-gray-500 mt-1">
                  Upload some files to get started with the chat feature
                </p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {documents.map((doc) => (
                  <div key={doc.id} className="p-6 flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                        <DocumentTextIcon className="w-5 h-5 text-primary-600" />
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">{doc.title}</h4>
                        <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                          <span>{doc.source}</span>
                          <span>•</span>
                          <span>{doc.chunk_count} chunks</span>
                          <span>•</span>
                          <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                    
                    <button
                      onClick={() => deleteDocument(doc.id, doc.title)}
                      className="text-red-600 hover:text-red-800 p-2"
                      title="Delete document"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Tips */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">
              💡 Tips for better results
            </h3>
            <ul className="space-y-2 text-sm text-blue-800">
              <li>• Use clear headings in your markdown files for better chunking</li>
              <li>• Include explanations with your code solutions</li>
              <li>• Organize notes by topic (e.g., "Dynamic Programming", "Graph Algorithms")</li>
              <li>• Add examples and edge cases to your problem solutions</li>
              <li>• Use consistent naming conventions for better search results</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
