import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, Loader2, FileText, CheckCircle, AlertCircle } from 'lucide-react'
import { api } from '../lib/api'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'

export function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [contactName, setContactName] = useState('')
  const [uploading, setUploading] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const [progress, setProgress] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  const [error, setError] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()

  const handleFileSelect = (selected: File) => {
    setFile(selected)
    if (!contactName) {
      const name = selected.name.replace(/\.(html|htm|txt|json|csv)$/i, '')
      setContactName(name)
    }
    setError('')
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0]
    if (selected) handleFileSelect(selected)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    const dropped = e.dataTransfer.files?.[0]
    if (dropped) handleFileSelect(dropped)
  }

  const handleUpload = async () => {
    if (!file) {
      setError('请选择文件')
      return
    }

    setUploading(true)
    setProgress('uploading')
    setError('')

    try {
      const result = await api.uploadRecord(file, contactName || file.name)
      setProgress('success')
      setTimeout(() => {
        navigate(`/analysis/${result.id}`)
      }, 1500)
    } catch (err: any) {
      setProgress('error')
      setError(err.response?.data?.detail || '上传失败，请重试')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">导入聊天记录</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">上传微信聊天记录文件进行分析</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>上传文件</CardTitle>
          <CardDescription>支持 HTML、TXT、JSON、CSV 格式的聊天记录文件</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* File drop zone */}
          <div
            className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
              file
                ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
                : isDragging
                  ? 'border-indigo-500 bg-indigo-50/50 dark:bg-indigo-900/10'
                  : 'border-slate-300 dark:border-slate-600 hover:border-indigo-400'
            }`}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".html,.htm,.txt,.json,.csv"
              onChange={handleFileChange}
              className="hidden"
            />

            {file ? (
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="flex items-center justify-center gap-3"
              >
                <FileText className="h-10 w-10 text-indigo-500" />
                <div className="text-left">
                  <p className="font-medium text-slate-900 dark:text-white">{file.name}</p>
                  <p className="text-sm text-slate-500">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
              </motion.div>
            ) : (
              <div className="space-y-2">
                <Upload className="mx-auto h-12 w-12 text-slate-400" />
                <p className="text-slate-600 dark:text-slate-400">
                  点击或拖拽文件到此处上传
                </p>
                <p className="text-sm text-slate-400">支持 HTML、TXT、JSON、CSV</p>
              </div>
            )}
          </div>

          {/* Contact name input */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
              联系人名称
            </label>
            <Input
              placeholder="输入联系人昵称（可选）"
              value={contactName}
              onChange={(e) => setContactName(e.target.value)}
            />
            <p className="text-xs text-slate-400">留空则使用文件名作为联系人名称</p>
          </div>

          {/* Error message */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="flex items-center gap-2 p-3 text-sm text-red-600 bg-red-50 dark:bg-red-900/20 rounded-lg"
              >
                <AlertCircle className="h-4 w-4" />
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Success message */}
          <AnimatePresence>
            {progress === 'success' && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2 p-3 text-sm text-green-600 bg-green-50 dark:bg-green-900/20 rounded-lg"
              >
                <CheckCircle className="h-4 w-4" />
                上传成功！正在跳转到分析页面...
              </motion.div>
            )}
          </AnimatePresence>

          {/* Upload button */}
          <Button
            className="w-full"
            size="lg"
            onClick={handleUpload}
            disabled={uploading || !file || progress === 'success'}
          >
            {uploading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                上传中...
              </>
            ) : progress === 'success' ? (
              <>
                <CheckCircle className="mr-2 h-4 w-4" />
                上传成功
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                开始上传
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}