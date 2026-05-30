import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { TopNav } from "./components/layout/TopNav";
import { CoursesPage } from "./pages/CoursesPage";
import { HomePage } from "./pages/HomePage";
import { QAPage } from "./pages/QAPage";
import { QuestionPage } from "./pages/QuestionPage";
import { SummaryPage } from "./pages/SummaryPage";
import { UploadPage } from "./pages/UploadPage";

export function App() {
  return (
    <BrowserRouter>
      <TopNav />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/courses" element={<CoursesPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/qa" element={<QAPage />} />
        <Route path="/questions" element={<QuestionPage />} />
        <Route path="/summary" element={<SummaryPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
