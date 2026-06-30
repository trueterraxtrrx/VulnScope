export type Asset = {
  id: string;
  organization_id: string;
  hostname: string;
  ip_address?: string | null;
  os_name?: string | null;
  os_version?: string | null;
  environment: string;
  owner?: string | null;
  criticality: number;
  last_seen_at?: string | null;
  created_at: string;
};

export type SoftwarePackage = {
  id: string;
  organization_id: string;
  asset_id: string;
  name: string;
  version: string;
  vendor?: string | null;
  package_type: string;
  created_at: string;
};

export type CVE = {
  id: string;
  cve_id: string;
  title: string;
  description?: string | null;
  severity: string;
  cvss_score: number;
  published_at?: string | null;
  references: string[];
  created_at: string;
};

export type Vulnerability = {
  id: string;
  organization_id: string;
  asset_id: string;
  software_package_id: string;
  cve_id: string;
  status: string;
  risk_score: number;
  detected_at: string;
  fixed_at?: string | null;
};

export type RemediationTask = {
  id: string;
  organization_id: string;
  asset_vulnerability_id?: string | null;
  title: string;
  description?: string | null;
  status: string;
  assignee?: string | null;
  due_date?: string | null;
  created_at: string;
};

export type DashboardStats = {
  assets: number;
  software_packages: number;
  cves: number;
  open_vulnerabilities: number;
  remediation_tasks: number;
  average_risk_score: number;
  severity_counts: Record<string, number>;
};
// Project version: VulnScope V1.3
