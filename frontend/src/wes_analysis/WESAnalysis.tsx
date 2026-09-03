import { ChangeEvent, useState } from "react";
import "./WESAnalysis.css";

interface Explanation {
  status?: string;
  summary?: string;
  what_was_found?: string;
  evidence_explanation?: string;
  classification_explanation?: string;
  limitations?: string[];
  patient_friendly_explanation?: string;
}

interface VariantResult {
  gene: string;
  variant: string;
  type: string;
  interpretation?: {
    classification?: string;
    confidence?: string;
    reasoning?: string[];
    identity?: Record<string, unknown>;
    evidence_summary?: Record<string, unknown>;
    explanation?: Explanation;
  };
}

interface AnalysisResponse {
  report_id: number;
  patient_id: number;
  report_name: string;
  status: string;
  variant_count: number;
  results: VariantResult[];
}

function WESAnalysis() {
  const [patientId, setPatientId] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState("");

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0] ?? null;
    setFile(selectedFile);
  };

  const analyzeReport = async () => {
    setError("");
    setResult(null);

    if (!patientId.trim()) {
      setError("Please enter a patient ID.");
      return;
    }

    if (!file) {
      setError("Please select a WES PDF.");
      return;
    }

    if (file.type !== "application/pdf") {
      setError("Only PDF files are supported.");
      return;
    }

    const formData = new FormData();
    formData.append("patient_id", patientId);
    formData.append("file", file);

    try {
      setLoading(true);

      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/wes/analyze",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail || "WES analysis failed."
        );
      }

      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong during WES analysis."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="wes-page">
      <div className="wes-container">
        <header className="wes-header">
          <h1>GeneGuard-AI</h1>
          <p>WES Analysis</p>
        </header>

        <section className="wes-upload-card">
          <h2>Upload WES Report</h2>

          <div className="wes-field">
            <label htmlFor="patientId">Patient ID</label>
            <input
              id="patientId"
              type="number"
              value={patientId}
              onChange={(event) => setPatientId(event.target.value)}
              placeholder="Enter patient ID"
            />
          </div>

          <div className="wes-field">
            <label htmlFor="wesFile">WES Report PDF</label>
            <input
              id="wesFile"
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileChange}
            />

            {file && (
              <p className="selected-file">
                Selected: {file.name}
              </p>
            )}
          </div>

          <button
            type="button"
            className="analyze-button"
            onClick={analyzeReport}
            disabled={loading}
          >
            {loading ? "Analyzing..." : "Analyze WES Report"}
          </button>

          {error && (
            <div className="wes-error">
              {error}
            </div>
          )}
        </section>

        {result && (
          <section className="wes-results">
            <div className="results-header">
              <div>
                <h2>Analysis Results</h2>
                <p>
                  Report: {result.report_name}
                </p>
              </div>

              <div className="results-count">
                {result.variant_count} variants found
              </div>
            </div>

            {result.results.map((variant, index) => {
              const interpretation =
                variant.interpretation;

              const explanation =
                interpretation?.explanation;

              return (
                <article
                  className="variant-card"
                  key={`${variant.gene}-${variant.variant}-${index}`}
                >
                  <div className="variant-top">
                    <div>
                      <h3>{variant.gene}</h3>
                      <p className="variant-name">
                        {variant.variant}
                      </p>
                    </div>

                    <div className="variant-badges">
                      <span className="badge">
                        {variant.type}
                      </span>

                      <span className="badge">
                        {interpretation?.classification ||
                          "Unknown"}
                      </span>

                      <span className="badge">
                        {interpretation?.confidence ||
                          "Unknown"}
                      </span>
                    </div>
                  </div>

                  {explanation?.summary && (
                    <div className="result-section">
                      <h4>Summary</h4>
                      <p>
                        {explanation.summary}
                      </p>
                    </div>
                  )}

                  {explanation?.what_was_found && (
                    <div className="result-section">
                      <h4>What was found</h4>
                      <p>
                        {explanation.what_was_found}
                      </p>
                    </div>
                  )}

                  {explanation?.evidence_explanation && (
                    <div className="result-section">
                      <h4>Evidence</h4>
                      <p>
                        {explanation.evidence_explanation}
                      </p>
                    </div>
                  )}

                  {explanation?.classification_explanation && (
                    <div className="result-section">
                      <h4>Classification</h4>
                      <p>
                        {explanation.classification_explanation}
                      </p>
                    </div>
                  )}

                  {explanation?.patient_friendly_explanation && (
                    <div className="patient-friendly">
                      <h4>Simple explanation</h4>
                      <p>
                        {explanation.patient_friendly_explanation}
                      </p>
                    </div>
                  )}

                  {explanation?.limitations &&
                    explanation.limitations.length > 0 && (
                      <div className="result-section">
                        <h4>Limitations</h4>

                        <ul>
                          {explanation.limitations.map(
                            (limitation, limitationIndex) => (
                              <li key={limitationIndex}>
                                {limitation}
                              </li>
                            )
                          )}
                        </ul>
                      </div>
                    )}
                </article>
              );
            })}
          </section>
        )}
      </div>
    </div>
  );
}

export default WESAnalysis;