import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/authContextValue";
import type { UserRole } from "../types";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState<UserRole>("candidate");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register({
        full_name: fullName,
        email,
        password,
        confirm_password: confirmPassword,
        role,
      });
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(extractError(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="mx-auto max-w-md space-y-6">
      <h1 className="text-2xl font-bold">Register</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <p className="rounded bg-red-50 px-3 py-2 text-sm text-red-600">
            {error}
          </p>
        )}
        <div>
          <label className="mb-1 block text-sm font-medium">Full name</label>
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
            className="w-full rounded border border-slate-300 px-3 py-2 focus:border-brand focus:outline-none"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full rounded border border-slate-300 px-3 py-2 focus:border-brand focus:outline-none"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full rounded border border-slate-300 px-3 py-2 focus:border-brand focus:outline-none"
          />
          <p className="mt-1 text-xs text-slate-500">
            8+ characters, with uppercase, lowercase, and a digit.
          </p>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">
            Confirm password
          </label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            className="w-full rounded border border-slate-300 px-3 py-2 focus:border-brand focus:outline-none"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">I am a</label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value as UserRole)}
            className="w-full rounded border border-slate-300 px-3 py-2 focus:border-brand focus:outline-none"
          >
            <option value="candidate">Candidate</option>
            <option value="recruiter">Recruiter</option>
          </select>
        </div>
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded bg-brand px-3 py-2 font-medium text-white disabled:opacity-60"
        >
          {submitting ? "Creating account…" : "Create account"}
        </button>
      </form>
      <p className="text-sm text-slate-600">
        Already have an account?{" "}
        <Link to="/login" className="text-brand hover:underline">
          Login
        </Link>
      </p>
    </section>
  );
}

interface ApiErrorShape {
  response?: { data?: { detail?: unknown } };
}

function extractError(err: unknown): string {
  const data = (err as ApiErrorShape)?.response?.data;
  if (data?.detail) {
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail.map((d: { msg?: string }) => d.msg ?? "").join(" ");
    }
  }
  return "Registration failed. Please review your details.";
}
