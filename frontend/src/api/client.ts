
const API_BASE_URL = import.meta.env.VITE_API_URL || "";

export interface QueryRequest {
  question: string;
}

export interface QueryResponse {
  answer?: string;
  response?: string;
  [key: string]: unknown;
}

export class APIError extends Error {
  constructor(
    public status: number,
    public detail: unknown
  ) {
    super(
      typeof detail === "string"
        ? detail
        : typeof detail === "object" && detail !== null && "message" in detail
          ? String(detail.message)
          : "API error"
    );
  }
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
    let detail: unknown;
    try {
      const json = await result.json();
      detail = json.detail || json;
    } catch {
      detail = result.statusText;
    }

    throw new APIError(result.status, detail);
  }

  return result.json();
}

