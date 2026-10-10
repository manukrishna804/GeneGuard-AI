import { useState, useRef, useCallback, useEffect } from 'react';

// ─── Types (matching real pipeline output shape) ──────────────────────────────

interface Patient {
  id: number;
  full_name: string;
  age?: number;
  gender?: string;
  email?: string;
}

interface VariantConsequence {
  transcript?: string;
  effect?: string;
  impact?: string;
  hgvsc?: string;
  hgvsp?: string;
}

interface ComputationalPredictions {
  cadd?: number;
  sift?: string[];
  polyphen?: { hdiv?: string[]; hvar?: string[] };
  revel?: number[];
}

interface ClinVarResult {
  status: 'found' | 'not_found' | 'not_available';
  records: any[];
}

interface ClinGenResult {
  status: string;
  caid?: string;
  community_standard_title?: string[];
}

interface SourcesResult {
  variantvalidator?: { status: string };
  myvariant?: { status: string };
  clingen?: { status: string };
  clinvar?: { status: string };
}

interface ValidVariantResult {
  status?: never; // valid results don't have status:'invalid'
  gene: string;
  variant: string;
  type: 'SNV' | 'CNV';
  validation: {
    valid: true;
    errors: string[];
    warnings: string[];
    external?: { variantvalidator?: { validated: boolean; warnings: string[] } };
  };
  identity: {
    transcript?: string;
    protein?: string;
    genomic?: string;
    assembly?: string;
    exon?: { start: string; end: string };
    vcf?: { chromosome: string; position: string; reference: string; alternate: string };
    clingen?: ClinGenResult;
    normalization?: any;
    search_region?: any;
  };
  evidence: {
    consequence?: VariantConsequence;
    computational_predictions?: ComputationalPredictions;
    conservation?: any;
    clinvar?: ClinVarResult;
    sources?: SourcesResult;
    dbvar?: any;
  };
  interpretation: {
    classification: 'VUS' | 'unsupported';
    confidence: string;
    reasoning: string[];
    variant: { gene: string; variant: string; type: string };
    identity?: { transcript?: string; protein?: string; genomic?: string; clingen_caid?: string };
    evidence_summary?: any;
  };
}

interface InvalidVariantResult {
  status: 'invalid';
  gene?: string;
  variant?: string;
  type?: string;
  validation: {
    valid: false;
    errors: string[];
    warnings: string[];
  };
}

type VariantResult = ValidVariantResult | InvalidVariantResult;

interface AnalysisResponse {
  report_id: number;
  patient_id: number;
  report_name: string;
  status: string;
  variant_count: number;
  results: VariantResult[];
}

// ─── State type ───────────────────────────────────────────────────────────────
type PageState = 'upload' | 'processing' | 'results';

// ─── Helper components ────────────────────────────────────────────────────────

function SourceBadge({ status, label }: { status: string; label: string }) {
  const found = status === 'found' || status === 'validated' || status === 'candidate_found';
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold border ${
        found
          ? 'bg-green-50 text-green-700 border-green-200'
          : 'bg-gray-100 text-gray-500 border-gray-200'
      }`}
    >
      <span className="material-symbols-outlined text-sm">{found ? 'check_circle' : 'remove_circle'}</span>
      {label}
    </span>
  );
}

function ClassificationBadge({ classification }: { classification: string }) {
  if (classification === 'VUS') {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">
        VUS
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold bg-gray-100 text-gray-500 border border-gray-200">
      {classification}
    </span>
  );
}

function ValidVariantCard({ result, index }: { result: ValidVariantResult; index: number }) {
  const [expanded, setExpanded] = useState(false);
  const { gene, variant, type, evidence, identity, interpretation } = result;
  const consequence = evidence.consequence;
  const predictions = evidence.computational_predictions;
  const clinvar = evidence.clinvar;
  const sources = evidence.sources;
  const clingen = identity.clingen;

  const clinvarNotFound =
    !clinvar || clinvar.status === 'not_found' || clinvar.status === 'not_available';

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
      {/* Card header */}
      <div className="p-5 flex flex-col sm:flex-row sm:items-start gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="font-bold text-gray-900 text-lg">{gene}</span>
            <span className="font-mono text-sm text-primary bg-primary/10 px-2 py-0.5 rounded border border-primary/20">
              {consequence?.hgvsc ?? variant}
            </span>
            {consequence?.hgvsp && (
              <span className="font-mono text-xs text-gray-600 bg-gray-50 px-2 py-0.5 rounded border border-gray-200">
                {consequence.hgvsp}
              </span>
            )}
            <span className="text-[10px] font-bold text-gray-500 bg-gray-100 px-2 py-0.5 rounded border border-gray-200 uppercase">
              {type}
            </span>
            <ClassificationBadge classification={interpretation.classification} />
          </div>

          {/* Identity line */}
          {identity.genomic && (
            <p className="text-xs text-gray-500 font-mono mb-3">{identity.genomic}</p>
          )}

          {/* Source badges */}
          <div className="flex flex-wrap gap-2">
            <SourceBadge status={sources?.variantvalidator?.status ?? 'unknown'} label="VariantValidator" />
            <SourceBadge status={sources?.myvariant?.status ?? 'unknown'} label="MyVariant" />
            <SourceBadge status={sources?.clingen?.status ?? 'unknown'} label="ClinGen" />
            {clinvarNotFound ? (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold border bg-blue-50 text-blue-700 border-blue-200">
                <span className="material-symbols-outlined text-sm">info</span>
                ClinVar: Novel / no prior record
              </span>
            ) : (
              <SourceBadge status="found" label="ClinVar" />
            )}
          </div>
        </div>

        {/* Predictions summary */}
        <div className="flex-shrink-0 flex flex-col gap-1 text-right min-w-[120px]">
          {predictions?.cadd != null && (
            <div className="text-xs text-gray-500">
              CADD <span className={`font-bold ${predictions.cadd >= 20 ? 'text-amber-600' : 'text-gray-700'}`}>{predictions.cadd}</span>
            </div>
          )}
          {predictions?.revel && predictions.revel.length > 0 && (
            <div className="text-xs text-gray-500">
              REVEL <span className={`font-bold ${Math.max(...predictions.revel) >= 0.5 ? 'text-amber-600' : 'text-gray-700'}`}>{Math.max(...predictions.revel).toFixed(3)}</span>
            </div>
          )}
          {clingen?.caid && (
            <div className="text-[10px] text-gray-400 font-mono">{clingen.caid}</div>
          )}
        </div>
      </div>

      {/* Reasoning */}
      <div className="px-5 pb-3">
        <div className="bg-gray-50 border border-gray-100 rounded-lg p-3">
          <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">System Assessment</p>
          <ul className="space-y-1">
            {interpretation.reasoning.map((r, i) => (
              <li key={i} className="text-xs text-gray-700 flex gap-2">
                <span className="text-gray-400 mt-0.5">•</span>
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Expand / collapse evidence */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-5 py-2.5 flex items-center justify-between bg-gray-50 border-t border-gray-100 text-xs font-semibold text-primary hover:bg-gray-100 transition-colors"
      >
        <span>{expanded ? 'Hide' : 'Show'} full evidence detail</span>
        <span className="material-symbols-outlined text-sm">{expanded ? 'expand_less' : 'expand_more'}</span>
      </button>

      {expanded && (
        <div className="px-5 py-4 border-t border-gray-100 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          {/* Consequence */}
          {consequence && (
            <div>
              <p className="font-bold text-gray-500 uppercase tracking-wider mb-2">Molecular Consequence</p>
              <table className="w-full">
                <tbody>
                  {Object.entries(consequence).map(([k, v]) => (
                    <tr key={k} className="border-b border-gray-50">
                      <td className="py-1 pr-3 text-gray-500 font-medium capitalize">{k.replace(/_/g, ' ')}</td>
                      <td className="py-1 font-mono text-gray-800">{String(v)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Computational predictions */}
          {predictions && (
            <div>
              <p className="font-bold text-gray-500 uppercase tracking-wider mb-2">Computational Predictions</p>
              <table className="w-full">
                <tbody>
                  {predictions.cadd != null && (
                    <tr className="border-b border-gray-50">
                      <td className="py-1 pr-3 text-gray-500">CADD</td>
                      <td className="py-1 font-mono">{predictions.cadd}</td>
                    </tr>
                  )}
                  {predictions.revel && (
                    <tr className="border-b border-gray-50">
                      <td className="py-1 pr-3 text-gray-500">REVEL</td>
                      <td className="py-1 font-mono">{predictions.revel.join(', ')}</td>
                    </tr>
                  )}
                  {predictions.sift && (
                    <tr className="border-b border-gray-50">
                      <td className="py-1 pr-3 text-gray-500">SIFT</td>
                      <td className="py-1 font-mono">{predictions.sift.join(', ')}</td>
                    </tr>
                  )}
                  {predictions.polyphen && (
                    <>
                      <tr className="border-b border-gray-50">
                        <td className="py-1 pr-3 text-gray-500">PolyPhen HDiv</td>
                        <td className="py-1 font-mono">{predictions.polyphen.hdiv?.join(', ')}</td>
                      </tr>
                      <tr className="border-b border-gray-50">
                        <td className="py-1 pr-3 text-gray-500">PolyPhen HVar</td>
                        <td className="py-1 font-mono">{predictions.polyphen.hvar?.join(', ')}</td>
                      </tr>
                    </>
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* VCF coordinates */}
          {identity.vcf && (
            <div>
              <p className="font-bold text-gray-500 uppercase tracking-wider mb-2">VCF Coordinates (GRCh38)</p>
              <table className="w-full">
                <tbody>
                  <tr className="border-b border-gray-50">
                    <td className="py-1 pr-3 text-gray-500">Chr</td>
                    <td className="py-1 font-mono">{identity.vcf.chromosome}</td>
                  </tr>
                  <tr className="border-b border-gray-50">
                    <td className="py-1 pr-3 text-gray-500">Pos</td>
                    <td className="py-1 font-mono">{identity.vcf.position}</td>
                  </tr>
                  <tr className="border-b border-gray-50">
                    <td className="py-1 pr-3 text-gray-500">Ref→Alt</td>
                    <td className="py-1 font-mono">{identity.vcf.reference}→{identity.vcf.alternate}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}

          {/* ClinVar detail */}
          <div>
            <p className="font-bold text-gray-500 uppercase tracking-wider mb-2">ClinVar</p>
            {clinvarNotFound ? (
              <div className="flex items-center gap-2 text-blue-600 bg-blue-50 border border-blue-100 rounded p-2">
                <span className="material-symbols-outlined text-sm">info</span>
                <span>No prior record found — Novel / not yet submitted to ClinVar</span>
              </div>
            ) : (
              <pre className="text-[10px] font-mono bg-gray-50 border border-gray-100 rounded p-2 overflow-auto max-h-40">
                {JSON.stringify(clinvar?.records, null, 2)}
              </pre>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function InvalidVariantCard({ result }: { result: InvalidVariantResult }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm opacity-80">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-5 py-3.5 flex items-center justify-between text-left"
      >
        <div className="flex flex-wrap items-center gap-2">
          <span className="material-symbols-outlined text-gray-400">cancel</span>
          <span className="font-mono text-sm text-gray-600">{result.variant ?? '(unknown variant)'}</span>
          {result.gene && <span className="font-semibold text-gray-700">{result.gene}</span>}
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-gray-100 text-gray-500 border border-gray-200 uppercase">
            Invalid
          </span>
        </div>
        <span className="material-symbols-outlined text-sm text-gray-400">
          {expanded ? 'expand_less' : 'expand_more'}
        </span>
      </button>
      {expanded && (
        <div className="px-5 pb-4 border-t border-gray-100">
          <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mt-3 mb-2">Validation Errors</p>
          <ul className="space-y-1">
            {result.validation.errors.map((e, i) => (
              <li key={i} className="text-xs text-red-700 flex gap-2">
                <span className="text-red-400">✕</span>
                <span>{e}</span>
              </li>
            ))}
          </ul>
          {result.validation.warnings.length > 0 && (
            <>
              <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mt-3 mb-2">Warnings</p>
              <ul className="space-y-1">
                {result.validation.warnings.map((w, i) => (
                  <li key={i} className="text-xs text-amber-700">⚠ {w}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function WESAnalysis() {
  const [pageState, setPageState] = useState<PageState>('upload');
  const [patients, setPatients] = useState<Patient[]>([]);
  const [patientsLoading, setPatientsLoading] = useState(true);
  const [patientsError, setPatientsError] = useState<string | null>(null);

  // Upload state
  const [selectedPatientId, setSelectedPatientId] = useState<string>('');
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [fileError, setFileError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Create patient inline form
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newPatientName, setNewPatientName] = useState('');
  const [newPatientAge, setNewPatientAge] = useState('');
  const [newPatientGender, setNewPatientGender] = useState('');
  const [creatingPatient, setCreatingPatient] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  // Processing state
  const abortRef = useRef<AbortController | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  // Results state
  const [response, setResponse] = useState<AnalysisResponse | null>(null);

  // ── Load patients on mount ────────────────────────────────────────────────
  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch('/api/v1/patients/');
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        const data: Patient[] = await res.json();
        setPatients(data);
      } catch (err: any) {
        setPatientsError(`Could not load patients: ${err.message}`);
      } finally {
        setPatientsLoading(false);
      }
    };
    load();
  }, []);

  // ── File handling ─────────────────────────────────────────────────────────
  const handleFile = (f: File | null) => {
    setFileError(null);
    if (!f) { setFile(null); return; }
    if (f.type !== 'application/pdf' && !f.name.toLowerCase().endsWith('.pdf')) {
      setFileError('Only PDF files are supported.');
      setFile(null);
      return;
    }
    if (f.size === 0) {
      setFileError('The selected file is empty.');
      setFile(null);
      return;
    }
    setFile(f);
  };

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files[0] ?? null);
  }, []);

  // ── Create patient ────────────────────────────────────────────────────────
  const handleCreatePatient = async () => {
    if (!newPatientName.trim()) { setCreateError('Full name is required.'); return; }
    setCreatingPatient(true);
    setCreateError(null);
    try {
      const res = await fetch('/api/v1/patients/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          full_name: newPatientName.trim(),
          age: newPatientAge ? parseInt(newPatientAge) : null,
          gender: newPatientGender || null,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? `Server returned ${res.status}`);
      }
      const created: Patient = await res.json();
      setPatients(prev => [...prev, created]);
      setSelectedPatientId(String(created.id));
      setShowCreateForm(false);
      setNewPatientName(''); setNewPatientAge(''); setNewPatientGender('');
    } catch (err: any) {
      setCreateError(err.message);
    } finally {
      setCreatingPatient(false);
    }
  };

  // ── Submit analysis ───────────────────────────────────────────────────────
  const handleAnalyze = async () => {
    if (!file || !selectedPatientId) return;
    setAnalysisError(null);
    setPageState('processing');

    const formData = new FormData();
    formData.append('patient_id', selectedPatientId);
    formData.append('file', file);

    abortRef.current = new AbortController();
    const timer = setTimeout(() => abortRef.current?.abort(), 3 * 60 * 1000); // 3 min

    try {
      const res = await fetch('/api/v1/wes/analyze', {
        method: 'POST',
        body: formData,
        signal: abortRef.current.signal,
      });

      clearTimeout(timer);

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: `Server error (${res.status})` }));
        let msg = err.detail ?? `Server returned ${res.status}`;
        if (res.status === 400) msg = `Bad request: ${msg}`;
        else if (res.status === 404) msg = `Patient not found. ${msg}`;
        else if (res.status === 500) msg = `Analysis failed: ${msg}`;
        throw new Error(msg);
      }

      const data: AnalysisResponse = await res.json();
      setResponse(data);
      setPageState('results');
    } catch (err: any) {
      clearTimeout(timer);
      if (err.name === 'AbortError') {
        setAnalysisError('Request timed out after 3 minutes. The backend may still be processing — check server logs.');
      } else {
        setAnalysisError(err.message ?? 'Network error — could not reach the backend.');
      }
      setPageState('upload');
    }
  };

  const handleCancel = () => {
    abortRef.current?.abort();
    setPageState('upload');
  };

  const handleReset = () => {
    setResponse(null);
    setFile(null);
    setAnalysisError(null);
    setPageState('upload');
  };

  // ─── Upload state ─────────────────────────────────────────────────────────
  if (pageState === 'upload') {
    const canSubmit = !!file && !!selectedPatientId;
    const selectedPatient = patients.find(p => String(p.id) === selectedPatientId);

    return (
      <div className="flex flex-col gap-6 h-full pb-10 max-w-3xl">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold text-gray-900">Genetic Disorder ID</h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200 flex items-center gap-1 uppercase tracking-wider">
              <div className="w-1.5 h-1.5 rounded-full bg-amber-500"></div> IN PROGRESS
            </span>
          </div>
          <p className="text-gray-500 mt-1">WES report parsing & ClinVar/gnomAD variant lookup</p>
        </div>

        {/* Error banner */}
        {analysisError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <span className="material-symbols-outlined text-red-500 mt-0.5">error</span>
            <div>
              <p className="font-semibold text-red-800 text-sm">Analysis failed</p>
              <p className="text-sm text-red-700 mt-0.5">{analysisError}</p>
            </div>
          </div>
        )}

        {/* Patient selection */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">person</span>
            1. Select Patient
          </h2>

          {patientsError && (
            <div className="bg-red-50 border border-red-200 rounded p-3 text-sm text-red-700 mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-red-500 text-sm">warning</span>
              {patientsError}
            </div>
          )}

          {patientsLoading ? (
            <div className="text-gray-400 text-sm flex items-center gap-2">
              <span className="material-symbols-outlined animate-spin text-primary">autorenew</span>
              Loading patients…
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              <select
                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none text-gray-900"
                value={selectedPatientId}
                onChange={e => setSelectedPatientId(e.target.value)}
              >
                <option value="">— Select a patient —</option>
                {patients.map(p => (
                  <option key={p.id} value={String(p.id)}>
                    {p.full_name} (ID: {p.id}){p.age ? `, ${p.age}y` : ''}{p.gender ? `, ${p.gender}` : ''}
                  </option>
                ))}
              </select>

              {selectedPatient && (
                <div className="flex items-center gap-2 text-xs text-gray-500 bg-gray-50 border border-gray-100 rounded px-3 py-1.5">
                  <span className="material-symbols-outlined text-sm text-green-600">check_circle</span>
                  Patient #{selectedPatient.id}: <span className="font-semibold text-gray-700">{selectedPatient.full_name}</span>
                </div>
              )}

              <button
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="self-start text-xs text-primary underline hover:no-underline"
              >
                {showCreateForm ? '▲ Cancel' : '+ Create new patient'}
              </button>

              {showCreateForm && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 flex flex-col gap-3">
                  <p className="text-xs font-bold text-gray-500 uppercase tracking-wider">New Patient</p>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="text-[11px] text-gray-500 font-medium block mb-1">Full Name *</label>
                      <input className="w-full px-3 py-2 bg-white border border-gray-200 rounded text-sm focus:border-primary outline-none" value={newPatientName} onChange={e => setNewPatientName(e.target.value)} placeholder="e.g. Jane Smith" />
                    </div>
                    <div>
                      <label className="text-[11px] text-gray-500 font-medium block mb-1">Age</label>
                      <input type="number" className="w-full px-3 py-2 bg-white border border-gray-200 rounded text-sm focus:border-primary outline-none" value={newPatientAge} onChange={e => setNewPatientAge(e.target.value)} placeholder="e.g. 34" />
                    </div>
                    <div>
                      <label className="text-[11px] text-gray-500 font-medium block mb-1">Gender</label>
                      <select className="w-full px-3 py-2 bg-white border border-gray-200 rounded text-sm focus:border-primary outline-none" value={newPatientGender} onChange={e => setNewPatientGender(e.target.value)}>
                        <option value="">— Optional —</option>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                  </div>
                  {createError && <p className="text-xs text-red-700">⚠ {createError}</p>}
                  <button
                    onClick={handleCreatePatient}
                    disabled={creatingPatient}
                    className="self-start bg-primary hover:bg-[#005049] text-white text-xs font-semibold px-4 py-2 rounded-lg disabled:opacity-50"
                  >
                    {creatingPatient ? 'Creating…' : 'Create Patient'}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* File upload */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">upload_file</span>
            2. Upload WES Report (PDF)
          </h2>

          <div
            onClick={() => fileInputRef.current?.click()}
            onDragOver={e => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
              dragOver ? 'border-primary bg-primary/5' : file ? 'border-green-400 bg-green-50' : 'border-gray-200 hover:border-primary hover:bg-gray-50'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,application/pdf"
              className="hidden"
              onChange={e => handleFile(e.target.files?.[0] ?? null)}
            />
            {file ? (
              <div className="flex flex-col items-center gap-2">
                <span className="material-symbols-outlined text-3xl text-green-500">description</span>
                <p className="font-semibold text-gray-900">{file.name}</p>
                <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                <button onClick={e => { e.stopPropagation(); setFile(null); }} className="text-xs text-red-500 hover:underline mt-1">Remove</button>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2">
                <span className="material-symbols-outlined text-3xl text-gray-400">cloud_upload</span>
                <p className="font-semibold text-gray-700">Drag and drop or click to browse</p>
                <p className="text-xs text-gray-400">PDF only</p>
              </div>
            )}
          </div>

          {fileError && (
            <p className="mt-2 text-xs text-red-700 flex items-center gap-1">
              <span className="material-symbols-outlined text-sm text-red-500">error</span>
              {fileError}
            </p>
          )}

          <p className="mt-3 text-xs text-gray-500 leading-relaxed">
            Upload a completed WES lab report (PDF). The system extracts the reported variants and checks them against ClinVar and gnomAD. It does not perform sequencing.
          </p>
        </div>

        {/* Submit */}
        <div className="flex items-center gap-4">
          <button
            onClick={handleAnalyze}
            disabled={!canSubmit}
            className="bg-primary hover:bg-[#005049] disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold text-sm px-8 py-3 rounded-lg shadow-sm transition-colors flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-lg">biotech</span>
            Analyze Report
          </button>
          {!canSubmit && (
            <p className="text-xs text-gray-400">
              {!selectedPatientId ? 'Select a patient first.' : 'Select a PDF file.'}
            </p>
          )}
        </div>
      </div>
    );
  }

  // ─── Processing state ─────────────────────────────────────────────────────
  if (pageState === 'processing') {
    return (
      <div className="flex flex-col gap-6 h-full pb-10 max-w-3xl">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Genetic Disorder ID</h1>
          <p className="text-gray-500 mt-1">WES report parsing & ClinVar/gnomAD variant lookup</p>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-10 shadow-sm flex flex-col items-center text-center gap-6">
          <div className="relative w-16 h-16">
            <div className="absolute inset-0 border-4 border-gray-100 rounded-full"></div>
            <div className="absolute inset-0 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          </div>

          <div>
            <p className="font-semibold text-gray-900 text-lg mb-1">Processing: <span className="font-mono text-primary text-base">{file?.name}</span></p>
            <p className="text-sm text-gray-500">Extracting variants and querying ClinVar/gnomAD. This can take a minute.</p>
          </div>

          <div className="flex flex-col gap-2 text-left w-full max-w-md bg-gray-50 border border-gray-100 rounded-lg p-4">
            <p className="text-[11px] font-bold text-gray-500 uppercase tracking-wider mb-1">Pipeline stages</p>
            {['PDF text extraction', 'Variant pattern extraction', 'Validation', 'Database lookup (ClinVar / gnomAD / ClinGen)', 'Evidence combination & interpretation'].map((stage, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-gray-500">
                <span className="material-symbols-outlined text-gray-300 text-sm">radio_button_unchecked</span>
                {stage}
              </div>
            ))}
            <p className="text-[10px] text-gray-400 mt-2">Stages shown for reference — the backend processes them synchronously. No live progress is available.</p>
          </div>

          <button onClick={handleCancel} className="text-sm text-red-600 border border-red-200 px-4 py-2 rounded-lg hover:bg-red-50 transition-colors">
            Cancel
          </button>
        </div>
      </div>
    );
  }

  // ─── Results state ────────────────────────────────────────────────────────
  if (!response) return null;

  const validResults = response.results.filter(r => r.status !== 'invalid') as ValidVariantResult[];
  const invalidResults = response.results.filter(r => r.status === 'invalid') as InvalidVariantResult[];

  return (
    <div className="flex flex-col gap-6 h-full pb-10">
      {/* Summary bar */}
      <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-col">
          <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <span className="material-symbols-outlined text-green-500">check_circle</span>
            {response.report_name}
          </h1>
          <p className="text-xs text-gray-500 mt-1">
            Report ID: <span className="font-mono">{response.report_id}</span> · Patient ID: <span className="font-mono">{response.patient_id}</span>
          </p>
        </div>
        <div className="flex gap-4">
          <div className="text-center">
            <p className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Total</p>
            <p className="text-2xl font-bold text-gray-900">{response.variant_count}</p>
          </div>
          <div className="text-center">
            <p className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Processed</p>
            <p className="text-2xl font-bold text-primary">{validResults.length}</p>
          </div>
          {invalidResults.length > 0 && (
            <div className="text-center">
              <p className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Invalid</p>
              <p className="text-2xl font-bold text-red-500">{invalidResults.length}</p>
            </div>
          )}
          <button onClick={handleReset} className="self-center bg-gray-50 border border-gray-200 text-sm text-primary font-medium px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors flex items-center gap-2">
            <span className="material-symbols-outlined text-sm">upload_file</span>
            Analyze another report
          </button>
        </div>
      </div>

      {/* Valid variants */}
      {validResults.length > 0 && (
        <section>
          <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <span className="material-symbols-outlined text-base text-amber-500">science</span>
            Processed Variants ({validResults.length})
          </h2>
          <div className="flex flex-col gap-4">
            {validResults.map((r, i) => (
              <ValidVariantCard key={i} result={r} index={i} />
            ))}
          </div>
        </section>
      )}

      {/* Invalid variants */}
      {invalidResults.length > 0 && (
        <section>
          <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <span className="material-symbols-outlined text-base text-red-400">cancel</span>
            Invalid / Skipped ({invalidResults.length})
          </h2>
          <div className="flex flex-col gap-2">
            {invalidResults.map((r, i) => (
              <InvalidVariantCard key={i} result={r} />
            ))}
          </div>
        </section>
      )}

      {response.variant_count === 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-10 shadow-sm flex flex-col items-center text-center">
          <span className="material-symbols-outlined text-3xl text-gray-400 mb-3">search_off</span>
          <h3 className="font-medium text-gray-900 mb-1">No variants extracted</h3>
          <p className="text-sm text-gray-500">The PDF was processed but no variant patterns (cDNA or CNV notation) were detected. Check that the report follows the expected format.</p>
        </div>
      )}
    </div>
  );
}
