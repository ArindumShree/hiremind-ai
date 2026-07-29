import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import interviewService from "../services/interview";
import type { Evaluation } from "../types";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";

export default function InterviewReviewPage() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [mediaUrl, setMediaUrl] = useState<string | null>(null);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["interview-review", id],
    queryFn: () => interviewService.get(id as string),
  });

  const speechMutation = useMutation({
    mutationFn: () => interviewService.analyzeSpeech(id as string),
  });
  const videoMutation = useMutation({
    mutationFn: () => interviewService.analyzeVideo(id as string),
  });
  const evalMutation = useMutation({
    mutationFn: () => interviewService.evaluate(id as string),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["eval", id] }),
  });

  const evaluationQuery = useQuery({
    queryKey: ["eval", id],
    queryFn: () => interviewService.getEvaluation(id as string),
    enabled: data?.status === "completed",
  });

  const answers = data?.questions ?? [];
  const mediaItem = answers.find((q) => q.media_path) ?? null;
  const mediaType = mediaItem?.media_type ?? null;

  useEffect(() => {
    let url: string | null = null;
    if (mediaItem?.media_path && id) {
      interviewService
        .getMedia(id)
        .then((u) => {
          url = u;
          setMediaUrl(u);
        })
        .catch(() => setMediaUrl(null));
    } else {
      setMediaUrl(null);
    }
    return () => {
      if (url) URL.revokeObjectURL(url);
    };
  }, [mediaItem?.media_path, id]);

  if (isLoading) return <Loading label="Loading interview..." />;
  if (isError) return <ErrorMessage message="Could not load interview." onRetry={() => void refetch()} />;
  if (!data) return null;

  const evaluation: Evaluation | null =
    evalMutation.data ?? evaluationQuery.data ?? null;

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Interview Review</h1>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
          {data.status}
        </span>
      </div>

      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => speechMutation.mutate()}
          disabled={speechMutation.isPending}
          className="rounded bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          Run Speech Analysis
        </button>
        <button
          type="button"
          onClick={() => videoMutation.mutate()}
          disabled={videoMutation.isPending}
          className="rounded bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          Run Video Analysis
        </button>
        <button
          type="button"
          onClick={() => evalMutation.mutate()}
          disabled={evalMutation.isPending}
          className="rounded bg-violet-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-violet-700 disabled:opacity-50"
        >
          Run Evaluation
        </button>
      </div>

      {speechMutation.isError && (
        <p className="text-sm text-amber-600">
          Speech analysis needs an audio answer; none was submitted (use Video
          Analysis for video answers).
        </p>
      )}
      {videoMutation.isError && (
        <p className="text-sm text-amber-600">
          Video analysis needs a video answer; none was submitted.
        </p>
      )}

      {speechMutation.data && (
        <MetricsCard title="Speech Metrics" metrics={speechMutation.data as unknown as Record<string, unknown>} />
      )}
      {videoMutation.data && (
        <MetricsCard title="Video Metrics" metrics={videoMutation.data as unknown as Record<string, unknown>} />
      )}

      {mediaUrl && (
        <div className="rounded border border-slate-200 bg-white p-4">
          <h2 className="font-semibold text-slate-900">Candidate answer media</h2>
          {mediaType && mediaType.startsWith("video") ? (
            <video src={mediaUrl} controls className="mt-2 w-full max-w-2xl rounded" />
          ) : (
            <audio src={mediaUrl} controls className="mt-2 w-full" />
          )}
        </div>
      )}

      <div className="space-y-4">
        <h2 className="font-semibold text-slate-900">Candidate answers</h2>
        {answers.length === 0 && (
          <p className="text-sm text-slate-500">No answers captured yet.</p>
        )}
        {answers.map((q, index) => (
          <div key={index} className="rounded border border-slate-200 bg-white p-4">
            <p className="font-semibold text-slate-900">
              {index + 1}. {q.question_text ?? q.text ?? "Question"}
            </p>
            <p className="mt-2 whitespace-pre-wrap text-sm text-slate-600">
              {q.text ?? <span className="italic text-slate-400">No answer text</span>}
            </p>
            {q.media_path && (
              <p className="mt-1 text-xs text-slate-500">
                Media: {q.media_type ?? "file"} ({q.media_path.split(/[\\/]/).pop()})
              </p>
            )}
          </div>
        ))}
      </div>

      <EvaluationPanel evaluation={evaluation} loading={evaluationQuery.isLoading} />
    </section>
  );
}

function MetricsCard({ title, metrics }: { title: string; metrics: Record<string, unknown> }) {
  const entries = Object.entries(metrics).filter(([, v]) => typeof v === "number");
  return (
    <div className="rounded border border-slate-200 bg-white p-4">
      <h2 className="font-semibold text-slate-900">{title}</h2>
      <ul className="mt-2 grid grid-cols-2 gap-1 text-sm text-slate-600">
        {entries.map(([k, v]) => (
          <li key={k}>{k}: {String(v)}</li>
        ))}
      </ul>
    </div>
  );
}

function EvaluationPanel({ evaluation, loading }: { evaluation: Evaluation | null; loading: boolean }) {
  if (loading) return <p className="text-sm text-slate-500">Loading evaluation...</p>;
  if (!evaluation) {
    return (
      <div className="rounded border border-slate-200 bg-white p-4">
        <p className="text-sm text-slate-500">
          No evaluation yet. Click "Run Evaluation" to score this interview.
        </p>
      </div>
    );
  }
  return (
    <div className="rounded border border-slate-200 bg-white p-4">
      <h2 className="font-semibold text-slate-900">Evaluation</h2>
      <p className="mt-1 text-sm text-slate-700">
        Overall score: <span className="font-semibold">{evaluation.overall_score}</span>/100
      </p>
      <ul className="mt-2 space-y-1 text-sm text-slate-600">
        {evaluation.dimensions?.map((d) => (
          <li key={d.name}>{d.name}: {d.score}</li>
        ))}
      </ul>
      {evaluation.ai_feedback && (
        <p className="mt-3 whitespace-pre-wrap text-sm text-slate-600">
          {evaluation.ai_feedback}
        </p>
      )}
    </div>
  );
}