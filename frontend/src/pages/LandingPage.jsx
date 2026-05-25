import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext.jsx";

export default function LandingPage() {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

  React.useEffect(() => {
    if (isAuthenticated) {
      const home =
        user?.role === "admin" ? "/admin" :
        user?.role === "manager" ? "/manager" :
        "/dashboard";
      navigate(home, { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <div className="max-w-4xl mx-auto px-6 py-16 text-center">
        <h1 className="text-4xl md:text-5xl font-extrabold text-slate-900 mb-4">LedgerFlow Analytics</h1>
        <p className="text-lg text-slate-700 mb-8">Secure, real-time ledger insights for finance teams — fast reconciliation and actionable dashboards.</p>
        <div className="flex justify-center gap-4">
          <a href="/login" className="bg-sky-600 hover:bg-sky-700 text-white px-6 py-3 rounded-md font-semibold">Get Started</a>
          <a href="#features" className="text-slate-700 px-6 py-3 rounded-md border border-slate-200">Learn more</a>
        </div>
      </div>
    </div>
  );
}
