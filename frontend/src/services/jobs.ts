import apiClient from "./api";
import type {
  Application,
  Job,
  PaginatedJobs,
} from "../types";

export interface JobQuery {
  search?: string;
  location?: string;
  employment_type?: string;
  status?: string;
  page?: number;
  page_size?: number;
}

export const jobService = {
  create(payload: Partial<Job> & { title: string; company_name: string }) {
    return apiClient.post<Job>("/jobs", payload).then((r) => r.data);
  },

  listMine() {
    return apiClient.get<Job[]>("/jobs/my").then((r) => r.data);
  },

  browse(query: JobQuery = {}) {
    return apiClient
      .get<PaginatedJobs>("/jobs", { params: query })
      .then((r) => r.data);
  },

  get(id: string) {
    return apiClient.get<Job>(`/jobs/${id}`).then((r) => r.data);
  },

  update(id: string, payload: Partial<Job>) {
    return apiClient.put<Job>(`/jobs/${id}`, payload).then((r) => r.data);
  },

  remove(id: string) {
    return apiClient.delete(`/jobs/${id}`).then((r) => r.status);
  },

  publish(id: string) {
    return apiClient
      .patch<Job>(`/jobs/${id}/publish`)
      .then((r) => r.data);
  },

  close(id: string) {
    return apiClient
      .patch<Job>(`/jobs/${id}/close`)
      .then((r) => r.data);
  },

  apply(id: string, cover_letter?: string) {
    return apiClient
      .post<Application>(`/jobs/${id}/apply`, { cover_letter })
      .then((r) => r.data);
  },

  listApplicants(id: string) {
    return apiClient
      .get<Application[]>(`/jobs/${id}/applications`)
      .then((r) => r.data);
  },

  updateApplicationStatus(applicationId: string, status: string) {
    return apiClient
      .patch<Application>(`/applications/${applicationId}/status`, { status })
      .then((r) => r.data);
  },

  myApplications() {
    return apiClient
      .get<Application[]>("/applications/my")
      .then((r) => r.data);
  },
};

export default jobService;
