import React, { useCallback, useEffect, useMemo, useState } from "react";
import { FiActivity, FiRefreshCw, FiShield } from "react-icons/fi";
import { api } from "../api/client.js";

const ACTION_COLORS = {
  upload_created: { bg: "#e8f5f0", color: "#0d6e56" },
  upload_approved: { bg: "#e8f5f0", color: "#0d6e56" },
  upload_declined: { bg: "#fcebeb", color: "#a32d2d" },
  reupload_requested: { bg: "#faeeda", color: "#854f0b" },
  reupload_submitted: { bg: "#e6f1fb", color: "#185fa5" },
  comment_added: { bg: "#eeedfe", color: "#534ab7" },
  user_assigned: { bg: "#e8f5f0", color: "#0d6e56" },
  user_reassigned: { bg: "#faeeda", color: "#854f0b" },
  login: { bg: "#f4f7f6", color: "#6b9080" },
  logout: { bg: "#f4f7f6", color: "#6b9080" },
};

export default function AuditPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterAction, setFilterAction] = useState("");

  const loadLogs = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get("/audit");
      setLogs(response.data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  const uniqueActions = useMemo(() => [...new Set(logs.map((log) => log.action))], [logs]);
  const filtered = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();
    return logs.filter((log) => {
      const matchesSearch = !normalizedSearch || [log.actor_name, log.action, log.target_label, log.detail]
        .some((value) => String(value || "").toLowerCase().includes(normalizedSearch));
      const matchesAction = !filterAction || log.action === filterAction;
      return matchesSearch && matchesAction;
    });
  }, [filterAction, logs, search]);

  return (
    <div className="app-page audit-page">
      <section className="audit-header">
        <div className="audit-title-row">
          <div className="audit-title-icon">
            <FiShield size={18} />
          </div>
          <div>
            <h1>Audit Log</h1>
            <p>Complete record of platform actions.</p>
          </div>
        </div>
        <button className="secondary-button" onClick={loadLogs}>
          <FiRefreshCw size={14} /> Refresh
        </button>
      </section>

      <section className="audit-filters">
        <label className="upload-search">
          <FiActivity />
          <input
            placeholder="Search by actor, action, or target..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </label>
        <select className="form-input" value={filterAction} onChange={(event) => setFilterAction(event.target.value)}>
          <option value="">All actions</option>
          {uniqueActions.map((action) => (
            <option key={action} value={action}>{formatAction(action)}</option>
          ))}
        </select>
      </section>

      <section className="elevated-panel audit-table-card">
        <div className="audit-table-scroll">
          <table className="audit-table">
            <thead>
              <tr>
                {["Time", "Actor", "Role", "Action", "Target", "Detail"].map((header) => (
                  <th key={header}>{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} className="audit-empty">Loading audit log...</td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="audit-empty">No audit entries found.</td>
                </tr>
              ) : filtered.map((log, index) => {
                const colors = ACTION_COLORS[log.action] || { bg: "#f4f7f6", color: "#6b9080" };
                return (
                  <tr key={log.id} style={{ animation: `staggerIn 0.3s ease-out ${index * 0.02}s both` }}>
                    <td className="audit-time">
                      {new Date(log.created_at).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}
                    </td>
                    <td className="audit-actor">{log.actor_name}</td>
                    <td><span className="audit-role">{log.actor_role}</span></td>
                    <td>
                      <span className="audit-action" style={{ background: colors.bg, color: colors.color }}>
                        {formatAction(log.action)}
                      </span>
                    </td>
                    <td className="audit-target">{log.target_label || "-"}</td>
                    <td className="audit-detail">{log.detail || "-"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <div className="audit-count">
        Showing {filtered.length} of {logs.length} entries - Last 200 actions
      </div>
    </div>
  );
}

function formatAction(action) {
  return String(action || "").replaceAll("_", " ");
}
