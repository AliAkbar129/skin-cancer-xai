import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, ShieldAlert, CheckCircle, Info } from 'lucide-react';

interface AnalysisProps {
  results: {
    prediction: string;
    probability: number;
    uncertainty: number;
    all_probabilities: Record<string, number>;
    xai: {
      gradcam: string;
      shap: string;
      lime: string;
    };
  };
  originalImage: string;
  onReset: () => void;
}

export function AnalysisResults({ results, originalImage, onReset }: AnalysisProps) {
  const [activeXAI, setActiveXAI] = useState<'none' | 'gradcam' | 'shap' | 'lime'>('gradcam');

  const xaiImage = activeXAI === 'none' ? originalImage : `data:image/jpeg;base64,${results.xai[activeXAI]}`;
  const isMalignant = ['Melanoma (mel)', 'Basal Cell Carcinoma (bcc)', 'Actinic Keratoses (akiec)'].includes(results.prediction);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="w-full max-w-5xl mx-auto space-y-6"
    >
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
          Analysis Complete
        </h2>
        <button 
          onClick={onReset}
          className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-medium transition-colors"
        >
          New Scan
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Left Column - Image & XAI */}
        <div className="space-y-4">
          <div className="relative aspect-square rounded-2xl overflow-hidden glass-panel border-white/20 p-2">
            <AnimatePresence mode="wait">
              <motion.img
                key={activeXAI}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                src={xaiImage}
                alt="Lesion analysis"
                className="w-full h-full object-cover rounded-xl"
              />
            </AnimatePresence>
            
            {/* Legend for XAI */}
            {activeXAI !== 'none' && (
              <div className="absolute bottom-4 left-4 right-4 p-3 bg-black/60 backdrop-blur-md rounded-lg text-xs">
                {activeXAI === 'gradcam' && "Grad-CAM: Heatmap highlights model's focus regions."}
                {activeXAI === 'shap' && "SHAP: Red indicates positive contribution, blue negative."}
                {activeXAI === 'lime' && "LIME: Highlights crucial superpixels for the prediction."}
              </div>
            )}
          </div>

          <div className="flex space-x-2">
            {['none', 'gradcam', 'shap', 'lime'].map((mode) => (
              <button
                key={mode}
                onClick={() => setActiveXAI(mode as any)}
                className={`flex-1 py-2 rounded-lg text-xs font-medium transition-colors ${
                  activeXAI === mode ? 'bg-blue-600 text-white' : 'bg-white/5 text-gray-400 hover:bg-white/10'
                }`}
              >
                {mode.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Right Column - Metrics */}
        <div className="space-y-6 flex flex-col justify-center">
          <div className={`p-6 rounded-2xl border ${isMalignant ? 'bg-red-500/10 border-red-500/30' : 'bg-emerald-500/10 border-emerald-500/30'}`}>
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-400 mb-1">Primary Prediction</p>
                <h3 className={`text-2xl font-bold ${isMalignant ? 'text-red-400' : 'text-emerald-400'}`}>
                  {results.prediction}
                </h3>
              </div>
              {isMalignant ? <ShieldAlert className="w-8 h-8 text-red-400" /> : <CheckCircle className="w-8 h-8 text-emerald-400" />}
            </div>
            
            <div className="mt-6 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Confidence</span>
                <span className="font-mono">{(results.probability * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-black/40 rounded-full h-2">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: `${results.probability * 100}%` }}
                  transition={{ duration: 1, delay: 0.2 }}
                  className={`h-2 rounded-full ${isMalignant ? 'bg-red-500' : 'bg-emerald-500'}`}
                />
              </div>
            </div>
          </div>

          <div className="glass-panel p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Activity className="w-5 h-5 text-purple-400" />
              <h4 className="font-medium text-purple-400">Model Uncertainty (MC-Dropout)</h4>
            </div>
            <p className="text-xs text-gray-400 mb-4">
              Measures the model's predictive variance. High uncertainty suggests seeking a dermatologist's review.
            </p>
            <div className="flex justify-between items-end">
              <div className="text-3xl font-mono">
                {results.uncertainty.toFixed(1)} <span className="text-sm text-gray-500">/ 100</span>
              </div>
              <div className={`text-sm ${results.uncertainty > 40 ? 'text-orange-400' : 'text-emerald-400'}`}>
                {results.uncertainty > 40 ? 'Review Recommended' : 'High Reliability'}
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
