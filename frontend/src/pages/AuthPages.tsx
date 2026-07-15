import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShieldCheck } from "lucide-react";
import { api, LoginResponse, setToken } from "../api/client";

function AuthShell({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#eef2f7] px-4">
      <div className="w-full max-w-md border border-line bg-white p-6">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center bg-ink text-white">
            <ShieldCheck size={20} />
          </div>
          <div>
            <div className="text-sm font-semibold uppercase tracking-wide">VulnScope</div>
            <h1 className="text-xl font-semibold">{title}</h1>
          </div>
        </div>
        {children}
      </div>
    </div>
  );
}

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const result = await api.post<LoginResponse>("/auth/login", { email, password });
      setToken(result.access_token);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  }

  return (
    <AuthShell title="VulnScope Login">
      <form className="space-y-4" onSubmit={submit}>
        <input className="focus-ring w-full border border-line px-3 py-2" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <input className="focus-ring w-full border border-line px-3 py-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
        {error && <div className="border border-danger/30 bg-red-50 px-3 py-2 text-sm text-danger">{error}</div>}
        <button className="focus-ring w-full bg-ink px-4 py-2 font-semibold text-white">Sign in</button>
      </form>
      <p className="mt-4 text-sm text-slate-600">
        Need a tenant? <Link className="font-semibold text-signal" to="/register">Create one</Link>
      </p>
    </AuthShell>
  );
}

export function RegisterPage() {
  const [organizationName, setOrganizationName] = useState("KRYNEX Demo");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("password123");
  const [fullName, setFullName] = useState("Security Admin");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const result = await api.post<LoginResponse>("/auth/register", { organization_name: organizationName, email, password, full_name: fullName });
      setToken(result.access_token);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    }
  }

  return (
    <AuthShell title="Create Tenant">
      <form className="space-y-4" onSubmit={submit}>
        <input className="focus-ring w-full border border-line px-3 py-2" value={organizationName} onChange={(e) => setOrganizationName(e.target.value)} placeholder="Organization" />
        <input className="focus-ring w-full border border-line px-3 py-2" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Full name" />
        <input className="focus-ring w-full border border-line px-3 py-2" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <input className="focus-ring w-full border border-line px-3 py-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
        {error && <div className="border border-danger/30 bg-red-50 px-3 py-2 text-sm text-danger">{error}</div>}
        <button className="focus-ring w-full bg-ink px-4 py-2 font-semibold text-white">Register</button>
      </form>
      <p className="mt-4 text-sm text-slate-600">
        Already registered? <Link className="font-semibold text-signal" to="/login">Sign in</Link>
      </p>
    </AuthShell>
  );
}
// Project version: VulnScope V1.5





