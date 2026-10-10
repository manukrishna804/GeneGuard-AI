import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/layout/Layout';
import ProtectedRoute from './components/layout/ProtectedRoute';
import Auth from './pages/Auth';
import Dashboard from './pages/Dashboard';
import WESAnalysis from './pages/WESAnalysis';
import FacialPhenotype from './pages/FacialPhenotype';
import ComplexDiseaseRisk from './pages/ComplexDiseaseRisk';
import ConsanguinityRisk from './pages/ConsanguinityRisk';
import Pharmacogenomics from './pages/Pharmacogenomics';
import FamilyPedigree from './pages/FamilyPedigree';
import PatientReport from './pages/PatientReport';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/auth" element={<Auth />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="wes-analysis" element={<WESAnalysis />} />
              <Route path="facial-phenotype" element={<FacialPhenotype />} />
              <Route path="complex-disease" element={<ComplexDiseaseRisk />} />
              <Route path="consanguinity" element={<ConsanguinityRisk />} />
              <Route path="pharmacogenomics" element={<Pharmacogenomics />} />
              <Route path="pedigree" element={<FamilyPedigree />} />
              <Route path="report" element={<PatientReport />} />
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
