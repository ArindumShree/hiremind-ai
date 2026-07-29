import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import candidateService from "../services/candidates";
import type { CandidateDetail } from "../types";
import ApplicationStatusBadge from "../components/ApplicationStatusBadge";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";

type Cell = (c: CandidateDetail) => React.ReactNode;

const ROWS: { label: string; render: Cell }[] = [
  { label: "Job", render: (c) => c.job_title ?? "-" },
  {
    label: "Status",
    render: (c) => <ApplicationStatusBadge status={c.status} />,
  },
  {
    label: "Skills",
    render: (c) => (c.skills.length ? c.skills.join(", ") : "-"),
  },
  {
    label: "Experience (yrs)",
    render: (c) => (c.experience_years != null ? c.experience_years : "-"),
  },
  { label: "College", render: (c) => c.college ?? "-" },
  {
    label: "Interview",
    render: (c) =>
      c.interview_status
        ? `${c.interview_status}${
            c.interview_score != null ? ` (${c.interview_score})` : ""
          }`
        : "-",
  },
  {
    label: "Evaluation",
    render: (c) =>
      c.evaluation_summary ? c.evaluation_summary.slice(0, 200) : "-",
  },
];

export default function CandidateComparePage() {
  const location = useLocation();
  const navigate = useNavigate();
  const preselect = (location.state as { preselect?: string[] } | null)
    ?.preselect;

  const [selected, setSelected] = useState<string[]>(preselect ?? []);

  const candidatesQuery = useQuery({
    queryKey: ["candidates-all"],
    queryFn: () => candidateService.list(),
  });

  const compareQuery = useQuery({
    queryKey: ["compare", selected],
    queryFn: () => candidateService.compare(selected),
    enabled: selected.length >= 2,
  });

  const all = candidatesQuery.data ?? [];

  function toggle(id: string) {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  }

  return (
    <section className="space-y-6">
      <button
        type="button"
        onClick={() => navigate("/recruiter/candidates")}
        className="text-sm text-brand hover:underline"
      >
        &larr; Back to candidates
      </button>
      <h1 className="text-2xl font-semibold">Compare Candidates</h1>

      {candidatesQuery.isError && (
        <ErrorMessage message="Could not load candidates." />
      )}
      {candidatesQuery.isLoading && <Loading label="Loading candidates..." />}

      {!candidatesQuery.isLoading && (
        <div className="rounded border border-slate-200 bg-white p-4">
          <p className="mb-2 text-sm text-slate-500">
            Select two or more candidates to compare.
          </p>
          <div className="flex flex-wrap gap-2">
            {all.map((c) => (
              <button
                key={c.application_id}
                type="button"
                onClick={() => toggle(c.application_id)}
                className={`rounded-full border px-3 py-1 text-sm ${
                  selected.includes(c.application_id)
                    ? "border-brand bg-brand text-white"
                    : "border-slate-300 text-slate-700"
                }`}
              >
                {c.full_name}
              </button>
            ))}
          </div>
        </div>
      )}

      {selected.length < 2 && (
        <p className="text-sm text-slate-500">
          Select at least two candidates.
        </p>
      )}

      {compareQuery.isError && (
        <ErrorMessage message="Could not compare selected candidates." />
      )}
      {compareQuery.isLoading && <Loading label="Comparing..." />}

      {compareQuery.data && (
        <div className="overflow-x-auto rounded border border-slate-200 bg-white">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 text-left text-slate-500">
              <tr>
                <th className="px-4 py-2">Field</th>
                {compareQuery.data.candidates.map((c) => (
                  <th key={c.application_id} className="px-4 py-2">
                    {c.full_name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {ROWS.map((row) => (
                <tr
                  key={row.label}
                  className="border-t border-slate-100 align-top"
                >
                  <td className="px-4 py-2 font-medium text-slate-700">
                    {row.label}
                  </td>
                  {compareQuery.data.candidates.map((c) => (
                    <td key={c.application_id} className="px-4 py-2 text-slate-700">
                      {row.render(c)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
