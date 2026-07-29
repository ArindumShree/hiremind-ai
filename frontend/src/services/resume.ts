import apiClient from "./api";
import type { Resume } from "../types";

export const resumeService = {
  get() {
    return apiClient.get<Resume>("/resume").then((r) => r.data);
  },

  upload(file: File) {
    const form = new FormData();
    form.append("file", file);
    return apiClient
      .post<Resume>("/resume/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },

  download() {
    return apiClient
      .get<Blob>("/resume/download", { responseType: "blob" })
      .then((r) => r.data);
  },

  remove() {
    return apiClient.delete("/resume").then((r) => r.data);
  },

  getForCandidate(candidateId: string) {
    return apiClient
      .get<Resume>(`/resume/candidate/${candidateId}`)
      .then((r) => r.data);
  },

  async viewForCandidate(candidateId: string) {
    const { data } = await apiClient.get<Blob>(
      `/resume/candidate/${candidateId}/download`,
      { responseType: "blob" },
    );
    const url = URL.createObjectURL(data);
    window.open(url, "_blank");
    setTimeout(() => URL.revokeObjectURL(url), 60000);
  },
};

export default resumeService;
