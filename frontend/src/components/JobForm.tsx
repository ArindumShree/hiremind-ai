import { useState } from "react";
import type { EmploymentType, Job } from "../types";
import { EMPLOYMENT_TYPE_TEXT } from "../types";

interface Props {
  initial?: Job;
  submitting: boolean;
  error: string | null;
  onSubmit: (values: JobFormValues) => void;
}

export interface JobFormValues {
  title: string;
  company_name: string;
  location: string;
  employment_type: EmploymentType | "";
  experience_required: string;
  salary_range: string;
  description: string;
  requirements: string;
  responsibilities: string;
  skills_required: string;
}

const EMPTY: JobFormValues = {
  title: "",
  company_name: "",
  location: "",
  employment_type: "",
  experience_required: "",
  salary_range: "",
  description: "",
  requirements: "",
  responsibilities: "",
  skills_required: "",
};

export default function JobForm({ initial, submitting, error, onSubmit }: Props) {
  const [values, setValues] = useState<JobFormValues>(
    initial
      ? {
          title: initial.title,
          company_name: initial.company_name,
          location: initial.location ?? "",
          employment_type: initial.employment_type ?? "",
          experience_required: initial.experience_required ?? "",
          salary_range: initial.salary_range ?? "",
          description: initial.description ?? "",
          requirements: initial.requirements ?? "",
          responsibilities: initial.responsibilities ?? "",
          skills_required: initial.skills_required ?? "",
        }
      : EMPTY,
  );

  function set<K extends keyof JobFormValues>(key: K, value: JobFormValues[K]) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit(values);
  }

  const input = "w-full rounded border border-slate-300 px-3 py-2 focus:border-brand focus:outline-none";

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <p className="rounded bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>
      )}
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium">Title</label>
          <input
            className={input}
            value={values.title}
            onChange={(e) => set("title", e.target.value)}
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Company</label>
          <input
            className={input}
            value={values.company_name}
            onChange={(e) => set("company_name", e.target.value)}
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Location</label>
          <input
            className={input}
            value={values.location}
            onChange={(e) => set("location", e.target.value)}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Employment type</label>
          <select
            className={input}
            value={values.employment_type}
            onChange={(e) =>
              set("employment_type", e.target.value as EmploymentType | "")
            }
          >
            <option value="">Select...</option>
            {(Object.keys(EMPLOYMENT_TYPE_TEXT) as EmploymentType[]).map((t) => (
              <option key={t} value={t}>
                {EMPLOYMENT_TYPE_TEXT[t]}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Experience</label>
          <input
            className={input}
            value={values.experience_required}
            onChange={(e) => set("experience_required", e.target.value)}
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Salary range</label>
          <input
            className={input}
            value={values.salary_range}
            onChange={(e) => set("salary_range", e.target.value)}
          />
        </div>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Description</label>
        <textarea
          className={input}
          rows={4}
          value={values.description}
          onChange={(e) => set("description", e.target.value)}
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Requirements</label>
        <textarea
          className={input}
          rows={3}
          value={values.requirements}
          onChange={(e) => set("requirements", e.target.value)}
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Responsibilities</label>
        <textarea
          className={input}
          rows={3}
          value={values.responsibilities}
          onChange={(e) => set("responsibilities", e.target.value)}
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Skills required</label>
        <input
          className={input}
          value={values.skills_required}
          onChange={(e) => set("skills_required", e.target.value)}
        />
      </div>
      <button
        type="submit"
        disabled={submitting}
        className="rounded bg-brand px-4 py-2 font-semibold text-white disabled:opacity-60"
      >
        {submitting ? "Saving..." : "Save"}
      </button>
    </form>
  );
}
