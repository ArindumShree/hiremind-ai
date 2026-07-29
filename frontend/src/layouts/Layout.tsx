import { ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/authContextValue";

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <Link to="/" className="text-lg font-semibold text-brand">
            HireMind AI
          </Link>
          <nav className="space-x-4 text-sm">
            <Link to="/" className="hover:text-brand">
              Home
            </Link>
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="hover:text-brand">
                  Dashboard
                </Link>
                {user?.role === "recruiter" && (
                  <Link to="/recruiter/jobs" className="hover:text-brand">
                    My Jobs
                  </Link>
                )}
                {user?.role === "candidate" && (
                  <>
                    <Link to="/jobs" className="hover:text-brand">
                      Browse Jobs
                    </Link>
                    <Link to="/applications/mine" className="hover:text-brand">
                      My Applications
                    </Link>
                    <Link to="/resume" className="hover:text-brand">
                      Resume
                    </Link>
                  </>
                )}
                <span className="text-slate-500">{user?.full_name}</span>
                <button
                  onClick={() => void handleLogout()}
                  className="hover:text-brand"
                >
                  Log out
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="hover:text-brand">
                  Login
                </Link>
                <Link to="/register" className="hover:text-brand">
                  Register
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
      <footer className="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-500">
        HireMind AI — AI-powered Hiring Intelligence Platform
      </footer>
    </div>
  );
}
