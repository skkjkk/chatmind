import { useState } from 'react'
import { motion } from 'framer-motion'
import { MessageCircle, Loader2, Sparkles, Lightbulb, Wand2 } from 'lucide-react'
import { api } from '../lib/api'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card'

const STYLE_OPTIONS = [
  { value: 'concise', label: '简洁', description: '简短直接' },
  { value: 'playful', label: '俏皮', description: '轻松有趣' },
  { value: 'warm', label: '热情', description: '温暖亲切' },
  { value: 'formal', label: '正式', description: '商务规范' },
  { value: 'tactful', label: '委婉', description: '含蓄礼貌' },
]

type Mode = 'smart' | 'quick' | 'improve'

export function ReplyPage() {
  const [mode, setMode] = useState<Mode>('smart')
  const [loading, setLoading] = useState(false)
  const [style, setStyle] = useState('concise')

  // Smart context mode
  const [draft, setDraft] = useState('')
  const [context, setContext] = useState('')
  const [smartResult, setSmartResult] = useState<any>(null)
  const [smartAnalysis, setSmartAnalysis] = useState('')

  // Quick question mode
  const [scenario, setScenario] = useState('')
  const [quickResult, setQuickResult] = useState<any>(null)
  const [quickAnalysis, setQuickAnalysis] = useState('')

  // Improve mode
  const [improveDraft, setImproveDraft] = useState('')
  const [improveResult, setImproveResult] = useState<any>(null)

  const handleSmartSubmit = () => {
    setLoading(true)
    setSmartAnalysis('')
    setSmartResult(null)
    api.streamSmartReply(
      draft, context, style,
      (text) => setSmartAnalysis(prev => prev + text),
      (suggestions, improvedReply) => {
        setSmartResult({ suggestions, improved_reply: improvedReply })
        setLoading(false)
      }
    )
  }

  const handleQuickSubmit = () => {
    setLoading(true)
    setQuickAnalysis('')
    setQuickResult(null)
    api.streamQuickReply(
      scenario, style,
      (text) => setQuickAnalysis(prev => prev + text),
      (suggestions) => {
        setQuickResult({ suggestions })
        setLoading(false)
      }
    )
  }

  const handleImproveSubmit = async () => {
    setLoading(true)
    try {
      const result = await api.improveDraft(improveDraft, style)
      setImproveResult(result)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">回复助手</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">智能生成回复建议，提升聊天效率</p>
      </div>

      {/* Mode tabs */}
      <div className="flex gap-2 mb-6">
        <Button
          variant={mode === 'smart' ? 'default' : 'outline'}
          onClick={() => setMode('smart')}
        >
          <MessageCircle className="mr-2 h-4 w-4" />
          智能语境
        </Button>
        <Button
          variant={mode === 'quick' ? 'default' : 'outline'}
          onClick={() => setMode('quick')}
        >
          <Lightbulb className="mr-2 h-4 w-4" />
          快速问答
        </Button>
        <Button
          variant={mode === 'improve' ? 'default' : 'outline'}
          onClick={() => setMode('improve')}
        >
          <Wand2 className="mr-2 h-4 w-4" />
          优化草稿
        </Button>
      </div>

      {/* Style selector */}
      <Card className="mb-6">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm">选择回复风格</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {STYLE_OPTIONS.map((option) => (
              <button
                key={option.value}
                onClick={() => setStyle(option.value)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  style === option.value
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Smart Context Mode */}
      {mode === 'smart' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <Card>
            <CardHeader>
              <CardTitle>智能语境模式</CardTitle>
              <CardDescription>基于对话背景优化您的回复</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">当前对话背景</label>
                <textarea
                  className="w-full h-24 p-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="对方说了什么？"
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">您的回复草稿</label>
                <textarea
                  className="w-full h-24 p-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="您想回复的内容..."
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                />
              </div>
              <Button onClick={handleSmartSubmit} disabled={loading || !context || !draft} className="w-full">
                {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
                获取建议
              </Button>

              {(smartAnalysis || smartResult) && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4 mt-6">
                  <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                    <p className="text-sm font-medium text-indigo-700 dark:text-indigo-300">语境分析</p>
                    <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                      {smartAnalysis}{loading && <span className="animate-pulse">▍</span>}
                    </p>
                  </div>
                  {smartResult && (
                    <>
                      <div className="space-y-3">
                        <p className="text-sm font-medium">回复建议</p>
                        {smartResult.suggestions?.map((s: any, i: number) => (
                          <div key={i} className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                            <p className="text-sm font-medium">{s.content}</p>
                            <p className="text-xs text-slate-500 mt-1">{s.reason}</p>
                          </div>
                        ))}
                      </div>
                      {smartResult.improved_reply && (
                        <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                          <p className="text-sm font-medium text-green-700 dark:text-green-300">优化后的回复</p>
                          <p className="text-sm mt-1">{smartResult.improved_reply}</p>
                        </div>
                      )}
                    </>
                  )}
                </motion.div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Quick Question Mode */}
      {mode === 'quick' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <Card>
            <CardHeader>
              <CardTitle>快速问答模式</CardTitle>
              <CardDescription>直接给出回复建议</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">场景描述</label>
                <textarea
                  className="w-full h-24 p-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="描述您遇到的聊天场景，比如：对方问我借钱..."
                  value={scenario}
                  onChange={(e) => setScenario(e.target.value)}
                />
              </div>
              <Button onClick={handleQuickSubmit} disabled={loading || !scenario} className="w-full">
                {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Lightbulb className="mr-2 h-4 w-4" />}
                获取建议
              </Button>

              {(quickAnalysis || quickResult) && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4 mt-6">
                  <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                    <p className="text-sm font-medium text-indigo-700 dark:text-indigo-300">场景分析</p>
                    <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                      {quickAnalysis}{loading && <span className="animate-pulse">▍</span>}
                    </p>
                  </div>
                  {quickResult && (
                    <div className="space-y-3">
                      <p className="text-sm font-medium">回复建议</p>
                      {quickResult.suggestions?.map((s: any, i: number) => (
                        <div key={i} className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                          <p className="text-sm font-medium">{s.content}</p>
                          <p className="text-xs text-slate-500 mt-1">{s.reason}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </motion.div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Improve Mode */}
      {mode === 'improve' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <Card>
            <CardHeader>
              <CardTitle>优化草稿</CardTitle>
              <CardDescription>将您的草稿润色得更好</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">原始草稿</label>
                <textarea
                  className="w-full h-32 p-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="输入您想优化的回复..."
                  value={improveDraft}
                  onChange={(e) => setImproveDraft(e.target.value)}
                />
              </div>
              <Button onClick={handleImproveSubmit} disabled={loading || !improveDraft} className="w-full">
                {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Wand2 className="mr-2 h-4 w-4" />}
                优化草稿
              </Button>

              {improveResult && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4 mt-6">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
                      <p className="text-sm font-medium text-slate-500">原始</p>
                      <p className="text-sm mt-1">{improveResult.original}</p>
                    </div>
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <p className="text-sm font-medium text-green-700 dark:text-green-300">优化后</p>
                      <p className="text-sm mt-1">{improveResult.improved}</p>
                    </div>
                  </div>
                  {improveResult.suggestions?.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-sm font-medium">优化建议</p>
                      {improveResult.suggestions.map((s: string, i: number) => (
                        <p key={i} className="text-sm text-slate-600 dark:text-slate-400">• {s}</p>
                      ))}
                    </div>
                  )}
                </motion.div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  )
}