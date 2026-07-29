import type { ApplicationStatus } from "../types";
import { APPLICATION_STATUS_TEXT } from "../types";

const STATUS_CLASS: Record<ApplicationStatus, string> = {
  applied: "bg-blue-100 text-blue-700",
  shortlisted: "bg-indigo-100 text-indigo-700",
  interview_scheduled: "bg-violet-100 text-violet-700",
  interview_completed: "bg-cyan-100 text-cyan-700",
  rejected: "bg-red-100 text-red-700",
  hired: "bg-green-100 text-green-700",
};

interface Props {
  status: ApplicationStatus;
}

export default function ApplicationStatusBadge({ status }: Props) {
  return (
    <span
      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${STATUS_CLASS[status]}`}
    >
      {APPLICATION_STATUS_TEXT[status]}
    </span>
  );
}
