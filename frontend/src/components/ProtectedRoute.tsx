import { Navigate } from "react-router-dom";
import { DEMO_MODE, getToken } from "../api/client";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (DEMO_MODE) return children;
  if (!getToken()) {
    return <Navigate to="/login" replace />;
  }
  return children;
}
// Project version: VulnScope V1.4
