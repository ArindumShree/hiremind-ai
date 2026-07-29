import apiClient from "./api";
import type { Interview, SpeechMetrics, VideoMetrics, Evaluation } from "../types";

export interface AnswerPayload {
  question_id: string;
  text?: string | null;
  media_path?: string | null;
  media_type?: string | null;
}

export const interviewService = {
  start(applicationId: string) {
    return apiClient
      .post<Interview>("/interviews", { application_id: applicationId })
      .then((r) => r.data);
  },

  get(id: string) {
    return apiClient.get<Interview>(`/interviews/${id}`).then((r) => r.data);
  },

  submit(id: string, answers: AnswerPayload[]) {
    return apiClient
      .post<Interview>(`/interviews/${id}/submit`, { answers })
      .then((r) => r.data);
  },

  submitWithMedia(id: string, answers: AnswerPayload[], file: File) {
    const form = new FormData();
    form.append("answers", JSON.stringify({ answers }));
    form.append("file", file);
    return apiClient
      .post<Interview>(`/interviews/${id}/submit/media`, form)
      .then((r) => r.data);
  },

  analyzeSpeech(id: string) {
    return apiClient
      .post<SpeechMetrics>(`/interviews/${id}/speech-analysis`)
      .then((r) => r.data);
  },

  analyzeVideo(id: string) {
    return apiClient
      .post<VideoMetrics>(`/interviews/${id}/video-analysis`)
      .then((r) => r.data);
  },

  evaluate(id: string) {
    return apiClient
      .post<Evaluation>(`/interviews/${id}/evaluate`)
      .then((r) => r.data);
  },

  getEvaluation(id: string) {
    return apiClient
      .get<Evaluation>(`/interviews/${id}/evaluation`)
      .then((r) => r.data);
  },

  async getMedia(id: string): Promise<string> {
    const { data } = await apiClient.get<Blob>(
      `/interviews/${id}/media`,
      { responseType: "blob" },
    );
    return URL.createObjectURL(data);
  },
};

export default interviewService;
