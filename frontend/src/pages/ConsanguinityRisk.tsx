import { useState } from 'react';

interface FamilyHistoryEntry {
  relationship: string;
  sex: string;
  health_status: string;
  condition: string;
  known_variant: string;
}

interface RiskResult {
  gene: string;
  condition: string;
  inheritance: string;
  parent1_status: string;
  parent2_status: string;
  affected_probability: number;
  carrier_probability: number;
  unaffected_probability: number;
  evidence_sources: string[];
  explanation: string;
}

interface InterventionRecommendation {
  option: string;
  reason: string;
}

interface InterventionAssessment {
  condition: string;
  inheritance: string;
  classification: string;
  recommendations: InterventionRecommendation[];
  disclaimer: string;
}

interface AssessmentResult {
  assessment_id?: string | null;
  status?: string;
  risks?: RiskResult[];
  shared_risk_count?: number;
  uncertain_variant_count?: number;
  compound_heterozygous_candidates?: unknown[];
  consanguinity_context?: string;
  family_history_context?: string[];
  interventions?: InterventionAssessment[];
  limitations?: string[];
}

export default function ConsanguinityRisk() {
  const [parent1File, setParent1File] = useState<File | null>(null);
  const [parent2File, setParent2File] = useState<File | null>(null);

  const [relationship, setRelationship] = useState('unknown');

  const [familyHistory, setFamilyHistory] = useState<FamilyHistoryEntry[]>([]);
  const [familyMember, setFamilyMember] = useState('');
  const [familySex, setFamilySex] = useState('');
  const [familyHealthStatus, setFamilyHealthStatus] = useState('');
  const [familyCondition, setFamilyCondition] = useState('');
  const [familyKnownVariant, setFamilyKnownVariant] = useState('');
  const [showFamilyForm, setShowFamilyForm] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<AssessmentResult | null>(null);

  const addFamilyHistory = () => {
    if (!familyMember || !familyHealthStatus) return;
    setFamilyHistory(prev => [
      ...prev,
      {
        relationship: familyMember,
        sex: familySex,
        health_status: familyHealthStatus,
        condition: familyCondition,
        known_variant: familyKnownVariant,
      }
    ]);
    setFamilyMember('');
    setFamilySex('');
    setFamilyHealthStatus('');
    setFamilyCondition('');
    setFamilyKnownVariant('');
    setShowFamilyForm(false);
  };

  const removeFamilyHistory = (index: number) => {
    setFamilyHistory(prev => prev.filter((_, i) => i !== index));
  };

  const handleAnalyze = async () => {
    if (!parent1File || !parent2File) {
      setError('Please upload both Parent 1 and Parent 2 VCF files.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('parent1_vcf', parent1File);
      formData.append('parent2_vcf', parent2File);
      formData.append('relationship', relationship);
      formData.append('family_history', JSON.stringify(familyHistory));

      const response = await fetch('/api/v1/consanguinity/assess-vcf', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.detail || 'Genetic risk assessment failed.');
      }

      setResult(data);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 h-full pb-10">
      <div className="flex items-center gap-2">
        <h1 className="text-3xl font-bold text-gray-900">Consanguinity Risk</h1>
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-green-50 text-green-700 border border-green-200 flex items-center gap-1 uppercase tracking-wider">
          <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div> READY
        </span>
      </div>
      <p className="text-gray-500">Assess potential genetic risks in offspring using parental genetic data and consanguinity context.</p>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl flex gap-3 items-start">
          <span className="material-symbols-outlined text-red-500">error</span>
          <div>
            <strong className="block font-medium">Assessment Error</strong>
            <p className="text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* 1. Parental Genetic Data */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-1 text-gray-900 flex items-center gap-2">
          <span className="material-symbols-outlined text-primary">family_history</span>
          1. Parental Genetic Data
        </h2>
        <p className="text-sm text-gray-500 mb-6">Upload the VCF genetic variant files for both parents.</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Parent 1 */}
          <div className="border border-gray-200 rounded-lg p-5">
            <h3 className="font-medium text-gray-900 mb-4 flex items-center gap-2">
              <span className="bg-gray-100 text-gray-600 rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">01</span>
              Parent 1 VCF
            </h3>
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <span className="material-symbols-outlined text-gray-400 text-3xl mb-2">upload_file</span>
                {parent1File ? (
                  <p className="text-sm font-semibold text-primary">{parent1File.name}</p>
                ) : (
                  <p className="text-sm text-gray-500"><span className="font-semibold text-primary">Click to upload</span> Parent 1 VCF</p>
                )}
              </div>
              <input type="file" accept=".vcf,.vcf.gz" className="hidden" onChange={(e) => setParent1File(e.target.files?.[0] || null)} />
            </label>
          </div>

          {/* Parent 2 */}
          <div className="border border-gray-200 rounded-lg p-5">
            <h3 className="font-medium text-gray-900 mb-4 flex items-center gap-2">
              <span className="bg-gray-100 text-gray-600 rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">02</span>
              Parent 2 VCF
            </h3>
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <span className="material-symbols-outlined text-gray-400 text-3xl mb-2">upload_file</span>
                {parent2File ? (
                  <p className="text-sm font-semibold text-primary">{parent2File.name}</p>
                ) : (
                  <p className="text-sm text-gray-500"><span className="font-semibold text-primary">Click to upload</span> Parent 2 VCF</p>
                )}
              </div>
              <input type="file" accept=".vcf,.vcf.gz" className="hidden" onChange={(e) => setParent2File(e.target.files?.[0] || null)} />
            </label>
          </div>
        </div>
      </div>

      {/* 2. Consanguinity */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-1 text-gray-900 flex items-center gap-2">
          <span className="material-symbols-outlined text-primary">diversity_1</span>
          2. Family &amp; Consanguinity Context
        </h2>
        <p className="text-sm text-gray-500 mb-6">Provide relationship information to improve contextual risk interpretation.</p>

        <div className="max-w-md">
          <label className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-2">Relationship between parents</label>
          <select 
            value={relationship} 
            onChange={(e) => setRelationship(e.target.value)}
            className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none text-gray-900"
          >
            <option value="unknown">Unknown</option>
            <option value="unrelated">Unrelated</option>
            <option value="first_cousin">First Cousins</option>
            <option value="second_cousin">Second Cousins</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>

      {/* 3. Family History */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-1 text-gray-900 flex items-center gap-2">
          <span className="material-symbols-outlined text-primary">history_edu</span>
          3. Family History (Optional)
        </h2>
        <p className="text-sm text-gray-500 mb-6">Add known inherited conditions or relevant family history.</p>

        {familyHistory.length > 0 && (
          <div className="space-y-3 mb-6">
            {familyHistory.map((entry, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{entry.relationship} <span className="text-gray-500 font-normal text-sm">({entry.sex || 'Unknown sex'})</span></h4>
                  <p className="text-sm text-gray-600 mt-1">Status: <span className="font-medium">{entry.health_status}</span></p>
                  {(entry.condition || entry.known_variant) && (
                    <p className="text-xs text-gray-500 mt-1">
                      {entry.condition && `Condition: ${entry.condition} `}
                      {entry.known_variant && `| Variant: ${entry.known_variant}`}
                    </p>
                  )}
                </div>
                <button onClick={() => removeFamilyHistory(index)} className="p-2 text-gray-400 hover:text-red-500 transition-colors">
                  <span className="material-symbols-outlined">delete</span>
                </button>
              </div>
            ))}
          </div>
        )}

        {showFamilyForm ? (
          <div className="p-5 border border-gray-200 rounded-lg bg-gray-50">
            <h4 className="font-medium text-gray-900 mb-4">Add Family Member</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1">Relation</label>
                <input type="text" placeholder="e.g. Sibling, parent" value={familyMember} onChange={e => setFamilyMember(e.target.value)} className="w-full px-3 py-2 bg-white border border-gray-200 rounded-md text-sm outline-none focus:border-primary" />
              </div>
              <div>
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1">Sex</label>
                <select value={familySex} onChange={e => setFamilySex(e.target.value)} className="w-full px-3 py-2 bg-white border border-gray-200 rounded-md text-sm outline-none focus:border-primary">
                  <option value="">Not specified</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="unknown">Unknown</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1">Health Status</label>
                <select value={familyHealthStatus} onChange={e => setFamilyHealthStatus(e.target.value)} className="w-full px-3 py-2 bg-white border border-gray-200 rounded-md text-sm outline-none focus:border-primary">
                  <option value="">Select status</option>
                  <option value="affected">Affected</option>
                  <option value="carrier">Carrier</option>
                  <option value="unaffected">Unaffected</option>
                  <option value="unknown">Unknown</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1">Condition (Optional)</label>
                <input type="text" placeholder="e.g. Cystic fibrosis" value={familyCondition} onChange={e => setFamilyCondition(e.target.value)} className="w-full px-3 py-2 bg-white border border-gray-200 rounded-md text-sm outline-none focus:border-primary" />
              </div>
              <div className="md:col-span-2">
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1">Known Variant (Optional)</label>
                <input type="text" placeholder="e.g. CFTR variant" value={familyKnownVariant} onChange={e => setFamilyKnownVariant(e.target.value)} className="w-full px-3 py-2 bg-white border border-gray-200 rounded-md text-sm outline-none focus:border-primary" />
              </div>
            </div>
            <div className="flex gap-3 mt-5">
              <button onClick={addFamilyHistory} disabled={!familyMember || !familyHealthStatus} className="bg-gray-900 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-800 disabled:opacity-50">Add Entry</button>
              <button onClick={() => setShowFamilyForm(false)} className="px-4 py-2 border border-gray-200 rounded-md text-sm font-medium hover:bg-gray-100">Cancel</button>
            </div>
          </div>
        ) : (
          <button onClick={() => setShowFamilyForm(true)} className="flex items-center gap-2 text-sm font-medium text-primary hover:text-[#005049] transition-colors">
            <span className="material-symbols-outlined text-lg">add_circle</span>
            {familyHistory.length > 0 ? 'Add Another Family Member' : 'Add Family Member'}
          </button>
        )}
      </div>

      <button 
        onClick={handleAnalyze}
        disabled={!parent1File || !parent2File || loading}
        className="w-full md:w-auto self-start bg-primary hover:bg-[#005049] text-white font-medium px-8 py-3 rounded-xl flex items-center justify-center gap-2 shadow-sm transition-colors disabled:opacity-50"
      >
        {loading ? (
          <><span className="material-symbols-outlined animate-spin">autorenew</span> Analyzing...</>
        ) : (
          <><span className="material-symbols-outlined">science</span> Analyze Genetic Risk</>
        )}
      </button>

      {result && (
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden mt-4 animate-fade-in">
          <div className="bg-gray-900 px-6 py-5 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white">Assessment Results</h2>
              <p className="text-gray-400 text-sm mt-1">Status: {result.status || 'Completed'}</p>
            </div>
            <span className="material-symbols-outlined text-white text-3xl opacity-50">verified</span>
          </div>

          <div className="p-6 space-y-8">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                <span className="text-3xl font-bold text-primary block">{result.risks?.length ?? 0}</span>
                <span className="text-sm text-gray-500 font-medium">Risk Conditions</span>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                <span className="text-3xl font-bold text-primary block">{result.shared_risk_count ?? 0}</span>
                <span className="text-sm text-gray-500 font-medium">Shared Variants</span>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                <span className="text-3xl font-bold text-primary block">{result.interventions?.length ?? 0}</span>
                <span className="text-sm text-gray-500 font-medium">Interventions</span>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                <span className="text-3xl font-bold text-primary block">{result.compound_heterozygous_candidates?.length ?? 0}</span>
                <span className="text-sm text-gray-500 font-medium">Compound Candidates</span>
              </div>
            </div>

            {/* Identified Risks */}
            {result.risks && result.risks.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 border-b pb-2">Identified Genetic Risks</h3>
                <div className="space-y-4">
                  {result.risks.map((risk, idx) => (
                    <div key={idx} className="border border-gray-200 rounded-lg p-5 hover:border-primary transition-colors">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <span className="inline-block px-2 py-0.5 rounded text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200 mb-2">{risk.gene}</span>
                          <h4 className="text-lg font-semibold text-gray-900">{risk.condition}</h4>
                        </div>
                        <span className="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-semibold rounded-full border border-gray-200">
                          {risk.inheritance.replaceAll('_', ' ')}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 mb-5 p-4 bg-gray-50 rounded-lg">
                        <div>
                          <span className="block text-xs font-bold text-gray-500 uppercase">Parent 1 Status</span>
                          <span className="font-medium text-gray-900">{risk.parent1_status}</span>
                        </div>
                        <div>
                          <span className="block text-xs font-bold text-gray-500 uppercase">Parent 2 Status</span>
                          <span className="font-medium text-gray-900">{risk.parent2_status}</span>
                        </div>
                      </div>

                      <div>
                        <h5 className="text-sm font-bold text-gray-900 mb-3">Offspring Probabilities</h5>
                        <div className="flex gap-4 mb-2">
                          <div className="flex-1">
                            <div className="flex justify-between text-xs mb-1">
                              <span className="font-semibold text-red-600">Affected</span>
                              <span className="font-bold">{(risk.affected_probability * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-gray-100 rounded-full h-2"><div className="bg-red-500 h-2 rounded-full" style={{ width: `${risk.affected_probability * 100}%` }}></div></div>
                          </div>
                          <div className="flex-1">
                            <div className="flex justify-between text-xs mb-1">
                              <span className="font-semibold text-orange-500">Carrier</span>
                              <span className="font-bold">{(risk.carrier_probability * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-gray-100 rounded-full h-2"><div className="bg-orange-400 h-2 rounded-full" style={{ width: `${risk.carrier_probability * 100}%` }}></div></div>
                          </div>
                          <div className="flex-1">
                            <div className="flex justify-between text-xs mb-1">
                              <span className="font-semibold text-green-600">Unaffected</span>
                              <span className="font-bold">{(risk.unaffected_probability * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-gray-100 rounded-full h-2"><div className="bg-green-500 h-2 rounded-full" style={{ width: `${risk.unaffected_probability * 100}%` }}></div></div>
                          </div>
                        </div>
                      </div>

                      <div className="mt-5 pt-4 border-t border-gray-100">
                        <p className="text-sm text-gray-700 leading-relaxed"><strong className="text-gray-900">Interpretation:</strong> {risk.explanation}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Interventions from intervention_engine.py */}
            {result.interventions && result.interventions.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 border-b pb-2 flex items-center gap-2">
                  <span className="material-symbols-outlined text-purple-600">medical_services</span>
                  Preconception Recommendations
                </h3>
                <div className="space-y-4">
                  {result.interventions.map((intervention, idx) => (
                    <div key={idx} className="bg-purple-50 border border-purple-100 rounded-lg p-5">
                      <div className="flex justify-between items-start mb-3">
                        <h4 className="font-semibold text-purple-900">{intervention.condition}</h4>
                        <span className="px-2 py-0.5 rounded text-xs font-bold bg-white text-purple-700 border border-purple-200">
                          {intervention.classification.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                      <div className="space-y-3 mt-4">
                        {intervention.recommendations.map((rec, rIdx) => (
                          <div key={rIdx} className="bg-white rounded p-3 border border-purple-100 shadow-sm flex gap-3">
                            <span className="material-symbols-outlined text-purple-500">assignment_turned_in</span>
                            <div>
                              <strong className="block text-sm text-gray-900">{rec.option}</strong>
                              <p className="text-xs text-gray-600 mt-1">{rec.reason}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                      <p className="text-[10px] text-purple-400 mt-4 uppercase tracking-wider">{intervention.disclaimer}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>
        </div>
      )}
    </div>
  );
}
