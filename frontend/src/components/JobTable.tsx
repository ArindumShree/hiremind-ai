import type { Job } from "../types";
import JobStatusBadge from "./JobStatusBadge";

interface Props {
  jobs: Job[];
  onEdit?: (job: Job) => void;
  onPublish?: (job: Job) => void;
  onClose?: (job: Job) => void;
  onDelete?: (job: Job) => void;
  onViewApplicants?: (job: Job) => void;
}

export default function JobTable({
  jobs,
  onEdit,
  onPublish,
  onClose,
  onDelete,
  onViewApplicants,
}: Props) {
  return (
    <div className="overflow-x-auto rounded border border-slate-200 bg-white">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-50 text-left text-slate-500">
          <tr>
            <th className="px-4 py-2">Title</th>
            <th className="px-4 py-2">Company</th>
            <th className="px-4 py-2">Location</th>
            <th className="px-4 py-2">Status</th>
            <th className="px-4 py-2 text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.id} className="border-t border-slate-100">
              <td className="px-4 py-2 font-medium text-slate-900">{job.title}</td>
              <td className="px-4 py-2 text-slate-600">{job.company_name}</td>
              <td className="px-4 py-2 text-slate-600">{job.location ?? "-"}</td>
              <td className="px-4 py-2">
                <JobStatusBadge status={job.status} />
              </td>
              <td className="px-4 py-2 text-right">
                <div className="flex justify-end gap-2">
                  {onEdit && (
                    <button
                      type="button"
                      onClick={() => onEdit(job)}
                      className="text-brand hover:underline"
                    >
                      Edit
                    </button>
                  )}
                  {onPublish && job.status !== "published" && (
                    <button
                      type="button"
                      onClick={() => onPublish(job)}
                      className="text-green-700 hover:underline"
                    >
                      Publish
                    </button>
                  )}
                  {onClose && job.status === "published" && (
                    <button
                      type="button"
                      onClick={() => onClose(job)}
                      className="text-red-700 hover:underline"
                    >
                      Close
                    </button>
                  )}
                  {onDelete && (
                    <button
                      type="button"
                      onClick={() => onDelete(job)}
                      className="text-slate-400 hover:underline"
                    >
                      Delete
                    </button>
                  )}
                  {onViewApplicants && (
                    <button
                      type="button"
                      onClick={() => onViewApplicants(job)}
                      className="text-violet-700 hover:underline"
                    >
                      Applicants
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
