import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { getToken } from './api/client';
import LoginForm from './components/LoginForm';
import NavBar from './components/NavBar';
import Dashboard from './pages/Dashboard';
import JobList from './pages/JobList';
import JobDetail from './pages/JobDetail';
import BuildDetail from './pages/BuildDetail';
import FolderBrowser from './pages/FolderBrowser';
import { useState } from 'react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 30_000 },
  },
});

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  return getToken() ? <>{children}</> : <Navigate to="/login" replace />;
}

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <NavBar />
      <main className="main-content">{children}</main>
    </>
  );
}

export default function App() {
  const [, setLoggedIn] = useState(!!getToken());

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route
            path="/login"
            element={
              getToken() ? (
                <Navigate to="/" replace />
              ) : (
                <LoginForm onSuccess={() => setLoggedIn(true)} />
              )
            }
          />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout><Dashboard /></Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/jobs"
            element={
              <ProtectedRoute>
                <Layout><JobList /></Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/jobs/detail"
            element={
              <ProtectedRoute>
                <Layout><JobDetail /></Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/builds/detail"
            element={
              <ProtectedRoute>
                <Layout><BuildDetail /></Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/folders"
            element={
              <ProtectedRoute>
                <Layout><FolderBrowser /></Layout>
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
