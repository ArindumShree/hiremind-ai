import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import jobService from "../services/jobs";
import JobForm, { type JobFormValues } from "../components/JobForm";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";

export default function EditJob() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["recruiter-job", id],
    queryFn: () => jobService.get(id as string),
    enabled: Boolean(id),
  });

  const mutation = useMutation({
    mutationFn: (values: JobFormValues) =>
      jobService.update(id as string, {
        ...values,
        employment_type: values.employment_type || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recruiter-jobs"] });
      navigate("/recruiter/jobs");
    },
    onError: (e: unknown) => setError(extractError(e)),
  });

  if (isLoading) return <Loading label="Loading job..." />;
  if (isError || !data) return <ErrorMessage message="Job not found." />;

  return (
    <section className="space-y-6">
      <h1 className="text-2xl font-semibold">Edit Job</h1>
      <JobForm
        initial={data}
        submitting={mutation.isPending}
        error={error}
        onSubmit={(values) => mutation.mutate(values)}
      />
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
  return "Could not update job.";
}
