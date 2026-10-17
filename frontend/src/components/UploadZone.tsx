import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, Image as ImageIcon } from 'lucide-react';
import { cn } from '../utils/cn';

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  isLoading: boolean;
}

export function UploadZone({ onFileSelect, isLoading }: UploadZoneProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024,
    disabled: isLoading
  });

  return (
    <div
      className={cn(
        "relative group cursor-pointer transition-all duration-300",
        isLoading && "opacity-50 pointer-events-none"
      )}
      {...getRootProps()}
    >
      <input {...getInputProps()} />
      <div className={cn(
        "absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl blur opacity-30 group-hover:opacity-70 transition duration-500",
        isDragActive && "opacity-100"
      )} />
      <div className={cn(
        "relative glass-panel p-12 flex flex-col items-center justify-center text-center space-y-4",
        isDragActive && "border-blue-400 bg-white/10"
      )}>
        <div className="p-4 bg-white/5 rounded-full">
          {isDragActive ? (
            <ImageIcon className="w-10 h-10 text-blue-400 animate-bounce" />
          ) : (
            <UploadCloud className="w-10 h-10 text-gray-300 group-hover:text-white transition-colors" />
          )}
        </div>
        <div>
          <p className="text-xl font-medium text-white mb-1">
            {isDragActive ? "Drop lesion image here..." : "Drag & drop your scan"}
          </p>
          <p className="text-sm text-gray-400">
            or click to browse from your device
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs text-gray-500 mt-4">
          <span>Supports JPG, JPEG, PNG</span>
          <span>•</span>
          <span>Max 5 MiB</span>
        </div>
      </div>
    </div>
  );
}
