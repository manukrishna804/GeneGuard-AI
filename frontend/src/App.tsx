import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
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
    <Router>
      <Routes>
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
      </Routes>
    </Router>
  );
}

export default App;
