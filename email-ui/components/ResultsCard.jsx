export default function ResultsCard({ result, selectedView }) {
  if (!result || !selectedView || !result[selectedView]) return null;

  const currentResult = result[selectedView];

  const getViewConfig = () => {
    const configs = {
      easy: {
        title: "Spam Detection",
        render: () => {
          const isSpam = currentResult.action.is_spam;
          return (
            <div className={`p-8 rounded-xl border ${isSpam ? 'bg-red-500/10 border-red-500/30' : 'bg-emerald-500/10 border-emerald-500/30'}`}>
              <div className="flex items-center gap-4">
                <span className="text-6xl">{isSpam ? '🚫' : '✅'}</span>
                <div>
                  <p className={`text-4xl font-bold ${isSpam ? 'text-red-300' : 'text-emerald-300'}`}>
                    {isSpam ? 'Spam Detected' : 'Legitimate'}
                  </p>
                </div>
              </div>
            </div>
          );
        }
      },

      medium: {
        title: "Priority",
        render: () => {
          const priority = currentResult.action.priority;
          return (
            <div className="p-8 rounded-xl border bg-yellow-500/10 border-yellow-500/30">
              <p className="text-4xl font-bold text-yellow-300">
                {priority?.toUpperCase()}
              </p>
            </div>
          );
        }
      },

      hard: {
        title: "Reply",
        render: () => {
          const shouldReply = currentResult.action.should_reply;
          return (
            <div className="p-8 rounded-xl border bg-blue-500/10 border-blue-500/30">
              <p className="text-4xl font-bold text-blue-300">
                {shouldReply ? "Reply Needed" : "No Reply"}
              </p>

              {shouldReply && currentResult.action.reply_text && (
                <p className="mt-4 text-gray-300 text-sm">
                  "{currentResult.action.reply_text}"
                </p>
              )}
            </div>
          );
        }
      }
    };

    return configs[selectedView];
  };

  const config = getViewConfig();

  return (
  <div className="glass rounded-2xl p-6 border h-full flex flex-col justify-between transition-all duration-300 hover:scale-[1.01]">

    {/* HEADER */}
    <div className="flex justify-between items-center mb-4">
      <h2 className="text-xl font-semibold text-white">
        {config.title}
      </h2>

      <div className="px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-xs text-emerald-300">
        Complete
      </div>
    </div>

    {/* MAIN RESULT (HERO SECTION) */}
    <div className="flex flex-col items-center justify-center text-center flex-1 py-6">

      {selectedView === "easy" && (
        <>
          <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-4 
            ${currentResult.action.is_spam 
              ? "bg-red-500/20 border border-red-500/40" 
              : "bg-emerald-500/20 border border-emerald-500/40"}`}
          >
            <span className="text-4xl">
              {currentResult.action.is_spam ? "🚫" : "✅"}
            </span>
          </div>

          <h1 className={`text-3xl font-bold 
            ${currentResult.action.is_spam ? "text-red-300" : "text-emerald-300"}`}
          >
            {currentResult.action.is_spam ? "Spam Detected" : "Legitimate Email"}
          </h1>
        </>
      )}

      {selectedView === "medium" && (
        <>
          <h1 className="text-4xl font-bold text-yellow-300">
            {currentResult.action.priority.toUpperCase()}
          </h1>
          <p className="text-gray-400 mt-2 text-sm">
            Priority classification
          </p>
        </>
      )}

      {selectedView === "hard" && (
        <>
          <h1 className="text-3xl font-bold text-blue-300">
            {currentResult.action.should_reply ? "Reply Needed" : "No Reply Needed"}
          </h1>

          {currentResult.action.reply_text && (
            <p className="mt-4 text-sm text-gray-300 max-w-xs">
              "{currentResult.action.reply_text}"
            </p>
          )}
        </>
      )}

    </div>

    {/* METRICS (CLEAN FOOTER) */}
    <div className="flex justify-between items-center gap-4 pt-6 border-t border-white/10">

      <div className="flex-1">
        <p className="text-sm text-gray-400 mb-2">Reward</p>
        <p className="text-4xl font-bold text-indigo-400">
          {currentResult.reward.toFixed(2)}
        </p>
        <p className="text-xs text-gray-500">/1.00</p>
      </div>

      <div className="flex-1 text-right">
        <p className="text-sm text-gray-400 mb-2">Latency</p>
        <p className="text-4xl font-bold text-emerald-400">
          {currentResult.latency_ms.toFixed(4)}
        </p>
        <p className="text-xs text-gray-500">ms</p>
      </div>

    </div>
  </div>
);
}