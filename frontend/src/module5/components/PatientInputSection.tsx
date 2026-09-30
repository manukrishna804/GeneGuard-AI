import React, { useState } from 'react';
import type { PatientPresetCase, VariantInput } from '../types';
import { PATIENT_PRESET_CASES } from '../mockData';

interface PatientInputSectionProps {
  patientId: number;
  setPatientId: (id: number) => void;
  medications: string[];
  setMedications: (meds: string[]) => void;
  variants: VariantInput[];
  setVariants: (vars: VariantInput[]) => void;
  selectedPresetId: string | null;
  onSelectPreset: (preset: PatientPresetCase) => void;
  onRunAnalysis: () => void;
  isLoading: boolean;
}

const COMMON_DRUGS = [
  'Plavix', 'Clopidogrel', 'Warfarin', 'Coumadin', 'Simvastatin',
  'Codeine', 'Fluorouracil', 'Capecitabine', 'Abacavir', 'Allopurinol', 'Tacrolimus'
];

export const PatientInputSection: React.FC<PatientInputSectionProps> = ({
  patientId,
  setPatientId,
  medications,
  setMedications,
  variants,
  setVariants,
  selectedPresetId,
  onSelectPreset,
  onRunAnalysis,
  isLoading
}) => {
  const [newMedInput, setNewMedInput] = useState('');
  const [geneInput, setGeneInput] = useState('CYP2C19');
  const [alleleInput, setAlleleInput] = useState('*2');
  const [zygosityInput, setZygosityInput] = useState('homozygous_alt');
  const [rsidInput, _setRsidInput] = useState('rs4244285');

  const handleAddMed = (drugName: string) => {
    const trimmed = drugName.trim();
    if (trimmed && !medications.includes(trimmed)) {
      setMedications([...medications, trimmed]);
      setNewMedInput('');
    }
  };

  const handleRemoveMed = (drugName: string) => {
    setMedications(medications.filter(m => m !== drugName));
  };

  const handleAddVariant = () => {
    if (!geneInput.trim()) return;
    const newVar: VariantInput = {
      gene: geneInput.trim().toUpperCase(),
      star_allele: alleleInput.trim() || undefined,
      rsid: rsidInput.trim() || undefined,
      zygosity: zygosityInput
    };
    setVariants([...variants, newVar]);
  };

  const handleRemoveVariant = (index: number) => {
    setVariants(variants.filter((_, i) => i !== index));
  };

  return (
    <div className="pgx-input-panel">
      <div>
        <h3 className="pgx-panel-title">
          <span>🧑‍⚕️</span>
          <span>Patient & Clinical Input</span>
        </h3>
        <p className="pgx-panel-subtitle">Select a clinical preset or configure custom patient medications and genomic variants.</p>
      </div>

      {/* Preset Patient Cases */}
      <div className="pgx-preset-section">
        <label className="pgx-label">
          <span>Clinical Benchmark Cases</span>
          <span style={{ fontSize: '11px', color: 'var(--pgx-text-muted)' }}>Click to load</span>
        </label>
        <div className="pgx-preset-list">
          {PATIENT_PRESET_CASES.map((preset) => {
            const isSelected = selectedPresetId === preset.id;
            return (
              <div
                key={preset.id}
                className={`pgx-preset-item ${isSelected ? 'selected' : ''}`}
                onClick={() => onSelectPreset(preset)}
              >
                <div className="pgx-preset-top">
                  <span className="pgx-preset-name">{preset.title}</span>
                  <span className="pgx-preset-category">{preset.category}</span>
                </div>
                <div className="pgx-preset-desc">{preset.clinicalContext}</div>
              </div>
            );
          })}
        </div>
      </div>

      <hr style={{ border: 'none', borderTop: '1px solid var(--pgx-border)', margin: 0 }} />

      {/* Patient ID */}
      <div className="pgx-form-group">
        <label className="pgx-label" htmlFor="patient-id-input">
          <span>Patient ID</span>
          <span style={{ fontSize: '11px', color: 'var(--pgx-text-muted)' }}>Required</span>
        </label>
        <input
          id="patient-id-input"
          type="number"
          className="pgx-input"
          value={patientId}
          onChange={(e) => setPatientId(Number(e.target.value) || 1)}
        />
      </div>

      {/* Medication List */}
      <div className="pgx-form-group">
        <label className="pgx-label" htmlFor="med-input">
          <span>Prescribed Medications ({medications.length})</span>
        </label>
        <div style={{ display: 'flex', gap: '8px' }}>
          <input
            id="med-input"
            type="text"
            className="pgx-input"
            placeholder="e.g. Plavix, Warfarin..."
            value={newMedInput}
            onChange={(e) => setNewMedInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleAddMed(newMedInput);
              }
            }}
          />
          <button
            type="button"
            className="pgx-btn pgx-btn-secondary"
            onClick={() => handleAddMed(newMedInput)}
          >
            Add
          </button>
        </div>

        {/* Quick Drug Buttons */}
        <div className="pgx-quick-drugs">
          {COMMON_DRUGS.map((d) => (
            <button
              key={d}
              type="button"
              className="pgx-quick-drug-btn"
              onClick={() => handleAddMed(d)}
            >
              + {d}
            </button>
          ))}
        </div>

        {/* Selected Medication Tags */}
        {medications.length > 0 && (
          <div className="pgx-tags-wrap">
            {medications.map((m) => (
              <span key={m} className="pgx-med-tag">
                💊 {m}
                <button type="button" onClick={() => handleRemoveMed(m)} title="Remove">×</button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Genomic Variants Builder */}
      <div className="pgx-form-group">
        <label className="pgx-label">
          <span>Genomic Pharmacogene Variants ({variants.length})</span>
        </label>

        {variants.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {variants.map((v, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  background: 'rgba(0,0,0,0.3)',
                  padding: '6px 10px',
                  borderRadius: '6px',
                  border: '1px solid var(--pgx-border)',
                  fontSize: '12px'
                }}
              >
                <div>
                  <strong style={{ color: '#a5b4fc' }}>{v.gene}</strong>{' '}
                  <span style={{ fontFamily: 'var(--mono)', color: '#38bdf8' }}>{v.star_allele || v.rsid || 'Variant'}</span>{' '}
                  <span style={{ color: 'var(--pgx-text-muted)' }}>({v.zygosity})</span>
                </div>
                <button
                  type="button"
                  onClick={() => handleRemoveVariant(idx)}
                  style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer' }}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ fontSize: '12px', color: 'var(--pgx-text-muted)', fontStyle: 'italic' }}>
            No custom variants added. Standard reference *1/*1 wildtype will be evaluated.
          </div>
        )}

        {/* Add custom variant row */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', marginTop: '6px' }}>
          <select
            className="pgx-select"
            value={geneInput}
            onChange={(e) => setGeneInput(e.target.value)}
          >
            <option value="CYP2C19">CYP2C19</option>
            <option value="CYP2D6">CYP2D6</option>
            <option value="CYP2C9">CYP2C9</option>
            <option value="DPYD">DPYD</option>
            <option value="TPMT">TPMT</option>
            <option value="SLCO1B1">SLCO1B1</option>
            <option value="VKORC1">VKORC1</option>
            <option value="HLA-B">HLA-B</option>
            <option value="CYP3A5">CYP3A5</option>
          </select>

          <input
            type="text"
            className="pgx-input"
            placeholder="Allele, e.g. *2, *4"
            value={alleleInput}
            onChange={(e) => setAlleleInput(e.target.value)}
          />

          <select
            className="pgx-select"
            value={zygosityInput}
            onChange={(e) => setZygosityInput(e.target.value)}
          >
            <option value="homozygous_alt">Homozygous Alt</option>
            <option value="heterozygous">Heterozygous</option>
            <option value="homozygous_ref">Homozygous Ref</option>
          </select>

          <button
            type="button"
            className="pgx-btn pgx-btn-secondary"
            style={{ padding: '6px 12px', fontSize: '12px' }}
            onClick={handleAddVariant}
          >
            + Add Variant
          </button>
        </div>
      </div>

      {/* Trigger Button */}
      <button
        type="button"
        className="pgx-btn pgx-btn-primary"
        style={{ width: '100%', padding: '14px', fontSize: '15px' }}
        onClick={onRunAnalysis}
        disabled={isLoading || medications.length === 0}
      >
        {isLoading ? (
          <span>⏳ Running CPIC & CDS Engine...</span>
        ) : (
          <span>🚀 Run Pharmacogenomics CDS Engine</span>
        )}
      </button>
    </div>
  );
};
