import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import interviewService, { type AnswerPayload } from "../services/interview";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";

export default function InterviewPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [file, setFile] = useState<File | null>(null);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["interview", id],
    queryFn: () => interviewService.get(id as string),
  });

  const submitMutation = useMutation({
    mutationFn: (payload: { answers: AnswerPayload[]; file: File | null }) => {
      if (payload.file) {
        return interviewService.submitWithMedia(id as string, payload.answers, payload.file);
      }
      return interviewService.submit(id as string, payload.answers);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["interview", id] });
      navigate("/applications/mine");
    },
  });

  if (isLoading) return <Loading label="Loading interview..." />;
  if (isError) return <ErrorMessage message="Could not load interview." onRetry={() => void refetch()} />;
  if (!data) return null;

  const isCompleted = data.status === "completed";

  function handleSubmit() {
    const collected: AnswerPayload[] = (data?.questions ?? []).map((q) => ({
      question_id: q.id ?? q.question_id ?? "",
      text: answers[q.id ?? q.question_id ?? ""] ?? null,
    }));
    submitMutation.mutate({ answers: collected, file });
  }

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Interview</h1>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
          {data.status}
        </span>
      </div>

      {isCompleted ? (
        <div className="rounded border border-slate-200 bg-white p-6">
          <p className="text-slate-600">
            This interview has been submitted. The recruiter will review your
            responses shortly.
          </p>
        </div>
      ) : (
        <>
          <p className="text-sm text-slate-500">
            Answer each question. You may also attach a single audio or video
            file (optional) to support your responses.
          </p>
          <div className="space-y-4">
            {(data.questions ?? []).map((q, index) => {
              const key = q.id ?? q.question_id ?? String(index);
              return (
                <div
                  key={key}
                  className="rounded border border-slate-200 bg-white p-4"
                >
                  <label className="block font-semibold text-slate-900">
                    {index + 1}. {q.text ?? q.question_text ?? "Question"}
                  </label>
                  <textarea
                    className="mt-2 w-full rounded border border-slate-300 p-2 text-sm"
                    rows={3}
                    value={answers[key] ?? ""}
                    onChange={(e) =>
                      setAnswers((prev) => ({ ...prev, [key]: e.target.value }))
                    }
                    placeholder="Type your answer..."
                  />
                </div>
              );
            })}
          </div>

          <div className="rounded border border-slate-200 bg-white p-4">
            <label className="block text-sm font-semibold text-slate-700">
              Optional media (audio/video)
            </label>
            <input
              type="file"
              accept="audio/*,video/*"
              className="mt-2 block text-sm"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
            {file && (
              <p className="mt-1 text-xs text-slate-500">{file.name}</p>
            )}
          </div>

          {submitMutation.isError && (
            <p className="text-sm text-red-600">
              Failed to submit interview. Please try again.
            </p>
          )}

          <button
            type="button"
            onClick={handleSubmit}
            disabled={submitMutation.isPending}
            className="rounded bg-violet-600 px-4 py-2 text-sm font-semibold text-white hover:bg-violet-700 disabled:opacity-50"
          >
            {submitMutation.isPending ? "Submitting..." : "Submit Interview"}
          </button>
        </>
      )}
    </section>
  );
}
