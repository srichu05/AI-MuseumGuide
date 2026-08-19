const getApiBase = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  return "http://127.0.0.1:5000";
};

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const base = getApiBase();
  const url = path.startsWith("http") ? path : `${base}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      ...(options?.headers || {}),
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || "API request failed");
  }
  return res.json();
}

export async function getArtifacts(params?: Record<string, string>) {
  const qs = params ? "?" + new URLSearchParams(params).toString() : "";
  return fetchApi<{ artifacts: Artifact[]; count: number }>(`/api/artifacts${qs}`);
}

export async function getArtifact(id: string) {
  return fetchApi<{ artifact: Artifact; exhibitions: Exhibition[]; related_works: Artifact[] }>(
    `/api/artifacts/${id}`
  );
}

export async function getGalleries() {
  return fetchApi<{ galleries: Gallery[] }>("/api/galleries");
}

export async function getExhibitions() {
  return fetchApi<{ exhibitions: Exhibition[] }>("/api/exhibitions");
}

export async function chatMessage(data: { query: string; session_id?: string; artifact_id?: string }) {
  return fetchApi<ChatResponse>("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function identifyArtifact(file: File, sessionId?: string) {
  const form = new FormData();
  form.append("image", file);
  if (sessionId) form.append("session_id", sessionId);
  const base = getApiBase();
  const url = `${base}/api/identify`;
  const res = await fetch(url, { method: "POST", body: form });
  return res.json();
}

export interface Artifact {
  artifact_id: string;
  name: string;
  type: string;
  artist_id?: string;
  artist_name?: string;
  period_name?: string;
  gallery_name?: string;
  floor?: number;
  year?: number;
  description?: string;
  image_path?: string;
}

export interface Exhibition {
  exhibition_id: string;
  name: string;
  start_date?: string;
  end_date?: string;
  description?: string;
}

export interface Gallery {
  gallery_id: string;
  name: string;
  floor?: number;
  location?: string;
  description?: string;
  artifact_count?: number;
  artifacts?: Artifact[];
}

export interface ChatResponse {
  session_id: string;
  query: string;
  answer: string;
  intent: string;
  sources: { title: string; source_type: string; document_id?: string }[];
  dialogue_state: Record<string, unknown>;
  latency_ms: number;
}

export interface IdentifyResponse {
  status: "identified" | "classified" | "unknown";
  message?: string;
  session_id?: string;
  artifact?: Artifact | null;
  confidence?: number | null;
  predicted_style?: string;
  recognition_source?: "cnn" | "groq_fallback" | string;
  model_version?: string;
  identification?: {
    predicted_style?: string;
    recognition_source?: string;
    cnn_confidence_recorded?: number;
    candidate_artist_name?: string;
  };
}

export function getArtifactImage(artifact: Artifact): string {
  if (artifact.image_path && artifact.image_path.startsWith("/")) {
    return artifact.image_path;
  }
  return `/artifacts/${artifact.artifact_id}.jpg`;
}
