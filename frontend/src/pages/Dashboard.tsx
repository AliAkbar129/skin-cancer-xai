import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Users, AlertTriangle, ShieldCheck, TrendingUp, ArrowUpRight, Activity, Clock } from 'lucide-react';
import { getScanRecords } from '../utils/storage';
import type { ScanRecord } from '../utils/storage';

const accuracyData = [
  { name: 'EfficientNet', score: 85.7 },
  { name: 'ViT', score: 83.9 },
  { name: 'Hybrid (Ours)', score: 89.4 },
];

const StatCard = ({ title, value, change, icon: Icon, color }: any) => {
  const colorMap: any = {
    blue: { bg: 'bg-blue-500/20', text: 'text-blue-400', glow: 'bg-blue-500/10' },
    red: { bg: 'bg-red-500/20', text: 'text-red-400', glow: 'bg-red-500/10' },
    emerald: { bg: 'bg-emerald-500/20', text: 'text-emerald-400', glow: 'bg-emerald-500/10' },
    purple: { bg: 'bg-purple-500/20', text: 'text-purple-400', glow: 'bg-purple-500/10' },
  };
  const theme = colorMap[color] || colorMap.blue;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative overflow-hidden rounded-2xl bg-white/5 border border-white/10 p-6 backdrop-blur-md group hover:bg-white/10 transition-colors"
    >
      <div className={`absolute top-0 right-0 w-32 h-32 ${theme.glow} rounded-full blur-3xl -mr-16 -mt-16 transition-transform group-hover:scale-150`} />
      <div className="relative z-10">
        <div className="flex justify-between items-start mb-4">
          <div className={`p-3 rounded-xl ${theme.bg} ${theme.text}`}>
            <Icon className="w-6 h-6" />
          </div>
          <div className="flex items-center space-x-1 text-emerald-400 text-sm font-medium bg-emerald-400/10 px-2 py-1 rounded-md">
            <ArrowUpRight className="w-3 h-3" />
            <span>{change}</span>
          </div>
        </div>
        <h3 className="text-gray-400 text-sm font-medium">{title}</h3>
        <p className="text-3xl font-bold text-gray-100 mt-1">{value}</p>
      </div>
    </motion.div>
  );
};

// Format date relative to now
function formatRelativeTime(dateString: string) {
  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
  const date = new Date(dateString);
  const now = new Date();
  const diffDays = Math.round((date.getTime() - now.getTime()) / (1000 * 3600 * 24));
  const diffHours = Math.round((date.getTime() - now.getTime()) / (1000 * 3600));
  const diffMins = Math.round((date.getTime() - now.getTime()) / (1000 * 60));

  if (Math.abs(diffMins) < 60) return rtf.format(diffMins, 'minute');
  if (Math.abs(diffHours) < 24) return rtf.format(diffHours, 'hour');
  return rtf.format(diffDays, 'day');
}

export function Dashboard() {
  const [recentScans, setRecentScans] = useState<ScanRecord[]>([]);

  useEffect(() => {
    // Load scans on mount
    setRecentScans(getScanRecords());
  }, []);

  const totalScans = recentScans.length;
  const highRiskCount = recentScans.filter(s => 
    ['Melanoma (mel)', 'Basal Cell Carcinoma (bcc)', 'Actinic Keratoses (akiec)'].includes(s.prediction)
  ).length;

  const avgConfidence = totalScans > 0 
    ? (recentScans.reduce((acc, curr) => acc + curr.confidence, 0) / totalScans * 100).toFixed(1)
    : "0.0";

  // Mocking the chart data dynamically based on today's count
  const scanData = [
    { name: 'Mon', scans: 45, highRisk: 4 },
    { name: 'Tue', scans: 52, highRisk: 7 },
    { name: 'Wed', scans: 38, highRisk: 2 },
    { name: 'Thu', scans: 65, highRisk: 12 },
    { name: 'Fri', scans: 48, highRisk: 5 },
    { name: 'Sat', scans: 25, highRisk: 1 },
    { name: 'Today', scans: 30 + totalScans, highRisk: 3 + highRiskCount },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Clinical Overview</h1>
        <p className="text-gray-400">Monitor diagnostic performance and recent patient scans.</p>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Scans (Live)" value={303 + totalScans} change={`+${totalScans} today`} icon={Activity} color="blue" />
        <StatCard title="High Risk Detected" value={34 + highRiskCount} change={`+${highRiskCount} today`} icon={AlertTriangle} color="red" />
        <StatCard title="Model Accuracy" value="89.4%" change="Stable" icon={ShieldCheck} color="emerald" />
        <StatCard title="Avg. Confidence" value={`${avgConfidence}%`} change="Live" icon={TrendingUp} color="purple" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-2 bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-md"
        >
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-white">Scan Volume & Risk Detection</h2>
            <select className="bg-black/50 border border-white/10 rounded-lg px-3 py-1 text-sm text-gray-300 outline-none focus:border-blue-500">
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
            </select>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={scanData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorScans" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="name" stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Area type="monotone" dataKey="scans" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorScans)" />
                <Area type="monotone" dataKey="highRisk" stroke="#ef4444" strokeWidth={3} fillOpacity={1} fill="url(#colorRisk)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Mini Chart - Paper Results */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-md flex flex-col"
        >
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-white">Architecture Comparison</h2>
            <p className="text-sm text-gray-400 mt-1">Accuracy on HAM10000 dataset</p>
          </div>
          <div className="flex-1 min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={accuracyData} layout="vertical" margin={{ top: 0, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={true} vertical={false} />
                <XAxis type="number" domain={[70, 100]} stroke="#6b7280" fontSize={12} />
                <YAxis dataKey="name" type="category" stroke="#9ca3af" fontSize={12} width={100} tickLine={false} axisLine={false} />
                <Tooltip cursor={{fill: 'rgba(255,255,255,0.05)'}} contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                <Bar dataKey="score" fill="#8b5cf6" radius={[0, 4, 4, 0]} barSize={24} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* Recent Scans Table */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white/5 border border-white/10 rounded-2xl backdrop-blur-md overflow-hidden"
      >
        <div className="p-6 border-b border-white/10 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-white">Your Recent Analyses (Live Data)</h2>
        </div>
        <div className="overflow-x-auto">
          {recentScans.length === 0 ? (
            <div className="p-12 text-center flex flex-col items-center">
              <Clock className="w-12 h-12 text-gray-500 mb-4" />
              <p className="text-gray-400">No analyses performed yet.</p>
              <p className="text-sm text-gray-500">Go to 'New Analysis' to run your first scan.</p>
            </div>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-black/20 text-xs uppercase tracking-wider text-gray-500 border-b border-white/10">
                  <th className="px-6 py-4 font-medium">Patient ID</th>
                  <th className="px-6 py-4 font-medium">Time</th>
                  <th className="px-6 py-4 font-medium">Prediction</th>
                  <th className="px-6 py-4 font-medium">Confidence</th>
                  <th className="px-6 py-4 font-medium">Uncertainty</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="text-sm text-gray-300 divide-y divide-white/5">
                {recentScans.map((row, i) => {
                  const isMalignant = ['Melanoma (mel)', 'Basal Cell Carcinoma (bcc)', 'Actinic Keratoses (akiec)'].includes(row.prediction);
                  const isReview = row.uncertainty > 40;
                  const statusLabel = isReview ? 'Review Needed' : (isMalignant ? 'Critical' : 'Benign');
                  
                  let badgeClass = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
                  if (isReview) badgeClass = "bg-orange-500/10 text-orange-400 border-orange-500/20";
                  else if (isMalignant) badgeClass = "bg-red-500/10 text-red-400 border-red-500/20";
                  
                  return (
                    <tr key={i} className="hover:bg-white/5 transition-colors group">
                      <td className="px-6 py-4 font-medium text-gray-200 group-hover:text-white transition-colors">{row.id}</td>
                      <td className="px-6 py-4 text-gray-400">{formatRelativeTime(row.date)}</td>
                      <td className="px-6 py-4">{row.prediction}</td>
                      <td className="px-6 py-4 font-mono">{(row.confidence * 100).toFixed(1)}%</td>
                      <td className="px-6 py-4 font-mono">{row.uncertainty.toFixed(1)}</td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${badgeClass}`}>
                          {statusLabel}
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </div>
      </motion.div>
    </div>
  );
}
