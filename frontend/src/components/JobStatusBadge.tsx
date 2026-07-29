import type { JobStatus } from "../types";
import { JOB_STATUS_TEXT } from "../types";

const STATUS_CLASS: Record<JobStatus, string> = {
  draft: "bg-slate-100 text-slate-600",
  published: "bg-green-100 text-green-700",
  closed: "bg-red-100 text-red-700",
  archived: "bg-amber-100 text-amber-700",
};

export default function JobStatusBadge({ status }: { status: JobStatus }) {
  return (
    <span
      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${STATUS_CLASS[status]}`}
    >
      {JOB_STATUS_TEXT[status]}
    </span>
  );
}
