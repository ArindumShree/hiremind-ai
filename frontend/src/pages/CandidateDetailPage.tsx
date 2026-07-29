import { useParams, useNavigate, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import candidateService from "../services/candidates";
import resumeService from "../services/resume";
import ApplicationStatusBadge from "../components/ApplicationStatusBadge";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";

export default function CandidateDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["candidate", id],
    queryFn: () => candidateService.get(id as string),
    enabled: Boolean(id),
  });

  async function handleViewResume() {
    if (!data?.candidate_id) return;
    try {
      await resumeService.viewForCandidate(data.candidate_id);
    } catch {
      alert("No resume available for this candidate.");
    }
  }

  if (isLoading) return <Loading label="Loading candidate..." />;
  if (isError || !data)
    return <ErrorMessage message="Candidate not found." />;

  return (
    <section className="space-y-6">
      <Link
        to="/recruiter/candidates"
        className="text-sm text-brand hover:underline"
      >
        &larr; Back to candidates
      </Link>

      <div className="flex items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">{data.full_name}</h1>
          <p className="text-slate-600">{data.email}</p>
          <p className="text-sm text-slate-500">
            Applied to {data.job_title ?? "—"} on{" "}
            {new Date(data.applied_at).toLocaleDateString()}
          </p>
        </div>
        <ApplicationStatusBadge status={data.status} />
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => candidateService.downloadReport(data.application_id)}
          className="rounded bg-brand px-3 py-2 text-sm font-semibold text-white"
        >
          Download report (JSON)
        </button>
        <button
          type="button"
          onClick={() => void handleViewResume()}
          className="rounded border border-slate-300 px-3 py-2 text-sm font-semibold"
        >
          View resume
        </button>
        <button
          type="button"
          onClick={() =>
            navigate("/recruiter/candidates/compare", {
              state: { preselect: [data.application_id] },
            })
          }
          className="rounded border border-slate-300 px-3 py-2 text-sm font-semibold"
        >
          Compare
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded border border-slate-200 bg-white p-4">
          <h2 className="font-semibold">Skills</h2>
          {data.skills.length ? (
            <p className="text-slate-700">{data.skills.join(", ")}</p>
          ) : (
            <p className="text-slate-500">No skills parsed.</p>
          )}
          {data.experience_years != null && (
            <p className="mt-2 text-slate-700">
              Experience: {data.experience_years} years
            </p>
          )}
          {data.college && (
            <p className="text-slate-700">College: {data.college}</p>
          )}
        </div>

        <div className="rounded border border-slate-200 bg-white p-4">
          <h2 className="font-semibold">Profile</h2>
          {data.profile ? (
            <dl className="space-y-1 text-sm text-slate-700">
              {data.profile.phone && (
                <div>
                  <span className="font-medium">Phone:</span>{" "}
                  {data.profile.phone}
                </div>
              )}
              {data.profile.college && (
                <div>
                  <span className="font-medium">College:</span>{" "}
                  {data.profile.college}
                </div>
              )}
              {data.profile.company && (
                <div>
                  <span className="font-medium">Company:</span>{" "}
                  {data.profile.company}
                </div>
              )}
              {data.profile.linkedin_url && (
                <div>
                  <a
                    className="text-brand hover:underline"
                    href={data.profile.linkedin_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    LinkedIn
                  </a>
                </div>
              )}
              {data.profile.github_url && (
                <div>
                  <a
                    className="text-brand hover:underline"
                    href={data.profile.github_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    GitHub
                  </a>
                </div>
              )}
            </dl>
          ) : (
            <p className="text-slate-500">No profile available.</p>
          )}
        </div>
      </div>

      {data.cover_letter && (
        <div className="rounded border border-slate-200 bg-white p-4">
          <h2 className="font-semibold">Cover letter</h2>
          <p className="whitespace-pre-line text-slate-700">
            {data.cover_letter}
          </p>
        </div>
      )}

      {data.evaluation_summary && (
        <div className="rounded border border-slate-200 bg-white p-4">
          <h2 className="font-semibold">AI Evaluation Summary</h2>
          <p className="whitespace-pre-line text-slate-700">
            {data.evaluation_summary}
          </p>
        </div>
      )}

      {data.interview_questions && data.interview_questions.length > 0 && (
        <div className="rounded border border-slate-200 bg-white p-4">
          <h2 className="font-semibold">Interview</h2>
          <ul className="space-y-3">
            {data.interview_questions.map((q, i) => (
              <li key={i} className="text-sm">
                <p className="font-medium text-slate-800">
                  {typeof q.question_text === "string"
                    ? q.question_text
                    : `Question ${i + 1}`}
                </p>
                <p className="text-slate-600">
                  {typeof q.text === "string" && q.text.trim()
                    ? q.text
                    : "No answer provided."}
                </p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
