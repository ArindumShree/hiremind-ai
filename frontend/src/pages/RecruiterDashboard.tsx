import { Link } from "react-router-dom";
import { useAuth } from "../context/authContextValue";

export default function RecruiterDashboard() {
  const { user } = useAuth();
  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-bold">Recruiter Dashboard</h1>
      <p className="text-slate-600">
        Welcome, {user?.full_name}. Manage your job postings below.
      </p>
      <div className="grid gap-4 sm:grid-cols-2">
        <Link
          to="/recruiter/jobs"
          className="rounded border border-slate-200 bg-white p-4 hover:border-brand"
        >
          <span className="font-medium">My Jobs</span>
          <p className="text-sm text-slate-500">Create, edit, publish and review applicants.</p>
        </Link>
        <Link
          to="/recruiter/jobs/new"
          className="rounded border border-slate-200 bg-white p-4 hover:border-brand"
        >
          <span className="font-medium">Post a Job</span>
          <p className="text-sm text-slate-500">Open a new role for candidates.</p>
        </Link>
        <Link
          to="/recruiter/candidates"
          className="rounded border border-slate-200 bg-white p-4 hover:border-brand"
        >
          <span className="font-medium">Review Candidates</span>
          <p className="text-sm text-slate-500">Browse, compare and report on applicants.</p>
        </Link>
      </div>
    </section>
  );
}
