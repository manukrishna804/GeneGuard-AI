import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

// --- Types ---
type DiseaseKey = 'diabetes' | 'heart_disease' | 'hypertension' | 'stroke' | 'ckd';

interface PredictionResponse {
  disease: string;
  prediction: number;
  risk_probability: number;
  risk_level: 'Low' | 'Moderate' | 'High';
}

interface OverallSummary {
  overall_risk: 'Low' | 'Moderate' | 'High' | 'None';
  diseases_assessed: number;
  high_risk_conditions: number;
  moderate_risk_conditions: number;
  low_risk_conditions: number;
}

export default function ComplexDiseaseRisk() {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState<DiseaseKey | 'overall'>('diabetes');

  // Shared basics
  const [basicAge, setBasicAge] = useState<number | ''>(52);
  const [basicSex, setBasicSex] = useState<'Male' | 'Female' | 'Other'>('Male');
  const [basicBmi, setBasicBmi] = useState<number | ''>(26.4);
  const [basicsApplied, setBasicsApplied] = useState(false);

  // Results map
  const [results, setResults] = useState<Partial<Record<DiseaseKey, PredictionResponse>>>({});
  const [loading, setLoading] = useState<Partial<Record<DiseaseKey, boolean>>>({});
  const [fieldErrors, setFieldErrors] = useState<Partial<Record<DiseaseKey, Record<string, string>>>>({});
  const [generalErrors, setGeneralErrors] = useState<Partial<Record<DiseaseKey, string>>>({});

  // 1. Diabetes Form State
  const [diabetesData, setDiabetesData] = useState({
    gender: 'Male',
    age: 52,
    hypertension: 0,
    heart_disease: 0,
    smoking_history: 'never',
    bmi: 26.4,
    HbA1c_level: 6.2,
    blood_glucose_level: 140,
  });

  // 2. Heart Disease Form State
  const [heartData, setHeartData] = useState({
    age: 52,
    sex: 'Male',
    cp: 'typical angina',
    trestbps: 135,
    chol: 245,
    fbs: true,
    restecg: 'normal',
    thalch: 148,
    exang: false,
    oldpeak: 1.4,
    slope: 'flat',
    ca: 1,
    thal: 'normal',
  });

  // 3. Hypertension Form State
  const [hypertensionData, setHypertensionData] = useState({
    Age: 52,
    Salt_Intake: 8.5,
    Stress_Score: 6,
    Sleep_Duration: 6.5,
    BMI: 26.4,
    BP_History: 'Prehypertension',
    Medication: 'None',
    Family_History: 'Yes',
    Exercise_Level: 'Moderate',
    Smoking_Status: 'Non-Smoker',
  });

  // 4. Stroke Form State
  const [strokeData, setStrokeData] = useState({
    gender: 'Male',
    age: 52,
    hypertension: 0,
    heart_disease: 0,
    ever_married: 'Yes',
    work_type: 'Private',
    Residence_type: 'Urban',
    avg_glucose_level: 110.5,
    bmi: 26.4,
    smoking_status: 'never smoked',
  });

  // 5. CKD Form State
  const [ckdData, setCkdData] = useState({
    Bp: 80,
    Sg: 1.02,
    Al: 1,
    Su: 0,
    Rbc: 0, // 0 = Normal, 1 = Abnormal
    Bu: 36,
    Sc: 1.2,
    Sod: 138,
    Pot: 4.4,
    Hemo: 14.8,
    Wbcc: 7600,
    Rbcc: 5.1,
    Htn: 0, // 0 = No, 1 = Yes
  });

  // Apply Basics to all forms
  const applyBasicsToAll = () => {
    if (basicAge !== '') {
      setDiabetesData((prev) => ({ ...prev, age: Number(basicAge) }));
      setHeartData((prev) => ({ ...prev, age: Number(basicAge) }));
      setHypertensionData((prev) => ({ ...prev, Age: Number(basicAge) }));
      setStrokeData((prev) => ({ ...prev, age: Number(basicAge) }));
    }
    if (basicSex) {
      setDiabetesData((prev) => ({ ...prev, gender: basicSex }));
      setHeartData((prev) => ({ ...prev, sex: basicSex === 'Other' ? 'Male' : basicSex }));
      setStrokeData((prev) => ({ ...prev, gender: basicSex }));
    }
    if (basicBmi !== '') {
      setDiabetesData((prev) => ({ ...prev, bmi: Number(basicBmi) }));
      setHypertensionData((prev) => ({ ...prev, BMI: Number(basicBmi) }));
      setStrokeData((prev) => ({ ...prev, bmi: Number(basicBmi) }));
    }
    setBasicsApplied(true);
    setTimeout(() => setBasicsApplied(false), 2500);
  };

  // Submit Handler
  const assessDisease = async (disease: DiseaseKey) => {
    setLoading((prev) => ({ ...prev, [disease]: true }));
    setFieldErrors((prev) => ({ ...prev, [disease]: {} }));
    setGeneralErrors((prev) => ({ ...prev, [disease]: '' }));

    let endpoint = '';
    let payload: Record<string, unknown> = {};

    switch (disease) {
      case 'diabetes':
        endpoint = '/api/v1/lifestyle/diabetes';
        payload = {
          ...diabetesData,
          age: Number(diabetesData.age),
          hypertension: Number(diabetesData.hypertension),
          heart_disease: Number(diabetesData.heart_disease),
          bmi: Number(diabetesData.bmi),
          HbA1c_level: Number(diabetesData.HbA1c_level),
          blood_glucose_level: Math.round(Number(diabetesData.blood_glucose_level)),
        };
        break;
      case 'heart_disease':
        endpoint = '/api/v1/lifestyle/heart-disease';
        payload = {
          ...heartData,
          age: Number(heartData.age),
          trestbps: Number(heartData.trestbps),
          chol: Number(heartData.chol),
          thalch: Number(heartData.thalch),
          oldpeak: Number(heartData.oldpeak),
          ca: Number(heartData.ca),
          fbs: Boolean(heartData.fbs),
          exang: Boolean(heartData.exang),
        };
        break;
      case 'hypertension':
        endpoint = '/api/v1/lifestyle/hypertension';
        payload = {
          ...hypertensionData,
          Age: Number(hypertensionData.Age),
          Salt_Intake: Number(hypertensionData.Salt_Intake),
          Stress_Score: Number(hypertensionData.Stress_Score),
          Sleep_Duration: Number(hypertensionData.Sleep_Duration),
          BMI: Number(hypertensionData.BMI),
        };
        break;
      case 'stroke':
        endpoint = '/api/v1/lifestyle/stroke';
        payload = {
          ...strokeData,
          age: Number(strokeData.age),
          hypertension: Number(strokeData.hypertension),
          heart_disease: Number(strokeData.heart_disease),
          avg_glucose_level: Number(strokeData.avg_glucose_level),
          bmi: Number(strokeData.bmi),
        };
        break;
      case 'ckd':
        endpoint = '/api/v1/lifestyle/ckd';
        payload = {
          Bp: Number(ckdData.Bp),
          Sg: Number(ckdData.Sg),
          Al: Number(ckdData.Al),
          Su: Number(ckdData.Su),
          Rbc: Number(ckdData.Rbc),
          Bu: Number(ckdData.Bu),
          Sc: Number(ckdData.Sc),
          Sod: Number(ckdData.Sod),
          Pot: Number(ckdData.Pot),
          Hemo: Number(ckdData.Hemo),
          Wbcc: Number(ckdData.Wbcc),
          Rbcc: Number(ckdData.Rbcc),
          Htn: Number(ckdData.Htn),
        };
        break;
    }

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const data: PredictionResponse = await response.json();
        setResults((prev) => ({ ...prev, [disease]: data }));
      } else if (response.status === 422) {
        const errorData = await response.json();
        const errors: Record<string, string> = {};
        if (Array.isArray(errorData.detail)) {
          errorData.detail.forEach((err: { loc?: (string | number)[]; msg?: string }) => {
            const fieldName = err.loc && err.loc.length > 1 ? String(err.loc[err.loc.length - 1]) : 'general';
            errors[fieldName] = err.msg || 'Invalid field value';
          });
        }
        setFieldErrors((prev) => ({ ...prev, [disease]: errors }));
        setGeneralErrors((prev) => ({
          ...prev,
          [disease]: 'Validation failed (422). Please check highlighted fields.',
        }));
      } else if (response.status === 500) {
        setGeneralErrors((prev) => ({
          ...prev,
          [disease]: 'Internal server error (500) while computing risk prediction.',
        }));
      } else {
        setGeneralErrors((prev) => ({
          ...prev,
          [disease]: `Request failed with status code ${response.status}.`,
        }));
      }
    } catch {
      setGeneralErrors((prev) => ({
        ...prev,
        [disease]: 'Network connection failure. Unable to contact API server.',
      }));
    } finally {
      setLoading((prev) => ({ ...prev, [disease]: false }));
    }
  };

  // Client-side overall summary calculation across completed assessments
  const calculateOverall = (): OverallSummary => {
    const assessed = Object.values(results).filter(Boolean) as PredictionResponse[];
    if (assessed.length === 0) {
      return {
        overall_risk: 'None',
        diseases_assessed: 0,
        high_risk_conditions: 0,
        moderate_risk_conditions: 0,
        low_risk_conditions: 0,
      };
    }
    const highs = assessed.filter((r) => r.risk_level === 'High').length;
    const mods = assessed.filter((r) => r.risk_level === 'Moderate').length;
    const lows = assessed.filter((r) => r.risk_level === 'Low').length;

    let overall: 'Low' | 'Moderate' | 'High' = 'Low';
    if (highs > 0) overall = 'High';
    else if (mods > 0) overall = 'Moderate';

    return {
      overall_risk: overall,
      diseases_assessed: assessed.length,
      high_risk_conditions: highs,
      moderate_risk_conditions: mods,
      low_risk_conditions: lows,
    };
  };

  const overallSummary = calculateOverall();

  const getRiskBadge = (level: 'Low' | 'Moderate' | 'High') => {
    switch (level) {
      case 'High':
        return (
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-300 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-rose-600 animate-pulse"></span> High Risk
          </span>
        );
      case 'Moderate':
        return (
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-300 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-amber-600"></span> Moderate Risk
          </span>
        );
      case 'Low':
      default:
        return (
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-600"></span> Low Risk
          </span>
        );
    }
  };

  const diseaseTabs: { id: DiseaseKey; label: string; icon: string }[] = [
    { id: 'diabetes', label: 'Diabetes', icon: 'bloodtype' },
    { id: 'heart_disease', label: 'Heart Disease', icon: 'favorite' },
    { id: 'hypertension', label: 'Hypertension', icon: 'speed' },
    { id: 'stroke', label: 'Stroke', icon: 'neurology' },
    { id: 'ckd', label: 'Chronic Kidney Disease', icon: 'vital_signs' },
  ];

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-200 pb-5">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Complex Disease Risk</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200 flex items-center gap-1">
              <span className="material-symbols-outlined text-xs">analytics</span> Module 3
            </span>
          </div>
          <p className="text-gray-500 text-sm mt-1">
            Machine learning multi-factor screening across 5 non-communicable lifestyle and biomarker conditions.
          </p>
        </div>

        {/* Global Summary Chip */}
        <div className="flex items-center gap-2 bg-gray-50 px-4 py-2.5 rounded-xl border border-gray-200">
          <span className="text-xs text-gray-500 font-medium">Screened:</span>
          <span className="text-sm font-bold text-gray-900">{overallSummary.diseases_assessed} / {diseaseTabs.length}</span>
          {overallSummary.overall_risk !== 'None' && (
            <div className="ml-2">{getRiskBadge(overallSummary.overall_risk)}</div>
          )}
        </div>
      </div>

      {/* Patient Basics Strip */}
      <div className="bg-gradient-to-r from-blue-50/70 via-indigo-50/40 to-slate-50 border border-blue-100 rounded-xl p-4 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center shadow-xs">
              <span className="material-symbols-outlined text-lg">badge</span>
            </div>
            <div>
              <h2 className="text-sm font-semibold text-gray-900">Patient Basics Strip</h2>
              <p className="text-xs text-gray-500">Quick-sync common attributes to prefill individual models</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-1.5 bg-white px-3 py-1.5 rounded-lg border border-gray-200 text-xs">
              <span className="text-gray-500 font-medium">Age:</span>
              <input
                type="number"
                min="1"
                max="120"
                value={basicAge}
                onChange={(e) => setBasicAge(e.target.value === '' ? '' : Number(e.target.value))}
                className="w-14 font-semibold text-gray-800 outline-none text-right"
              />
              <span className="text-gray-400">yr</span>
            </div>

            <div className="flex items-center gap-1.5 bg-white px-3 py-1.5 rounded-lg border border-gray-200 text-xs">
              <span className="text-gray-500 font-medium">Sex:</span>
              <select
                value={basicSex}
                onChange={(e) => setBasicSex(e.target.value as 'Male' | 'Female' | 'Other')}
                className="font-semibold text-gray-800 outline-none bg-transparent"
              >
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="flex items-center gap-1.5 bg-white px-3 py-1.5 rounded-lg border border-gray-200 text-xs">
              <span className="text-gray-500 font-medium">BMI:</span>
              <input
                type="number"
                step="0.1"
                min="5"
                max="80"
                value={basicBmi}
                onChange={(e) => setBasicBmi(e.target.value === '' ? '' : Number(e.target.value))}
                className="w-14 font-semibold text-gray-800 outline-none text-right"
              />
              <span className="text-gray-400">kg/m²</span>
            </div>

            <button
              type="button"
              onClick={applyBasicsToAll}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                basicsApplied
                  ? 'bg-emerald-600 text-white shadow-xs'
                  : 'bg-blue-600 hover:bg-blue-700 text-white shadow-xs'
              }`}
            >
              <span className="material-symbols-outlined text-sm">
                {basicsApplied ? 'check_circle' : 'sync'}
              </span>
              {basicsApplied ? 'Applied to Forms!' : 'Apply to Forms'}
            </button>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex flex-wrap items-center gap-2 border-b border-gray-200 pb-2">
        {diseaseTabs.map((tab) => {
          const res = results[tab.id];
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-white hover:bg-gray-50 text-gray-700 border border-gray-200'
              }`}
            >
              <span className="material-symbols-outlined text-lg">{tab.icon}</span>
              <span>{tab.label}</span>
              {res && (
                <span
                  className={`ml-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                    isActive
                      ? 'bg-white/20 text-white'
                      : res.risk_level === 'High'
                      ? 'bg-rose-100 text-rose-800'
                      : res.risk_level === 'Moderate'
                      ? 'bg-amber-100 text-amber-800'
                      : 'bg-emerald-100 text-emerald-800'
                  }`}
                >
                  {res.risk_level}
                </span>
              )}
            </button>
          );
        })}

        <button
          onClick={() => setActiveTab('overall')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all ml-auto ${
            activeTab === 'overall'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200'
          }`}
        >
          <span className="material-symbols-outlined text-lg">assessment</span>
          <span>Overall Summary</span>
          {overallSummary.diseases_assessed > 0 && (
            <span className="w-5 h-5 rounded-full bg-indigo-200 text-indigo-900 text-[11px] font-bold flex items-center justify-center">
              {overallSummary.diseases_assessed}
            </span>
          )}
        </button>
      </div>

      {/* TAB CONTENT */}

      {/* 1. DIABETES */}
      {activeTab === 'diabetes' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-red-50 text-red-600 flex items-center justify-center border border-red-100">
                  <span className="material-symbols-outlined text-xl">bloodtype</span>
                </div>
                <div>
                  <h2 className="text-base font-bold text-gray-900">Type 2 Diabetes Screening</h2>
                  <p className="text-xs text-gray-500">XGBoost biomarker classification model</p>
                </div>
              </div>

              <button
                type="button"
                onClick={() =>
                  setDiabetesData({
                    gender: 'Female',
                    age: 62,
                    hypertension: 1,
                    heart_disease: 0,
                    smoking_history: 'former',
                    bmi: 31.8,
                    HbA1c_level: 7.4,
                    blood_glucose_level: 185,
                  })
                }
                className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-1"
              >
                <span className="material-symbols-outlined text-sm">tune</span> Load High-Risk Sample
              </button>
            </div>

            {generalErrors.diabetes && (
              <div className="mb-5 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                <span className="material-symbols-outlined text-base">error</span>
                <span>{generalErrors.diabetes}</span>
              </div>
            )}

            <form
              onSubmit={(e) => {
                e.preventDefault();
                assessDisease('diabetes');
              }}
              className="space-y-4"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Gender */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Gender</label>
                  <select
                    value={diabetesData.gender}
                    onChange={(e) => setDiabetesData({ ...diabetesData, gender: e.target.value })}
                    className={`w-full px-3 py-2 text-sm rounded-lg border ${
                      fieldErrors.diabetes?.gender ? 'border-rose-400 bg-rose-50/30' : 'border-gray-200'
                    } focus:ring-2 focus:ring-blue-500 focus:outline-none`}
                  >
                    <option value="Female">Female</option>
                    <option value="Male">Male</option>
                    <option value="Other">Other</option>
                  </select>
                  {fieldErrors.diabetes?.gender && (
                    <p className="text-rose-600 text-[11px] mt-0.5">{fieldErrors.diabetes.gender}</p>
                  )}
                </div>

                {/* Age */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Age (1–120)</label>
                  <input
                    type="number"
                    min="1"
                    max="120"
                    value={diabetesData.age}
                    onChange={(e) => setDiabetesData({ ...diabetesData, age: Number(e.target.value) })}
                    className={`w-full px-3 py-2 text-sm rounded-lg border ${
                      fieldErrors.diabetes?.age ? 'border-rose-400 bg-rose-50/30' : 'border-gray-200'
                    } focus:ring-2 focus:ring-blue-500 focus:outline-none`}
                    required
                  />
                  {fieldErrors.diabetes?.age && (
                    <p className="text-rose-600 text-[11px] mt-0.5">{fieldErrors.diabetes.age}</p>
                  )}
                </div>

                {/* Hypertension */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Hypertension History</label>
                  <select
                    value={diabetesData.hypertension}
                    onChange={(e) => setDiabetesData({ ...diabetesData, hypertension: Number(e.target.value) })}
                    className={`w-full px-3 py-2 text-sm rounded-lg border ${
                      fieldErrors.diabetes?.hypertension ? 'border-rose-400 bg-rose-50/30' : 'border-gray-200'
                    } focus:ring-2 focus:ring-blue-500 focus:outline-none`}
                  >
                    <option value={0}>No (0)</option>
                    <option value={1}>Yes (1)</option>
                  </select>
                </div>

                {/* Heart Disease */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Heart Disease History</label>
                  <select
                    value={diabetesData.heart_disease}
                    onChange={(e) => setDiabetesData({ ...diabetesData, heart_disease: Number(e.target.value) })}
                    className={`w-full px-3 py-2 text-sm rounded-lg border ${
                      fieldErrors.diabetes?.heart_disease ? 'border-rose-400 bg-rose-50/30' : 'border-gray-200'
                    } focus:ring-2 focus:ring-blue-500 focus:outline-none`}
                  >
                    <option value={0}>No (0)</option>
                    <option value={1}>Yes (1)</option>
                  </select>
                </div>

                {/* Smoking History */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Smoking History</label>
                  <select
                    value={diabetesData.smoking_history}
                    onChange={(e) => setDiabetesData({ ...diabetesData, smoking_history: e.target.value })}
                    className={`w-full px-3 py-2 text-sm rounded-lg border ${
                      fieldErrors.diabetes?.smoking_history ? 'border-rose-400 bg-rose-50/30' : 'border-gray-200'
                    } focus:ring-2 focus:ring-blue-500 focus:outline-none`}
                  >
                    <option value="never">Never</option>
                    <option value="current">Current</option>
                    <option value="former">Former</option>
                    <option value="ever">Ever</option>
                    <option value="not current">Not Current</option>
                    <option value="No Info">No Info</option>
                  </select>
                  {fieldErrors.diabetes?.smoking_history && (
                    <p className="text-rose-600 text-[11px] mt-0.5">{fieldErrors.diabetes.smoking_history}</p>
                  )}
                </div>

                {/* BMI */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">BMI (5–80 kg/m²)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="5"
                    max="80"
                    value={diabetesData.bmi}
                    onChange={(e) => setDiabetesData({ ...diabetesData, bmi: Number(e.target.value) })}
                    className={`w-full px-3 py-2 text-sm rounded-lg border ${
                      fieldErrors.diabetes?.bmi ? 'border-rose-400 bg-rose-50/30' : 'border-gray-200'
                    } focus:ring-2 focus:ring-blue-500 focus:outline-none`}
                    required
                  />
                  {fieldErrors.diabetes?.bmi && (
                    <p className="text-rose-600 text-[11px] mt-0.5">{fieldErrors.diabetes.bmi}</p>
                  )}
                </div>

                {/* HbA1c */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">HbA1c Level (0–20 %)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="20"
                    value={diabetesData.HbA1c_level}
                    onChange={(e) => setDiabetesData({ ...diabetesData, HbA1c_level: Number(e.target.value) })}
                    className={`w-full px-3 py-2 text-sm rounded-lg border ${
                      fieldErrors.diabetes?.HbA1c_level ? 'border-rose-400 bg-rose-50/30' : 'border-gray-200'
                    } focus:ring-2 focus:ring-blue-500 focus:outline-none`}
                    required
                  />
                  {fieldErrors.diabetes?.HbA1c_level && (
                    <p className="text-rose-600 text-[11px] mt-0.5">{fieldErrors.diabetes.HbA1c_level}</p>
                  )}
                </div>

                {/* Blood Glucose Level */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Blood Glucose Level (1–1000 mg/dL, integer)
                  </label>
                  <input
                    type="number"
                    step="1"
                    min="1"
                    max="1000"
                    value={diabetesData.blood_glucose_level}
                    onChange={(e) =>
                      setDiabetesData({ ...diabetesData, blood_glucose_level: Number(e.target.value) })
                    }
                    className={`w-full px-3 py-2 text-sm rounded-lg border ${
                      fieldErrors.diabetes?.blood_glucose_level ? 'border-rose-400 bg-rose-50/30' : 'border-gray-200'
                    } focus:ring-2 focus:ring-blue-500 focus:outline-none`}
                    required
                  />
                  {fieldErrors.diabetes?.blood_glucose_level && (
                    <p className="text-rose-600 text-[11px] mt-0.5">
                      {fieldErrors.diabetes.blood_glucose_level}
                    </p>
                  )}
                </div>
              </div>

              <div className="pt-3">
                <button
                  type="submit"
                  disabled={loading.diabetes}
                  className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm transition-all shadow-sm flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading.diabetes ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Evaluating Risk...
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined text-base">analytics</span>
                      Assess Diabetes Risk
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Result Card */}
          <ResultPanel diseaseName="Diabetes" result={results.diabetes} onSwitchTab={setActiveTab} />
        </div>
      )}

      {/* 2. HEART DISEASE */}
      {activeTab === 'heart_disease' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center border border-rose-100">
                  <span className="material-symbols-outlined text-xl">favorite</span>
                </div>
                <div>
                  <h2 className="text-base font-bold text-gray-900">Heart Disease Risk</h2>
                  <p className="text-xs text-gray-500">Random Forest clinical risk classifier</p>
                </div>
              </div>

              <button
                type="button"
                onClick={() =>
                  setHeartData({
                    age: 63,
                    sex: 'Male',
                    cp: 'asymptomatic',
                    trestbps: 160,
                    chol: 285,
                    fbs: true,
                    restecg: 'lv hypertrophy',
                    thalch: 108,
                    exang: true,
                    oldpeak: 2.8,
                    slope: 'flat',
                    ca: 2,
                    thal: 'reversable defect',
                  })
                }
                className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-1"
              >
                <span className="material-symbols-outlined text-sm">tune</span> Load High-Risk Sample
              </button>
            </div>

            {generalErrors.heart_disease && (
              <div className="mb-5 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                <span className="material-symbols-outlined text-base">error</span>
                <span>{generalErrors.heart_disease}</span>
              </div>
            )}

            <form
              onSubmit={(e) => {
                e.preventDefault();
                assessDisease('heart_disease');
              }}
              className="space-y-4"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Age */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Age (1–120)</label>
                  <input
                    type="number"
                    min="1"
                    max="120"
                    value={heartData.age}
                    onChange={(e) => setHeartData({ ...heartData, age: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Sex */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Sex</label>
                  <select
                    value={heartData.sex}
                    onChange={(e) => setHeartData({ ...heartData, sex: e.target.value })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                  </select>
                </div>

                {/* Chest Pain (cp) */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Chest Pain Type (cp)</label>
                  <select
                    value={heartData.cp}
                    onChange={(e) => setHeartData({ ...heartData, cp: e.target.value })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="typical angina">Typical Angina</option>
                    <option value="atypical angina">Atypical Angina</option>
                    <option value="non-anginal">Non-anginal</option>
                    <option value="asymptomatic">Asymptomatic</option>
                  </select>
                </div>

                {/* Resting Blood Pressure (trestbps) */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Resting BP (trestbps: 1–300 mm Hg)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="300"
                    value={heartData.trestbps}
                    onChange={(e) => setHeartData({ ...heartData, trestbps: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Cholesterol */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Serum Cholesterol (chol: 1–1000 mg/dl)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="1000"
                    value={heartData.chol}
                    onChange={(e) => setHeartData({ ...heartData, chol: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Resting ECG */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Resting ECG (restecg)</label>
                  <select
                    value={heartData.restecg}
                    onChange={(e) => setHeartData({ ...heartData, restecg: e.target.value })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="normal">Normal</option>
                    <option value="st-t abnormality">ST-T Abnormality</option>
                    <option value="lv hypertrophy">LV Hypertrophy</option>
                  </select>
                </div>

                {/* Max Heart Rate (thalch) */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Max Heart Rate (thalch: 1–300 bpm)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="300"
                    value={heartData.thalch}
                    onChange={(e) => setHeartData({ ...heartData, thalch: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* ST Depression (oldpeak) */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    ST Depression (oldpeak: 0–20)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="20"
                    value={heartData.oldpeak}
                    onChange={(e) => setHeartData({ ...heartData, oldpeak: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Slope */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Peak ST Slope (slope)</label>
                  <select
                    value={heartData.slope}
                    onChange={(e) => setHeartData({ ...heartData, slope: e.target.value })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="upsloping">Upsloping</option>
                    <option value="flat">Flat</option>
                    <option value="downsloping">Downsloping</option>
                  </select>
                </div>

                {/* Number of Major Vessels (ca) */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Major Vessels (ca: 0–4)</label>
                  <input
                    type="number"
                    min="0"
                    max="4"
                    value={heartData.ca}
                    onChange={(e) => setHeartData({ ...heartData, ca: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Thalassemia (thal) */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Thalassemia (thal)</label>
                  <select
                    value={heartData.thal}
                    onChange={(e) => setHeartData({ ...heartData, thal: e.target.value })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="normal">Normal</option>
                    <option value="fixed defect">Fixed Defect</option>
                    <option value="reversable defect">Reversible defect</option>
                  </select>
                </div>

                {/* Boolean Toggles: FBS & EXANG */}
                <div className="flex flex-col justify-center gap-3 bg-gray-50 p-3 rounded-xl border border-gray-200">
                  <label className="flex items-center gap-2 cursor-pointer text-xs font-medium text-gray-800">
                    <input
                      type="checkbox"
                      checked={heartData.fbs}
                      onChange={(e) => setHeartData({ ...heartData, fbs: e.target.checked })}
                      className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-gray-300"
                    />
                    <span>Fasting Blood Sugar &gt; 120 mg/dL (fbs: bool)</span>
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer text-xs font-medium text-gray-800">
                    <input
                      type="checkbox"
                      checked={heartData.exang}
                      onChange={(e) => setHeartData({ ...heartData, exang: e.target.checked })}
                      className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-gray-300"
                    />
                    <span>Exercise-Induced Angina (exang: bool)</span>
                  </label>
                </div>
              </div>

              <div className="pt-3">
                <button
                  type="submit"
                  disabled={loading.heart_disease}
                  className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm transition-all shadow-sm flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading.heart_disease ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Evaluating Risk...
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined text-base">favorite</span>
                      Assess Heart Disease Risk
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          <ResultPanel diseaseName="Heart Disease" result={results.heart_disease} onSwitchTab={setActiveTab} />
        </div>
      )}

      {/* 3. HYPERTENSION */}
      {activeTab === 'hypertension' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center border border-amber-100">
                  <span className="material-symbols-outlined text-xl">speed</span>
                </div>
                <div>
                  <h2 className="text-base font-bold text-gray-900">Hypertension Risk</h2>
                  <p className="text-xs text-gray-500">Lifestyle and clinical blood pressure model</p>
                </div>
              </div>

              <button
                type="button"
                onClick={() =>
                  setHypertensionData({
                    Age: 58,
                    Salt_Intake: 22,
                    Stress_Score: 8,
                    Sleep_Duration: 5.0,
                    BMI: 30.5,
                    BP_History: 'Hypertension',
                    Medication: 'ACE Inhibitor',
                    Family_History: 'Yes',
                    Exercise_Level: 'Low',
                    Smoking_Status: 'Smoker',
                  })
                }
                className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-1"
              >
                <span className="material-symbols-outlined text-sm">tune</span> Load High-Risk Sample
              </button>
            </div>

            {generalErrors.hypertension && (
              <div className="mb-5 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                <span className="material-symbols-outlined text-base">error</span>
                <span>{generalErrors.hypertension}</span>
              </div>
            )}

            <form
              onSubmit={(e) => {
                e.preventDefault();
                assessDisease('hypertension');
              }}
              className="space-y-4"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Age */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Age (1–120)</label>
                  <input
                    type="number"
                    min="1"
                    max="120"
                    value={hypertensionData.Age}
                    onChange={(e) => setHypertensionData({ ...hypertensionData, Age: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Salt Intake */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Salt Intake (0–50, as recorded in training data)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="50"
                    value={hypertensionData.Salt_Intake}
                    onChange={(e) =>
                      setHypertensionData({ ...hypertensionData, Salt_Intake: Number(e.target.value) })
                    }
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Stress Score */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Stress Score (0–10)</label>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    max="10"
                    value={hypertensionData.Stress_Score}
                    onChange={(e) =>
                      setHypertensionData({ ...hypertensionData, Stress_Score: Number(e.target.value) })
                    }
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Sleep Duration */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Sleep Duration (0–24 h)</label>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    max="24"
                    value={hypertensionData.Sleep_Duration}
                    onChange={(e) =>
                      setHypertensionData({ ...hypertensionData, Sleep_Duration: Number(e.target.value) })
                    }
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* BMI */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">BMI (5–80)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="5"
                    max="80"
                    value={hypertensionData.BMI}
                    onChange={(e) => setHypertensionData({ ...hypertensionData, BMI: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* BP History */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">BP History</label>
                  <select
                    value={hypertensionData.BP_History}
                    onChange={(e) => setHypertensionData({ ...hypertensionData, BP_History: e.target.value })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="Normal">Normal</option>
                    <option value="Prehypertension">Prehypertension</option>
                    <option value="Hypertension">Hypertension</option>
                  </select>
                </div>

                {/* Medication */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Medication</label>
                  <select
                    value={hypertensionData.Medication}
                    onChange={(e) => setHypertensionData({ ...hypertensionData, Medication: e.target.value })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="None">None</option>
                    <option value="ACE Inhibitor">ACE Inhibitor</option>
                    <option value="Beta Blocker">Beta Blocker</option>
                    <option value="Diuretic">Diuretic</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                {/* Family History */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Family History</label>
                  <select
                    value={hypertensionData.Family_History}
                    onChange={(e) =>
                      setHypertensionData({ ...hypertensionData, Family_History: e.target.value })
                    }
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="No">No</option>
                    <option value="Yes">Yes</option>
                  </select>
                </div>

                {/* Exercise Level */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Exercise Level</label>
                  <select
                    value={hypertensionData.Exercise_Level}
                    onChange={(e) =>
                      setHypertensionData({ ...hypertensionData, Exercise_Level: e.target.value })
                    }
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="Low">Low</option>
                    <option value="Moderate">Moderate</option>
                    <option value="High">High</option>
                  </select>
                </div>

                {/* Smoking Status */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Smoking Status</label>
                  <select
                    value={hypertensionData.Smoking_Status}
                    onChange={(e) =>
                      setHypertensionData({ ...hypertensionData, Smoking_Status: e.target.value })
                    }
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="Non-Smoker">Non-Smoker</option>
                    <option value="Smoker">Smoker</option>
                  </select>
                </div>
              </div>

              <div className="pt-3">
                <button
                  type="submit"
                  disabled={loading.hypertension}
                  className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm transition-all shadow-sm flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading.hypertension ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Evaluating Risk...
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined text-base">speed</span>
                      Assess Hypertension Risk
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          <ResultPanel diseaseName="Hypertension" result={results.hypertension} onSwitchTab={setActiveTab} />
        </div>
      )}

      {/* 4. STROKE */}
      {activeTab === 'stroke' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center border border-purple-100">
                  <span className="material-symbols-outlined text-xl">neurology</span>
                </div>
                <div>
                  <h2 className="text-base font-bold text-gray-900">Stroke Risk Assessment</h2>
                  <p className="text-xs text-gray-500">Cerebrovascular risk predictive model</p>
                </div>
              </div>

              <button
                type="button"
                onClick={() =>
                  setStrokeData({
                    gender: 'Male',
                    age: 74,
                    hypertension: 1,
                    heart_disease: 1,
                    ever_married: 'Yes',
                    work_type: 'Self-employed',
                    Residence_type: 'Urban',
                    avg_glucose_level: 215.3,
                    bmi: 34.2,
                    smoking_status: 'smokes',
                  })
                }
                className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-1"
              >
                <span className="material-symbols-outlined text-sm">tune</span> Load High-Risk Sample
              </button>
            </div>

            {generalErrors.stroke && (
              <div className="mb-5 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                <span className="material-symbols-outlined text-base">error</span>
                <span>{generalErrors.stroke}</span>
              </div>
            )}

            <form
              onSubmit={(e) => {
                e.preventDefault();
                assessDisease('stroke');
              }}
              className="space-y-4"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Gender */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Gender</label>
                  <select
                    value={strokeData.gender}
                    onChange={(e) => setStrokeData({ ...strokeData, gender: e.target.value })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                {/* Age */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Age (1–120)</label>
                  <input
                    type="number"
                    min="1"
                    max="120"
                    value={strokeData.age}
                    onChange={(e) => setStrokeData({ ...strokeData, age: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Hypertension */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Hypertension</label>
                  <select
                    value={strokeData.hypertension}
                    onChange={(e) => setStrokeData({ ...strokeData, hypertension: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value={0}>No (0)</option>
                    <option value={1}>Yes (1)</option>
                  </select>
                </div>

                {/* Heart Disease */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Heart Disease</label>
                  <select
                    value={strokeData.heart_disease}
                    onChange={(e) => setStrokeData({ ...strokeData, heart_disease: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value={0}>No (0)</option>
                    <option value={1}>Yes (1)</option>
                  </select>
                </div>

                {/* Ever Married */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Ever Married</label>
                  <select
                    value={strokeData.ever_married}
                    onChange={(e) => setStrokeData({ ...strokeData, ever_married: e.target.value })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="Yes">Yes</option>
                    <option value="No">No</option>
                  </select>
                </div>

                {/* Work Type */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Work Type</label>
                  <select
                    value={strokeData.work_type}
                    onChange={(e) => setStrokeData({ ...strokeData, work_type: e.target.value })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="Private">Private</option>
                    <option value="Self-employed">Self-employed</option>
                    <option value="Govt_job">Government Job</option>
                    <option value="children">Children</option>
                    <option value="Never_worked">Never Worked</option>
                  </select>
                </div>

                {/* Residence Type */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Residence Type</label>
                  <select
                    value={strokeData.Residence_type}
                    onChange={(e) => setStrokeData({ ...strokeData, Residence_type: e.target.value })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="Urban">Urban</option>
                    <option value="Rural">Rural</option>
                  </select>
                </div>

                {/* Avg Glucose Level */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Avg Glucose Level (1–1000 mg/dL)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="1"
                    max="1000"
                    value={strokeData.avg_glucose_level}
                    onChange={(e) =>
                      setStrokeData({ ...strokeData, avg_glucose_level: Number(e.target.value) })
                    }
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* BMI */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">BMI (5–80)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="5"
                    max="80"
                    value={strokeData.bmi}
                    onChange={(e) => setStrokeData({ ...strokeData, bmi: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Smoking Status */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Smoking Status</label>
                  <select
                    value={strokeData.smoking_status}
                    onChange={(e) => setStrokeData({ ...strokeData, smoking_status: e.target.value })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="never smoked">Never Smoked</option>
                    <option value="formerly smoked">Formerly Smoked</option>
                    <option value="smokes">Smokes</option>
                    <option value="Unknown">Unknown</option>
                  </select>
                </div>
              </div>

              <div className="pt-3">
                <button
                  type="submit"
                  disabled={loading.stroke}
                  className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm transition-all shadow-sm flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading.stroke ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Evaluating Risk...
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined text-base">neurology</span>
                      Assess Stroke Risk
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          <ResultPanel diseaseName="Stroke" result={results.stroke} onSwitchTab={setActiveTab} />
        </div>
      )}

      {/* 5. CKD */}
      {activeTab === 'ckd' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center border border-teal-100">
                  <span className="material-symbols-outlined text-xl">vital_signs</span>
                </div>
                <div>
                  <h2 className="text-base font-bold text-gray-900">Chronic Kidney Disease (CKD)</h2>
                  <p className="text-xs text-gray-500">Renal biochemistry & urine analysis model</p>
                </div>
              </div>

              <button
                type="button"
                onClick={() =>
                  setCkdData({
                    Bp: 90,
                    Sg: 1.01,
                    Al: 3,
                    Su: 2,
                    Rbc: 1, // Abnormal
                    Bu: 82,
                    Sc: 3.4,
                    Sod: 131,
                    Pot: 5.6,
                    Hemo: 9.8,
                    Wbcc: 11200,
                    Rbcc: 3.8,
                    Htn: 1, // Yes
                  })
                }
                className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-1"
              >
                <span className="material-symbols-outlined text-sm">tune</span> Load High-Risk Sample
              </button>
            </div>

            {generalErrors.ckd && (
              <div className="mb-5 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                <span className="material-symbols-outlined text-base">error</span>
                <span>{generalErrors.ckd}</span>
              </div>
            )}

            <form
              onSubmit={(e) => {
                e.preventDefault();
                assessDisease('ckd');
              }}
              className="space-y-4"
            >
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Bp */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Blood Pressure (1–300)</label>
                  <input
                    type="number"
                    min="1"
                    max="300"
                    value={ckdData.Bp}
                    onChange={(e) => setCkdData({ ...ckdData, Bp: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Specific Gravity (Sg) */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Specific Gravity (1.0–1.1)</label>
                  <input
                    type="number"
                    step="0.005"
                    min="1.0"
                    max="1.1"
                    value={ckdData.Sg}
                    onChange={(e) => setCkdData({ ...ckdData, Sg: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Albumin (Al) */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Albumin (0–5)</label>
                  <input
                    type="number"
                    min="0"
                    max="5"
                    value={ckdData.Al}
                    onChange={(e) => setCkdData({ ...ckdData, Al: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Sugar (Su) */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Sugar (0–5)</label>
                  <input
                    type="number"
                    min="0"
                    max="5"
                    value={ckdData.Su}
                    onChange={(e) => setCkdData({ ...ckdData, Su: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* RBC (Confirmed labels: 0=Normal, 1=Abnormal) */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Red Blood Cells (Rbc)</label>
                  <select
                    value={ckdData.Rbc}
                    onChange={(e) => setCkdData({ ...ckdData, Rbc: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value={0}>0: Normal</option>
                    <option value={1}>1: Abnormal</option>
                  </select>
                </div>

                {/* Blood Urea (Bu) */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Blood Urea (1–500 mg/dl)</label>
                  <input
                    type="number"
                    min="1"
                    max="500"
                    value={ckdData.Bu}
                    onChange={(e) => setCkdData({ ...ckdData, Bu: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Serum Creatinine (Sc) */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Serum Creatinine (1–30)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="1"
                    max="30"
                    value={ckdData.Sc}
                    onChange={(e) => setCkdData({ ...ckdData, Sc: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Sodium (Sod) */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Sodium (1–200 mEq/L)</label>
                  <input
                    type="number"
                    min="1"
                    max="200"
                    value={ckdData.Sod}
                    onChange={(e) => setCkdData({ ...ckdData, Sod: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Potassium (Pot) */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Potassium (1–20 mEq/L)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="1"
                    max="20"
                    value={ckdData.Pot}
                    onChange={(e) => setCkdData({ ...ckdData, Pot: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Hemoglobin (Hemo) */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Hemoglobin (1–30 g/dl)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="1"
                    max="30"
                    value={ckdData.Hemo}
                    onChange={(e) => setCkdData({ ...ckdData, Hemo: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* WBC Count (Wbcc) */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">WBC Count (1–50000 /cumm)</label>
                  <input
                    type="number"
                    min="1"
                    max="50000"
                    value={ckdData.Wbcc}
                    onChange={(e) => setCkdData({ ...ckdData, Wbcc: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* RBC Count (Rbcc) */}
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">RBC Count (1–15 m/cmm)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="1"
                    max="15"
                    value={ckdData.Rbcc}
                    onChange={(e) => setCkdData({ ...ckdData, Rbcc: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    required
                  />
                </div>

                {/* Hypertension (Htn - Confirmed: 0=No, 1=Yes) */}
                <div className="md:col-span-3">
                  <label className="block text-xs font-semibold text-gray-700 mb-1">Hypertension Status (Htn)</label>
                  <select
                    value={ckdData.Htn}
                    onChange={(e) => setCkdData({ ...ckdData, Htn: Number(e.target.value) })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value={0}>0: No (Not Hypertensive)</option>
                    <option value={1}>1: Yes (Hypertensive)</option>
                  </select>
                </div>
              </div>

              <div className="pt-3">
                <button
                  type="submit"
                  disabled={loading.ckd}
                  className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl text-sm transition-all shadow-sm flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading.ckd ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Evaluating Risk...
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined text-base">vital_signs</span>
                      Assess Chronic Kidney Disease Risk
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          <ResultPanel diseaseName="Chronic Kidney Disease" result={results.ckd} onSwitchTab={setActiveTab} />
        </div>
      )}

      {/* OVERALL SUMMARY TAB */}
      {activeTab === 'overall' && (
        <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-100 pb-4">
            <div>
              <h2 className="text-lg font-bold text-gray-900">Overall Disease Screening Summary</h2>
              <p className="text-xs text-gray-500">
                Consolidated overview computed across completed independent risk assessments
              </p>
            </div>
            {overallSummary.overall_risk !== 'None' && getRiskBadge(overallSummary.overall_risk)}
          </div>

          {overallSummary.diseases_assessed === 0 ? (
            <div className="py-12 text-center">
              <div className="w-16 h-16 rounded-full bg-gray-50 border border-gray-100 flex items-center justify-center mx-auto mb-3">
                <span className="material-symbols-outlined text-3xl text-gray-400">pending_actions</span>
              </div>
              <h3 className="text-sm font-semibold text-gray-800">No Assessments Completed Yet</h3>
              <p className="text-xs text-gray-500 max-w-sm mx-auto mt-1 mb-4">
                Fill in the data for any condition (or click Load Sample Data) and evaluate its risk to see summary
                analytics.
              </p>
              <button
                onClick={() => setActiveTab('diabetes')}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl shadow-xs"
              >
                Start with Diabetes
              </button>
            </div>
          ) : (
            <>
              {/* Stat Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-gray-50 border border-gray-200">
                  <div className="text-xs text-gray-500 font-medium">Assessed</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">
                    {overallSummary.diseases_assessed} <span className="text-xs text-gray-400 font-normal">/ 5</span>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-rose-50/70 border border-rose-200">
                  <div className="text-xs text-rose-700 font-medium">High Risk</div>
                  <div className="text-2xl font-bold text-rose-800 mt-1">
                    {overallSummary.high_risk_conditions}
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200">
                  <div className="text-xs text-amber-700 font-medium">Moderate Risk</div>
                  <div className="text-2xl font-bold text-amber-800 mt-1">
                    {overallSummary.moderate_risk_conditions}
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-emerald-50/70 border border-emerald-200">
                  <div className="text-xs text-emerald-700 font-medium">Low Risk</div>
                  <div className="text-2xl font-bold text-emerald-800 mt-1">
                    {overallSummary.low_risk_conditions}
                  </div>
                </div>
              </div>

              {/* Conditions List */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500">Completed Assessments</h3>
                <div className="divide-y divide-gray-100 border border-gray-200 rounded-xl overflow-hidden">
                  {diseaseTabs.map((d) => {
                    const res = results[d.id];
                    return (
                      <div
                        key={d.id}
                        className="p-4 flex items-center justify-between hover:bg-gray-50/60 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <span className="material-symbols-outlined text-gray-400">{d.icon}</span>
                          <div>
                            <span className="text-sm font-semibold text-gray-900">{d.label}</span>
                            <div className="text-[11px] text-gray-400">
                              {res
                                ? `Model Prediction Class: ${res.prediction}`
                                : 'Assessment pending — not submitted'}
                            </div>
                          </div>
                        </div>

                        {res ? (
                          <div className="flex items-center gap-4">
                            <div className="text-right">
                              <span className="text-sm font-bold text-gray-900">
                                {(res.risk_probability * 100).toFixed(1)}%
                              </span>
                              <div className="text-[10px] text-gray-400">model-estimated probability</div>
                            </div>
                            {getRiskBadge(res.risk_level)}
                          </div>
                        ) : (
                          <button
                            onClick={() => setActiveTab(d.id)}
                            className="text-xs font-semibold text-blue-600 hover:text-blue-800 hover:underline"
                          >
                            Assess Now &rarr;
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Mandatory Disclaimer (always shown) */}
      <div className="bg-amber-50/70 border border-amber-200 rounded-xl p-4 flex items-start gap-3 shadow-xs">
        <span className="material-symbols-outlined text-amber-600 text-xl shrink-0 mt-0.5">info</span>
        <div className="text-xs text-amber-900 leading-relaxed">
          <p className="font-semibold text-amber-950">Clinical Screening Disclaimer</p>
          <p className="mt-0.5">
            Screening estimate from a model trained on public datasets; not validated for Indian populations; not a
            diagnosis. Risk cutoffs are predefined statistical bands (&lt;33% Low, 33–66% Moderate, &gt;66% High), not
            established clinical intervention thresholds.
          </p>
        </div>
      </div>
    </div>
  );
}

// Subcomponent: Individual Result Panel
function ResultPanel({
  diseaseName,
  result,
  onSwitchTab,
}: {
  diseaseName: string;
  result?: PredictionResponse;
  onSwitchTab: (tab: DiseaseKey | 'overall') => void;
}) {
  if (!result) {
    return (
      <div className="bg-gray-50/70 border border-dashed border-gray-300 rounded-2xl p-6 flex flex-col items-center justify-center text-center h-full min-h-[300px]">
        <div className="w-12 h-12 rounded-full bg-white border border-gray-200 flex items-center justify-center mb-3 text-gray-400 shadow-xs">
          <span className="material-symbols-outlined text-2xl">pending</span>
        </div>
        <h3 className="text-sm font-bold text-gray-800 mb-1">Awaiting Assessment</h3>
        <p className="text-xs text-gray-500 max-w-xs mb-4">
          Complete the form and click assess to calculate {diseaseName} probability.
        </p>
      </div>
    );
  }

  const probPercent = (result.risk_probability * 100).toFixed(1);

  return (
    <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between border-b border-gray-100 pb-3 mb-4">
          <span className="text-xs font-bold uppercase tracking-wider text-gray-500">Screening Result</span>
          <span
            className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${
              result.risk_level === 'High'
                ? 'bg-rose-100 text-rose-800 border border-rose-200'
                : result.risk_level === 'Moderate'
                ? 'bg-amber-100 text-amber-800 border border-amber-200'
                : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
            }`}
          >
            {result.risk_level} Risk
          </span>
        </div>

        {/* Probability display */}
        <div className="text-center py-4 bg-gray-50/80 rounded-xl border border-gray-100 mb-4">
          <div className="text-4xl font-extrabold text-gray-900 tracking-tight">{probPercent}%</div>
          <div className="text-xs font-medium text-gray-500 mt-1">model-estimated probability</div>
        </div>

        {/* Visual Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-[11px] font-semibold text-gray-500 mb-1">
            <span>0% (Low)</span>
            <span>33%</span>
            <span>66%</span>
            <span>100% (High)</span>
          </div>
          <div className="h-2.5 w-full bg-gray-100 rounded-full overflow-hidden flex">
            <div
              className={`h-full transition-all duration-500 ${
                result.risk_level === 'High'
                  ? 'bg-rose-500'
                  : result.risk_level === 'Moderate'
                  ? 'bg-amber-500'
                  : 'bg-emerald-500'
              }`}
              style={{ width: `${Math.min(100, Math.max(0, result.risk_probability * 100))}%` }}
            ></div>
          </div>
        </div>

        {/* Band explanation note */}
        <div className="bg-blue-50/60 border border-blue-100 rounded-xl p-3 text-[11px] text-blue-900 leading-relaxed mb-4">
          <span className="font-semibold">Note on Probability Bands:</span> Bands are fixed cutoffs (&lt;33% Low,
          33–66% Moderate, &gt;66% High), not clinical thresholds.
        </div>
      </div>

      <div className="pt-2">
        <button
          type="button"
          onClick={() => onSwitchTab('overall')}
          className="w-full py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold text-xs rounded-xl transition-all flex items-center justify-center gap-1.5"
        >
          <span className="material-symbols-outlined text-sm">assessment</span>
          View Overall Summary
        </button>
      </div>
    </div>
  );
}
