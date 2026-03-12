const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

async function handleResponse<T>(response: Response, context: string): Promise<T> {
  if (!response.ok) {
    let detail: string | undefined;
    try {
      const body = (await response.json()) as { detail?: string };
      detail = body.detail;
    } catch {
      // ignore parse errors
    }
    throw new Error(detail ?? `${context}: HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function apiGet<T>(path: string): Promise<T> {
  return fetch(`${API_BASE_URL}${path}`).then((res) =>
    handleResponse<T>(res, `GET ${path}`)
  );
}

export function apiPost<TBody, TResponse>(path: string, body: TBody): Promise<TResponse> {
  return fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).then((res) => handleResponse<TResponse>(res, `POST ${path}`));
}

export function apiDelete<T>(path: string): Promise<T> {
  return fetch(`${API_BASE_URL}${path}`, { method: "DELETE" }).then((res) =>
    handleResponse<T>(res, `DELETE ${path}`)
  );
}
