export async function apiFetch(url: string, options: RequestInit = {}) {
  const headers: Record<string, string> = {};
  if (options.headers) Object.assign(headers, options.headers);
  return fetch(url, { ...options, headers });
}
