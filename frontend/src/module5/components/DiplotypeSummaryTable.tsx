import React from 'react';
import type { DiplotypeCall } from '../types';

interface DiplotypeSummaryTableProps {
  calls: DiplotypeCall[];
}

export const DiplotypeSummaryTable: React.FC<DiplotypeSummaryTableProps> = ({ calls }) => {
  if (!calls || calls.length === 0) return null;

  const getPhenotypeBadgeClass = (pheno: string) => {
    const p = pheno.toLowerCase();
    if (p.includes('poor') || p.includes('high risk') || p.includes('positive') || p.includes('deficient')) {
      return 'pheno-pm';
    }
    if (p.includes('intermediate') || p.includes('decreased') || p.includes('sensitivity')) {
      return 'pheno-im';
    }
    if (p.includes('ultra') || p.includes('rapid')) {
      return 'pheno-um';
    }
    return 'pheno-nm';
  };

  return (
    <div className="pgx-diplotype-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 className="pgx-panel-title" style={{ margin: 0 }}>
          <span>🧬</span>
          <span>Genomic Pharmacogene & Phenotype Profile</span>
        </h3>
        <span style={{ fontSize: '12px', color: 'var(--pgx-text-muted)' }}>
          {calls.length} Gene{calls.length > 1 ? 's' : ''} Profiled
        </span>
      </div>

      <table className="pgx-table">
        <thead>
          <tr>
            <th>Pharmacogene</th>
            <th>Diplotype Call</th>
            <th>Activity Score</th>
            <th>Metabolizer Phenotype</th>
            <th>Annotation Source</th>
          </tr>
        </thead>
        <tbody>
          {calls.map((c, i) => (
            <tr key={i}>
              <td>
                <span className="pgx-gene-tag">{c.gene}</span>
              </td>
              <td>
                <span className="pgx-diplotype-tag">{c.diplotype}</span>
              </td>
              <td>
                {c.activity_score !== null && c.activity_score !== undefined ? (
                  <span style={{ fontWeight: 600, color: '#38bdf8' }}>{c.activity_score.toFixed(2)}</span>
                ) : (
                  <span style={{ color: 'var(--pgx-text-faint)' }}>N/A (Direct)</span>
                )}
              </td>
              <td>
                <span className={`pgx-pheno-badge ${getPhenotypeBadgeClass(c.phenotype)}`}>
                  {c.phenotype}
                </span>
              </td>
              <td>
                <span style={{ fontSize: '11px', color: 'var(--pgx-text-muted)' }}>{c.source || 'CPIC/PharmVar'}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
