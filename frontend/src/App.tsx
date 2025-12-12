import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Layout, AuthLayout } from "./components/layout/Layout";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { Dashboard } from "./pages/Dashboard";
import { NewsPage } from "./pages/News";
import { FiltersPage } from "./pages/Filters";
import { SettingsPage } from "./pages/Settings";
import "./index.css";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Auth Routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Route>

        {/* Protected Routes */}
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/news" element={<NewsPage />} />
          <Route path="/filters" element={<FiltersPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>

        {/* Redirect root to dashboard */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        {/* 404 - Redirect to dashboard */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
