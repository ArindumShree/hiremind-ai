export type UserRole = "candidate" | "recruiter";

export type EmploymentType =
  | "full_time"
  | "part_time"
  | "contract"
  | "intern"
  | "freelance";

export type JobStatus = "draft" | "published" | "closed" | "archived";

export type ApplicationStatus =
  | "applied"
  | "shortlisted"
  | "interview_scheduled"
  | "interview_completed"
  | "rejected"
  | "hired";

export interface UserProfile {
  id: string;
  user_id: string;
  phone: string | null;
  college: string | null;
  company: string | null;
  linkedin_url: string | null;
  github_url: string | null;
  bio: string | null;
  profile_picture: string | null;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  full_name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserWithProfile extends User {
  profile: UserProfile | null;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Job {
  id: string;
  title: string;
  company_name: string;
  location: string | null;
  employment_type: EmploymentType | null;
  experience_required: string | null;
  salary_range: string | null;
  description: string | null;
  requirements: string | null;
  responsibilities: string | null;
  skills_required: string | null;
  status: JobStatus;
  posted_by: string;
  created_at: string;
  updated_at: string;
}

export interface Application {
  id: string;
  candidate_id: string;
  job_id: string;
  status: ApplicationStatus;
  cover_letter: string | null;
  applied_at: string;
  updated_at: string;
  candidate?: User;
  interview_id?: string | null;
}

export interface InterviewQuestion {
  id?: string;
  question_id?: string;
  text?: string | null;
  question_text?: string | null;
  category?: string | null;
  media_path?: string | null;
  media_type?: string | null;
}

export interface Interview {
  id: string;
  application_id: string;
  status: InterviewStatus;
  questions: InterviewQuestion[] | null;
  started_at: string | null;
  submitted_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PageMeta {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface PaginatedJobs {
  items: Job[];
  meta: PageMeta;
}

export interface ApiError {
  detail: unknown;
}

export interface Resume {
  id: string;
  candidate_id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  created_at: string;
}

export const EMPLOYMENT_TYPE_TEXT: Record<EmploymentType, string> = {
  full_time: "Full-time",
  part_time: "Part-time",
  contract: "Contract",
  intern: "Intern",
  freelance: "Freelance",
};

export const JOB_STATUS_TEXT: Record<JobStatus, string> = {
  draft: "Draft",
  published: "Published",
  closed: "Closed",
  archived: "Archived",
};

export const APPLICATION_STATUS_TEXT: Record<ApplicationStatus, string> = {
  applied: "Applied",
  shortlisted: "Shortlisted",
  interview_scheduled: "Interview Scheduled",
  interview_completed: "Interview Completed",
  rejected: "Rejected",
  hired: "Hired",
};

export type InterviewStatus =
  | "pending"
  | "active"
  | "completed";

export interface CandidateSummary {
  application_id: string;
  candidate_id: string;
  job_id: string;
  job_title: string | null;
  full_name: string;
  email: string;
  status: ApplicationStatus;
  applied_at: string;
  skills: string[];
  experience_years: number | null;
  college: string | null;
  interview_status: InterviewStatus | null;
  interview_score: number | null;
  evaluation_summary: string | null;
  evaluation: Evaluation | null;
}

export interface SpeechMetrics {
  transcript: string;
  word_count: number;
  duration_seconds: number | null;
  words_per_minute: number | null;
  filler_word_count: number;
  filler_word_ratio: number;
  fluency_score: number;
  confidence_score: number;
  clarity_score: number | null;
}

export interface VideoMetrics {
  frames_sampled: number;
  frames_with_face: number;
  face_detection_ratio: number;
  avg_face_confidence: number;
  eye_contact_score: number;
  posture_score: number;
  engagement_score: number;
}

export interface EvaluationDimension {
  name: string;
  score: number;
  weight: number;
}

export interface Evaluation {
  overall_score: number;
  dimensions: EvaluationDimension[];
  summary: string;
  ai_feedback: string | null;
}

export interface CandidateDetail extends CandidateSummary {
  cover_letter: string | null;
  profile: {
    phone: string | null;
    college: string | null;
    company: string | null;
    linkedin_url: string | null;
    github_url: string | null;
    bio: string | null;
  } | null;
  interview_questions: Array<Record<string, unknown>> | null;
  parsed_fields: Record<string, unknown> | null;
}

export interface CandidateComparison {
  candidates: CandidateDetail[];
  generated_at: string;
}

export const INTERVIEW_STATUS_TEXT: Record<InterviewStatus, string> = {
  pending: "Pending",
  active: "Active",
  completed: "Completed",
};
