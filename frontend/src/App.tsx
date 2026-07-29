import { Routes, Route } from "react-router-dom";
import Layout from "./layouts/Layout";
import { AuthProvider } from "./context/AuthContext";
import { ProtectedRoute } from "./routes/ProtectedRoute";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import RecruiterDashboard from "./pages/RecruiterDashboard";
import CandidateDashboard from "./pages/CandidateDashboard";
import CandidateDetailPage from "./pages/CandidateDetailPage";
import CandidateComparePage from "./pages/CandidateComparePage";
import RecruiterJobList from "./pages/RecruiterJobList";
import CreateJob from "./pages/CreateJob";
import EditJob from "./pages/EditJob";
import ViewApplicants from "./pages/ViewApplicants";
import BrowseJobs from "./pages/BrowseJobs";
import JobDetails from "./pages/JobDetails";
import AppliedJobs from "./pages/AppliedJobs";
import ResumePage from "./pages/ResumePage";
import InterviewPage from "./pages/InterviewPage";
import InterviewReviewPage from "./pages/InterviewReviewPage";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <AuthProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/candidate"
            element={
              <ProtectedRoute roles={["candidate"]}>
                <CandidateDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/recruiter"
            element={
              <ProtectedRoute roles={["recruiter"]}>
                <RecruiterDashboard />
              </ProtectedRoute>
            }
          />

          {/* Recruiter job management */}
          <Route
            path="/recruiter/jobs"
            element={
              <ProtectedRoute roles={["recruiter"]}>
                <RecruiterJobList />
              </ProtectedRoute>
            }
          />

          {/* Recruiter candidate review */}
          <Route
            path="/recruiter/candidates"
            element={
              <ProtectedRoute roles={["recruiter"]}>
                <CandidateDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/recruiter/candidates/compare"
            element={
              <ProtectedRoute roles={["recruiter"]}>
                <CandidateComparePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/recruiter/candidates/:id"
            element={
              <ProtectedRoute roles={["recruiter"]}>
                <CandidateDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/recruiter/jobs/new"
            element={
              <ProtectedRoute roles={["recruiter"]}>
                <CreateJob />
              </ProtectedRoute>
            }
          />
          <Route
            path="/recruiter/jobs/:id/edit"
            element={
              <ProtectedRoute roles={["recruiter"]}>
                <EditJob />
              </ProtectedRoute>
            }
          />
          <Route
            path="/recruiter/jobs/:id/applicants"
            element={
              <ProtectedRoute roles={["recruiter"]}>
                <ViewApplicants />
              </ProtectedRoute>
            }
          />
          <Route
            path="/recruiter/interviews/:id"
            element={
              <ProtectedRoute roles={["recruiter"]}>
                <InterviewReviewPage />
              </ProtectedRoute>
            }
          />

          {/* Candidate job browsing / applying */}
          <Route
            path="/jobs"
            element={
              <ProtectedRoute roles={["candidate"]}>
                <BrowseJobs />
              </ProtectedRoute>
            }
          />
          <Route
            path="/jobs/:id"
            element={
              <ProtectedRoute roles={["candidate"]}>
                <JobDetails />
              </ProtectedRoute>
            }
          />
          <Route
            path="/applications/mine"
            element={
              <ProtectedRoute roles={["candidate"]}>
                <AppliedJobs />
              </ProtectedRoute>
            }
          />
          <Route
            path="/resume"
            element={
              <ProtectedRoute roles={["candidate"]}>
                <ResumePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/candidate/interviews/:id"
            element={
              <ProtectedRoute roles={["candidate"]}>
                <InterviewPage />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </Layout>
    </AuthProvider>
  );
}
