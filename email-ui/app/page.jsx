'use client';

import { useState } from 'react';
import InputCard from '@/components/InputCard';
import ResultsCard from '@/components/ResultsCard';
import { compareEmail } from '@/lib/api';

export default function Page() {
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [task, setTask] = useState('easy');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedView, setSelectedView] = useState("easy");
  const handleAnalyze = async () => {
  console.log("HANDLE ANALYZE RUNNING");

  if (!subject.trim() || !body.trim()) {
    setError('Please enter both email subject and body');
    return;
  }

  setError(null);
  setLoading(true);
  setResult(null);

  try {
    const tasks = ["easy", "medium", "hard"];

    const results = await Promise.all(
      tasks.map((t) => compareEmail(t, subject, body))
    );

    console.log("RESULTS:", results);

    setResult({
      easy: results[0],
      medium: results[1],
      hard: results[2],
    });

  } catch (err) {
    console.error(err);
    setError(err.message || 'An error occurred');
  } finally {
    setLoading(false);
  }
};
  return (
    <div className="gradient-bg min-h-screen flex flex-col items-center justify-center p-4 sm:p-6 lg:p-8 overflow-hidden">
      {/* Background grid effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 opacity-5" style={{
          backgroundImage: 'linear-gradient(rgba(99,102,241,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(99,102,241,0.1) 1px, transparent 1px)',
          backgroundSize: '50px 50px'
        }} />
      </div>

      {/* Animated gradient orbs */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl opacity-20 animate-pulse" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl opacity-20 animate-pulse" />

      <div className="relative z-10 w-full max-w-5xl">
        {/* Header */}
        <div className="text-center mb-16 slide-up">
          <div className="mb-4 flex justify-center gap-2">
            <span className="px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-sm font-light">AI-Powered Analysis</span>
          </div>
          <h1 className="text-5xl sm:text-6xl font-bold text-white mb-4 tracking-tight">
            Email Assistant
          </h1>
          <p className="text-xl text-gray-400 font-light max-w-2xl mx-auto">
            Analyze emails with advanced AI-powered insights. Detect spam, classify priority, and generate replies instantly.
          </p>
          <div className="flex justify-center gap-3 mt-8">
            <div className="w-2 h-2 rounded-full bg-indigo-500 glow-primary" />
            <div className="w-2 h-2 rounded-full bg-emerald-500 glow-accent" />
            <div className="w-2 h-2 rounded-full bg-indigo-500 glow-primary" />
          </div>
        </div>

        {/* Main container */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
          {/* Input section */}
          <div className="lg:col-span-2 slide-up" style={{animationDelay: '0.1s'}}>
            <InputCard
              subject={subject}
              setSubject={setSubject}
              body={body}
              setBody={setBody}
              task={selectedView}
              setTask={setSelectedView}
              onAnalyze={handleAnalyze}
              loading={loading}
              error={error}
            />
          </div>

          {/* Results section */}
          <div className="lg:col-span-1 slide-up" style={{animationDelay: '0.2s'}}>
            {result ? (
              <ResultsCard result={result} selectedView={selectedView} />
            ) : (
              <div className="glass p-8 rounded-2xl h-full flex flex-col items-center justify-center border-2 border-dashed border-indigo-500/30 hover:border-indigo-500/60 transition-all duration-300">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-full bg-indigo-500/10 flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <p className="text-gray-400 font-light">
                    Results will appear here
                  </p>
                  <p className="text-gray-600 text-sm mt-2">
                    Analyze an email to get started
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer stats */}
        <div className="grid grid-cols-3 gap-4 mt-16 slide-up" style={{animationDelay: '0.3s'}}>
          <div className="glass p-6 rounded-xl text-center hover:bg-white/10 transition-all duration-300">
            <div className="text-3xl font-bold text-indigo-400">3</div>
            <div className="text-xs text-gray-500 mt-2 font-light">Analysis Types</div>
          </div>
          <div className="glass p-6 rounded-xl text-center hover:bg-white/10 transition-all duration-300">
            <div className="text-3xl font-bold text-emerald-400">AI</div>
            <div className="text-xs text-gray-500 mt-2 font-light">Smart Detection</div>
          </div>
          <div className="glass p-6 rounded-xl text-center hover:bg-white/10 transition-all duration-300">
            <div className="text-3xl font-bold text-purple-400">Real-time</div>
            <div className="text-xs text-gray-500 mt-2 font-light">Responses</div>
          </div>
        </div>
      </div>
    </div>
  );
}
