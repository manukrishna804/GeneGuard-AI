import React from 'react';

interface HeaderProps {
  isLiveApi: boolean;
  onOpenExplorer: () => void;
  onReset: () => void;
}

export const Header: React.FC<HeaderProps> = ({ isLiveApi, onOpenExplorer, onReset }) => {
  return (
    <header className="pgx-header">
      <div className="pgx-header-title-area">
        <div className="pgx-logo-badge" title="GeneGuard Module 5">
          💊
        </div>
        <div>
          <h1>Module 5: Pharmacogenomics (PGx) Engine</h1>
          <div className="pgx-header-subtitle">
            <span>Clinical Decision Support (CDS) · Rule-Based Architecture (No ML)</span>
            <span>•</span>
            <span className="pgx-status-pill">
              <span className="pgx-status-dot" style={{ backgroundColor: isLiveApi ? '#10b981' : '#6366f1' }}></span>
              {isLiveApi ? 'FastAPI Live Backend' : 'Active Deterministic Engine'}
            </span>
          </div>
        </div>
      </div>

      <div className="pgx-header-actions">
        <button className="pgx-btn pgx-btn-secondary" onClick={onOpenExplorer}>
          🔍 CPIC Guideline Explorer
        </button>
        <button className="pgx-btn pgx-btn-secondary" onClick={onReset}>
          🔄 Reset Form
        </button>
      </div>
    </header>
  );
};
