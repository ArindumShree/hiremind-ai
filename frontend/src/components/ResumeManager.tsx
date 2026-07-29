import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import resumeService from "../services/resume";
import Loading from "./Loading";
import ErrorMessage from "./ErrorMessage";

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

interface Props {
  onUploaded?: () => void;
}

export default function ResumeManager({ onUploaded }: Props) {
  const queryClient = useQueryClient();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["resume"],
    queryFn: async () => {
      try {
        return await resumeService.get();
      } catch (err) {
        // 404 simply means no resume uploaded yet — still show the upload UI.
        const status = (err as { response?: { status?: number } })?.response
          ?.status;
        if (status === 404) return null;
        throw err;
      }
    },
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => resumeService.upload(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resume"] });
      onUploaded?.();
    },
  });

  const removeMutation = useMutation({
    mutationFn: () => resumeService.remove(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resume"] });
    },
  });

  if (isLoading) return <Loading label="Loading resume..." />;
  if (isError)
    return <ErrorMessage message="Could not load resume information." />;

  return (
    <section className="space-y-3 rounded border border-slate-200 bg-white p-4">
      <h2 className="font-semibold">Resume</h2>

      {data ? (
        <div className="space-y-2 text-sm text-slate-700">
          <p>
            <span className="font-medium">{data.filename}</span> (
            {formatSize(data.size_bytes)})
          </p>
          <p className="text-slate-500">
            Uploaded {new Date(data.created_at).toLocaleDateString()}
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              className="rounded border border-slate-300 px-3 py-1 text-sm hover:border-brand"
              onClick={async () => {
                const blob = await resumeService.download();
                const url = URL.createObjectURL(blob);
                const link = document.createElement("a");
                link.href = url;
                link.download = data.filename;
                link.click();
                URL.revokeObjectURL(url);
              }}
            >
              Download
            </button>
            <button
              type="button"
              className="rounded border border-red-300 px-3 py-1 text-sm text-red-600 hover:border-red-500"
              disabled={removeMutation.isPending}
              onClick={() => removeMutation.mutate()}
            >
              Remove
            </button>
          </div>
        </div>
      ) : (
        <p className="text-sm text-slate-500">No resume uploaded yet.</p>
      )}

      <div>
        <label className="block text-sm font-medium">
          {data ? "Replace resume" : "Upload resume"}
        </label>
        <input
          type="file"
          accept=".pdf,.doc,.docx"
          className="mt-1 block w-full text-sm text-slate-700"
          disabled={uploadMutation.isPending}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) uploadMutation.mutate(file);
            e.target.value = "";
          }}
        />
        <p className="mt-1 text-xs text-slate-500">
          PDF, DOC or DOCX. Max 25 MB.
        </p>
      </div>

      {uploadMutation.isError && (
        <ErrorMessage message="Upload failed. Check the file type and size." />
      )}
    </section>
  );
}
