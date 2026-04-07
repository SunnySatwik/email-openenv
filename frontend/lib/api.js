const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://dante6969-email-openenv.hf.space";

/**
 * Validate and normalize API response structure
 * Ensures: { action: {...}, reward: number, latency_ms: number }
 */
function normalizeResponse(data) {
  return {
    action: data?.action || {},
    reward: typeof data?.reward === "number" ? data.reward : 0,
    latency_ms: typeof data?.latency_ms === "number" ? data.latency_ms : 0,
  };
}

export async function compareEmail(task, subject, body) {
  const trueLabelMap = {
    easy: { spam: true },
    medium: { priority: "high" },
    hard: { reply_required: true }
  };

  const response = await fetch(`${API_BASE_URL}/compare`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      task: task,
      email: {
        id: "1",
        sender: "user@test.com",
        subject: subject,
        body: body,
        timestamp: new Date().toISOString(),
        true_label: trueLabelMap[task]
      }
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `API Error: ${response.status} ${response.statusText}`
    );
  }

  const data = await response.json();

  // Validate and normalize response structure
  return normalizeResponse(data);
}