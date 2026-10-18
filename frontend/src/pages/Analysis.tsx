import { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { UploadZone } from '../components/UploadZone';
import { AnalysisResults } from '../components/AnalysisResults';

export function Analysis() {
  const [file, setFile] = useState<File | null>(null);
  const [originalImageUrl, setOriginalImageUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = async (selectedFile: File) => {
    setFile(selectedFile);
    if (originalImageUrl) URL.revokeObjectURL(originalImageUrl);
    setOriginalImageUrl(URL.createObjectURL(selectedFile));
    setIsAnalyzing(true);
    setError(null);
    setResults(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const backendUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/analyze`;
      const response = await axios.post(backendUrl, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setResults(response.data);
      

    } catch (err) {
      console.error(err);
      setError(axios.isAxiosError(err) ? String(err.response?.data?.detail || 'Backend unavailable') : 'Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const reset = () => {
    if (originalImageUrl) URL.revokeObjectURL(originalImageUrl);
    setFile(null);
    setOriginalImageUrl(null);
    setResults(null);
    setError(null);
  };

  return (
    <div className="w-full max-w-7xl mx-auto min-h-[80vh] flex flex-col justify-center items-center">
      <AnimatePresence mode="wait">
        {!file && !results && (
          <motion.div
            key="upload"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="w-full max-w-3xl text-center space-y-8"
          >
            <div className="space-y-4">
              <h1 className="text-4xl font-bold text-white">New AI Analysis</h1>
              <p className="text-gray-400 max-w-xl mx-auto">
                Upload a dermoscopic image. The installed trained baseline will return research probabilities. A model must be trained before this feature is available.
              </p>
            </div>
            <UploadZone onFileSelect={handleFileSelect} isLoading={false} />
          </motion.div>
        )}

        {isAnalyzing && (
          <motion.div
            key="analyzing"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col items-center justify-center space-y-6 my-20"
          >
            <div className="relative w-32 h-32">
              <div className="absolute inset-0 border-t-2 border-blue-500 rounded-full animate-spin"></div>
              <div className="absolute inset-2 border-r-2 border-purple-500 rounded-full animate-spin-reverse"></div>
              <div className="absolute inset-4 border-b-2 border-emerald-500 rounded-full animate-spin"></div>
              <Loader2 className="absolute inset-0 m-auto w-8 h-8 text-white animate-pulse" />
            </div>
            <div className="text-center">
                <p className="text-lg font-medium text-gray-200">Processing Scan...</p>
                <p className="text-sm text-gray-500 mt-2">Computing probabilities using the installed research model</p>
            </div>
          </motion.div>
        )}

        {error && (
           <motion.div
            key="error"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="glass-panel p-6 border-red-500/50 bg-red-500/10 text-red-200 text-center max-w-lg"
           >
              <p>{error}</p>
              <button onClick={reset} className="mt-4 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-sm font-medium transition-colors">
                Try Again
              </button>
           </motion.div>
        )}

        {results && !isAnalyzing && (
          <AnalysisResults 
            results={results} 
            originalImage={originalImageUrl!} 
            onReset={reset} 
          />
        )}
      </AnimatePresence>
    </div>
  );
}
