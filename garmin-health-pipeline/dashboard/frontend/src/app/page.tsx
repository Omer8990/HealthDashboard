'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts'

// Types
interface DashboardMetrics {
  current_bio_age: number
  aging_velocity: number
  longevity_score: number
  years_gained: number
  streak_days: number
  level: number
  xp: number
}

interface HealthTrends {
  trends: {
    dates: string[]
    resting_heart_rate: number[]
    total_steps: number[]
    total_calories: number[]
    activities_count: number[]
    biological_age: number[]
    longevity_score: number[]
  }
}

interface Activity {
  activity_type: string
  activity_name: string
  start_time: string
  duration_minutes: number
  distance_km: number
  calories: number
  avg_heart_rate: number
  max_heart_rate: number
}

interface Insight {
  type: 'achievement' | 'success' | 'recommendation'
  title: string
  message: string
  impact: string
  icon: string
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [trends, setTrends] = useState<HealthTrends | null>(null)
  const [activities, setActivities] = useState<Activity[]>([])
  const [insights, setInsights] = useState<Insight[]>([])
  const [activeTab, setActiveTab] = useState<'overview' | 'trends' | 'activities' | 'insights'>('overview')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsRes, trendsRes, activitiesRes, insightsRes] = await Promise.all([
          fetch('http://localhost:8000/api/dashboard/overview'),
          fetch('http://localhost:8000/api/health/trends?days=30'),
          fetch('http://localhost:8000/api/activities/detailed?days=14'),
          fetch('http://localhost:8000/api/insights/health')
        ])

        const [metricsData, trendsData, activitiesData, insightsData] = await Promise.all([
          metricsRes.json(),
          trendsRes.json(),
          activitiesRes.json(),
          insightsRes.json()
        ])

        setMetrics(metricsData)
        setTrends(trendsData)
        setActivities(activitiesData.activities || [])
        setInsights(insightsData.insights || [])
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full"
        />
        <span className="ml-4 text-cyan-400 text-xl font-mono">LOADING HEALTH MATRIX...</span>
      </div>
    )
  }

  const formatTrendsData = () => {
    if (!trends?.trends) return []
    return trends.trends.dates.map((date, i) => ({
      date: new Date(date).toLocaleDateString(),
      rhr: trends.trends.resting_heart_rate[i],
      steps: trends.trends.total_steps[i],
      bioAge: trends.trends.biological_age[i],
      longevityScore: trends.trends.longevity_score[i],
      activities: trends.trends.activities_count[i]
    }))
  }

  const activityTypeColors = {
    running: '#ff6b6b',
    cycling: '#4ecdc4', 
    strength_training: '#ffe66d',
    walking: '#95e1d3',
    swimming: '#74b9ff',
    unknown: '#a29bfe'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black text-white font-mono">
      {/* Neural Network Background */}
      <div className="fixed inset-0 opacity-10 pointer-events-none">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(120,119,198,0.3),transparent_70%)]" />
        {[...Array(50)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-cyan-400 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              opacity: [0, 1, 0],
              scale: [0, 1, 0],
            }}
            transition={{
              duration: Math.random() * 3 + 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      {/* Header */}
      <motion.header
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="relative z-10 border-b border-cyan-500/30 bg-black/80 backdrop-blur-sm"
      >
        <div className="container mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                🧬 LONGEVITY MATRIX
              </h1>
              <p className="text-gray-400 mt-1">BIOLOGICAL AGE: {metrics?.current_bio_age.toFixed(1)} YEARS</p>
            </div>
            <div className="flex gap-4">
              <div className="text-right">
                <p className="text-cyan-400 font-bold text-xl">LVL {metrics?.level}</p>
                <p className="text-gray-400">{metrics?.xp.toLocaleString()} XP</p>
              </div>
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center text-2xl">
                🏆
              </div>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Navigation */}
      <nav className="relative z-10 bg-black/60 backdrop-blur-sm border-b border-gray-800">
        <div className="container mx-auto px-6">
          <div className="flex space-x-8">
            {(['overview', 'trends', 'activities', 'insights'] as const).map((tab) => (
              <motion.button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-2 font-medium transition-colors relative ${
                  activeTab === tab ? 'text-cyan-400' : 'text-gray-400 hover:text-white'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {tab.toUpperCase()}
                {activeTab === tab && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400"
                  />
                )}
              </motion.button>
            ))}
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-6 py-8 relative z-10">
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-8"
            >
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <motion.div
                  whileHover={{ scale: 1.05, rotateY: 5 }}
                  className="bg-gradient-to-br from-gray-900 to-gray-800 border border-cyan-500/30 rounded-xl p-6 relative overflow-hidden"
                >
                  <div className="absolute top-0 right-0 w-20 h-20 bg-cyan-500/10 rounded-full -mr-10 -mt-10" />
                  <div className="relative">
                    <p className="text-gray-400 text-sm mb-1">BIOLOGICAL AGE</p>
                    <p className="text-3xl font-bold text-cyan-400">{metrics?.current_bio_age.toFixed(1)}</p>
                    <p className="text-green-400 text-sm mt-2">
                      {metrics && metrics.years_gained > 0 ? '+' : ''}{metrics?.years_gained.toFixed(1)} years vs chronological
                    </p>
                  </div>
                </motion.div>

                <motion.div
                  whileHover={{ scale: 1.05, rotateY: 5 }}
                  className="bg-gradient-to-br from-gray-900 to-gray-800 border border-purple-500/30 rounded-xl p-6 relative overflow-hidden"
                >
                  <div className="absolute top-0 right-0 w-20 h-20 bg-purple-500/10 rounded-full -mr-10 -mt-10" />
                  <div className="relative">
                    <p className="text-gray-400 text-sm mb-1">LONGEVITY SCORE</p>
                    <p className="text-3xl font-bold text-purple-400">{metrics?.longevity_score}/100</p>
                    <p className={`text-sm mt-2 ${(metrics?.longevity_score || 0) >= 90 ? 'text-green-400' : 'text-yellow-400'}`}>
                      {(metrics?.longevity_score || 0) >= 90 ? 'ELITE STATUS' : 'OPTIMIZING'}
                    </p>
                  </div>
                </motion.div>

                <motion.div
                  whileHover={{ scale: 1.05, rotateY: 5 }}
                  className="bg-gradient-to-br from-gray-900 to-gray-800 border border-green-500/30 rounded-xl p-6 relative overflow-hidden"
                >
                  <div className="absolute top-0 right-0 w-20 h-20 bg-green-500/10 rounded-full -mr-10 -mt-10" />
                  <div className="relative">
                    <p className="text-gray-400 text-sm mb-1">AGING VELOCITY</p>
                    <p className="text-3xl font-bold text-green-400">
                      {((metrics?.aging_velocity || 0) * 100).toFixed(1)}%
                    </p>
                    <p className="text-green-400 text-sm mt-2">
                      {(metrics?.aging_velocity || 0) < 0 ? 'AGING SLOWER' : 'AGING FASTER'}
                    </p>
                  </div>
                </motion.div>

                <motion.div
                  whileHover={{ scale: 1.05, rotateY: 5 }}
                  className="bg-gradient-to-br from-gray-900 to-gray-800 border border-orange-500/30 rounded-xl p-6 relative overflow-hidden"
                >
                  <div className="absolute top-0 right-0 w-20 h-20 bg-orange-500/10 rounded-full -mr-10 -mt-10" />
                  <div className="relative">
                    <p className="text-gray-400 text-sm mb-1">ACTIVITY STREAK</p>
                    <p className="text-3xl font-bold text-orange-400">{metrics?.streak_days}</p>
                    <p className="text-orange-400 text-sm mt-2">DAYS ACTIVE</p>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          )}

          {activeTab === 'trends' && (
            <motion.div
              key="trends"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-8"
            >
              <h2 className="text-2xl font-bold text-cyan-400">HEALTH TRENDS ANALYSIS</h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Heart Rate Trends */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-gradient-to-br from-gray-900 to-gray-800 border border-red-500/30 rounded-xl p-6"
                >
                  <h3 className="text-lg font-bold mb-4 text-red-400">RESTING HEART RATE</h3>
                  <div className="h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={formatTrendsData()}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey="date" stroke="#9CA3AF" />
                        <YAxis stroke="#9CA3AF" />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#1F2937',
                            border: '1px solid #374151',
                            borderRadius: '8px',
                            color: '#fff'
                          }}
                        />
                        <Line
                          type="monotone"
                          dataKey="rhr"
                          stroke="#EF4444"
                          strokeWidth={3}
                          dot={{ fill: '#EF4444', strokeWidth: 2, r: 4 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </motion.div>

                {/* Steps Trends */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="bg-gradient-to-br from-gray-900 to-gray-800 border border-green-500/30 rounded-xl p-6"
                >
                  <h3 className="text-lg font-bold mb-4 text-green-400">DAILY STEPS</h3>
                  <div className="h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={formatTrendsData()}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey="date" stroke="#9CA3AF" />
                        <YAxis stroke="#9CA3AF" />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#1F2937',
                            border: '1px solid #374151',
                            borderRadius: '8px',
                            color: '#fff'
                          }}
                        />
                        <Area
                          type="monotone"
                          dataKey="steps"
                          stroke="#10B981"
                          fill="#10B981"
                          fillOpacity={0.3}
                          strokeWidth={2}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </motion.div>

                {/* Biological Age Trends */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="bg-gradient-to-br from-gray-900 to-gray-800 border border-purple-500/30 rounded-xl p-6"
                >
                  <h3 className="text-lg font-bold mb-4 text-purple-400">BIOLOGICAL AGE</h3>
                  <div className="h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={formatTrendsData()}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey="date" stroke="#9CA3AF" />
                        <YAxis stroke="#9CA3AF" />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#1F2937',
                            border: '1px solid #374151',
                            borderRadius: '8px',
                            color: '#fff'
                          }}
                        />
                        <Line
                          type="monotone"
                          dataKey="bioAge"
                          stroke="#A855F7"
                          strokeWidth={3}
                          dot={{ fill: '#A855F7', strokeWidth: 2, r: 4 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </motion.div>

                {/* Activity Frequency */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="bg-gradient-to-br from-gray-900 to-gray-800 border border-blue-500/30 rounded-xl p-6"
                >
                  <h3 className="text-lg font-bold mb-4 text-blue-400">ACTIVITY FREQUENCY</h3>
                  <div className="h-48">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={formatTrendsData()}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis dataKey="date" stroke="#9CA3AF" />
                        <YAxis stroke="#9CA3AF" />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#1F2937',
                            border: '1px solid #374151',
                            borderRadius: '8px',
                            color: '#fff'
                          }}
                        />
                        <Bar dataKey="activities" fill="#3B82F6" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          )}

          {activeTab === 'activities' && (
            <motion.div
              key="activities"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-8"
            >
              <h2 className="text-2xl font-bold text-cyan-400">ACTIVITY LOG</h2>
              
              <div className="grid gap-4">
                {activities.map((activity, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    whileHover={{ scale: 1.02 }}
                    className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-xl p-6 hover:border-cyan-500/30 transition-colors"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex items-center space-x-4">
                        <div 
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: (activityTypeColors as any)[activity.activity_type] || activityTypeColors.unknown }}
                        />
                        <div>
                          <h3 className="font-bold text-white">{activity.activity_name}</h3>
                          <p className="text-gray-400 text-sm">{new Date(activity.start_time).toLocaleString()}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-cyan-400 font-bold">{activity.calories} cal</p>
                        <p className="text-gray-400 text-sm">{activity.duration_minutes.toFixed(0)} min</p>
                      </div>
                    </div>
                    <div className="mt-4 grid grid-cols-4 gap-4 text-center">
                      <div>
                        <p className="text-gray-400 text-xs">DISTANCE</p>
                        <p className="text-white font-bold">{activity.distance_km.toFixed(1)} km</p>
                      </div>
                      <div>
                        <p className="text-gray-400 text-xs">AVG HR</p>
                        <p className="text-red-400 font-bold">{activity.avg_heart_rate} bpm</p>
                      </div>
                      <div>
                        <p className="text-gray-400 text-xs">MAX HR</p>
                        <p className="text-red-500 font-bold">{activity.max_heart_rate} bpm</p>
                      </div>
                      <div>
                        <p className="text-gray-400 text-xs">TYPE</p>
                        <p className="text-white font-bold capitalize">{activity.activity_type.replace('_', ' ')}</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {activeTab === 'insights' && (
            <motion.div
              key="insights"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-8"
            >
              <h2 className="text-2xl font-bold text-cyan-400">AI HEALTH INSIGHTS</h2>
              
              <div className="grid gap-6">
                {insights.map((insight, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    whileHover={{ scale: 1.02 }}
                    className={`bg-gradient-to-br from-gray-900 to-gray-800 border rounded-xl p-6 ${
                      insight.type === 'achievement' ? 'border-yellow-500/30' :
                      insight.type === 'success' ? 'border-green-500/30' :
                      'border-blue-500/30'
                    }`}
                  >
                    <div className="flex items-start space-x-4">
                      <div className="text-3xl">{insight.icon}</div>
                      <div className="flex-1">
                        <div className="flex justify-between items-start">
                          <div>
                            <h3 className={`font-bold text-lg ${
                              insight.type === 'achievement' ? 'text-yellow-400' :
                              insight.type === 'success' ? 'text-green-400' :
                              'text-blue-400'
                            }`}>
                              {insight.title}
                            </h3>
                            <p className="text-gray-300 mt-2">{insight.message}</p>
                          </div>
                          <div className="text-right">
                            <p className={`font-bold ${
                              insight.type === 'achievement' ? 'text-yellow-400' :
                              insight.type === 'success' ? 'text-green-400' :
                              'text-blue-400'
                            }`}>
                              {insight.impact}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-gray-800 bg-black/80 backdrop-blur-sm mt-16">
        <div className="container mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <p className="text-gray-400">LONGEVITY MATRIX v2.0 | POWERED BY GARMIN DATA</p>
            <p className="text-gray-400">LAST SYNC: {new Date().toLocaleTimeString()}</p>
          </div>
        </div>
      </footer>
    </div>
  )
}