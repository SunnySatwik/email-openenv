const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
        true_label: trueLabelMap[task]   // 🔥 correct placement
      }
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `API Error: ${response.status} ${response.statusText}`
    );
  }

  return response.json();
}