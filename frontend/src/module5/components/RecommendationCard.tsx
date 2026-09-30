import React, { useState } from 'react';
import type { GeneDrugRecommendation } from '../types';

interface RecommendationCardProps {
  recommendation: GeneDrugRecommendation;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendation: rec }) => {
  const [activeTab, setActiveTab] = useState<'clinician' | 'patient' | 'json'>('clinician');

  const getActionabilityBadge = (action: string) => {
    const a = action.toLowerCase();
    if (a.includes('contraindicated') || a.includes('severe toxicity') || a.includes('alternative') || a.includes('boxed warning')) {
      return <span className="pgx-rec-action-badge act-critical">🚫 {rec.actionability}</span>;
    }
    if (a.includes('major dose') || a.includes('dose adjustment') || a.includes('toxicity')) {
      return <span className="pgx-rec-action-badge act-warning">⚠️ {rec.actionability}</span>;
    }
    return <span className="pgx-rec-action-badge act-standard">✅ {rec.actionability}</span>;
  };

  return (
    <div className={`pgx-rec-card urgency-${rec.rank_priority}`}>
      <div className="pgx-rec-header">
        <div className="pgx-rec-drug-info">
          <h3 className="pgx-rec-drug-name">{rec.drug}</h3>
          <span className="pgx-rec-gene-pill">
            Target: <strong>{rec.gene}</strong> ({rec.diplotype})
          </span>
          {rec.fda_label_status && (
            <span className="pgx-badge pgx-badge-fda">
              FDA {rec.fda_label_status}
            </span>
          )}
        </div>
        <div>
          {getActionabilityBadge(rec.actionability)}
        </div>
      </div>

      <div className="pgx-rec-body">
        {/* Main Recommendation Statement */}
        <div className="pgx-rec-statement">
          <h4>Clinical Guideline Recommendation</h4>
          <p className="pgx-rec-text">{rec.recommendation}</p>
          <p className="pgx-implication-text">
            <strong>Biological Implication:</strong> {rec.clinical_implication}
          </p>
        </div>

        {/* Evidence Metadata Grid */}
        <div className="pgx-evidence-grid">
          <div className="pgx-evidence-item">
            <span className="pgx-evidence-label">Evidence Level</span>
            <span className="pgx-evidence-val" style={{ color: '#818cf8' }}>
              {rec.evidence_level} {rec.pharmgkb_level ? `· ClinPGx ${rec.pharmgkb_level}` : ''}
            </span>
          </div>
          <div className="pgx-evidence-item">
            <span className="pgx-evidence-label">Metabolizer Phenotype</span>
            <span className="pgx-evidence-val" style={{ color: '#38bdf8' }}>{rec.phenotype}</span>
          </div>
          <div className="pgx-evidence-item">
            <span className="pgx-evidence-label">Primary Source</span>
            <span className="pgx-evidence-val">{rec.source}</span>
          </div>
          <div className="pgx-evidence-item">
            <span className="pgx-evidence-label">Specialist Routing</span>
            <span className="pgx-evidence-val" style={{ color: '#f59e0b' }}>
              👨‍⚕️ {rec.specialist}
            </span>
          </div>
        </div>

        {/* Tabbed Explanation Layer */}
        <div>
          <div className="pgx-tabs-header">
            <button
              type="button"
              className={`pgx-tab-btn ${activeTab === 'clinician' ? 'active' : ''}`}
              onClick={() => setActiveTab('clinician')}
            >
              📋 Clinician Pharmacology Summary
            </button>
            <button
              type="button"
              className={`pgx-tab-btn ${activeTab === 'patient' ? 'active' : ''}`}
              onClick={() => setActiveTab('patient')}
            >
              💬 Patient-Friendly Plain Language
            </button>
            <button
              type="button"
              className={`pgx-tab-btn ${activeTab === 'json' ? 'active' : ''}`}
              onClick={() => setActiveTab('json')}
            >
              ⚙️ Structured JSON Payload
            </button>
          </div>

          <div style={{ marginTop: '10px' }}>
            {activeTab === 'clinician' && (
              <div className="pgx-tab-content">
                <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
                  <span style={{ fontSize: '18px' }}>🩺</span>
                  <p style={{ margin: 0 }}>{rec.clinician_summary}</p>
                </div>
              </div>
            )}

            {activeTab === 'patient' && (
              <div className="pgx-tab-content" style={{ background: 'rgba(99, 102, 241, 0.08)', borderColor: 'rgba(99, 102, 241, 0.25)' }}>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
                  <span style={{ fontSize: '18px' }}>🗣️</span>
                  <p style={{ margin: 0, color: '#e0e7ff' }}>{rec.patient_explanation}</p>
                </div>
              </div>
            )}

            {activeTab === 'json' && (
              <div className="pgx-tab-content">
                <pre className="pgx-json-block">{JSON.stringify(rec, null, 2)}</pre>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
