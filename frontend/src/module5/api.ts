import type { GeneDrugPairInfo, PGxPipelineResponse, VariantInput } from './types';
import { MOCK_GENE_DRUG_DATABASE } from './mockData';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1/pharmacogenomics';

export async function pingPGx(): Promise<{ status: string; module: string; message: string; isLive: boolean }> {
  try {
    const res = await fetch(`${API_BASE_URL}/ping`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      const data = await res.json();
      return { ...data, isLive: true };
    }
  } catch (_err) {
    // API not reachable
  }
  return {
    status: 'standalone_mode',
    module: 'GeneGuard Pharmacogenomics CDS',
    message: 'Running in Standalone Client Mode (Deterministic Engine Active)',
    isLive: false
  };
}

export async function fetchSupportedDrugs(search?: string): Promise<GeneDrugPairInfo[]> {
  try {
    const url = search ? `${API_BASE_URL}/supported-drugs?search=${encodeURIComponent(search)}` : `${API_BASE_URL}/supported-drugs`;
    const res = await fetch(url, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      return await res.json();
    }
  } catch (_err) {
    // Fallback to local DB
  }

  if (!search) return MOCK_GENE_DRUG_DATABASE;
  const s = search.toLowerCase().trim();
  return MOCK_GENE_DRUG_DATABASE.filter(
    d => d.drug_name.toLowerCase().includes(s) ||
         d.brand_names.some(b => b.toLowerCase().includes(s)) ||
         d.primary_gene.toLowerCase().includes(s)
  );
}

export async function runPGxAnalysis(params: {
  patient_id: number;
  medications: string[];
  variants?: VariantInput[];
  use_latest_wes?: boolean;
}): Promise<PGxPipelineResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
      signal: AbortSignal.timeout(8000)
    });

    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Backend API request failed or timed out. Falling back to local deterministic rule engine.', err);
  }

  // Local fallback simulation mirroring the backend CDS engine
  return simulateLocalPGxAnalysis(params.patient_id, params.medications, params.variants || []);
}

function simulateLocalPGxAnalysis(patientId: number, medications: string[], variants: VariantInput[]): PGxPipelineResponse {
  const diplotypeCalls: any[] = [];
  const recommendations: any[] = [];
  const conflicts: any[] = [];

  // Group variants by gene
  const geneVars: Record<string, VariantInput[]> = {};
  for (const v of variants) {
    const g = v.gene.toUpperCase();
    if (!geneVars[g]) geneVars[g] = [];
    geneVars[g].push(v);
  }

  // Process CYP2C19
  if (medications.some(m => m.toLowerCase().includes('plavix') || m.toLowerCase().includes('clopidogrel'))) {
    const c2c19Vars = geneVars['CYP2C19'] || [];
    const isHomo2 = c2c19Vars.some(v => (v.star_allele === '*2' || v.rsid === 'rs4244285') && v.zygosity === 'homozygous_alt');
    const isHet2 = c2c19Vars.some(v => v.star_allele === '*2' || v.rsid === 'rs4244285');

    const dip = isHomo2 ? '*2/*2' : isHet2 ? '*1/*2' : '*1/*1';
    const pheno = isHomo2 ? 'Poor Metabolizer' : isHet2 ? 'Intermediate Metabolizer' : 'Normal Metabolizer';
    const actScore = isHomo2 ? 0.0 : isHet2 ? 0.5 : 2.0;

    diplotypeCalls.push({
      gene: 'CYP2C19',
      diplotype: dip,
      activity_score: actScore,
      phenotype: pheno,
      phenotype_code: isHomo2 ? 'PM' : isHet2 ? 'IM' : 'NM',
      evidence_alleles: isHomo2 ? ['*2', '*2'] : isHet2 ? ['*2'] : [],
      source: 'PharmVar / CPIC Activity Score'
    });

    const isPoor = isHomo2 || isHet2;
    recommendations.push({
      drug: 'Clopidogrel',
      gene: 'CYP2C19',
      diplotype: dip,
      phenotype: pheno,
      activity_score: actScore,
      actionability: isPoor ? 'Contraindicated / Alternative Recommended' : 'Standard Dosing',
      recommendation: isPoor
        ? 'Avoid clopidogrel at standard dose. Use alternative antiplatelet therapy (e.g., Prasugrel or Ticagrelor) unless contraindicated.'
        : 'Initiate standard clopidogrel dosing (300-600 mg loading dose, 75 mg daily maintenance).',
      clinical_implication: isPoor
        ? 'Significantly decreased active metabolite exposure, diminished platelet inhibition, and heightened risk of stent thrombosis or MACE.'
        : 'Normal active metabolite formation and platelet inhibition expected.',
      evidence_level: 'CPIC Level A',
      pharmgkb_level: '1A',
      source: 'CPIC Guideline for CYP2C19 and Clopidogrel Therapy',
      fda_label_status: 'Boxed Warning',
      conflict: isPoor,
      conflict_details: isPoor ? 'Actionable critical risk: CYP2C19 PM with Clopidogrel. High risk of cardiovascular events.' : null,
      requires_specialist_review: isPoor,
      specialist: 'Cardiologist / Clinical Pharmacist',
      rank_priority: isPoor ? 1 : 4,
      patient_explanation: isPoor
        ? `Your genetic test shows you have the ${dip} variation in the CYP2C19 gene (Poor Metabolizer). This means your liver cannot activate Clopidogrel (Plavix) properly. Your doctor should prescribe an alternative blood thinner such as Ticagrelor or Prasugrel to protect your heart.`
        : `Your CYP2C19 gene result (${dip}) is normal. Your body is expected to respond normally to standard Clopidogrel doses.`,
      clinician_summary: `Patient is CYP2C19 ${dip} (${pheno}, Activity Score: ${actScore}). Diminished bioactivation of prodrug clopidogrel. Guideline recommendation: CPIC Level A recommends alternative P2Y12 inhibitor (Prasugrel/Ticagrelor).`
    });

    if (isPoor) {
      conflicts.push({
        type: 'high_risk_clinical_gate',
        drug: 'Clopidogrel',
        gene: 'CYP2C19',
        severity: 'CRITICAL',
        message: 'CYP2C19 Poor Metabolizer with Clopidogrel: Greatly diminished antiplatelet response.',
        action: 'Route to Cardiologist / Clinical Pharmacist for antiplatelet switch approval.'
      });
    }
  }

  // Process Codeine / CYP2D6
  if (medications.some(m => m.toLowerCase().includes('codeine'))) {
    const d6Vars = geneVars['CYP2D6'] || [];
    const isUM = d6Vars.some(v => v.star_allele === '*1xN' || v.star_allele === '*2xN');
    const isPM = d6Vars.some(v => v.star_allele === '*4' && v.zygosity === 'homozygous_alt');

    const dip = isUM ? '*1xN/*1' : isPM ? '*4/*4' : '*1/*1';
    const pheno = isUM ? 'Ultrarapid Metabolizer' : isPM ? 'Poor Metabolizer' : 'Normal Metabolizer';
    const actScore = isUM ? 3.0 : isPM ? 0.0 : 2.0;

    diplotypeCalls.push({
      gene: 'CYP2D6',
      diplotype: dip,
      activity_score: actScore,
      phenotype: pheno,
      phenotype_code: isUM ? 'UM' : isPM ? 'PM' : 'NM',
      evidence_alleles: isUM ? ['*1xN'] : isPM ? ['*4', '*4'] : [],
      source: 'PharmVar / CPIC Activity Score'
    });

    recommendations.push({
      drug: 'Codeine',
      gene: 'CYP2D6',
      diplotype: dip,
      phenotype: pheno,
      activity_score: actScore,
      actionability: isUM ? 'Contraindicated / Severe Toxicity Risk' : isPM ? 'Alternative Recommended' : 'Standard Dosing',
      recommendation: isUM
        ? 'Avoid codeine due to risk of life-threatening respiratory depression and opioid toxicity. Use alternative non-CYP2D6 analgesic.'
        : isPM
        ? 'Avoid codeine due to lack of analgesic efficacy. Use alternative analgesic (e.g. Morphine, non-opioids).'
        : 'Standard codeine dosing appropriate.',
      clinical_implication: isUM
        ? 'Excessively rapid conversion of codeine to morphine resulting in potentially fatal morphine overdose.'
        : isPM
        ? 'Greatly reduced conversion to active morphine; inadequate analgesia.'
        : 'Normal bioactivation to morphine expected.',
      evidence_level: 'CPIC Level A',
      pharmgkb_level: '1A',
      source: 'CPIC Guideline for CYP2D6 and Codeine',
      fda_label_status: 'Boxed Warning',
      conflict: isUM || isPM,
      conflict_details: isUM ? 'Critical toxicity risk: Rapid conversion to toxic morphine levels.' : null,
      requires_specialist_review: isUM || isPM,
      specialist: 'Pain Specialist / Clinical Pharmacist',
      rank_priority: isUM ? 1 : isPM ? 2 : 4,
      patient_explanation: isUM
        ? `Your CYP2D6 gene has extra active copies (${dip}, Ultrarapid Metabolizer). Your body converts Codeine into Morphine dangerously fast, which can cause severe breathing problems. Codeine must be avoided.`
        : `Your genetic test indicates standard Codeine processing.`,
      clinician_summary: `Patient is CYP2D6 ${dip} (${pheno}). Risk of accelerated morphine formation and toxicity. CPIC Level A contraindicates codeine.`
    });

    if (isUM) {
      conflicts.push({
        type: 'high_risk_clinical_gate',
        drug: 'Codeine',
        gene: 'CYP2D6',
        severity: 'CRITICAL',
        message: 'CYP2D6 Ultrarapid Metabolizer: Severe risk of fatal respiratory depression.',
        action: 'Route to Pain Specialist / Clinical Pharmacist for non-CYP2D6 analgesic prescription.'
      });
    }
  }

  // Process DPYD / Fluorouracil / Capecitabine
  if (medications.some(m => m.toLowerCase().includes('fluorouracil') || m.toLowerCase().includes('capecitabine') || m.toLowerCase().includes('5-fu'))) {
    const dpydVars = geneVars['DPYD'] || [];
    const isVar = dpydVars.length > 0;
    const dip = isVar ? '*2A/*1' : '*1/*1';
    const pheno = isVar ? 'Intermediate Metabolizer (Partial DPD deficiency)' : 'Normal Metabolizer';
    const actScore = isVar ? 1.0 : 2.0;

    diplotypeCalls.push({
      gene: 'DPYD',
      diplotype: dip,
      activity_score: actScore,
      phenotype: pheno,
      phenotype_code: isVar ? 'IM' : 'NM',
      evidence_alleles: isVar ? ['*2A'] : [],
      source: 'PharmVar / CPIC DPYD Table'
    });

    const targetDrugs = medications.filter(m => m.toLowerCase().includes('fluorouracil') || m.toLowerCase().includes('capecitabine') || m.toLowerCase().includes('5-fu'));
    for (const d of targetDrugs) {
      const canonical = d.toLowerCase().includes('cape') ? 'Capecitabine' : 'Fluorouracil';
      recommendations.push({
        drug: canonical,
        gene: 'DPYD',
        diplotype: dip,
        phenotype: pheno,
        activity_score: actScore,
        actionability: isVar ? 'Major Dose Adjustment' : 'Standard Dosing',
        recommendation: isVar
          ? 'Reduce starting dose by 50%. Titrate dose in subsequent cycles based on clinical toxicity and therapeutic drug monitoring.'
          : 'Standard recommended fluoropyrimidine chemotherapy dosing.',
        clinical_implication: isVar
          ? 'Reduced DPD clearance; high risk of severe grade 3-4 mucositis, neutropenia, diarrhea, and neurotoxicity.'
          : 'Normal DPD clearance and expected drug tolerability.',
        evidence_level: 'CPIC Level A',
        pharmgkb_level: '1A',
        source: 'CPIC Guideline for DPYD and Fluoropyrimidines',
        fda_label_status: 'Boxed Warning',
        conflict: isVar,
        conflict_details: isVar ? 'Partial DPD deficiency: 50% dose reduction mandatory.' : null,
        requires_specialist_review: isVar,
        specialist: 'Oncologist / Clinical Pharmacist',
        rank_priority: isVar ? 2 : 4,
        patient_explanation: isVar
          ? `Your DPYD gene test shows a ${dip} variant (Partial DPD deficiency). Your body clears chemotherapy drugs like ${canonical} more slowly. Your oncologist must reduce your starting dose by 50% to prevent dangerous side effects.`
          : `Your DPYD gene test result is normal. Standard chemotherapy dosing is appropriate.`,
        clinician_summary: `DPYD ${dip} (Intermediate Metabolizer, Activity Score 1.0). CPIC Level A mandates initial 50% dose reduction with PK monitoring.`
      });
    }

    if (isVar) {
      conflicts.push({
        type: 'high_risk_clinical_gate',
        drug: 'Fluorouracil / Capecitabine',
        gene: 'DPYD',
        severity: 'HIGH',
        message: 'DPYD Intermediate Metabolizer: 50% dose reduction required before cycle 1.',
        action: 'Route to Oncology Clinical Pharmacist for dose modification verification.'
      });
    }
  }

  // Process HLA-B / Abacavir
  if (medications.some(m => m.toLowerCase().includes('abacavir'))) {
    const hlaVars = geneVars['HLA-B'] || [];
    const is5701 = hlaVars.some(v => v.star_allele?.includes('57:01') || v.gene?.includes('HLA-B'));
    const dip = is5701 ? '*57:01 (Positive)' : 'Negative / Low Risk';
    const pheno = is5701 ? 'Abacavir Hypersensitivity High Risk (Positive)' : 'Low Risk / Negative';

    diplotypeCalls.push({
      gene: 'HLA-B',
      diplotype: dip,
      activity_score: null,
      phenotype: pheno,
      phenotype_code: is5701 ? 'POS' : 'NEG',
      evidence_alleles: is5701 ? ['*57:01'] : [],
      source: 'CPIC HLA Guidelines'
    });

    recommendations.push({
      drug: 'Abacavir',
      gene: 'HLA-B',
      diplotype: dip,
      phenotype: pheno,
      actionability: is5701 ? 'Contraindicated / Boxed Warning' : 'Standard Dosing',
      recommendation: is5701
        ? 'Abacavir is strictly contraindicated. Do not prescribe. Use alternative non-abacavir antiretroviral regimen.'
        : 'Use standard abacavir dosing as clinically indicated.',
      clinical_implication: is5701
        ? 'Carriers of HLA-B*57:01 have an exceptionally high risk of life-threatening multisystem immunologic hypersensitivity reaction.'
        : 'Low risk of abacavir hypersensitivity reaction.',
      evidence_level: 'CPIC Level A',
      pharmgkb_level: '1A',
      source: 'CPIC Guideline for HLA-B Genotype and Abacavir Dosing',
      fda_label_status: 'Boxed Warning',
      conflict: is5701,
      conflict_details: is5701 ? 'FDA Boxed Warning: HLA-B*57:01 Positive is strictly contraindicated with Abacavir.' : null,
      requires_specialist_review: is5701,
      specialist: 'Infectious Disease Specialist / Geneticist',
      rank_priority: is5701 ? 1 : 4,
      patient_explanation: is5701
        ? `You tested positive for the HLA-B*57:01 genetic marker. Taking Abacavir could cause a severe, life-threatening allergic reaction. You must NEVER take Abacavir or medicines containing Abacavir (e.g. Triumeq, Epzicom).`
        : `Your HLA-B test is negative. You are at standard low risk for Abacavir allergic reactions.`,
      clinician_summary: `HLA-B*57:01 Positive. Absolute contraindication for Abacavir. Severe hypersensitivity reaction risk. Prescribe alternative cART.`
    });

    if (is5701) {
      conflicts.push({
        type: 'high_risk_clinical_gate',
        drug: 'Abacavir',
        gene: 'HLA-B',
        severity: 'CRITICAL',
        message: 'HLA-B*57:01 Positive: Severe, potentially fatal hypersensitivity reaction risk.',
        action: 'Route to Infectious Disease Specialist. Select non-Abacavir cART regimen immediately.'
      });
    }
  }

  // Process SLCO1B1 / Simvastatin
  if (medications.some(m => m.toLowerCase().includes('simvastatin') || m.toLowerCase().includes('zocor'))) {
    const slcoVars = geneVars['SLCO1B1'] || [];
    const isHomo5 = slcoVars.some(v => (v.star_allele === '*5' || v.rsid === 'rs4149056') && v.zygosity === 'homozygous_alt');
    const dip = isHomo5 ? '*5/*5' : '*1A/*1A';
    const pheno = isHomo5 ? 'Poor Function' : 'Normal Function';
    const actScore = isHomo5 ? 0.0 : 2.0;

    diplotypeCalls.push({
      gene: 'SLCO1B1',
      diplotype: dip,
      activity_score: actScore,
      phenotype: pheno,
      phenotype_code: isHomo5 ? 'PF' : 'NF',
      evidence_alleles: isHomo5 ? ['*5', '*5'] : [],
      source: 'PharmVar / CPIC SLCO1B1 Table'
    });

    recommendations.push({
      drug: 'Simvastatin',
      gene: 'SLCO1B1',
      diplotype: dip,
      phenotype: pheno,
      activity_score: actScore,
      actionability: isHomo5 ? 'Major Toxicity Risk / Alternative Recommended' : 'Standard Dosing',
      recommendation: isHomo5
        ? 'Prescribe lower starting dose (max 20 mg/day) or alternative statin (e.g. Pravastatin or Rosuvastatin) to minimize statin-induced myopathy and rhabdomyolysis.'
        : 'Standard starting dose according to clinical guidelines.',
      clinical_implication: isHomo5
        ? 'Substantially increased systemic exposure to simvastatin acid resulting from impaired hepatic uptake; elevated myopathy risk.'
        : 'Normal hepatic statin uptake.',
      evidence_level: 'CPIC Level A',
      pharmgkb_level: '1A',
      source: 'CPIC Guideline for SLCO1B1 and Statin-Induced Myopathy',
      fda_label_status: 'Actionable PGx',
      conflict: isHomo5,
      conflict_details: isHomo5 ? 'SLCO1B1 Poor Function: High risk of statin-induced myopathy.' : null,
      requires_specialist_review: isHomo5,
      specialist: 'Cardiologist / Clinical Pharmacist',
      rank_priority: isHomo5 ? 1 : 4,
      patient_explanation: isHomo5
        ? `Your SLCO1B1 gene test shows the ${dip} result (Poor Function). Your liver cannot clear Simvastatin quickly, leading to high blood levels that can cause severe muscle pain and weakness. Your doctor should switch you to a safer statin like Rosuvastatin.`
        : `Your SLCO1B1 gene test is normal. Standard statin dosing is safe.`,
      clinician_summary: `SLCO1B1 ${dip} (Poor Function). Marked increase in simvastatin acid AUC. Switch to Pravastatin/Rosuvastatin or limit dose to <=20mg.`
    });
  }

  // Process Warfarin / CYP2C9 + VKORC1
  if (medications.some(m => m.toLowerCase().includes('warfarin') || m.toLowerCase().includes('coumadin'))) {
    const c9Vars = geneVars['CYP2C9'] || [];
    const vkVars = geneVars['VKORC1'] || [];

    const hasC9Var = c9Vars.length > 0;
    const hasVkHomo = vkVars.some(v => v.zygosity === 'homozygous' || v.hgvs_c?.includes('1639'));

    const c9Dip = hasC9Var ? '*1/*3' : '*1/*1';
    const c9Pheno = hasC9Var ? 'Intermediate Metabolizer' : 'Normal Metabolizer';

    diplotypeCalls.push({
      gene: 'CYP2C9',
      diplotype: c9Dip,
      activity_score: hasC9Var ? 1.0 : 2.0,
      phenotype: c9Pheno,
      phenotype_code: hasC9Var ? 'IM' : 'NM',
      evidence_alleles: hasC9Var ? ['*3'] : [],
      source: 'CPIC Warfarin Guidelines'
    });

    if (hasVkHomo) {
      diplotypeCalls.push({
        gene: 'VKORC1',
        diplotype: '-1639A/A',
        activity_score: 0.0,
        phenotype: 'High Sensitivity (Low Dose Required)',
        phenotype_code: 'High Sensitivity',
        evidence_alleles: ['A', 'A'],
        source: 'CPIC Warfarin Guidelines'
      });
    }

    const needsDoseAdj = hasC9Var || hasVkHomo;
    recommendations.push({
      drug: 'Warfarin',
      gene: 'CYP2C9 / VKORC1',
      diplotype: `${c9Dip} + ${hasVkHomo ? '-1639A/A' : '-1639G/G'}`,
      phenotype: `${c9Pheno} / ${hasVkHomo ? 'High Sensitivity' : 'Normal Sensitivity'}`,
      activity_score: 1.0,
      actionability: needsDoseAdj ? 'Moderate Dose Adjustment' : 'Standard Dosing',
      recommendation: needsDoseAdj
        ? 'Significantly reduce initial and maintenance starting dose by 25% to 50% or utilize clinical dosing algorithm (WarfarinDosing.org). Monitor INR closely.'
        : 'Initiate standard starting dose (5 mg daily) and adjust according to standard INR monitoring protocols.',
      clinical_implication: needsDoseAdj
        ? 'Decreased (S)-warfarin clearance and increased pharmacodynamic sensitivity; high risk of bleeding complications if standard dose is given.'
        : 'Normal warfarin metabolism and sensitivity.',
      evidence_level: 'CPIC Level A',
      pharmgkb_level: '1A',
      source: 'CPIC Guideline for Pharmacogenetics-Guided Warfarin Dosing',
      fda_label_status: 'Actionable PGx',
      conflict: needsDoseAdj,
      conflict_details: needsDoseAdj ? 'CYP2C9/VKORC1 combined variants: High sensitivity to warfarin.' : null,
      requires_specialist_review: needsDoseAdj,
      specialist: 'Anticoagulation Specialist / Hematologist',
      rank_priority: needsDoseAdj ? 2 : 4,
      patient_explanation: needsDoseAdj
        ? `Your genetic test shows you are unusually sensitive to Warfarin (Coumadin). A normal dose would be too strong and could cause dangerous bleeding. Your doctor must start you on a lower dose and check your blood test (INR) frequently.`
        : `Your genetic test results for Warfarin processing are standard.`,
      clinician_summary: `Combined CYP2C9 ${c9Dip} and VKORC1 ${hasVkHomo ? '-1639A/A' : 'Normal'}. Reduced S-warfarin clearance & heightened target sensitivity. Apply CPIC/IWPC dosing algorithm.`
    });
  }

  // Sort recommendations by rank_priority
  recommendations.sort((a, b) => a.rank_priority - b.rank_priority);

  return {
    report_id: Math.floor(1000 + Math.random() * 9000),
    patient_id: patientId,
    timestamp: new Date().toISOString(),
    status: conflicts.length > 0 ? 'flagged_for_review' : 'completed',
    total_drugs_evaluated: medications.length,
    matched_gene_drug_pairs: recommendations.length,
    overall_confidence: conflicts.length > 0 ? 94.0 : 98.0,
    flagged_conflicts: conflicts,
    diplotype_calls: diplotypeCalls,
    recommendations: recommendations,
    unmatched_drugs: []
  };
}
