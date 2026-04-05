export default function InputCard({
  subject,
  setSubject,
  body,
  setBody,
  task,
  setTask,
  onAnalyze,
  loading,
  error,
})
{
  return (
    <div className="glass rounded-2xl p-8 space-y-6 border">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-2xl font-bold text-white">Email Analysis</h2>
        <div className="flex gap-2">
          <div className="w-3 h-3 rounded-full bg-indigo-500 glow-primary" />
          <div className="w-3 h-3 rounded-full bg-indigo-500/50" />
          <div className="w-3 h-3 rounded-full bg-indigo-500/30" />
        </div>
      </div>
      <p className="text-gray-400 text-sm font-light">Paste your email content and select an analysis type</p>

      <div className="space-y-5">
        {/* Subject Input */}
        <div>
          <label htmlFor="subject" className="block text-sm font-semibold text-gray-200 mb-2 flex items-center gap-2">
            <svg className="w-4 h-4 text-indigo-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
              <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
            </svg>
            Subject Line
          </label>
          <input
            id="subject"
            type="text"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="e.g., Limited time offer: 50% off today only"
            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 hover:bg-white/10"
            disabled={loading}
          />
        </div>

        {/* Body Input */}
        <div>
          <label htmlFor="body" className="block text-sm font-semibold text-gray-200 mb-2 flex items-center gap-2">
            <svg className="w-4 h-4 text-indigo-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
            </svg>
            Email Body
          </label>
          <textarea
            id="body"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Paste the full email content here..."
            rows="6"
            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 hover:bg-white/10 resize-none font-light"
            disabled={loading}
          />
        </div>

        {/* Task Selection */}
        <div>
          <label htmlFor="task" className="block text-sm font-semibold text-gray-200 mb-3">Analysis Type</label>
          <div className="grid grid-cols-3 gap-3">
            {[
              { value: 'easy', label: 'Spam', icon: '🚫' },
              { value: 'medium', label: 'Priority', icon: '⭐' },
              { value: 'hard', label: 'Reply', icon: '✉️' }
            ].map((option) => (
              <button
                key={option.value}
                onClick={() => setTask(option.value)}
                disabled={loading}
                className={`py-3 px-3 rounded-lg transition-all duration-200 flex flex-col items-center gap-2 font-medium text-sm ${
                  task === option.value
                    ? 'bg-indigo-500/30 border-2 border-indigo-500 text-indigo-200 shadow-lg shadow-indigo-500/20'
                    : 'bg-white/5 border-2 border-white/10 text-gray-300 hover:bg-white/10 hover:border-white/20'
                } disabled:opacity-50`}
              >
                <span className="text-xl">{option.icon}</span>
                <span>{option.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg fade-in">
            <div className="flex gap-3 items-start">
              <svg className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <p className="text-red-300 text-sm font-light">{error}</p>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          onClick={() => {
              console.log("BUTTON CLICKED");
              onAnalyze();
            }}
          disabled={loading}
          className="w-full mt-8 px-6 py-4 bg-gradient-to-r from-indigo-600 to-indigo-500 text-white font-semibold rounded-lg hover:from-indigo-700 hover:to-indigo-600 transition-all duration-300 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed flex items-center justify-center gap-3 group relative overflow-hidden glow-primary"
        >
          <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          {loading ? (
            <>
              <svg
                className="animate-spin h-5 w-5 text-white relative z-10"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              <span className="relative z-10">Analyzing with AI...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5 relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span className="relative z-10">Analyze Email</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
