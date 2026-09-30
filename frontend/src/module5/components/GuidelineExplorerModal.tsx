import React, { useEffect, useState } from 'react';
import type { GeneDrugPairInfo } from '../types';
import { fetchSupportedDrugs } from '../api';

interface GuidelineExplorerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectDrug: (drugName: string) => void;
}

export const GuidelineExplorerModal: React.FC<GuidelineExplorerModalProps> = ({
  isOpen,
  onClose,
  onSelectDrug
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [drugs, setDrugs] = useState<GeneDrugPairInfo[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      fetchSupportedDrugs(searchTerm).then((res) => {
        setDrugs(res);
        setLoading(false);
      });
    }
  }, [isOpen, searchTerm]);

  if (!isOpen) return null;

  return (
    <div className="pgx-modal-overlay" onClick={onClose}>
      <div className="pgx-modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="pgx-modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '24px' }}>📚</span>
            <div>
              <h3 style={{ margin: 0, fontSize: '18px', color: '#fff' }}>CPIC & FDA Pharmacogenomic Guideline Database</h3>
              <p style={{ margin: 0, fontSize: '12px', color: 'var(--pgx-text-muted)' }}>
                Authoritative Gene-Drug associations curated from CPIC Levels A–D & FDA Boxed Warnings
              </p>
            </div>
          </div>
          <button className="pgx-close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="pgx-modal-body">
          <input
            type="text"
            className="pgx-input"
            placeholder="Search by drug name, brand name (e.g. Plavix, Lipitor), or gene (e.g. CYP2C19)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            autoFocus
          />

          {loading ? (
            <div style={{ textAlign: 'center', padding: '30px', color: 'var(--pgx-text-muted)' }}>
              Loading guideline database...
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {drugs.map((d, i) => (
                <div
                  key={i}
                  style={{
                    padding: '12px 16px',
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid var(--pgx-border)',
                    borderRadius: '8px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: '12px'
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <strong style={{ fontSize: '15px', color: '#fff' }}>{d.drug_name}</strong>
                      <span className="pgx-badge pgx-badge-cpic">CPIC {d.cpic_level}</span>
                      <span className="pgx-badge pgx-badge-pharmgkb">ClinPGx {d.pharmgkb_level}</span>
                      {d.fda_label_status && (
                        <span className="pgx-badge pgx-badge-fda">FDA {d.fda_label_status}</span>
                      )}
                    </div>

                    <div style={{ fontSize: '12px', color: 'var(--pgx-text-muted)', marginTop: '4px' }}>
                      Primary Gene: <strong style={{ color: '#a5b4fc' }}>{d.primary_gene}</strong>
                      {d.brand_names.length > 0 && (
                        <span> · Brands: {d.brand_names.join(', ')}</span>
                      )}
                      <span> · Area: {d.therapeutic_area}</span>
                    </div>
                  </div>

                  <button
                    type="button"
                    className="pgx-btn pgx-btn-secondary"
                    style={{ padding: '6px 12px', fontSize: '12px', flexShrink: 0 }}
                    onClick={() => {
                      onSelectDrug(d.drug_name);
                      onClose();
                    }}
                  >
                    + Add to Patient
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
