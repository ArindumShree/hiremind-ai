import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import jobService from "../services/jobs";
import { EMPLOYMENT_TYPE_TEXT } from "../types";
import type { EmploymentType } from "../types";
import JobStatusBadge from "../components/JobStatusBadge";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";

export default function JobDetails() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [cover, setCover] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [applied, setApplied] = useState(false);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["job", id],
    queryFn: () => jobService.get(id as string),
    enabled: Boolean(id),
  });

  const applyMutation = useMutation({
    mutationFn: () => jobService.apply(id as string, cover),
    onSuccess: () => {
      setApplied(true);
      queryClient.invalidateQueries({ queryKey: ["my-applications"] });
    },
    onError: (e: unknown) => setError(extractError(e)),
  });

  if (isLoading) return <Loading label="Loading job..." />;
  if (isError || !data) return <ErrorMessage message="Job not found." />;

  return (
    <section className="space-y-6">
      <Link to="/jobs" className="text-sm text-brand hover:underline">
        &larr; Back to jobs
      </Link>
      <div className="flex items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">{data.title}</h1>
          <p className="text-slate-600">{data.company_name}</p>
        </div>
        <JobStatusBadge status={data.status} />
      </div>
      <div className="flex flex-wrap gap-2 text-sm text-slate-500">
        {data.location && <span>{data.location}</span>}
        {data.employment_type && (
          <span>{EMPLOYMENT_TYPE_TEXT[data.employment_type as EmploymentType]}</span>
        )}
        {data.salary_range && <span>{data.salary_range}</span>}
        {data.experience_required && <span>Exp: {data.experience_required}</span>}
      </div>

      {data.description && (
        <div>
          <h2 className="font-semibold">Description</h2>
          <p className="whitespace-pre-line text-slate-700">{data.description}</p>
        </div>
      )}
      {data.requirements && (
        <div>
          <h2 className="font-semibold">Requirements</h2>
          <p className="whitespace-pre-line text-slate-700">{data.requirements}</p>
        </div>
      )}
      {data.responsibilities && (
        <div>
          <h2 className="font-semibold">Responsibilities</h2>
          <p className="whitespace-pre-line text-slate-700">{data.responsibilities}</p>
        </div>
      )}
      {data.skills_required && (
        <div>
          <h2 className="font-semibold">Skills</h2>
          <p className="text-slate-700">{data.skills_required}</p>
        </div>
      )}

      {data.status === "published" && !applied && (
        <div className="space-y-2 rounded border border-slate-200 p-4">
          <h2 className="font-semibold">Apply</h2>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <textarea
            className="w-full rounded border border-slate-300 px-3 py-2 focus:border-brand focus:outline-none"
            rows={3}
            placeholder="Cover letter (optional)"
            value={cover}
            onChange={(e) => setCover(e.target.value)}
          />
          <button
            type="button"
            disabled={applyMutation.isPending}
            onClick={() => applyMutation.mutate()}
            className="rounded bg-brand px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
          >
            {applyMutation.isPending ? "Applying..." : "Apply now"}
          </button>
        </div>
      )}
      {applied && (
        <p className="rounded bg-green-50 px-3 py-2 text-sm text-green-700">
          Application submitted.
        </p>
      )}
    </section>
  );
}

interface ApiErrorShape {
  response?: { data?: { detail?: unknown } };
}

function extractError(err: unknown): string {
  const shape = err as ApiErrorShape;
  const detail = shape.response?.data?.detail;
  if (typeof detail === "string") return detail;
  return "Could not submit application.";
}
