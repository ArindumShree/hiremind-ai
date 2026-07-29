import apiClient from "./api";
import type {
  CandidateComparison,
  CandidateDetail,
  CandidateSummary,
} from "../types";

export interface CandidateQuery {
  job_id?: string;
  status?: string;
  search?: string;
}

export const candidateService = {
  list(query: CandidateQuery = {}) {
    return apiClient
      .get<CandidateSummary[]>("/candidates", { params: query })
      .then((r) => r.data);
  },

  get(applicationId: string) {
    return apiClient
      .get<CandidateDetail>(`/candidates/${applicationId}`)
      .then((r) => r.data);
  },

  compare(applicationIds: string[]) {
    return apiClient
      .post<CandidateComparison>("/candidates/compare", {
        application_ids: applicationIds,
      })
      .then((r) => r.data);
  },

  async downloadReport(applicationId: string) {
    const resp = await apiClient.get<Record<string, unknown>>(
      `/candidates/${applicationId}/report`,
      { responseType: "json" },
    );
    const blob = new Blob([JSON.stringify(resp.data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `candidate-${applicationId}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  },
};

export default candidateService;
