'use client';
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Activity, Brain, Heart, Shield, Trophy, Zap } from 'lucide-react';
import axios from 'axios';

interface DashboardMetrics {
  current_bio_age: number;
  aging_velocity: number;
  longevity_score: number;
  years_gained: number;
  streak_days: number;
  level: number;
  xp: number;
}

interface Protocol {
  protocol_name: string;
  target_value: number;
  actual_value: number;
  adherence_percentage: number;
  impact_years: number;
}

interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlocked: boolean;
  xp_reward: number;
  unlock_date?: string;
  progress?: number;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [protocols, setProtocols] = useState<Protocol[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsRes, protocolsRes, achievementsRes] = await Promise.all([
          axios.get(`${API_URL}/api/dashboard/overview`),
          axios.get(`${API_URL}/api/protocols/adherence`),
          axios.get(`${API_URL}/api/achievements`)
        ]);

        setMetrics(metricsRes.data);
        setProtocols(protocolsRes.data.protocols);
        setAchievements(achievementsRes.data.achievements);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="w-16 h-16 border-4 border-cyber-cyan border-t-transparent rounded-full"
        />
        <span className="ml-4 font-mono text-cyber-cyan">INITIALIZING MATRIX...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6">
      {/* Header */}
      <motion.header
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-cyber font-black text-transparent bg-gradient-to-r from-cyber-cyan via-cyber-purple to-cyber-pink bg-clip-text">
              🧬 LONGEVITY MATRIX
            </h1>
            <p className="text-lg font-mono mt-2 text-neon-green">
              BIOLOGICAL OPTIMIZATION PROTOCOL
            </p>
          </div>
          <div className="text-right font-mono">
            <div className="text-cyber-cyan text-sm">
              {currentTime.toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </div>
            <div className="text-cyber-pink text-2xl font-bold">
              {currentTime.toLocaleTimeString('en-US', { hour12: false })}
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Biological Age */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-matrix-surface border border-cyber-cyan rounded-lg p-6 relative overflow-hidden neon-glow"
        >
          <div className="scan-line"></div>
          <div className="flex items-center justify-between mb-4">
            <Brain className="w-8 h-8 text-cyber-cyan" />
            <span className="text-xs font-mono text-cyber-cyan opacity-75">BIO.AGE</span>
          </div>
          <div className="space-y-2">
            <div className="text-3xl font-bold text-cyber-pink font-mono">
              {metrics?.current_bio_age}
            </div>
            <div className="text-sm text-cyber-cyan">
              Aging Rate: <span className="text-neon-green">{metrics?.aging_velocity}%</span>
            </div>
          </div>
        </motion.div>

        {/* Longevity Score */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-matrix-surface border border-neon-green rounded-lg p-6 relative overflow-hidden neon-glow"
        >
          <div className="scan-line"></div>
          <div className="flex items-center justify-between mb-4">
            <Heart className="w-8 h-8 text-neon-green" />
            <span className="text-xs font-mono text-neon-green opacity-75">SCORE</span>
          </div>
          <div className="space-y-2">
            <div className="text-3xl font-bold text-neon-green font-mono">
              {metrics?.longevity_score}/100
            </div>
            <div className="text-sm text-cyber-cyan">
              Years Gained: <span className="text-cyber-pink">+{metrics?.years_gained}</span>
            </div>
          </div>
        </motion.div>

        {/* Level & XP */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-matrix-surface border border-cyber-purple rounded-lg p-6 relative overflow-hidden neon-glow"
        >
          <div className="scan-line"></div>
          <div className="flex items-center justify-between mb-4">
            <Trophy className="w-8 h-8 text-cyber-purple" />
            <span className="text-xs font-mono text-cyber-purple opacity-75">LEVEL</span>
          </div>
          <div className="space-y-2">
            <div className="text-3xl font-bold text-cyber-purple font-mono">
              {metrics?.level}
            </div>
            <div className="text-sm text-cyber-cyan">
              XP: <span className="text-cyber-pink">{metrics?.xp}</span>
            </div>
          </div>
        </motion.div>

        {/* Streak */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="bg-matrix-surface border border-cyber-pink rounded-lg p-6 relative overflow-hidden neon-glow"
        >
          <div className="scan-line"></div>
          <div className="flex items-center justify-between mb-4">
            <Zap className="w-8 h-8 text-cyber-pink" />
            <span className="text-xs font-mono text-cyber-pink opacity-75">STREAK</span>
          </div>
          <div className="space-y-2">
            <div className="text-3xl font-bold text-cyber-pink font-mono">
              {metrics?.streak_days}
            </div>
            <div className="text-sm text-cyber-cyan">
              Days Active
            </div>
          </div>
        </motion.div>
      </div>

      {/* Protocols Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Protocol Adherence */}
        <motion.div
          initial={{ x: -50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="bg-matrix-surface border border-matrix-border rounded-lg p-6"
        >
          <h2 className="text-2xl font-cyber font-bold text-cyber-cyan mb-6 flex items-center">
            <Shield className="w-6 h-6 mr-2" />
            PROTOCOL STATUS
          </h2>
          <div className="space-y-4">
            {protocols.map((protocol, index) => (
              <motion.div
                key={protocol.protocol_name}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.1 * index }}
                className="flex items-center justify-between p-4 bg-matrix-bg rounded border border-matrix-border"
              >
                <div className="flex-1">
                  <div className="font-mono text-cyber-cyan font-semibold">
                    {protocol.protocol_name}
                  </div>
                  <div className="text-sm text-gray-400">
                    {protocol.actual_value}/{protocol.target_value} 
                    ({protocol.adherence_percentage.toFixed(1)}% adherence)
                  </div>
                </div>
                <div className="text-right">
                  <div className={`font-mono text-lg font-bold ${
                    protocol.adherence_percentage >= 100 ? 'text-neon-green' :
                    protocol.adherence_percentage >= 80 ? 'text-cyber-cyan' :
                    'text-cyber-pink'
                  }`}>
                    {protocol.adherence_percentage >= 100 ? '✓' : 
                     protocol.adherence_percentage >= 80 ? '~' : '✗'}
                  </div>
                  <div className="text-xs text-cyber-purple">
                    +{protocol.impact_years}y
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Achievements */}
        <motion.div
          initial={{ x: 50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="bg-matrix-surface border border-matrix-border rounded-lg p-6"
        >
          <h2 className="text-2xl font-cyber font-bold text-cyber-cyan mb-6 flex items-center">
            <Trophy className="w-6 h-6 mr-2" />
            ACHIEVEMENTS
          </h2>
          <div className="space-y-4">
            {achievements.map((achievement, index) => (
              <motion.div
                key={achievement.id}
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.1 * index }}
                className={`flex items-center p-4 rounded border ${
                  achievement.unlocked 
                    ? 'bg-matrix-bg border-neon-green' 
                    : 'bg-gray-900 border-gray-600 opacity-60'
                }`}
              >
                <div className="text-2xl mr-4">{achievement.icon}</div>
                <div className="flex-1">
                  <div className={`font-mono font-semibold ${
                    achievement.unlocked ? 'text-neon-green' : 'text-gray-400'
                  }`}>
                    {achievement.name}
                  </div>
                  <div className="text-sm text-gray-400">
                    {achievement.description}
                  </div>
                  {!achievement.unlocked && achievement.progress && (
                    <div className="mt-2 bg-gray-800 rounded-full h-2">
                      <div 
                        className="bg-cyber-cyan h-2 rounded-full transition-all"
                        style={{ width: `${achievement.progress}%` }}
                      ></div>
                    </div>
                  )}
                </div>
                <div className="text-right">
                  <div className="text-cyber-purple font-mono text-sm">
                    {achievement.xp_reward} XP
                  </div>
                  {achievement.unlocked && achievement.unlock_date && (
                    <div className="text-xs text-gray-500">
                      {new Date(achievement.unlock_date).toLocaleDateString()}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Footer */}
      <motion.footer
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="text-center py-8 border-t border-matrix-border"
      >
        <p className="font-mono text-cyber-cyan text-sm glitch">
          🧬 HACK YOUR BIOLOGY • REVERSE YOUR AGE • REACH THE FUTURE 🚀
        </p>
      </motion.footer>
    </div>
  );
}