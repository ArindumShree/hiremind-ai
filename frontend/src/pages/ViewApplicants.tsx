import { useParams, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import jobService from "../services/jobs";
import interviewService from "../services/interview";
import type { Application } from "../types";
import ApplicationStatusBadge from "../components/ApplicationStatusBadge";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";

export default function ViewApplicants() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["applicants", id],
    queryFn: () => jobService.listApplicants(id as string),
  });

  const shortlistMutation = useMutation({
    mutationFn: (applicationId: string) =>
      jobService.updateApplicationStatus(applicationId, "shortlisted"),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applicants", id] }),
  });

  const startMutation = useMutation({
    mutationFn: (applicationId: string) =>
      interviewService.start(applicationId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applicants", id] }),
  });

  if (isLoading) return <Loading label="Loading applicants..." />;

  return (
    <section className="space-y-6">
      <h1 className="text-2xl font-semibold">Applicants</h1>
      {isError && <ErrorMessage message="Could not load applicants." />}
      {!isLoading && data && data.length === 0 && (
        <p className="text-slate-600">No applicants yet.</p>
      )}
      {data && data.length > 0 && (
        <div className="overflow-x-auto rounded border border-slate-200 bg-white">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 text-left text-slate-500">
              <tr>
                <th className="px-4 py-2">Candidate</th>
                <th className="px-4 py-2">Email</th>
                <th className="px-4 py-2">Applied</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2">Action</th>
              </tr>
            </thead>
            <tbody>
              {data.map((app: Application) => (
                <tr key={app.id} className="border-t border-slate-100">
                  <td className="px-4 py-2 font-medium text-slate-900">
                    {app.candidate?.full_name ?? "-"}
                  </td>
                  <td className="px-4 py-2 text-slate-600">
                    {app.candidate?.email ?? "-"}
                  </td>
                  <td className="px-4 py-2 text-slate-600">
                    {new Date(app.applied_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-2">
                    <ApplicationStatusBadge status={app.status} />
                  </td>
                  <td className="px-4 py-2 space-x-2">
                    {app.status === "applied" && (
                      <button
                        type="button"
                        onClick={() => shortlistMutation.mutate(app.id)}
                        disabled={shortlistMutation.isPending}
                        className="rounded bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
                      >
                        Shortlist
                      </button>
                    )}
                    {(app.status === "shortlisted" || app.status === "applied") &&
                      !app.interview_id && (
                        <button
                          type="button"
                          onClick={() => startMutation.mutate(app.id)}
                          disabled={startMutation.isPending}
                          className="rounded bg-violet-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-violet-700 disabled:opacity-50"
                        >
                          Start Interview
                        </button>
                      )}
                    {app.interview_id && (
                      <Link
                        to={`/recruiter/interviews/${app.interview_id}`}
                        className="rounded border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                      >
                        Review
                      </Link>
                    )}
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
