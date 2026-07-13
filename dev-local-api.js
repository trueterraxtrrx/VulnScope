import http from "node:http";

const token = "local-admin-token";

const state = {
  org: { id: "org-local", name: "KRYNEX Demo" },
  user: {
    id: "user-admin",
    organization_id: "org-local",
    email: "admin@krynex.local",
    full_name: "Security Admin",
    role: "admin"
  },
  assets: [
    {
      id: "asset-web-01",
      organization_id: "org-local",
      hostname: "web-01",
      ip_address: "10.0.0.10",
      os_name: "Ubuntu",
      os_version: "24.04",
      environment: "production",
      owner: "platform",
      criticality: 4,
      last_seen_at: null,
      created_at: new Date().toISOString()
    }
  ],
  software: [
    {
      id: "pkg-openssl",
      organization_id: "org-local",
      asset_id: "asset-web-01",
      name: "openssl",
      version: "3.0.13",
      vendor: "OpenSSL",
      package_type: "deb",
      created_at: new Date().toISOString()
    }
  ],
  cves: [
    {
      id: "cve-local-1",
      cve_id: "CVE-2026-0001",
      title: "OpenSSL package vulnerability",
      description: "Demo defensive-only CVE record matching installed openssl packages.",
      severity: "high",
      cvss_score: 8.1,
      published_at: null,
      references: [],
      created_at: new Date().toISOString()
    }
  ],
  vulnerabilities: [],
  tasks: [],
  imports: [],
  apiKeys: [],
  logs: []
};

function json(res, status, body) {
  res.writeHead(status, {
    "content-type": "application/json",
    "access-control-allow-origin": "*",
    "access-control-allow-methods": "GET,POST,PATCH,DELETE,OPTIONS",
    "access-control-allow-headers": "authorization,content-type"
  });
  res.end(JSON.stringify(body));
}

function readBody(req) {
  return new Promise((resolve) => {
    let data = "";
    req.on("data", (chunk) => {
      data += chunk;
    });
    req.on("end", () => {
      resolve(data ? JSON.parse(data) : {});
    });
  });
}

function audit(action, targetType = null, targetId = null, metadata = {}) {
  state.logs.unshift({
    id: `log-${Date.now()}-${state.logs.length}`,
    organization_id: "org-local",
    user_id: "user-admin",
    action,
    target_type: targetType,
    target_id: targetId,
    metadata_json: metadata,
    created_at: new Date().toISOString()
  });
}

function score(asset, cve) {
  const criticality = { 1: 0.7, 2: 0.9, 3: 1.0, 4: 1.25, 5: 1.5 }[asset.criticality] ?? 1;
  const exposure = asset.environment === "internet" ? 1.5 : asset.environment === "production" ? 1.25 : asset.environment === "staging" ? 1.0 : 0.8;
  return Math.min(10, Math.round(cve.cvss_score * criticality * exposure * 100) / 100);
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url ?? "/", "http://localhost:4445");
  if (req.method === "OPTIONS") return json(res, 204, {});
  if (url.pathname === "/health") return json(res, 200, { status: "ok" });

  const authed = req.headers.authorization === `Bearer ${token}`;
  const publicRoute = ["/auth/login", "/auth/register"].includes(url.pathname);
  if (!publicRoute && !authed) return json(res, 401, { detail: "Invalid token" });

  if (req.method === "POST" && url.pathname === "/auth/login") {
    const body = await readBody(req);
    if (body.email === "admin@krynex.local" && body.password === "password123") {
      audit("auth.login");
      return json(res, 200, { access_token: token, token_type: "bearer" });
    }
    return json(res, 401, { detail: "Invalid credentials" });
  }

  if (req.method === "POST" && url.pathname === "/auth/register") {
    return json(res, 200, { access_token: token, token_type: "bearer" });
  }

  if (req.method === "GET" && url.pathname === "/me") {
    return json(res, 200, { ...state.user, organization: state.org });
  }

  if (req.method === "GET" && url.pathname === "/assets") return json(res, 200, state.assets);
  if (req.method === "POST" && url.pathname === "/assets") {
    const body = await readBody(req);
    const asset = { id: `asset-${Date.now()}`, organization_id: "org-local", created_at: new Date().toISOString(), ...body };
    state.assets.push(asset);
    audit("asset.created", "asset", asset.id);
    return json(res, 200, asset);
  }
  if (req.method === "GET" && url.pathname.startsWith("/assets/")) {
    const asset = state.assets.find((item) => item.id === url.pathname.split("/").pop());
    return asset ? json(res, 200, asset) : json(res, 404, { detail: "Asset not found" });
  }

  if (req.method === "GET" && url.pathname === "/software") return json(res, 200, state.software);
  if (req.method === "POST" && url.pathname === "/software") {
    const body = await readBody(req);
    const item = { id: `pkg-${Date.now()}`, organization_id: "org-local", created_at: new Date().toISOString(), ...body };
    state.software.push(item);
    audit("software.created", "software_package", item.id);
    return json(res, 200, item);
  }

  if (req.method === "GET" && url.pathname === "/cves") return json(res, 200, state.cves);
  if (req.method === "POST" && url.pathname === "/cves") {
    const body = await readBody(req);
    const cve = { id: `cve-${Date.now()}`, created_at: new Date().toISOString(), published_at: null, references: [], ...body };
    state.cves.push(cve);
    audit("cve.created", "cve", cve.id);
    return json(res, 200, cve);
  }

  if (req.method === "GET" && url.pathname === "/vulnerabilities") return json(res, 200, state.vulnerabilities);
  if (req.method === "POST" && url.pathname === "/vulnerabilities/match") {
    let created = 0;
    for (const pkg of state.software) {
      const asset = state.assets.find((item) => item.id === pkg.asset_id);
      for (const cve of state.cves) {
        if (!asset || !`${cve.title} ${cve.description ?? ""}`.toLowerCase().includes(pkg.name.toLowerCase())) continue;
        if (state.vulnerabilities.some((v) => v.asset_id === asset.id && v.software_package_id === pkg.id && v.cve_id === cve.id)) continue;
        state.vulnerabilities.push({
          id: `vuln-${Date.now()}-${created}`,
          organization_id: "org-local",
          asset_id: asset.id,
          software_package_id: pkg.id,
          cve_id: cve.id,
          status: "open",
          risk_score: score(asset, cve),
          detected_at: new Date().toISOString(),
          fixed_at: null
        });
        created += 1;
      }
    }
    audit("vulnerability.match", null, null, { created });
    return json(res, 200, { created, message: `Created ${created} vulnerability records` });
  }
  if (req.method === "PATCH" && url.pathname.startsWith("/vulnerabilities/") && url.pathname.endsWith("/status")) {
    const id = url.pathname.split("/")[2];
    const body = await readBody(req);
    const vuln = state.vulnerabilities.find((item) => item.id === id);
    if (!vuln) return json(res, 404, { detail: "Vulnerability not found" });
    vuln.status = body.status;
    vuln.fixed_at = ["fixed", "accepted", "false_positive"].includes(body.status) ? new Date().toISOString() : null;
    audit("vulnerability.status_updated", "asset_vulnerability", vuln.id, { status: body.status });
    return json(res, 200, vuln);
  }

  if (req.method === "GET" && url.pathname === "/remediation-tasks") return json(res, 200, state.tasks);
  if (req.method === "POST" && url.pathname === "/remediation-tasks") {
    const body = await readBody(req);
    const task = { id: `task-${Date.now()}`, organization_id: "org-local", created_at: new Date().toISOString(), ...body };
    state.tasks.push(task);
    audit("remediation.created", "remediation_task", task.id);
    return json(res, 200, task);
  }
  if (req.method === "PATCH" && url.pathname.startsWith("/remediation-tasks/")) {
    const task = state.tasks.find((item) => item.id === url.pathname.split("/").pop());
    if (!task) return json(res, 404, { detail: "Task not found" });
    Object.assign(task, await readBody(req));
    audit("remediation.updated", "remediation_task", task.id);
    return json(res, 200, task);
  }

  if (req.method === "GET" && url.pathname === "/imports") return json(res, 200, state.imports);
  if (req.method === "POST" && url.pathname === "/imports/scan-results") {
    const body = await readBody(req);
    const record = {
      id: `import-${Date.now()}`,
      organization_id: "org-local",
      source: body.source ?? "api",
      status: "processed",
      summary: { assets_created: body.assets?.length ?? 0 },
      asset_count: body.assets?.length ?? 0,
      software_count: body.assets?.flatMap((asset) => asset.software ?? []).length ?? 0,
      vulnerability_count: 0,
      created_at: new Date().toISOString()
    };
    state.imports.unshift(record);
    audit("import.scan_results", "import", record.id, record.summary);
    return json(res, 200, record);
  }

  if (req.method === "GET" && url.pathname === "/dashboard/stats") {
    const open = state.vulnerabilities.filter((item) => item.status === "open");
    const avg = open.length ? open.reduce((sum, item) => sum + item.risk_score, 0) / open.length : 0;
    const severity_counts = {};
    for (const vuln of open) {
      const cve = state.cves.find((item) => item.id === vuln.cve_id);
      if (cve) severity_counts[cve.severity] = (severity_counts[cve.severity] ?? 0) + 1;
    }
    return json(res, 200, {
      assets: state.assets.length,
      software_packages: state.software.length,
      cves: state.cves.length,
      open_vulnerabilities: open.length,
      remediation_tasks: state.tasks.length,
      average_risk_score: Math.round(avg * 100) / 100,
      severity_counts
    });
  }

  if (req.method === "GET" && url.pathname === "/audit-logs") return json(res, 200, state.logs);
  if (req.method === "GET" && url.pathname === "/api-keys") return json(res, 200, state.apiKeys);
  if (req.method === "POST" && url.pathname === "/api-keys") {
    const body = await readBody(req);
    const apiToken = `vscope_${Math.random().toString(36).slice(2)}${Date.now()}`;
    const key = { id: `key-${Date.now()}`, name: body.name, key_prefix: apiToken.slice(0, 14), created_at: new Date().toISOString(), last_used_at: null };
    state.apiKeys.unshift(key);
    audit("api_key.created", "api_key", key.id);
    return json(res, 200, { ...key, token: apiToken });
  }

  return json(res, 404, { detail: "Not found" });
});

server.listen(4445, "127.0.0.1", () => {
  console.log("VulnScope local API listening on http://127.0.0.1:4445");
  console.log("Admin: admin@krynex.local / password123");
});
// Project version: VulnScope V1.5




