import { useAuth } from "../context/authContextValue";

export default function Dashboard() {
  const { user, logout } = useAuth();

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <button
          onClick={() => void logout()}
          className="rounded border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100"
        >
          Log out
        </button>
      </div>
      <p className="text-slate-600">
        Welcome, {user?.full_name}. You are signed in as a{" "}
        <span className="font-medium">{user?.role}</span>.
      </p>
      <p className="text-slate-600">
        Role-specific dashboards are available below. Resume, jobs, and AI
        interview features arrive in later stages.
      </p>
      <div className="grid gap-4 sm:grid-cols-2">
        <a
          href="/candidate"
          className="rounded border border-slate-200 bg-white p-4 hover:border-brand"
        >
          <span className="font-medium">Candidate Dashboard</span>
          <p className="text-sm text-slate-500">
            Interview scheduling and status.
          </p>
        </a>
        <a
          href="/recruiter"
          className="rounded border border-slate-200 bg-white p-4 hover:border-brand"
        >
          <span className="font-medium">Recruiter Dashboard</span>
          <p className="text-sm text-slate-500">
            Job postings and candidate evaluations.
          </p>
        </a>
      </div>
    </section>
  );
}
