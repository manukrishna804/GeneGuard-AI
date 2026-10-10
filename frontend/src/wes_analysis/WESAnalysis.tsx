import { useState } from "react";
import type { ChangeEvent } from "react";
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

interface PRSQC {
  total_model_variants: number;
  matched_variants: number;
  aligned_variants: number;
  missing_variants: number;
  coverage: number;
  alignment_rate: number;
  status: string;
}

interface PRSResult {
  disease: string;
  patient_id?: string;
  vcf_sample_id?: string;
  pgs_id: string;
  model_name?: string;
  genome_build?: string;
  prs?: number;
  score_100?: number | null;
  score_100_status?: string;
  score_100_reference?: string;
  contributions?: unknown[];
  qc?: PRSQC;
  status: string;
  error?: string;
}

interface PRSResponse {
  patient_id: string;
  vcf_sample_id?: string;
  diseases_processed: number;
  results: PRSResult[];
}

function WESAnalysis() {
  // --------------------------------------------------
  // Common patient ID
  // --------------------------------------------------

  const [patientId, setPatientId] = useState("");

  // --------------------------------------------------
  // WES state
  // --------------------------------------------------

  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] =
    useState<AnalysisResponse | null>(null);
  const [error, setError] = useState("");

  // --------------------------------------------------
  // PRS state
  // --------------------------------------------------

  const [prsVcf, setPrsVcf] =
    useState<File | null>(null);
  const [prsLoading, setPrsLoading] =
    useState(false);
  const [prsResult, setPrsResult] =
    useState<PRSResponse | null>(null);
  const [prsError, setPrsError] =
    useState("");

  // --------------------------------------------------
  // WES file handler
  // --------------------------------------------------

  const handleFileChange = (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    const selectedFile =
      event.target.files?.[0] ?? null;

    setFile(selectedFile);
  };

  // --------------------------------------------------
  // PRS VCF handler
  // --------------------------------------------------

  const handlePrsVcfChange = (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    const selectedFile =
      event.target.files?.[0] ?? null;

    setPrsVcf(selectedFile);
  };

  // --------------------------------------------------
  // WES analysis
  // --------------------------------------------------

  const analyzeReport = async () => {
    setError("");
    setResult(null);

    if (!patientId.trim()) {
      setError(
        "Please enter a patient ID."
      );
      return;
    }

    if (!file) {
      setError(
        "Please select a WES PDF."
      );
      return;
    }

    if (file.type !== "application/pdf") {
      setError(
        "Only PDF files are supported."
      );
      return;
    }

    const formData = new FormData();

    formData.append(
      "patient_id",
      patientId.trim()
    );

    formData.append(
      "file",
      file
    );

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
          data?.detail ||
            "WES analysis failed."
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

  // --------------------------------------------------
  // PRS calculation
  // --------------------------------------------------

  const calculatePRS = async () => {
    setPrsError("");
    setPrsResult(null);

    if (!patientId.trim()) {
      setPrsError(
        "Please enter a patient ID."
      );
      return;
    }

    if (!prsVcf) {
      setPrsError(
        "Please select a compressed VCF (.vcf.gz)."
      );
      return;
    }

    if (
      !prsVcf.name
        .toLowerCase()
        .endsWith(".vcf.gz")
    ) {
      setPrsError(
        "PRS requires a compressed VCF (.vcf.gz)."
      );
      return;
    }

    const formData = new FormData();

    formData.append(
      "patient_id",
      patientId.trim()
    );

    formData.append(
      "vcf",
      prsVcf
    );

    try {
      setPrsLoading(true);

      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/prs/calculate",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            "PRS calculation failed."
        );
      }

      setPrsResult(data);
    } catch (err) {
      setPrsError(
        err instanceof Error
          ? err.message
          : "Something went wrong during PRS calculation."
      );
    } finally {
      setPrsLoading(false);
    }
  };

  return (
    <div className="wes-page">
      <div className="wes-container">

        {/* ==================================================
            PAGE HEADER
            ================================================== */}

        <header className="wes-header">
          <h1>GeneGuard-AI</h1>

          <p>
            WES Analysis &amp; Polygenic Risk Scoring
          </p>
        </header>

        {/* ==================================================
            COMMON PATIENT INFORMATION
            ================================================== */}

        <section className="wes-upload-card">
          <h2>Patient Information</h2>

          <div className="wes-field">
            <label htmlFor="patientId">
              Patient ID
            </label>

            <input
              id="patientId"
              type="text"
              value={patientId}
              onChange={(event) =>
                setPatientId(event.target.value)
              }
              placeholder="Enter patient ID"
            />
          </div>
        </section>

        {/* ==================================================
            WES UPLOAD
            ================================================== */}

        <section className="wes-upload-card">
          <h2>Upload WES Report</h2>

          <div className="wes-field">
            <label htmlFor="wesFile">
              WES Report PDF
            </label>

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
            {loading
              ? "Analyzing..."
              : "Analyze WES Report"}
          </button>

          {error && (
            <div className="wes-error">
              {error}
            </div>
          )}
        </section>

        {/* ==================================================
            PRS UPLOAD
            ================================================== */}

        <section className="wes-upload-card">
          <h2>
            Calculate Polygenic Risk Scores
          </h2>

          <p>
            Upload the patient's compressed VCF
            file. GeneGuard-AI automatically
            handles the VCF index and calculates
            PRS for all five configured diseases.
          </p>

          <div className="wes-field">
            <label htmlFor="prsVcf">
              Patient VCF (.vcf.gz)
            </label>

            <input
              id="prsVcf"
              type="file"
              accept=".vcf.gz"
              onChange={handlePrsVcfChange}
            />

            {prsVcf && (
              <p className="selected-file">
                Selected: {prsVcf.name}
              </p>
            )}
          </div>

          <button
            type="button"
            className="analyze-button"
            onClick={calculatePRS}
            disabled={prsLoading}
          >
            {prsLoading
              ? "Calculating PRS..."
              : "Calculate PRS"}
          </button>

          {prsError && (
            <div className="wes-error">
              {prsError}
            </div>
          )}
        </section>

        {/* ==================================================
            WES RESULTS
            ================================================== */}

        {result && (
          <section className="wes-results">
            <div className="results-header">
              <div>
                <h2>
                  WES Analysis Results
                </h2>

                <p>
                  Patient ID:{" "}
                  {result.patient_id}
                </p>

                <p>
                  Report:{" "}
                  {result.report_name}
                </p>
              </div>

              <div className="results-count">
                {result.variant_count} variants found
              </div>
            </div>

            {result.results.map(
              (variant, index) => {
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
                        <h3>
                          {variant.gene}
                        </h3>

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
                        <h4>
                          What was found
                        </h4>

                        <p>
                          {
                            explanation.what_was_found
                          }
                        </p>
                      </div>
                    )}

                    {explanation?.evidence_explanation && (
                      <div className="result-section">
                        <h4>Evidence</h4>

                        <p>
                          {
                            explanation.evidence_explanation
                          }
                        </p>
                      </div>
                    )}

                    {explanation?.classification_explanation && (
                      <div className="result-section">
                        <h4>
                          Classification
                        </h4>

                        <p>
                          {
                            explanation.classification_explanation
                          }
                        </p>
                      </div>
                    )}

                    {explanation?.patient_friendly_explanation && (
                      <div className="patient-friendly">
                        <h4>
                          Simple explanation
                        </h4>

                        <p>
                          {
                            explanation.patient_friendly_explanation
                          }
                        </p>
                      </div>
                    )}

                    {explanation?.limitations &&
                      explanation.limitations.length >
                        0 && (
                        <div className="result-section">
                          <h4>
                            Limitations
                          </h4>

                          <ul>
                            {explanation.limitations.map(
                              (
                                limitation,
                                limitationIndex
                              ) => (
                                <li
                                  key={
                                    limitationIndex
                                  }
                                >
                                  {limitation}
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                  </article>
                );
              }
            )}
          </section>
        )}

        {/* ==================================================
            PRS RESULTS
            ================================================== */}

        {prsResult && (
          <section className="wes-results">
            <div className="results-header">
              <div>
                <h2>
                  Polygenic Risk Scores
                </h2>

                <p>
                  Patient ID:{" "}
                  {prsResult.patient_id}
                </p>

                
              </div>

              <div className="results-count">
                {prsResult.diseases_processed}{" "}
                diseases
              </div>
            </div>

            {prsResult.results.map((prs) => {
              const hasQc = !!prs.qc;

              const coveragePercent =
                hasQc && prs.qc
                  ? (
                      prs.qc.coverage * 100
                    ).toFixed(1)
                  : "N/A";

              const alignmentPercent =
                hasQc && prs.qc
                  ? (
                      prs.qc.alignment_rate *
                      100
                    ).toFixed(1)
                  : "N/A";

              return (
                <article
                  className="variant-card"
                  key={prs.disease}
                >
                  {/* ----------------------------------------
                      PRS HEADER
                      ---------------------------------------- */}

                  <div className="variant-top">
                    <div>
                      <h3>
                        {prs.disease}
                      </h3>

                      <p className="variant-name">
                        {prs.model_name ||
                          prs.pgs_id}
                      </p>
                    </div>

                    <div className="variant-badges">
                      <span className="badge">
                        {prs.status}
                      </span>

                      <span className="badge">
                        {prs.pgs_id}
                      </span>
                    </div>
                  </div>

                  {/* ----------------------------------------
                      ERROR
                      ---------------------------------------- */}

                  {prs.status === "ERROR" ? (
                    <div className="wes-error">
                      {prs.error ||
                        "PRS calculation failed."}
                    </div>
                  ) : (
                    <>
                      {/* --------------------------------------
                          RAW PRS
                          -------------------------------------- */}

                      <div className="result-section">
                        <h4>
                          Raw PRS
                        </h4>

                        <p>
                          {prs.prs !== undefined
                            ? prs.prs
                            : "Not available"}
                        </p>
                      </div>

                      {/* --------------------------------------
                          SCORE 100
                          -------------------------------------- */}

                      <div className="result-section">
                        <h4>
                          Score 100
                        </h4>

                        <p>
                          {prs.score_100 !==
                            null &&
                          prs.score_100 !==
                            undefined
                            ? prs.score_100
                            : "Not available"}
                        </p>

                        <p>
                          Status:{" "}
                          {prs.score_100_status ||
                            "Not specified"}
                        </p>

                        <p>
                          Reference:{" "}
                          {prs.score_100_reference ||
                            "Not specified"}
                        </p>
                      </div>

                      {/* --------------------------------------
                          MODEL
                          -------------------------------------- */}

                      <div className="result-section">
                        <h4>
                          Model
                        </h4>

                        <p>
                          PGS ID:{" "}
                          {prs.pgs_id}
                        </p>

                        <p>
                          Genome build:{" "}
                          {prs.genome_build ||
                            "Not specified"}
                        </p>
                      </div>

                      {/* --------------------------------------
                          QC
                          -------------------------------------- */}

                      {hasQc && prs.qc && (
                        <div className="result-section">
                          <h4>
                            Quality Control
                          </h4>

                          <p>
                            Matched variants:{" "}
                            {
                              prs.qc
                                .matched_variants
                            }{" "}
                            /{" "}
                            {
                              prs.qc
                                .total_model_variants
                            }
                          </p>

                          <p>
                            Coverage:{" "}
                            {coveragePercent}%
                          </p>

                          <p>
                            Aligned variants:{" "}
                            {
                              prs.qc
                                .aligned_variants
                            }
                          </p>

                          <p>
                            Alignment rate:{" "}
                            {alignmentPercent}%
                          </p>

                          <p>
                            Missing variants:{" "}
                            {
                              prs.qc
                                .missing_variants
                            }
                          </p>

                          <p>
                            QC status:{" "}
                            {prs.qc.status}
                          </p>
                        </div>
                      )}

                      {/* --------------------------------------
                          DEVELOPMENT NOTICE
                          -------------------------------------- */}

                      {prs.score_100_status ===
                        "DEVELOPMENT_ONLY" && (
                        <div className="patient-friendly">
                          <h4>
                            Development notice
                          </h4>

                          <p>
                            The normalized 0–100
                            score currently uses
                            synthetic reference
                            data and is for
                            development/testing
                            only. The raw PRS and
                            QC values above are the
                            calculated outputs.
                          </p>
                        </div>
                      )}
                    </>
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