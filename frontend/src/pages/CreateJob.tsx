import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import jobService from "../services/jobs";
import JobForm, { type JobFormValues } from "../components/JobForm";

export default function CreateJob() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (values: JobFormValues) =>
      jobService.create({
        ...values,
        employment_type: values.employment_type || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recruiter-jobs"] });
      navigate("/recruiter/jobs");
    },
    onError: (e: unknown) => setError(extractError(e)),
  });

  return (
    <section className="space-y-6">
      <h1 className="text-2xl font-semibold">Create Job</h1>
      <JobForm
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
  return "Could not create job.";
}
