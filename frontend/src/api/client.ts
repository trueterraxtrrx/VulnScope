const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:4445";
export const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === "true";

const now = new Date().toISOString();
const demoAssets = [
  { id: "asset-demo-1", hostname: "edge-gateway-01", ip_address: "10.40.0.12", os_name: "Ubuntu", os_version: "24.04", environment: "production", criticality: 5, created_at: now },
  { id: "asset-demo-2", hostname: "crm-api-02", ip_address: "10.40.1.24", os_name: "Debian", os_version: "12", environment: "internal", criticality: 4, created_at: now }
];
const demoCves = [
  { id: "cve-demo-1", cve_id: "CVE-2026-10001", title: "Demo OpenSSL package exposure", severity: "high", cvss_score: 8.1, description: "Public demo finding.", references: [] },
  { id: "cve-demo-2", cve_id: "CVE-2026-10002", title: "Demo web server misconfiguration", severity: "medium", cvss_score: 5.9, description: "Public demo finding.", references: [] }
];
const demoVulnerabilities = [
  { id: "vuln-demo-1", asset_id: "asset-demo-1", cve_id: "cve-demo-1", risk_score: 92, status: "open", detected_at: now },
  { id: "vuln-demo-2", asset_id: "asset-demo-2", cve_id: "cve-demo-2", risk_score: 54, status: "accepted", detected_at: now }
];
const demoStore: Record<string, unknown> = {
  "/dashboard/stats": {
    assets: demoAssets.length,
    software_packages: 18,
    open_vulnerabilities: 2,
    remediation_tasks: 4,
    average_risk_score: 73,
    severity_counts: { critical: 0, high: 1, medium: 1, low: 0 }
  },
  "/assets": demoAssets,
  "/cves": demoCves,
  "/vulnerabilities": demoVulnerabilities,
  "/remediation-tasks": [
    { id: "task-demo-1", title: "Patch edge-gateway-01 OpenSSL", status: "open", priority: "high", due_date: now }
  ],
  "/imports": [
    { id: "import-demo-1", filename: "demo-sbom.json", status: "processed", created_at: now }
  ],
  "/software": [
    { id: "pkg-demo-1", name: "openssl", version: "3.0.13", vendor: "OpenSSL" }
  ]
};

function demoResponse<T>(path: string, options: RequestInit): T {
  if (options.method === "POST") {
    if (path === "/vulnerabilities/match" || path === "/imports/scan-results") return { ok: true } as T;
    const body = options.body ? JSON.parse(String(options.body)) : {};
    const created = { id: `demo-${Date.now()}`, created_at: now, ...body };
    const list = Array.isArray(demoStore[path]) ? demoStore[path] as unknown[] : [];
    demoStore[path] = [created, ...list];
    return created as T;
  }
  if (options.method === "PATCH") return { ok: true } as T;
  if (path.startsWith("/assets/")) return demoAssets.find((asset) => asset.id === path.split("/").pop()) as T;
  return (demoStore[path] ?? []) as T;
}

export type LoginResponse = {
  access_token: string;
  token_type: string;
};

export function getToken(): string | null {
  if (DEMO_MODE) return localStorage.getItem("vulnscope_token") || "demo-token";
  return localStorage.getItem("vulnscope_token");
}

export function setToken(token: string): void {
  localStorage.setItem("vulnscope_token", token);
}

export function clearToken(): void {
  localStorage.removeItem("vulnscope_token");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  if (DEMO_MODE) return demoResponse<T>(path, options);

  const token = getToken();
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) => request<T>(path, { method: "POST", body: JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) => request<T>(path, { method: "PATCH", body: JSON.stringify(body) })
};
// Project version: VulnScope V1.5

