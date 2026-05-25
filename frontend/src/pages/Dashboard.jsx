import React from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import { FiDownload, FiFilter, FiRefreshCw, FiX, FiChevronLeft, FiChevronRight } from "react-icons/fi";
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid,
  ResponsiveContainer, Tooltip, XAxis, YAxis
} from "recharts";
import { DayPicker } from "react-day-picker";
import { format, addMonths, subMonths, addYears, subYears } from "date-fns";
import "react-day-picker/dist/style.css";
import { api } from "../api/client.js";
import { useAuth } from "../auth/AuthContext.jsx";
import { useWebSocket } from "../hooks/useWebSocket.js";

// ─── date presets — "custom" now opens the calendar picker ───────────────────

const DATE_PRESETS = [
  { key: "this_month",    label: "This Month" },
  { key: "six_months",    label: "6 Months" },
  { key: "twelve_months", label: "12 Months" },
  { key: "custom",        label: "Custom Range" }
];

const filterPillStyle = (active) => ({
  background:  active ? "#6366F1" : "#F6F7FD",
  color:       active ? "#fff"    : "#8A90A8",
  borderColor: active ? "#6366F1" : "#D9DCF4",
  border: "1px solid",
  borderRadius: 10,
  fontSize: 11,
  fontWeight: 500,
  padding: "7px 10px",
  cursor: "pointer"
});

// ─── inline calendar styles scoped to .lf-rdp ────────────────────────────────

const RDP_STYLES = `
  .lf-rdp { --rdp-cell-size: 36px; margin: 0; }
  .lf-rdp .rdp-months { display: flex; gap: 1.5rem; }
  .lf-rdp .rdp-month { flex: 1; }
  .lf-rdp .rdp-caption { display: flex; justify-content: center; padding: 0; margin-bottom: 1rem; }
  .lf-rdp .rdp-nav { display: none; }
  .lf-rdp .rdp-table { border-collapse: collapse; width: 100%; }
  .lf-rdp .rdp-head_cell {
    font-size: 10px; font-weight: 600; color: #9BA1B7;
    text-align: center; padding: 4px;
    text-transform: uppercase; letter-spacing: 0.06em;
  }
  .lf-rdp .rdp-cell { text-align: center; padding: 0; }
  .lf-rdp .rdp-day {
    width: 36px; height: 36px; border: none;
    background: transparent; cursor: pointer;
    border-radius: 8px; font-size: 13px; color: #3D3F5C;
  }
  .lf-rdp .rdp-day:hover:not(.rdp-day_selected):not(.rdp-day_disabled) {
    background-color: #EEF2FF;
  }
  .lf-rdp .rdp-day_selected {
    background-color: #6366F1 !important;
    color: white !important; font-weight: 500;
  }
  .lf-rdp .rdp-day_selected:hover { background-color: #4F46E5 !important; }
  .lf-rdp .rdp-day_today { background-color: #F6F7FD; font-weight: 600; }
  .lf-rdp .rdp-day_outside { color: #D9DCF4; }
  .lf-rdp .rdp-day_disabled { color: #D9DCF4; cursor: not-allowed; }
  .lf-rdp .rdp-day_range_start, .lf-rdp .rdp-day_range_end {
    background-color: #6366F1 !important; color: white !important;
  }
  .lf-rdp .rdp-day_range_middle {
    background-color: #EEF2FF !important; color: #3D3F5C !important;
    border-radius: 0;
  }
  .lf-rdp .rdp-caption_label { font-size: 13px; font-weight: 600; color: #3D3F5C; }
`;

// ─── DateRangePicker — floats below the "Custom Range" pill ──────────────────

function DateRangePicker({ onSelect, onClose }) {
  const [range, setRange]   = useState(undefined);
  const [month, setMonth]   = useState(new Date());
  const pickerRef           = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if (pickerRef.current && !pickerRef.current.contains(e.target)) onClose();
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [onClose]);

  const handleApply = () => {
    if (range?.from && range?.to) {
      onSelect({ from: range.from, to: range.to });
      onClose();
    }
  };

  return (
    <>
      <style>{RDP_STYLES}</style>
      <div
        ref={pickerRef}
        style={{
          position: "absolute",
          top: "calc(100% + 8px)",
          left: 0,
          background: "#fff",
          border: "1px solid #D9DCF4",
          borderRadius: 14,
          boxShadow: "0 8px 32px rgba(99,102,241,0.13)",
          padding: 20,
          zIndex: 100,
          minWidth: 560,
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: "#3D3F5C" }}>Select Date Range</span>
          <button
            onClick={onClose}
            style={{ background: "none", border: "none", cursor: "pointer", color: "#8A90A8", display: "flex", alignItems: "center", padding: 4, borderRadius: 6 }}
          >
            <FiX size={14} />
          </button>
        </div>

        {/* Month navigation */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
          <div style={{ display: "flex", gap: 4 }}>
            <NavBtn onClick={() => setMonth(subYears(month, 1))}  title="Prev year">
              <FiChevronLeft size={12} /><FiChevronLeft size={12} style={{ marginLeft: -5 }} />
            </NavBtn>
            <NavBtn onClick={() => setMonth(subMonths(month, 1))} title="Prev month">
              <FiChevronLeft size={12} />
            </NavBtn>
          </div>

          <span style={{ fontSize: 12, fontWeight: 600, color: "#3D3F5C" }}>
            {format(month, "MMMM yyyy")}
          </span>

          <div style={{ display: "flex", gap: 4 }}>
            <NavBtn onClick={() => setMonth(addMonths(month, 1))} title="Next month">
              <FiChevronRight size={12} />
            </NavBtn>
            <NavBtn onClick={() => setMonth(addYears(month, 1))}  title="Next year">
              <FiChevronRight size={12} /><FiChevronRight size={12} style={{ marginLeft: -5 }} />
            </NavBtn>
          </div>
        </div>

        {/* Calendar */}
        <div className="lf-rdp">
          <DayPicker
            mode="range"
            selected={range}
            onSelect={setRange}
            month={month}
            onMonthChange={setMonth}
            numberOfMonths={2}
            disabled={{ after: new Date() }}
          />
        </div>

        {/* Footer */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 16, paddingTop: 14, borderTop: "1px solid #E2E5F5" }}>
          <span style={{ fontSize: 11, color: "#8A90A8" }}>
            {range?.from && range?.to
              ? `${format(range.from, "MMM dd, yyyy")} – ${format(range.to, "MMM dd, yyyy")}`
              : "Pick a start and end date"}
          </span>
          <div style={{ display: "flex", gap: 8 }}>
            <button
              onClick={onClose}
              className="secondary-button"
              style={{ padding: "6px 14px", fontSize: 12 }}
            >
              Cancel
            </button>
            <button
              onClick={handleApply}
              disabled={!range?.from || !range?.to}
              style={{
                padding: "6px 14px", fontSize: 12, fontWeight: 600,
                background: range?.from && range?.to ? "#6366F1" : "#D9DCF4",
                color: "#fff", border: "none", borderRadius: 9, cursor: range?.from && range?.to ? "pointer" : "not-allowed"
              }}
            >
              Apply
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

function NavBtn({ onClick, title, children }) {
  return (
    <button
      onClick={onClick}
      title={title}
      style={{ display: "inline-flex", alignItems: "center", padding: "4px 6px", background: "#F6F7FD", border: "1px solid #D9DCF4", borderRadius: 6, cursor: "pointer", color: "#8A90A8" }}
      onMouseEnter={e => { e.currentTarget.style.background = "#EEF2FF"; e.currentTarget.style.color = "#6366F1"; }}
      onMouseLeave={e => { e.currentTarget.style.background = "#F6F7FD"; e.currentTarget.style.color = "#8A90A8"; }}
    >
      {children}
    </button>
  );
}

// ─── main Dashboard ───────────────────────────────────────────────────────────

export default function Dashboard() {
  const { user } = useAuth();
  const [data, setData]               = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  const [datePreset, setDatePreset]   = useState("six_months");
  const [showPicker, setShowPicker]   = useState(false);
  const [customLabel, setCustomLabel] = useState(null); // e.g. "Apr 01 – May 25"
  const [filters, setFilters]         = useState(() => ({
    status: "",
    ...datesForPreset("six_months")
  }));

  const loadKpis = useCallback(async () => {
    const params = new URLSearchParams();
    if (filters.status)   params.set("status",    filters.status);
    if (filters.dateFrom) params.set("date_from", `${filters.dateFrom}T00:00:00`);
    if (filters.dateTo)   params.set("date_to",   `${filters.dateTo}T23:59:59`);
    const response = await api.get(
      `/analytics/kpis${params.toString() ? `?${params.toString()}` : ""}`
    );
    setData(response.data);
  }, [filters]);

  useEffect(() => { loadKpis(); }, [loadKpis]);

  useWebSocket(
    "dashboard",
    useCallback(
      (event) => { if (event.event === "dashboard_refresh") loadKpis(); },
      [loadKpis]
    )
  );

  const totals = data?.totals || {};

  const trend =
    data?.upload_trends?.map((item) => ({
      day:      new Date(item.day).toLocaleDateString(),
      uploads:  item.uploads,
      approved: item.approved  || 0,
      declined: item.declined  || 0
    })) || [];

  const transactionTrend =
    data?.transaction_amount_trend?.map((item) => ({
      date:   new Date(item.date).toLocaleDateString(),
      amount: Number(item.amount || 0)
    })) || [];

  const kpiCards = [
    { label: "IN REVIEW",    value: totals.pending   ?? 0 },
    { label: "APPROVED",     value: totals.approved  ?? 0 },
    { label: "TOTAL AMOUNT", value: `₹${Number(totals.total_amount ?? 0).toLocaleString("en-IN")}` },
    { label: "REJECTED",     value: totals.declined  ?? 0 },
    { label: "COMPLETED",    value: totals.reviewed  ?? 0 }
  ];

  const amountCards = [
    { label: "TRANSACTION INITIATED", amount: Number(totals.transaction_initiated_amount ?? totals.total_amount ?? 0), delta: `${Number(totals.uploads ?? 0).toLocaleString("en-IN")} total` },
    { label: "PENDING",               amount: Number(totals.pending_amount ?? 0),                                      delta: "Awaiting review" },
    { label: "SUCCESSFUL",            amount: Number(totals.approved_amount ?? totals.cash ?? 0),                      delta: `${Number(totals.approval_rate ?? 0).toFixed(1)}% rate` },
    { label: "FAILED",                amount: Number(totals.declined_amount ?? 0),                                     delta: "Needs attention" }
  ];

  function updateFilter(name, value) {
    setFilters((cur) => ({ ...cur, [name]: value }));
  }

  function selectDatePreset(preset) {
    setDatePreset(preset);
    setShowPicker(false);
    setCustomLabel(null);
    if (preset !== "custom") {
      setFilters((cur) => ({ ...cur, ...datesForPreset(preset) }));
    } else {
      setShowPicker(true);
    }
  }

  function handleCustomRange({ from, to }) {
    const dateFrom = toDateInputValue(from);
    const dateTo   = toDateInputValue(to);
    setFilters((cur) => ({ ...cur, dateFrom, dateTo }));
    setCustomLabel(`${format(from, "MMM dd")} – ${format(to, "MMM dd, yyyy")}`);
  }

  function exportDashboardCsv() {
    const rows = [["Metric", "Value"], ...kpiCards.map((c) => [c.label, c.value])];
    const csv  = rows.map((r) => r.map((cell) => `"${String(cell).replaceAll('"', '""')}"`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href = url;
    a.download = `ledgerflow-dashboard-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="lf-analytics-page">
      {/* Header */}
      <section className="lf-analytics-page__header">
        <div>
          <h1>Analytics Overview</h1>
          <p>
            {user?.role === "employee"
              ? "Monitor your upload performance and key metrics"
              : "Monitor your transaction performance and key metrics"}
          </p>
        </div>
        <div className="lf-analytics-page__actions">
          <button className="secondary-button" onClick={() => setShowFilters((v) => !v)}>
            <FiFilter /> Filter
          </button>
          <button className="secondary-button" onClick={exportDashboardCsv}>
            <FiDownload /> Export
          </button>
          <button className="lf-reference-icon-button" onClick={loadKpis} type="button">
            <FiRefreshCw size={17} />
          </button>
        </div>
      </section>

      {/* Filters */}
      {showFilters && (
        <section className="lf-analytics-filters">
          <label>
            <span>Transaction Status</span>
            <select
              className="form-input"
              value={filters.status}
              onChange={(e) => updateFilter("status", e.target.value)}
            >
              <option value="">All statuses</option>
              <option value="Initiated">Initiated</option>
              <option value="Pending">Pending</option>
              <option value="Successful">Successful</option>
              <option value="Failed">Failed</option>
            </select>
          </label>

          <div>
            <span>Transaction Date</span>
            {/* Pill row + floating picker */}
            <div style={{ position: "relative", display: "inline-block" }}>
              <div className="lf-analytics-filters__pills">
                {DATE_PRESETS.map((p) => (
                  <button
                    key={p.key}
                    type="button"
                    style={filterPillStyle(datePreset === p.key)}
                    onClick={() => selectDatePreset(p.key)}
                  >
                    {p.key === "custom" && customLabel ? customLabel : p.label}
                  </button>
                ))}
              </div>

              {showPicker && (
                <DateRangePicker
                  onSelect={handleCustomRange}
                  onClose={() => setShowPicker(false)}
                />
              )}
            </div>
          </div>

          {/* Legacy manual date inputs — visible only when custom is active but picker is closed */}
          {datePreset === "custom" && !showPicker && customLabel && (
            <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <label>
                <span>From</span>
                <input
                  type="date"
                  className="form-input"
                  value={filters.dateFrom}
                  onChange={(e) => updateFilter("dateFrom", e.target.value)}
                />
              </label>
              <label>
                <span>To</span>
                <input
                  type="date"
                  className="form-input"
                  value={filters.dateTo}
                  onChange={(e) => updateFilter("dateTo", e.target.value)}
                />
              </label>
            </div>
          )}
        </section>
      )}

      {/* KPI Cards */}
      <section className="lf-kpi-grid" style={{ display: "grid", gridTemplateColumns: `repeat(${kpiCards.length}, 1fr)`, gap: 16 }}>
        {kpiCards.map((card) => (
          <div key={card.label} className="lf-kpi-card">
            <div className="lf-kpi-card__label">{card.label}</div>
            <div className="lf-kpi-card__value">{card.value}</div>
          </div>
        ))}
      </section>

      {/* Amount Cards */}
      <section className="lf-amount-grid">
        {amountCards.map((card) => (
          <div key={card.label} className="lf-amount-card">
            <div className="lf-kpi-card__label">{card.label}</div>
            <div className="lf-amount-card__row">
              <div className="lf-kpi-card__value">
                ₹{Math.round(card.amount).toLocaleString("en-IN")}
              </div>
              <div className="lf-kpi-card__delta">{card.delta}</div>
            </div>
          </div>
        ))}
      </section>

      {/* Charts */}
      <section className="lf-chart-grid">
        <div className="lf-chart-card">
          <div className="lf-chart-card__head">
            <h2>Activity Trend</h2>
            <p>Daily transaction volume over time</p>
          </div>
          <div className="lf-chart-card__body" style={{ height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trend}>
                <defs>
                  <linearGradient id="lfChartFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#6366F1" stopOpacity={0.28} />
                    <stop offset="95%" stopColor="#6366F1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E5F5" vertical={false} />
                <XAxis dataKey="day"  tick={{ fontSize: 11, fill: "#9BA1B7" }} />
                <YAxis               tick={{ fontSize: 11, fill: "#9BA1B7" }} />
                <Tooltip />
                <Area type="monotone" dataKey="uploads" stroke="#6366F1" fill="url(#lfChartFill)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="lf-chart-card">
          <div className="lf-chart-card__head">
            <h2>Revenue / Expenses</h2>
            <p>Monthly comparison breakdown</p>
          </div>
          <div className="lf-chart-card__body" style={{ height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={transactionTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E5F5" vertical={false} />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#9BA1B7" }} />
                <YAxis               tick={{ fontSize: 11, fill: "#9BA1B7" }} />
                <Tooltip formatter={(v) => [`₹${Number(v).toLocaleString("en-IN")}`, "Amount"]} />
                <Bar dataKey="amount" fill="#6366F1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>
    </div>
  );
}

// ─── helpers ──────────────────────────────────────────────────────────────────

function datesForPreset(preset) {
  const today = new Date();
  const end   = toDateInputValue(today);
  if (preset === "this_month")
    return { dateFrom: toDateInputValue(new Date(today.getFullYear(), today.getMonth(), 1)), dateTo: end };
  if (preset === "six_months")
    return { dateFrom: toDateInputValue(new Date(today.getFullYear(), today.getMonth() - 5, 1)), dateTo: end };
  if (preset === "twelve_months")
    return { dateFrom: toDateInputValue(new Date(today.getFullYear(), today.getMonth() - 11, 1)), dateTo: end };
  return { dateFrom: "", dateTo: "" };
}

function toDateInputValue(date) {
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 10);
}
