import React from 'react';

interface PipelineStagesTrackerProps {
  currentStage: number; // 0 for idle, 1-12 for active/completed
}

const STAGES = [
  { num: 1, name: '1. Ingestion', desc: 'WES / Direct Input' },
  { num: 2, name: '2. Gene Filter', desc: 'Pharmacogenes' },
  { num: 3, name: '3. Diplotype', desc: 'PharmVar Caller' },
  { num: 4, name: '4. Phenotype', desc: 'Activity Score' },
  { num: 5, name: '5. Drug Match', desc: 'Gene-Drug Pairs' },
  { num: 6, name: '6. CPIC / ClinPGx', desc: 'Guideline Fetch' },
  { num: 7, name: '7. Evidence', desc: 'Aggregator' },
  { num: 8, name: '8. Conflict', desc: 'Specialist Gates' },
  { num: 9, name: '9. Ranker', desc: 'Actionability Priority' },
  { num: 10, name: '10. AI Explainer', desc: 'Patient/Clinician' },
  { num: 11, name: '11. JSON Output', desc: 'pgx_recommendations' },
  { num: 12, name: '12. CDS Report', desc: 'Module 6 Delivery' }
];

export const PipelineStagesTracker: React.FC<PipelineStagesTrackerProps> = ({ currentStage }) => {
  return (
    <div className="pgx-stages-panel">
      <div className="pgx-stages-header">
        <div className="pgx-stages-title">
          <span>⚡</span>
          <span>12-Stage Deterministic PGx Clinical Decision Support Pipeline</span>
        </div>
        <div className="pgx-guideline-bar" style={{ margin: 0, padding: '4px 10px' }}>
          <span className="pgx-badge pgx-badge-cpic">CPIC Levels A–D</span>
          <span className="pgx-badge pgx-badge-pharmgkb">PharmGKB / ClinPGx 1A</span>
          <span className="pgx-badge pgx-badge-fda">FDA Biomarkers</span>
        </div>
      </div>

      <div className="pgx-stepper-grid">
        {STAGES.map((s) => {
          const isCompleted = currentStage >= s.num;
          const isActive = currentStage === s.num;
          return (
            <div
              key={s.num}
              className={`pgx-step-card ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
            >
              <div className="pgx-step-number">
                {isCompleted && currentStage > s.num ? '✓' : s.num}
              </div>
              <div className="pgx-step-content">
                <div className="pgx-step-name">{s.name}</div>
                <div className="pgx-step-desc">{s.desc}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
