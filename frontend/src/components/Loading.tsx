export default function Loading({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex items-center justify-center py-12 text-slate-500">
      <span className="animate-pulse">{label}</span>
    </div>
  );
}
