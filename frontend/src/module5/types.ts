export interface VariantInput {
  gene: string;
  hgvs_c?: string;
  hgvs_p?: string;
  rsid?: string;
  zygosity?: 'heterozygous' | 'homozygous_alt' | 'homozygous_ref' | string;
  star_allele?: string;
}

export interface DiplotypeCall {
  gene: string;
  diplotype: string;
  activity_score?: number | null;
  phenotype: string;
  phenotype_code?: string | null;
  evidence_alleles?: string[];
  source?: string;
}

export interface GeneDrugRecommendation {
  drug: string;
  gene: string;
  diplotype: string;
  phenotype: string;
  activity_score?: number | null;
  actionability: string;
  recommendation: string;
  clinical_implication: string;
  evidence_level: string;
  pharmgkb_level?: string | null;
  source: string;
  fda_label_status?: string | null;
  conflict: boolean;
  conflict_details?: string | null;
  requires_specialist_review: boolean;
  specialist: string;
  rank_priority: number;
  patient_explanation: string;
  clinician_summary: string;
}

export interface FlaggedConflict {
  type: string;
  drug: string;
  gene: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  message: string;
  action: string;
}

export interface PGxPipelineResponse {
  report_id?: number | null;
  patient_id: number;
  timestamp: string;
  status: 'completed' | 'flagged_for_review' | 'pending' | 'failed';
  total_drugs_evaluated: number;
  matched_gene_drug_pairs: number;
  overall_confidence: number;
  flagged_conflicts: FlaggedConflict[];
  diplotype_calls: DiplotypeCall[];
  recommendations: GeneDrugRecommendation[];
  unmatched_drugs: string[];
  full_evidence_package?: any[];
}

export interface GeneDrugPairInfo {
  drug_name: string;
  brand_names: string[];
  primary_gene: string;
  secondary_genes: string[];
  therapeutic_area: string;
  cpic_level: string;
  pharmgkb_level: string;
  fda_label_status: string;
}

export interface PatientPresetCase {
  id: string;
  title: string;
  category: string;
  patientId: number;
  patientName: string;
  age: number;
  gender: string;
  clinicalContext: string;
  medications: string[];
  variants: VariantInput[];
  expectedHighlight: string;
}
