import { useState } from 'react'
import './App.css'

interface FamilyHistoryEntry {
  relationship: string
  sex: string
  health_status: string
  condition: string
  known_variant: string
}

interface RiskResult {
  gene: string
  condition: string
  inheritance: string
  parent1_status: string
  parent2_status: string
  affected_probability: number
  carrier_probability: number
  unaffected_probability: number
  evidence_sources: string[]
  explanation: string
}

interface AssessmentResult {
  assessment_id?: string | null
  status?: string
  risks?: RiskResult[]
  shared_risk_count?: number
  uncertain_variant_count?: number
  compound_heterozygous_candidates?: unknown[]
  consanguinity_context?: string
  family_history_context?: string[]
  limitations?: string[]
}

function App() {
  const [parent1File, setParent1File] = useState<File | null>(null)
  const [parent2File, setParent2File] = useState<File | null>(null)

  const [relationship, setRelationship] = useState('unknown')

  const [familyHistory, setFamilyHistory] = useState<
    FamilyHistoryEntry[]
  >([])

  const [familyMember, setFamilyMember] = useState('')
  const [familySex, setFamilySex] = useState('')
  const [familyHealthStatus, setFamilyHealthStatus] = useState('')
  const [familyCondition, setFamilyCondition] = useState('')
  const [familyKnownVariant, setFamilyKnownVariant] = useState('')

  const [showFamilyForm, setShowFamilyForm] = useState(false)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [result, setResult] =
    useState<AssessmentResult | null>(null)

  /* =========================================
     Family History
     ========================================= */

  const addFamilyHistory = () => {
    if (!familyMember || !familyHealthStatus) {
      return
    }

    const entry: FamilyHistoryEntry = {
      relationship: familyMember,
      sex: familySex,
      health_status: familyHealthStatus,
      condition: familyCondition,
      known_variant: familyKnownVariant,
    }

    setFamilyHistory((previous) => [
      ...previous,
      entry,
    ])

    setFamilyMember('')
    setFamilySex('')
    setFamilyHealthStatus('')
    setFamilyCondition('')
    setFamilyKnownVariant('')

    setShowFamilyForm(false)
  }

  /* =========================================
     Analyze Module 4
     ========================================= */

  const handleAnalyze = async () => {
    if (!parent1File || !parent2File) {
      setError(
        'Please upload both Parent 1 and Parent 2 VCF files.'
      )
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const formData = new FormData()

      formData.append(
        'parent1_vcf',
        parent1File
      )

      formData.append(
        'parent2_vcf',
        parent2File
      )

      formData.append(
        'relationship',
        relationship
      )

      formData.append(
        'family_history',
        JSON.stringify(familyHistory)
      )

      const response = await fetch(
        '/api/v1/consanguinity/assess-vcf',
        {
          method: 'POST',
          body: formData,
        }
      )

      const data = await response.json()

      if (!response.ok) {
        const message =
          data?.detail ||
          'Genetic risk assessment failed.'

        throw new Error(message)
      }

      setResult(data)
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError(
          'An unexpected error occurred.'
        )
      }
    } finally {
      setLoading(false)
    }
  }

  /* =========================================
     Render
     ========================================= */

  return (
    <div className="app">

      {/* =====================================
          Header
          ===================================== */}

      <header className="header">

        <div className="brand">

          <div className="brand-icon">
            G
          </div>

          <div>
            <h1>
              GeneGuard-AI
            </h1>

            <p>
              Precision Genetic Healthcare
            </p>
          </div>

        </div>

        <div className="module-badge">
          Module 4
        </div>

      </header>


      {/* =====================================
          Main
          ===================================== */}

      <main className="main-container">

        {/* ===================================
            Page Heading
            =================================== */}

        <section className="page-heading">

          <span className="eyebrow">
            CONSANGUINITY &amp; RISK ASSESSMENT
          </span>

          <h2>
            Offspring Genetic Risk
            <span> Assessment</span>
          </h2>

          <p>
            Assess potential genetic risks in offspring
            using parental genetic data, inheritance
            patterns, consanguinity context, and family
            history.
          </p>

        </section>


        {/* ===================================
            1. Parental Genetic Data
            =================================== */}

        <section className="card">

          <div className="section-header">

            <div>

              <h3>
                1. Parental Genetic Data
              </h3>

              <p>
                Upload the genetic variant files
                for both parents.
              </p>

            </div>

          </div>


          <div className="parent-grid">

            {/* Parent 1 */}

            <div className="upload-card">

              <div className="parent-title">

                <div className="parent-number">
                  01
                </div>

                <div>

                  <h4>
                    Parent 1
                  </h4>

                  <p>
                    VCF genetic variant file
                  </p>

                </div>

              </div>


              <label className="upload-area">

                <input
                  type="file"
                  accept=".vcf,.vcf.gz"
                  onChange={(event) =>
                    setParent1File(
                      event.target.files?.[0] ||
                      null
                    )
                  }
                />

                <div className="upload-icon">
                  ↑
                </div>


                {parent1File ? (
                  <>
                    <strong>
                      {parent1File.name}
                    </strong>

                    <span>
                      File selected
                    </span>
                  </>
                ) : (
                  <>
                    <strong>
                      Upload Parent 1 VCF
                    </strong>

                    <span>
                      Click to browse or select
                      a .vcf file
                    </span>
                  </>
                )}

              </label>

            </div>


            {/* Parent 2 */}

            <div className="upload-card">

              <div className="parent-title">

                <div className="parent-number">
                  02
                </div>

                <div>

                  <h4>
                    Parent 2
                  </h4>

                  <p>
                    VCF genetic variant file
                  </p>

                </div>

              </div>


              <label className="upload-area">

                <input
                  type="file"
                  accept=".vcf,.vcf.gz"
                  onChange={(event) =>
                    setParent2File(
                      event.target.files?.[0] ||
                      null
                    )
                  }
                />

                <div className="upload-icon">
                  ↑
                </div>


                {parent2File ? (
                  <>
                    <strong>
                      {parent2File.name}
                    </strong>

                    <span>
                      File selected
                    </span>
                  </>
                ) : (
                  <>
                    <strong>
                      Upload Parent 2 VCF
                    </strong>

                    <span>
                      Click to browse or select
                      a .vcf file
                    </span>
                  </>
                )}

              </label>

            </div>

          </div>

        </section>


        {/* ===================================
            2. Consanguinity
            =================================== */}

        <section className="card">

          <div className="section-header">

            <div>

              <h3>
                2. Family &amp; Consanguinity Context
              </h3>

              <p>
                Provide relationship information to
                improve contextual risk interpretation.
              </p>

            </div>

          </div>


          <div className="form-grid">

            <div className="form-group">

              <label htmlFor="relationship">
                Relationship between parents
              </label>

              <select
                id="relationship"
                value={relationship}
                onChange={(event) =>
                  setRelationship(
                    event.target.value
                  )
                }
              >

                <option value="unknown">
                  Unknown
                </option>

                <option value="unrelated">
                  Unrelated
                </option>

                <option value="first_cousin">
                  First Cousins
                </option>

                <option value="second_cousin">
                  Second Cousins
                </option>

                <option value="other">
                  Other
                </option>

              </select>

            </div>

          </div>


          <div className="info-box">

            <div className="info-icon">
              i
            </div>

            <div>

              <strong>
                Important
              </strong>

              <p>
                Consanguinity is treated as contextual
                information. It is not applied as a
                fixed genetic risk multiplier.
              </p>

            </div>

          </div>

        </section>


        {/* ===================================
            3. Family History
            =================================== */}

        <section className="card">

          <div className="section-header">

            <div>

              <h3>
                3. Family History
              </h3>

              <p>
                Add known inherited conditions or
                relevant family history.
              </p>

            </div>

          </div>


          <div className="family-history-content">

            {/* Empty state */}

            {familyHistory.length === 0 &&
              !showFamilyForm && (

                <div className="family-history-empty">

                  <div className="placeholder-icon">
                    +
                  </div>

                  <div>

                    <strong>
                      Add Family History
                    </strong>

                    <p>
                      Add known inherited conditions
                      or relevant family history.
                    </p>

                  </div>

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() =>
                      setShowFamilyForm(true)
                    }
                  >
                    Add Entry
                  </button>

                </div>

              )}


            {/* Existing entries */}

            {familyHistory.map(
              (entry, index) => (

                <div
                  className="family-entry"
                  key={index}
                >

                  <div className="family-entry-number">
                    {index + 1}
                  </div>

                  <div className="family-entry-info">

                    <strong>
                      {entry.relationship}
                    </strong>

                    <p>
                      {entry.sex ||
                        'Sex not specified'}
                      {' · '}
                      {entry.health_status}
                    </p>

                    {entry.condition && (
                      <p>
                        Condition:{' '}
                        {entry.condition}
                      </p>
                    )}

                    {entry.known_variant && (
                      <p>
                        Known variant:{' '}
                        {entry.known_variant}
                      </p>
                    )}

                  </div>

                </div>

              )
            )}


            {/* Add another */}

            {familyHistory.length > 0 &&
              !showFamilyForm && (

                <button
                  type="button"
                  className="secondary-button add-another-button"
                  onClick={() =>
                    setShowFamilyForm(true)
                  }
                >
                  + Add Another
                </button>

              )}


            {/* Family history form */}

            {showFamilyForm && (

              <div className="family-form">

                <div className="family-form-grid">

                  {/* Relation */}

                  <div className="form-group">

                    <label>
                      Family Member / Relation
                    </label>

                    <input
                      type="text"
                      placeholder="e.g. Sibling, parent, uncle"
                      value={familyMember}
                      onChange={(event) =>
                        setFamilyMember(
                          event.target.value
                        )
                      }
                    />

                  </div>


                  {/* Sex */}

                  <div className="form-group">

                    <label>
                      Sex
                    </label>

                    <select
                      value={familySex}
                      onChange={(event) =>
                        setFamilySex(
                          event.target.value
                        )
                      }
                    >

                      <option value="">
                        Not specified
                      </option>

                      <option value="male">
                        Male
                      </option>

                      <option value="female">
                        Female
                      </option>

                      <option value="unknown">
                        Unknown
                      </option>

                    </select>

                  </div>


                  {/* Health status */}

                  <div className="form-group">

                    <label>
                      Health Status
                    </label>

                    <select
                      value={familyHealthStatus}
                      onChange={(event) =>
                        setFamilyHealthStatus(
                          event.target.value
                        )
                      }
                    >

                      <option value="">
                        Select status
                      </option>

                      <option value="affected">
                        Affected
                      </option>

                      <option value="carrier">
                        Carrier
                      </option>

                      <option value="unaffected">
                        Unaffected
                      </option>

                      <option value="unknown">
                        Unknown
                      </option>

                    </select>

                  </div>


                  {/* Condition */}

                  <div className="form-group">

                    <label>
                      Condition
                    </label>

                    <input
                      type="text"
                      placeholder="e.g. Cystic fibrosis"
                      value={familyCondition}
                      onChange={(event) =>
                        setFamilyCondition(
                          event.target.value
                        )
                      }
                    />

                  </div>


                  {/* Known variant */}

                  <div className="form-group family-form-wide">

                    <label>
                      Known Variant
                    </label>

                    <input
                      type="text"
                      placeholder="e.g. CFTR variant or gene"
                      value={familyKnownVariant}
                      onChange={(event) =>
                        setFamilyKnownVariant(
                          event.target.value
                        )
                      }
                    />

                  </div>

                </div>


                {/* Form actions */}

                <div className="family-form-actions">

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() =>
                      setShowFamilyForm(false)
                    }
                  >
                    Cancel
                  </button>

                  <button
                    type="button"
                    className="primary-small-button"
                    onClick={addFamilyHistory}
                    disabled={
                      !familyMember ||
                      !familyHealthStatus
                    }
                  >
                    Add Family History
                  </button>

                </div>

              </div>

            )}

          </div>

        </section>


        {/* ===================================
            Error
            =================================== */}

        {error && (

          <div className="error-box">

            <strong>
              Assessment Error
            </strong>

            <p>
              {error}
            </p>

          </div>

        )}


        {/* ===================================
            Analyze
            =================================== */}

        <section className="action-section">

          <button
            type="button"
            className="analyze-button"
            disabled={
              !parent1File ||
              !parent2File ||
              loading
            }
            onClick={handleAnalyze}
          >

            {loading
              ? 'Analyzing...'
              : 'Analyze Genetic Risk'}

            {!loading && (
              <span>
                →
              </span>
            )}

          </button>


          <p>
            Both parent VCF files are required
            to perform the assessment.
          </p>

        </section>


        {/* ===================================
            Results Dashboard
            =================================== */}

        {result && (

          <section className="results-section">

            {/* Results header */}

            <div className="results-header">

              <div>

                <span className="eyebrow">
                  ANALYSIS COMPLETE
                </span>

                <h3>
                  Offspring Genetic Risk Assessment
                </h3>

                <p>
                  Potential inherited risks identified
                  from the parental genetic data.
                </p>

              </div>


              <div className="status-badge">

                <span className="status-dot"></span>

                {result.status ||
                  'completed'}

              </div>

            </div>


            {/* Summary */}

            <div className="summary-grid">

              <div className="summary-card">

                <span>
                  Risk Conditions
                </span>

                <strong>
                  {result.risks?.length ?? 0}
                </strong>

                <small>
                  Conditions requiring review
                </small>

              </div>


              <div className="summary-card">

                <span>
                  Shared Risk Variants
                </span>

                <strong>
                  {result.shared_risk_count ?? 0}
                </strong>

                <small>
                  Relevant variants shared
                </small>

              </div>


              <div className="summary-card">

                <span>
                  Uncertain Variants
                </span>

                <strong>
                  {result.uncertain_variant_count ?? 0}
                </strong>

                <small>
                  Not used for definitive risk
                </small>

              </div>


              <div className="summary-card">

                <span>
                  Compound Candidates
                </span>

                <strong>
                  {result
                    .compound_heterozygous_candidates
                    ?.length ?? 0}
                </strong>

                <small>
                  Potential candidates
                </small>

              </div>

            </div>


            {/* Identified risks */}

            <div className="risk-list">

              <div className="results-subheading">

                <h4>
                  Identified Genetic Risks
                </h4>

                <p>
                  Mendelian inheritance-based
                  assessment for each relevant
                  condition.
                </p>

              </div>


              {result.risks?.map(
                (risk, index) => (

                  <div
                    className="risk-card"
                    key={`${risk.gene}-${index}`}
                  >

                    {/* Risk header */}

                    <div className="risk-card-header">

                      <div>

                        <div className="gene-label">
                          {risk.gene}
                        </div>

                        <h4>
                          {risk.condition}
                        </h4>

                      </div>


                      <div className="inheritance-badge">

                        {risk.inheritance.replaceAll(
                          '_',
                          ' '
                        )}

                      </div>

                    </div>


                    {/* Parent status */}

                    <div className="parent-status-grid">

                      <div className="parent-status">

                        <span>
                          Parent 1
                        </span>

                        <strong>
                          {risk.parent1_status}
                        </strong>

                      </div>


                      <div className="parent-status">

                        <span>
                          Parent 2
                        </span>

                        <strong>
                          {risk.parent2_status}
                        </strong>

                      </div>

                    </div>


                    {/* Probability */}

                    <div className="probability-section">

                      <h5>
                        Estimated Offspring Probability
                      </h5>


                      <div className="probability-grid">

                        <div className="probability-item affected">

                          <span>
                            Affected
                          </span>

                          <strong>
                            {(
                              risk.affected_probability *
                              100
                            ).toFixed(0)}
                            %
                          </strong>

                        </div>


                        <div className="probability-item carrier">

                          <span>
                            Carrier
                          </span>

                          <strong>
                            {(
                              risk.carrier_probability *
                              100
                            ).toFixed(0)}
                            %
                          </strong>

                        </div>


                        <div className="probability-item unaffected">

                          <span>
                            Unaffected
                          </span>

                          <strong>
                            {(
                              risk.unaffected_probability *
                              100
                            ).toFixed(0)}
                            %
                          </strong>

                        </div>

                      </div>


                      {/* Probability bar */}

                      <div className="probability-bar">

                        <div
                          className="bar-affected"
                          style={{
                            width: `${
                              risk.affected_probability *
                              100
                            }%`,
                          }}
                        />

                        <div
                          className="bar-carrier"
                          style={{
                            width: `${
                              risk.carrier_probability *
                              100
                            }%`,
                          }}
                        />

                        <div
                          className="bar-unaffected"
                          style={{
                            width: `${
                              risk.unaffected_probability *
                              100
                            }%`,
                          }}
                        />

                      </div>

                    </div>


                    {/* Evidence */}

                    <div className="evidence-section">

                      <h5>
                        Evidence Sources
                      </h5>

                      <div className="evidence-list">

                        {risk.evidence_sources.map(
                          (
                            source,
                            sourceIndex
                          ) => (

                            <span
                              key={sourceIndex}
                            >
                              {source}
                            </span>

                          )
                        )}

                      </div>

                    </div>


                    {/* Explanation */}

                    <div className="explanation-section">

                      <h5>
                        Interpretation
                      </h5>

                      <p>
                        {risk.explanation}
                      </p>

                    </div>

                  </div>

                )
              )}

            </div>


            {/* Context */}

            <div className="context-grid">

              {/* Consanguinity */}

              <div className="context-card">

                <div className="context-icon">
                  C
                </div>

                <div>

                  <h4>
                    Consanguinity Context
                  </h4>

                  <p>
                    {result.consanguinity_context ||
                      'No consanguinity information was provided.'}
                  </p>

                </div>

              </div>


              {/* Family history */}

              <div className="context-card">

                <div className="context-icon">
                  F
                </div>

                <div>

                  <h4>
                    Family History
                  </h4>


                  {result.family_history_context &&
                  result.family_history_context.length >
                    0 ? (

                    <ul>

                      {result.family_history_context.map(
                        (
                          item,
                          index
                        ) => (

                          <li key={index}>
                            {item}
                          </li>

                        )
                      )}

                    </ul>

                  ) : (

                    <p>
                      No family history entries
                      were provided.
                    </p>

                  )}

                </div>

              </div>

            </div>


            {/* Limitations */}

            <div className="limitations-card">

              <h4>
                Important Limitations
              </h4>

              <ul>

                {result.limitations?.map(
                  (
                    limitation,
                    index
                  ) => (

                    <li key={index}>
                      {limitation}
                    </li>

                  )
                )}

              </ul>

            </div>

          </section>

        )}

      </main>


      {/* =====================================
          Footer
          ===================================== */}

      <footer className="footer">

        <p>
          GeneGuard-AI · Module 4 ·
          Consanguinity &amp; Offspring Genetic
          Risk Assessment
        </p>

      </footer>

    </div>
  )
}

export default App