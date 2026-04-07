export default function ResultsCard({ result, selectedView }) {
  // Null-safe checks with comprehensive fallbacks
  if (!result || !selectedView || !result[selectedView]) return null;

  const currentResult = result[selectedView];

  // Handle error responses from API
  if (currentResult?.action?.error) {
    return (
      <div className="glass rounded-2xl p-6 border h-full flex flex-col justify-center">
        <div className="text-center">
          <p className="text-red-300 text-sm font-light">
            Analysis failed: {currentResult.action.error}
          </p>
        </div>
      </div>
    );
  }

  const getViewConfig = () => {
    const configs = {
      easy: {
        title: "Spam Detection",
        render: () => {
          // Safely extract is_spam with optional chaining, default to false
          const isSpam = currentResult?.action?.is_spam ?? false;
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
          // Safely extract priority with optional chaining, default to "Unknown"
          const priority = currentResult?.action?.priority ?? "unknown";
          return (
            <div className="p-8 rounded-xl border bg-yellow-500/10 border-yellow-500/30">
              <p className="text-4xl font-bold text-yellow-300">
                {priority?.toUpperCase() || "UNKNOWN"}
              </p>
            </div>
          );
        }
      },

      hard: {
        title: "Reply",
        render: () => {
          // Safely extract should_reply with optional chaining, default to false
          const shouldReply = currentResult?.action?.should_reply ?? false;
          const replyText = currentResult?.action?.reply_text ?? "";
          return (
            <div className="p-8 rounded-xl border bg-blue-500/10 border-blue-500/30">
              <p className="text-4xl font-bold text-blue-300">
                {shouldReply ? "Reply Needed" : "No Reply"}
              </p>

              {shouldReply && replyText && (
                <p className="mt-4 text-gray-300 text-sm">
                  "{replyText}"
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

  // Safely extract reward and latency with fallbacks
  const reward = currentResult?.reward ?? 0;
  const latency = currentResult?.latency_ms ?? 0;

  // Safely extract action fields with defaults
  const isSpam = currentResult?.action?.is_spam ?? false;
  const priority = currentResult?.action?.priority ?? "unknown";
  const shouldReply = currentResult?.action?.should_reply ?? false;
  const replyText = currentResult?.action?.reply_text ?? "";

  return (
    <div className="glass rounded-2xl p-6 border h-full flex flex-col justify-between transition-all duration-300 hover:scale-[1.01]">

      {/* HEADER */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-white">
          {config?.title || "Results"}
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
              ${isSpam
                ? "bg-red-500/20 border border-red-500/40"
                : "bg-emerald-500/20 border border-emerald-500/40"}`}
            >
              <span className="text-4xl">
                {isSpam ? "🚫" : "✅"}
              </span>
            </div>

            <h1 className={`text-3xl font-bold
              ${isSpam ? "text-red-300" : "text-emerald-300"}`}
            >
              {isSpam ? "Spam Detected" : "Legitimate Email"}
            </h1>
          </>
        )}

        {selectedView === "medium" && (
          <>
            <h1 className="text-4xl font-bold text-yellow-300">
              {priority?.toUpperCase() || "UNKNOWN"}
            </h1>
            <p className="text-gray-400 mt-2 text-sm">
              Priority classification
            </p>
          </>
        )}

        {selectedView === "hard" && (
          <>
            <h1 className="text-3xl font-bold text-blue-300">
              {shouldReply ? "Reply Needed" : "No Reply Needed"}
            </h1>

            {shouldReply && replyText && (
              <p className="mt-4 text-sm text-gray-300 max-w-xs">
                "{replyText}"
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
            {typeof reward === "number" ? reward.toFixed(2) : "0.00"}
          </p>
          <p className="text-xs text-gray-500">/1.00</p>
        </div>

        <div className="flex-1 text-right">
          <p className="text-sm text-gray-400 mb-2">Latency</p>
          <p className="text-4xl font-bold text-emerald-400">
            {typeof latency === "number" ? latency.toFixed(2) : "0.00"}
          </p>
          <p className="text-xs text-gray-500">ms</p>
        </div>

      </div>
    </div>
  );
}