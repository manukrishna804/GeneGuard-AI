import React, { useEffect, useState } from 'react';
import './styles/module5.css';
import { Header } from './components/Header';
import { PipelineStagesTracker } from './components/PipelineStagesTracker';
import { PatientInputSection } from './components/PatientInputSection';
import { ConflictAlertBanner } from './components/ConflictAlertBanner';
import { DiplotypeSummaryTable } from './components/DiplotypeSummaryTable';
import { RecommendationCard } from './components/RecommendationCard';
import { GuidelineExplorerModal } from './components/GuidelineExplorerModal';
import { PatientPresetCase, PGxPipelineResponse, VariantInput } from './types';
import { pingPGx, runPGxAnalysis } from './api';

export const Module5Dashboard: React.FC = () => {
  const [isLiveApi, setIsLiveApi] = useState(false);
  const [isExplorerOpen, setIsExplorerOpen] = useState(false);
  const [pipelineStage, setPipelineStage] = useState(12);

  // Patient & Input States
  const [patientId, setPatientId] = useState<number>(101);
  const [medications, setMedications] = useState<string[]>(['Plavix']);
  const [variants, setVariants] = useState<VariantInput[]>([
    {
      gene: 'CYP2C19',
      rsid: 'rs4244285',
      zygosity: 'homozygous_alt',
      star_allele: '*2'
    }
  ]);
  const [selectedPresetId, setSelectedPresetId] = useState<string | null>('case_cardio_cyp2c19');

  // Results State
  const [results, setResults] = useState<PGxPipelineResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [filterAction, setFilterAction] = useState<string>('all');

  // Check Backend Status on Mount
  useEffect(() => {
    pingPGx().then((res) => {
      setIsLiveApi(res.isLive);
    });
    // Trigger initial analysis on mount
    handleExecuteAnalysis();
  }, []);

  const handleSelectPreset = (preset: PatientPresetCase) => {
    setSelectedPresetId(preset.id);
    setPatientId(preset.patientId);
    setMedications(preset.medications);
    setVariants(preset.variants);
  };

  const handleReset = () => {
    setSelectedPresetId(null);
    setPatientId(1);
    setMedications(['Plavix']);
    setVariants([]);
    setResults(null);
    setPipelineStage(0);
  };

  const handleExecuteAnalysis = async () => {
    if (medications.length === 0) return;
    setIsLoading(true);

    // Animate stages for visual tracking
    setPipelineStage(1);
    const interval = setInterval(() => {
      setPipelineStage((prev) => (prev < 12 ? prev + 1 : 12));
    }, 120);

    try {
      const response = await runPGxAnalysis({
        patient_id: patientId,
        medications: medications,
        variants: variants,
        use_latest_wes: false
      });
      clearInterval(interval);
      setPipelineStage(12);
      setResults(response);
    } catch (err) {
      clearInterval(interval);
      console.error('Error running PGx analysis:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredRecommendations = (results?.recommendations || []).filter((rec) => {
    if (filterAction === 'all') return true;
    if (filterAction === 'critical') {
      return (
        rec.actionability.toLowerCase().includes('contraindicated') ||
        rec.actionability.toLowerCase().includes('severe toxicity') ||
        rec.actionability.toLowerCase().includes('alternative')
      );
    }
    if (filterAction === 'adjustment') {
      return rec.actionability.toLowerCase().includes('dose');
    }
    if (filterAction === 'standard') {
      return rec.actionability.toLowerCase().includes('standard');
    }
    return true;
  });

  const handleExportJSON = () => {
    if (!results) return;
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pgx_recommendations_patient_${results.patient_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrintReport = () => {
    window.print();
  };

  return (
    <div className="pgx-dashboard-container">
      <div className="pgx-content-wrapper">
        <Header
          isLiveApi={isLiveApi}
          onOpenExplorer={() => setIsExplorerOpen(true)}
          onReset={handleReset}
        />

        <PipelineStagesTracker currentStage={pipelineStage} />

        <div className="pgx-main-grid">
          {/* Left Side: Inputs */}
          <PatientInputSection
            patientId={patientId}
            setPatientId={setPatientId}
            medications={medications}
            setMedications={setMedications}
            variants={variants}
            setVariants={setVariants}
            selectedPresetId={selectedPresetId}
            onSelectPreset={handleSelectPreset}
            onRunAnalysis={handleExecuteAnalysis}
            isLoading={isLoading}
          />

          {/* Right Side: Results */}
          <div className="pgx-results-panel">
            {results && (
              <>
                {/* Metrics Bar */}
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
                    gap: '14px'
                  }}
                >
                  <div
                    style={{
                      background: 'var(--pgx-bg-card)',
                      border: '1px solid var(--pgx-border)',
                      borderRadius: 'var(--pgx-radius-md)',
                      padding: '16px',
                      backdropFilter: 'blur(16px)'
                    }}
                  >
                    <div style={{ fontSize: '11px', color: 'var(--pgx-text-muted)' }}>Drugs Screened</div>
                    <div style={{ fontSize: '24px', fontWeight: 700, color: '#fff', marginTop: '4px' }}>
                      {results.total_drugs_evaluated}
                    </div>
                  </div>

                  <div
                    style={{
                      background: 'var(--pgx-bg-card)',
                      border: '1px solid var(--pgx-border)',
                      borderRadius: 'var(--pgx-radius-md)',
                      padding: '16px',
                      backdropFilter: 'blur(16px)'
                    }}
                  >
                    <div style={{ fontSize: '11px', color: 'var(--pgx-text-muted)' }}>CPIC Guideline Pairs</div>
                    <div style={{ fontSize: '24px', fontWeight: 700, color: '#818cf8', marginTop: '4px' }}>
                      {results.matched_gene_drug_pairs}
                    </div>
                  </div>

                  <div
                    style={{
                      background: 'var(--pgx-bg-card)',
                      border: '1px solid var(--pgx-border)',
                      borderRadius: 'var(--pgx-radius-md)',
                      padding: '16px',
                      backdropFilter: 'blur(16px)'
                    }}
                  >
                    <div style={{ fontSize: '11px', color: 'var(--pgx-text-muted)' }}>Overall Confidence</div>
                    <div style={{ fontSize: '24px', fontWeight: 700, color: '#34d399', marginTop: '4px' }}>
                      {results.overall_confidence}%
                    </div>
                  </div>

                  <div
                    style={{
                      background: 'var(--pgx-bg-card)',
                      border: '1px solid var(--pgx-border)',
                      borderRadius: 'var(--pgx-radius-md)',
                      padding: '16px',
                      backdropFilter: 'blur(16px)'
                    }}
                  >
                    <div style={{ fontSize: '11px', color: 'var(--pgx-text-muted)' }}>Clinical Review Gates</div>
                    <div
                      style={{
                        fontSize: '24px',
                        fontWeight: 700,
                        color: results.flagged_conflicts.length > 0 ? '#f87171' : '#34d399',
                        marginTop: '4px'
                      }}
                    >
                      {results.flagged_conflicts.length}
                    </div>
                  </div>
                </div>

                {/* Conflict Alert Banner */}
                <ConflictAlertBanner conflicts={results.flagged_conflicts} />

                {/* Diplotype / Phenotype Matrix */}
                <DiplotypeSummaryTable calls={results.diplotype_calls} />

                {/* Actionability Filter & Export Controls */}
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    gap: '12px'
                  }}
                >
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    <button
                      type="button"
                      className={`pgx-tab-btn ${filterAction === 'all' ? 'active' : ''}`}
                      onClick={() => setFilterAction('all')}
                    >
                      All Recommendations ({results.recommendations.length})
                    </button>
                    <button
                      type="button"
                      className={`pgx-tab-btn ${filterAction === 'critical' ? 'active' : ''}`}
                      onClick={() => setFilterAction('critical')}
                    >
                      🚫 Critical / Alternative Required
                    </button>
                    <button
                      type="button"
                      className={`pgx-tab-btn ${filterAction === 'adjustment' ? 'active' : ''}`}
                      onClick={() => setFilterAction('adjustment')}
                    >
                      ⚠️ Dose Adjustments
                    </button>
                    <button
                      type="button"
                      className={`pgx-tab-btn ${filterAction === 'standard' ? 'active' : ''}`}
                      onClick={() => setFilterAction('standard')}
                    >
                      ✅ Standard Dosing
                    </button>
                  </div>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      type="button"
                      className="pgx-btn pgx-btn-secondary"
                      style={{ padding: '6px 12px', fontSize: '12px' }}
                      onClick={handleExportJSON}
                    >
                      📥 Export pgx_recommendations.json (Module 6)
                    </button>
                    <button
                      type="button"
                      className="pgx-btn pgx-btn-secondary"
                      style={{ padding: '6px 12px', fontSize: '12px' }}
                      onClick={handlePrintReport}
                    >
                      🖨️ Print Clinical Report
                    </button>
                  </div>
                </div>

                {/* Recommendations Cards List */}
                <div className="pgx-rec-list">
                  {filteredRecommendations.length > 0 ? (
                    filteredRecommendations.map((rec, index) => (
                      <RecommendationCard key={index} recommendation={rec} />
                    ))
                  ) : (
                    <div style={{ textAlign: 'center', padding: '40px', color: 'var(--pgx-text-muted)' }}>
                      No recommendations matched the selected filter.
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      <GuidelineExplorerModal
        isOpen={isExplorerOpen}
        onClose={() => setIsExplorerOpen(false)}
        onSelectDrug={(d) => {
          if (!medications.includes(d)) {
            setMedications([...medications, d]);
          }
        }}
      />
    </div>
  );
};
export default Module5Dashboard;
