import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { useAuth } from './hooks/useAuth';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import NewAnalysis from './pages/NewAnalysis';
import PreviousReports from './pages/PreviousReports';
import Dataset from './pages/Dataset';
import ModelPerformance from './pages/ModelPerformance';
import About from './pages/About';
import MainLayout from './components/Layout/MainLayout';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const auth = useAuth();
  if (auth?.loading) return <div>Loading...</div>;
  if (!auth?.user) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="new-analysis" element={<NewAnalysis />} />
            <Route path="reports" element={<PreviousReports />} />
            <Route path="dataset" element={<Dataset />} />
            <Route path="model-performance" element={<ModelPerformance />} />
            <Route path="about" element={<About />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
