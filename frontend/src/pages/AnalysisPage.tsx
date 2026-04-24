import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Loader2, BarChart3, Users, Heart, Sparkles, Clock, MessageSquare, Hash, Smile } from 'lucide-react'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { api } from '../lib/api'
import type { StatsResponse, PersonalityResponse, RelationResponse } from '../types'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#22c55e', '#06b6d4']

export function AnalysisPage() {
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [stats, setStats] = useState<StatsResponse | null>(null)
  const [personality, setPersonality] = useState<PersonalityResponse | null>(null)
  const [relation, setRelation] = useState<RelationResponse | null>(null)

  useEffect(() => {
    if (id) loadData()
  }, [id])

  const loadData = async () => {
    try {
      const [statsData, personalityData, relationData] = await Promise.all([
        api.getStats(id!),
        api.getPersonality(id!),
        api.getRelation(id!),
      ])
      setStats(statsData)
      setPersonality(personalityData)
      setRelation(relationData)
    } catch (err) {
      console.error('Failed to load analysis:', err)
    } finally {
      setLoading(false)
    }
  }

  const runAnalysis = async () => {
    setAnalyzing(true)
    try {
      await api.runAnalysis(id!)
      await loadData()
    } catch (err) {
      console.error('Failed to run analysis:', err)
    } finally {
      setAnalyzing(false)
    }
  }

  const getTimeDistributionData = () => {
    if (!stats?.time_distribution) return []
    return Object.entries(stats.time_distribution).map(([name, value]) => ({
      name,
      value,
    }))
  }

  const getMessageTypeData = () => {
    if (!stats?.message_types) return []
    return Object.entries(stats.message_types).map(([name, value]) => ({
      name: name === 'text' ? '文字' : name === 'image' ? '图片' : name === 'voice' ? '语音' : name === 'emoji' ? '表情' : name,
      value,
    }))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="text-center py-16">
        <p className="text-slate-500">没有找到分析数据</p>
        <Button onClick={runAnalysis} className="mt-4">
          运行分析
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">分析报告</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">聊天记录详细分析</p>
        </div>
        <Button onClick={runAnalysis} disabled={analyzing}>
          {analyzing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
          重新分析
        </Button>
      </div>

      {/* Stats Section */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-indigo-600">{stats.total_messages}</p>
              <p className="text-sm text-slate-500 mt-1">总消息数</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-indigo-600">{stats.my_percentage}%</p>
              <p className="text-sm text-slate-500 mt-1">我的占比</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-purple-600">{stats.their_percentage}%</p>
              <p className="text-sm text-slate-500 mt-1">对方占比</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-pink-600">{stats.avg_message_length}</p>
              <p className="text-sm text-slate-500 mt-1">平均字数</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-indigo-600" />
              消息时间分布
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={getTimeDistributionData()}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-purple-600" />
              消息类型分布
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={getMessageTypeData()}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {getMessageTypeData().map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Personality */}
      {personality && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5 text-indigo-600" />
              性格分析
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 md:grid-cols-2">
              {/* My traits */}
              <div className="space-y-4">
                <h4 className="font-medium">你的性格特征</h4>
                {personality.details?.my_style_traits && (
                  <div className="flex flex-wrap gap-2">
                    {personality.details.my_style_traits.map((trait: string) => (
                      <span key={trait} className="px-2 py-1 text-xs rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300">
                        {trait}
                      </span>
                    ))}
                  </div>
                )}
                <div className="space-y-3">
                  {[
                    { label: "O 开放性", desc: "思维开放·好奇探索", value: personality.my_openness ?? personality.my_extroversion_score, color: "bg-violet-500" },
                    { label: "C 尽责性", desc: "自律认真·有条理", value: personality.my_conscientiousness ?? personality.my_rational_score, color: "bg-blue-500" },
                    { label: "E 外向性", desc: "主动活跃·社交能量", value: personality.my_extraversion ?? personality.my_extroversion_score, color: "bg-indigo-500" },
                    { label: "A 宜人性", desc: "友善温和·乐于合作", value: personality.my_agreeableness ?? personality.my_positive_score, color: "bg-emerald-500" },
                    { label: "N 神经质", desc: "情绪敏感·易受影响", value: personality.my_neuroticism ?? (100 - personality.my_direct_score), color: "bg-rose-500" },
                  ].map(t => (
                    <div key={t.label}>
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="text-sm font-medium">{t.label}</span>
                          <span className="text-xs text-slate-400 ml-2">{t.desc}</span>
                        </div>
                        <span className="text-sm font-medium">{t.value.toFixed(0)}</span>
                      </div>
                      <div className="h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden mt-1">
                        <div className={`h-full ${t.color} rounded-full transition-all`} style={{ width: `${t.value}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
                <p className="text-sm text-slate-500 mt-4">
                  互动风格: <span className="font-medium text-indigo-600">{personality.my_interaction_style}</span>
                </p>
              </div>
              {/* Their traits */}
              <div className="space-y-4">
                <h4 className="font-medium">对方性格特征</h4>
                {personality.details?.their_style_traits && (
                  <div className="flex flex-wrap gap-2">
                    {personality.details.their_style_traits.map((trait: string) => (
                      <span key={trait} className="px-2 py-1 text-xs rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300">
                        {trait}
                      </span>
                    ))}
                  </div>
                )}
                <div className="space-y-3">
                  {[
                    { label: "O 开放性", desc: "思维开放·好奇探索", value: personality.their_openness ?? personality.their_extroversion_score, color: "bg-violet-500" },
                    { label: "C 尽责性", desc: "自律认真·有条理", value: personality.their_conscientiousness ?? personality.their_rational_score, color: "bg-blue-500" },
                    { label: "E 外向性", desc: "主动活跃·社交能量", value: personality.their_extraversion ?? personality.their_extroversion_score, color: "bg-indigo-500" },
                    { label: "A 宜人性", desc: "友善温和·乐于合作", value: personality.their_agreeableness ?? personality.their_positive_score, color: "bg-emerald-500" },
                    { label: "N 神经质", desc: "情绪敏感·易受影响", value: personality.their_neuroticism ?? (100 - personality.their_direct_score), color: "bg-rose-500" },
                  ].map(t => (
                    <div key={t.label}>
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="text-sm font-medium">{t.label}</span>
                          <span className="text-xs text-slate-400 ml-2">{t.desc}</span>
                        </div>
                        <span className="text-sm font-medium">{t.value.toFixed(0)}</span>
                      </div>
                      <div className="h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden mt-1">
                        <div className={`h-full ${t.color} rounded-full transition-all`} style={{ width: `${t.value}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
                <p className="text-sm text-slate-500 mt-4">
                  互动风格: <span className="font-medium text-purple-600">{personality.their_interaction_style}</span>
                </p>
              </div>
            </div>
            {personality.summary && (
              <div className="mt-6 p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                <p className="text-sm text-indigo-700 dark:text-indigo-300">{personality.summary}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Relation */}
      {relation && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Heart className="h-5 w-5 text-pink-600" />
              关系分析
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 md:grid-cols-4">
              <div className="text-center p-4 bg-pink-50 dark:bg-pink-900/20 rounded-lg">
                <p className="text-3xl font-bold text-pink-600">{relation.intimacy_score}</p>
                <p className="text-sm text-slate-500 mt-1">亲密度评分</p>
              </div>
              <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <p className="text-3xl font-bold text-purple-600">{relation.my_initiative_index.toFixed(0)}</p>
                <p className="text-sm text-slate-500 mt-1">你的主动指数</p>
              </div>
              <div className="text-center p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                <p className="text-3xl font-bold text-indigo-600">{relation.their_initiative_index.toFixed(0)}</p>
                <p className="text-sm text-slate-500 mt-1">对方主动指数</p>
              </div>
              <div className="text-center p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
                <p className="text-3xl font-bold text-amber-600">
                  {relation.response_time_minutes < 60
                    ? `${relation.response_time_minutes.toFixed(0)}分`
                    : `${(relation.response_time_minutes / 60).toFixed(1)}时`}
                </p>
                <p className="text-sm text-slate-500 mt-1">中位回复时间</p>
              </div>
            </div>
            <div className="mt-6 flex items-center justify-center gap-8 flex-wrap">
              <div className="text-center">
                <p className="text-lg font-medium text-slate-700 dark:text-slate-300">关系趋势</p>
                <p className={`text-2xl font-bold mt-1 ${
                  relation.trend?.direction === '升温中' ? 'text-green-600' :
                  relation.trend?.direction === '降温中' ? 'text-red-500' :
                  'text-slate-600'
                }`}>{relation.trend?.direction || '数据不足'}</p>
                <p className="text-xs text-slate-400 mt-1">{relation.trend?.description || ''}</p>
              </div>
              <div className="text-center">
                <p className="text-lg font-medium text-slate-700 dark:text-slate-300">角色定位</p>
                <p className="text-sm text-slate-500 mt-1">{relation.role_summary}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Hourly Heatmap */}
      {stats?.hourly_heatmap && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-indigo-600" />
              时段活跃度
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={stats.hourly_heatmap}>
                <XAxis dataKey="hour" tickFormatter={(h) => `${h}:00`} />
                <YAxis />
                <Tooltip labelFormatter={(h) => `${h}:00`} />
                <Bar dataKey="count" fill="#6366f1" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Stats Details */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-indigo-600" />
                对话统计
              </CardTitle>
            </CardHeader>
            <CardContent>
              {stats.conversations ? (
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">总对话轮次</span>
                    <span className="text-sm font-medium">{stats.conversations.total}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">平均每次对话消息数</span>
                    <span className="text-sm font-medium">{stats.conversations.avg_per_conversation}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">最长单次对话</span>
                    <span className="text-sm font-medium">{stats.conversations.max_length} 条</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">熬夜消息</span>
                    <span className="text-sm font-medium">{stats.late_night_count} 条 ({stats.late_night_percentage}%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">周末消息</span>
                    <span className="text-sm font-medium">{stats.weekend_count} 条 ({stats.weekend_percentage}%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-slate-600">时间跨度</span>
                    <span className="text-sm font-medium">{stats.time_span_days} 天</span>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-slate-400">暂无数据</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-purple-600" />
                回复速度
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-slate-600">你的中位回复时间</span>
                  <span className="text-sm font-medium">{stats.my_median_response_minutes < 60 ? `${stats.my_median_response_minutes.toFixed(0)} 分钟` : `${(stats.my_median_response_minutes / 60).toFixed(1)} 小时`}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-slate-600">对方中位回复时间</span>
                  <span className="text-sm font-medium">{stats.their_median_response_minutes < 60 ? `${stats.their_median_response_minutes.toFixed(0)} 分钟` : `${(stats.their_median_response_minutes / 60).toFixed(1)} 小时`}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Word & Emoji Stats */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Hash className="h-5 w-5 text-indigo-600" />
                常用字
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <p className="text-xs text-slate-400 mb-2">你的常用字 TOP 10</p>
                  <div className="flex flex-wrap gap-2">
                    {stats.my_top_words?.slice(0, 10).map((w: string, i: number) => (
                      <span key={i} className="px-2 py-1 text-xs bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 rounded">
                        {w}
                      </span>
                    )) || <span className="text-xs text-slate-400">暂无数据</span>}
                  </div>
                </div>
                <div>
                  <p className="text-xs text-slate-400 mb-2">对方的常用字 TOP 10</p>
                  <div className="flex flex-wrap gap-2">
                    {stats.their_top_words?.slice(0, 10).map((w: string, i: number) => (
                      <span key={i} className="px-2 py-1 text-xs bg-purple-50 dark:bg-purple-900/20 text-purple-600 rounded">
                        {w}
                      </span>
                    )) || <span className="text-xs text-slate-400">暂无数据</span>}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Smile className="h-5 w-5 text-pink-600" />
                表情使用
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <p className="text-xs text-slate-400 mb-2">你的常用表情 TOP 5</p>
                  <div className="space-y-1">
                    {stats.my_emoji_top?.slice(0, 5).map(([emoji, count]: [string, number], i: number) => (
                      <div key={i} className="flex justify-between text-sm">
                        <span>{emoji}</span>
                        <span className="text-slate-400">{count} 次</span>
                      </div>
                    )) || <span className="text-xs text-slate-400">暂无数据</span>}
                  </div>
                </div>
                <div>
                  <p className="text-xs text-slate-400 mb-2">对方的常用表情 TOP 5</p>
                  <div className="space-y-1">
                    {stats.their_emoji_top?.slice(0, 5).map(([emoji, count]: [string, number], i: number) => (
                      <div key={i} className="flex justify-between text-sm">
                        <span>{emoji}</span>
                        <span className="text-slate-400">{count} 次</span>
                      </div>
                    )) || <span className="text-xs text-slate-400">暂无数据</span>}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}