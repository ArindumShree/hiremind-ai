import ResumeManager from "../components/ResumeManager";

export default function ResumePage() {
  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-bold">My Resume</h1>
      <p className="text-slate-600">
        Upload your resume so recruiters can review it when you apply.
      </p>
      <div className="max-w-xl">
        <ResumeManager />
      </div>
    </section>
  );
}
