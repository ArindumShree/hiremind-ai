import { Link } from "react-router-dom";
import type { Job } from "../types";
import { EMPLOYMENT_TYPE_TEXT } from "../types";
import JobStatusBadge from "./JobStatusBadge";

interface Props {
  job: Job;
}

export default function JobCard({ job }: Props) {
  return (
    <Link
      to={`/jobs/${job.id}`}
      className="block rounded border border-slate-200 bg-white p-4 transition hover:border-brand"
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-semibold text-slate-900">{job.title}</h3>
          <p className="text-sm text-slate-600">{job.company_name}</p>
        </div>
        <JobStatusBadge status={job.status} />
      </div>
      <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-500">
        {job.location && <span>{job.location}</span>}
        {job.employment_type && (
          <span>{EMPLOYMENT_TYPE_TEXT[job.employment_type]}</span>
        )}
        {job.salary_range && <span>{job.salary_range}</span>}
      </div>
    </Link>
  );
}
