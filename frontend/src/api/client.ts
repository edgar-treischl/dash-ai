
const API_BASE_URL = import.meta.env.VITE_API_URL || "";

export interface QueryRequest {
  question: string;
}

export interface QueryResponse {
  answer?: string;
  response?: string;
  [key: string]: unknown;
}

export async function askQuestion(
  question: string
): Promise<QueryResponse> {
  const result = await fetch(`${API_BASE_URL}/api/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  if (!result.ok) {
    throw new Error(
      `API error: ${result.status} ${result.statusText}`
    );
  }

  return result.json();
}
