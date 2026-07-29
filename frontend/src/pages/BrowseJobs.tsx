import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import jobService, { type JobQuery } from "../services/jobs";
import JobCard from "../components/JobCard";
import Loading from "../components/Loading";
import ErrorMessage from "../components/ErrorMessage";

const PAGE_SIZE = 10;

export default function BrowseJobs() {
  const [query, setQuery] = useState<JobQuery>({ page: 1, page_size: PAGE_SIZE });
  const [searchInput, setSearchInput] = useState("");
  const [locationInput, setLocationInput] = useState("");

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["browse-jobs", query],
    queryFn: () => jobService.browse(query),
  });

  function applyFilters(e: React.FormEvent) {
    e.preventDefault();
    setQuery((prev) => ({
      ...prev,
      search: searchInput || undefined,
      location: locationInput || undefined,
      page: 1,
    }));
  }

  const totalPages = data?.meta.total_pages ?? 0;

  return (
    <section className="space-y-6">
      <h1 className="text-2xl font-semibold">Browse Jobs</h1>

      <form onSubmit={applyFilters} className="flex flex-wrap gap-2">
        <input
          className="rounded border border-slate-300 px-3 py-2 focus:border-brand focus:outline-none"
          placeholder="Search title or company"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
        />
        <input
          className="rounded border border-slate-300 px-3 py-2 focus:border-brand focus:outline-none"
          placeholder="Location"
          value={locationInput}
          onChange={(e) => setLocationInput(e.target.value)}
        />
        <button
          type="submit"
          className="rounded bg-brand px-4 py-2 text-sm font-semibold text-white"
        >
          Search
        </button>
      </form>

      {isError && <ErrorMessage message="Could not load jobs." onRetry={() => void refetch()} />}
      {isLoading && <Loading label="Loading jobs..." />}

      {!isLoading && data && data.items.length === 0 && (
        <p className="text-slate-600">No jobs found.</p>
      )}

      {!isLoading && data && data.items.length > 0 && (
        <>
          <div className="grid gap-4 sm:grid-cols-2">
            {data.items.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>

          <div className="flex items-center justify-between text-sm text-slate-500">
            <span>
              Page {data.meta.page} of {totalPages} ({data.meta.total} jobs)
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={(query.page ?? 1) <= 1}
                onClick={() =>
                  setQuery((prev) => ({ ...prev, page: (prev.page ?? 1) - 1 }))
                }
                className="rounded border border-slate-300 px-3 py-1 disabled:opacity-50"
              >
                Previous
              </button>
              <button
                type="button"
                disabled={(query.page ?? 1) >= totalPages}
                onClick={() =>
                  setQuery((prev) => ({ ...prev, page: (prev.page ?? 1) + 1 }))
                }
                className="rounded border border-slate-300 px-3 py-1 disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </section>
  );
}
