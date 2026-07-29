import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import jobService from "../services/jobs";
import type { Job } from "../types";
import JobTable from "../components/JobTable";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";

export default function RecruiterJobList() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["recruiter-jobs"],
    queryFn: () => jobService.listMine(),
  });

  const publishMutation = useMutation({
    mutationFn: (job: Job) => jobService.publish(job.id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recruiter-jobs"] }),
    onError: (e: unknown) => setError(extractError(e)),
  });

  const closeMutation = useMutation({
    mutationFn: (job: Job) => jobService.close(job.id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recruiter-jobs"] }),
    onError: (e: unknown) => setError(extractError(e)),
  });

  const deleteMutation = useMutation({
    mutationFn: (job: Job) => jobService.remove(job.id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recruiter-jobs"] }),
    onError: (e: unknown) => setError(extractError(e)),
  });

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">My Jobs</h1>
        <Link
          to="/recruiter/jobs/new"
          className="rounded bg-brand px-3 py-2 text-sm font-semibold text-white"
        >
          Create Job
        </Link>
      </div>

      {error && <ErrorMessage message={error} />}

      {isLoading && <Loading label="Loading jobs..." />}
      {!isLoading && data && data.length === 0 && (
        <p className="text-slate-600">You have not posted any jobs yet.</p>
      )}
      {!isLoading && data && data.length > 0 && (
        <JobTable
          jobs={data}
          onEdit={(job) => navigate(`/recruiter/jobs/${job.id}/edit`)}
          onPublish={(job) => publishMutation.mutate(job)}
          onClose={(job) => closeMutation.mutate(job)}
          onDelete={(job) => {
            if (window.confirm(`Delete "${job.title}"?`)) {
              deleteMutation.mutate(job);
            }
          }}
          onViewApplicants={(job) =>
            navigate(`/recruiter/jobs/${job.id}/applicants`)
          }
        />
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
  return "Action failed. Please try again.";
}
