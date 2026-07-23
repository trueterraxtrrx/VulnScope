import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import { Card, PageHeader } from "../components/Layout";
import { Asset } from "../types/models";

export function AssetDetailPage() {
  const { id } = useParams();
  const [asset, setAsset] = useState<Asset | null>(null);

  useEffect(() => {
    if (id) api.get<Asset>(`/assets/${id}`).then(setAsset);
  }, [id]);

  if (!asset) return <div>Loading...</div>;

  return (
    <>
      <PageHeader title={asset.hostname} />
      <Card>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[
            ["IP address", asset.ip_address || "-"],
            ["OS", [asset.os_name, asset.os_version].filter(Boolean).join(" ") || "-"],
            ["Environment", asset.environment],
            ["Owner", asset.owner || "-"],
            ["Criticality", asset.criticality],
            ["Last seen", asset.last_seen_at || "-"]
          ].map(([label, value]) => (
            <div key={String(label)}>
              <div className="text-xs uppercase text-slate-500">{label}</div>
              <div className="mt-1 font-medium">{value}</div>
            </div>
          ))}
        </div>
      </Card>
    </>
  );
}
// Project version: VulnScope V1.5









