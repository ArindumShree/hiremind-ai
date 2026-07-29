import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import jobService from "../services/jobs";
import ApplicationStatusBadge from "../components/ApplicationStatusBadge";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";

export default function AppliedJobs() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["my-applications"],
    queryFn: () => jobService.myApplications(),
  });

  if (isLoading) return <Loading label="Loading applications..." />;
  if (isError) return <ErrorMessage message="Could not load applications." onRetry={() => void refetch()} />;

  return (
    <section className="space-y-6">
      <h1 className="text-2xl font-semibold">My Applications</h1>
      {data && data.length === 0 && (
        <p className="text-slate-600">
          You have not applied to any jobs yet.{" "}
          <Link to="/jobs" className="text-brand hover:underline">
            Browse jobs
          </Link>
        </p>
      )}
      {data && data.length > 0 && (
        <div className="space-y-3">
          {data.map((app) => (
            <div
              key={app.id}
              className="flex items-center justify-between rounded border border-slate-200 bg-white p-4"
            >
              <div>
                <Link
                  to={`/jobs/${app.job_id}`}
                  className="font-semibold text-slate-900 hover:text-brand"
                >
                  View job
                </Link>
                <p className="text-sm text-slate-500">
                  Applied {new Date(app.applied_at).toLocaleDateString()}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <ApplicationStatusBadge status={app.status} />
                {app.interview_id && app.status === "interview_scheduled" && (
                  <Link
                    to={`/candidate/interviews/${app.interview_id}`}
                    className="rounded bg-violet-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-violet-700"
                  >
                    Take Interview
                  </Link>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
