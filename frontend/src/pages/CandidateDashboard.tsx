import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import candidateService from "../services/candidates";
import jobService from "../services/jobs";
import type { ApplicationStatus, Job } from "../types";
import { APPLICATION_STATUS_TEXT } from "../types";
import ApplicationStatusBadge from "../components/ApplicationStatusBadge";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";

const STATUS_OPTIONS: ApplicationStatus[] = [
  "applied",
  "shortlisted",
  "interview_scheduled",
  "interview_completed",
  "rejected",
  "hired",
];

export default function CandidateDashboard() {
  const navigate = useNavigate();
  const [jobId, setJobId] = useState<string>("");
  const [status, setStatus] = useState<string>("");
  const [search, setSearch] = useState<string>("");

  const jobsQuery = useQuery({
    queryKey: ["recruiter-jobs-candidates"],
    queryFn: () => jobService.listMine(),
  });

  const query = useQuery({
    queryKey: ["candidates", jobId, status, search],
    queryFn: () =>
      candidateService.list({
        job_id: jobId || undefined,
        status: status || undefined,
        search: search || undefined,
      }),
  });

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Candidates</h1>
        <button
          type="button"
          onClick={() => navigate("/recruiter/candidates/compare")}
          className="rounded bg-brand px-3 py-2 text-sm font-semibold text-white"
        >
          Compare candidates
        </button>
      </div>

      <div className="flex flex-wrap gap-3">
        <input
          className="rounded border border-slate-300 px-3 py-2 text-sm focus:border-brand focus:outline-none"
          placeholder="Search name or email"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="rounded border border-slate-300 px-3 py-2 text-sm focus:border-brand focus:outline-none"
          value={jobId}
          onChange={(e) => setJobId(e.target.value)}
        >
          <option value="">All jobs</option>
          {(jobsQuery.data as Job[] | undefined)?.map((job) => (
            <option key={job.id} value={job.id}>
              {job.title}
            </option>
          ))}
        </select>
        <select
          className="rounded border border-slate-300 px-3 py-2 text-sm focus:border-brand focus:outline-none"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="">All statuses</option>
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {APPLICATION_STATUS_TEXT[s]}
            </option>
          ))}
        </select>
      </div>

      {query.isError && <ErrorMessage message="Could not load candidates." />}
      {query.isLoading && <Loading label="Loading candidates..." />}
      {!query.isLoading && query.data && query.data.length === 0 && (
        <p className="text-slate-600">No candidates match your filters.</p>
      )}

      {!query.isLoading && query.data && query.data.length > 0 && (
        <div className="overflow-x-auto rounded border border-slate-200 bg-white">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 text-left text-slate-500">
              <tr>
                <th className="px-4 py-2">Name</th>
                <th className="px-4 py-2">Job</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2">Skills</th>
                <th className="px-4 py-2">Interview</th>
                <th className="px-4 py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {query.data.map((c) => (
                <tr
                  key={c.application_id}
                  className="border-t border-slate-100"
                >
                  <td className="px-4 py-2">
                    <div className="font-medium text-slate-900">
                      {c.full_name}
                    </div>
                    <div className="text-slate-500">{c.email}</div>
                  </td>
                  <td className="px-4 py-2 text-slate-600">
                    {c.job_title ?? "-"}
                  </td>
                  <td className="px-4 py-2">
                    <ApplicationStatusBadge status={c.status} />
                  </td>
                  <td className="px-4 py-2 text-slate-600">
                    {c.skills.length ? c.skills.join(", ") : "-"}
                  </td>
                  <td className="px-4 py-2 text-slate-600">
                    {c.interview_status ?? "-"}
                    {c.interview_score != null && (
                      <span className="ml-1 text-slate-400">
                        ({c.interview_score})
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-2">
                    <button
                      type="button"
                      onClick={() =>
                        navigate(
                          `/recruiter/candidates/${c.application_id}`,
                        )
                      }
                      className="text-brand hover:underline"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
