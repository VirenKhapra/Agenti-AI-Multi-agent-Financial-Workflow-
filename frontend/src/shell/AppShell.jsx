import React from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import {
  FiActivity,
  FiArchive,
  FiBell,
  FiCheckSquare,
  FiChevronDown,
  FiCommand,
  FiDatabase,
  FiLogOut,
  FiSearch,
  FiSettings,
  FiTrendingUp,
  FiUploadCloud,
  FiUserCheck,
  FiX,
} from "react-icons/fi";
import { createPortal } from "react-dom";
import { api } from "../api/client.js";
import { useAuth } from "../auth/AuthContext.jsx";

const navItems = [
  { to: "/dashboard", label: "Analytics", icon: FiTrendingUp, keywords: ["overview", "kpi", "transactions"] },
  { to: "/submissions", label: "Submissions", icon: FiArchive, keywords: ["history", "conversation", "reupload"] },
  { to: "/manager", label: "Manager", icon: FiCheckSquare, roles: ["manager"], keywords: ["review", "queue", "approve"] },
  { to: "/admin", label: "Admin", icon: FiUserCheck, roles: ["admin"], keywords: ["assignments", "managers", "employees"] },
  { to: "/settings", label: "Settings", icon: FiSettings, keywords: ["account", "profile", "security"] },
  { to: "/uploads", label: "Upload Center", icon: FiUploadCloud, keywords: ["upload", "files", "preview"] },
  { to: "/audit", label: "Audit Log", icon: FiActivity, roles: ["admin"], keywords: ["audit", "events", "history"] },
];

export default function AppShell() {
  const { user, logout } = useAuth();
  const [pendingActions, setPendingActions] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);
  const [commandQuery, setCommandQuery] = useState("");
  const navigate = useNavigate();
  const location = useLocation();

  const visibleNavItems = useMemo(
    () => navItems.filter((item) => !item.roles || item.roles.includes(user?.role)),
    [user?.role],
  );

  const initials = (user?.name || "LF")
    .split(" ")
    .map((word) => word[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  const commandItems = useMemo(() => {
    const query = commandQuery.trim().toLowerCase();
    if (!query) return visibleNavItems;
    return visibleNavItems.filter((item) => [item.label, ...(item.keywords || [])].join(" ").toLowerCase().includes(query));
  }, [commandQuery, visibleNavItems]);

  const loadPendingActions = useCallback(async () => {
    if (!user) {
      setPendingActions(0);
      setNotifications([]);
      return;
    }

    const endpoint = ["manager", "admin"].includes(user.role) ? "/uploads?status=pending" : "/uploads";
    const response = await api.get(endpoint);
    const items = response.data.slice(0, 5);
    setNotifications(items);
    setPendingActions(
      user.role === "employee"
        ? items.filter((item) => item.status === "pending" || item.status === "processing").length
        : response.data.length,
    );
  }, [user]);

  useEffect(() => {
    loadPendingActions().catch(() => {
      setPendingActions(0);
      setNotifications([]);
    });
  }, [loadPendingActions]);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setCommandOpen(true);
      }
      if (event.key === "Escape") {
        setCommandOpen(false);
        setShowNotifications(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  useEffect(() => {
    if (!commandOpen) setCommandQuery("");
  }, [commandOpen]);

  function openNotification(upload) {
    setShowNotifications(false);
    if (user?.role === "manager") return navigate(`/manager?submission_id=${upload.id}`);
    if (user?.role === "admin") return navigate("/admin");
    navigate("/uploads");
  }

  function goToCommandItem(item) {
    navigate(item.to);
    setCommandOpen(false);
  }

  return (
    <div className="lf-reference-shell">
      <aside className="lf-reference-sidebar">
        <div className="lf-reference-sidebar__brand">
          <div className="lf-reference-sidebar__logo">LF</div>
          <div>
            <div className="lf-reference-sidebar__title">LedgerFlow</div>
            <div className="lf-reference-sidebar__role">{user?.role ? `${user.role.charAt(0).toUpperCase()}${user.role.slice(1)}` : "Workspace"}</div>
          </div>
        </div>

        <nav className="lf-reference-sidebar__nav">
          {visibleNavItems.slice(0, 5).map((item) => {
            const Icon = item.icon;
            return (
              <NavLink key={item.to} to={item.to} className={({ isActive }) => `lf-reference-sidebar__link${isActive || location.pathname.startsWith(item.to + "/") ? " is-active" : ""}`}>
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        <div className="lf-reference-sidebar__footer">
          <div className="lf-reference-sidebar__user-avatar">{initials}</div>
          <div className="lf-reference-sidebar__user-copy">
            <strong>{user?.name || "User"}</strong>
            <span>{user?.email || ""}</span>
          </div>
        </div>
      </aside>

      <div className="lf-reference-main">
        <header className="lf-reference-topbar">
          <button className="lf-reference-search" onClick={() => setCommandOpen(true)} type="button">
            <FiSearch size={18} />
            <span>Search or run a command...</span>
            <kbd><FiCommand size={11} /> K</kbd>
          </button>

          <div className="lf-reference-topbar__right">
            <div className="lf-reference-connection">
              <span className="lf-reference-connection__dot" />
              <span>Connected</span>
            </div>

            <div className="lf-reference-notification-wrap">
              <button className="lf-reference-icon-button" onClick={async () => { await loadPendingActions(); setShowNotifications((v) => !v); }} type="button">
                <FiBell size={18} />
                {pendingActions > 0 && <span className="lf-reference-notification-badge">{pendingActions > 9 ? "9+" : pendingActions}</span>}
              </button>
              {showNotifications && (
                <div className="lf-reference-notification-panel">
                  <div className="lf-reference-notification-panel__head">
                    <strong>Notifications</strong>
                    <button className="lf-reference-icon-button is-small" onClick={() => setShowNotifications(false)} type="button"><FiX size={14} /></button>
                  </div>
                  <div>
                    {notifications.length ? notifications.map((upload) => (
                      <button key={upload.id} className="lf-reference-notification-row" onClick={() => openNotification(upload)} type="button">
                        <div>
                          <strong>{upload.filename}</strong>
                          <span>{upload.total_rows || upload.rows || 0} rows</span>
                        </div>
                      </button>
                    )) : <div className="lf-reference-empty">No notifications right now.</div>}
                  </div>
                </div>
              )}
            </div>

            <div className="lf-reference-avatar">{initials}</div>
            <button className="lf-reference-icon-button" onClick={logout} type="button"><FiLogOut size={18} /></button>
          </div>
        </header>

        <main className="lf-reference-content">
          <Outlet />
        </main>
      </div>

      {commandOpen && createPortal(
        <div className="lf-command-overlay" onClick={() => setCommandOpen(false)} role="presentation">
          <div className="lf-command-dialog" onClick={(event) => event.stopPropagation()}>
            <div className="lf-command-dialog__input">
              <FiSearch size={16} />
              <input autoFocus value={commandQuery} onChange={(event) => setCommandQuery(event.target.value)} placeholder="Jump to a page" />
            </div>
            <div className="lf-command-dialog__results">
              {commandItems.length ? commandItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button key={item.to} className="lf-command-result" onClick={() => goToCommandItem(item)} type="button">
                    <span className="lf-command-result__icon"><Icon size={15} /></span>
                    <span className="lf-command-result__copy"><strong>{item.label}</strong><small>{item.keywords?.join(" • ")}</small></span>
                  </button>
                );
              }) : <div className="lf-empty-inline">No matching pages.</div>}
            </div>
          </div>
        </div>,
        document.body,
      )}
    </div>
  );
}
