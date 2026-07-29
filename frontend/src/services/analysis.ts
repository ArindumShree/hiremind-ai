import apiClient from "./api";
import type { Evaluation, SpeechMetrics, VideoMetrics } from "../types";

export const analysisService = {
  analyzeSpeech(interviewId: string) {
    return apiClient
      .post<SpeechMetrics>(`/interviews/${interviewId}/speech-analysis`)
      .then((r) => r.data);
  },

  analyzeVideo(interviewId: string) {
    return apiClient
      .post<VideoMetrics>(`/interviews/${interviewId}/video-analysis`)
      .then((r) => r.data);
  },

  evaluate(interviewId: string) {
    return apiClient
      .post<Evaluation>(`/interviews/${interviewId}/evaluate`)
      .then((r) => r.data);
  },

  getEvaluation(interviewId: string) {
    return apiClient
      .get<Evaluation>(`/interviews/${interviewId}/evaluation`)
      .then((r) => r.data);
  },
};

export default analysisService;
