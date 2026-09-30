import type { GeneDrugPairInfo, PatientPresetCase } from './types';

export const PATIENT_PRESET_CASES: PatientPresetCase[] = [
  {
    id: 'case_cardio_cyp2c19',
    title: 'Post-PCI Cardiology Case',
    category: 'Cardiovascular',
    patientId: 101,
    patientName: 'David Miller',
    age: 58,
    gender: 'Male',
    clinicalContext: 'Underwent coronary stent placement (PCI). Prescribed dual antiplatelet therapy with Plavix (Clopidogrel).',
    medications: ['Plavix'],
    variants: [
      {
        gene: 'CYP2C19',
        rsid: 'rs4244285',
        hgvs_c: 'c.681G>A',
        hgvs_p: 'p.Pro227=',
        zygosity: 'homozygous_alt',
        star_allele: '*2'
      }
    ],
    expectedHighlight: 'CYP2C19 *2/*2 Poor Metabolizer — Clopidogrel resistance. Switch to Prasugrel or Ticagrelor.'
  },
  {
    id: 'case_pain_cyp2d6',
    title: 'Post-Surgical Analgesia Case',
    category: 'Pain Management',
    patientId: 102,
    patientName: 'Sophia Chen',
    age: 34,
    gender: 'Female',
    clinicalContext: 'Post-operative pain management following orthopedic surgery. Prescribed Codeine with Acetaminophen.',
    medications: ['Codeine'],
    variants: [
      {
        gene: 'CYP2D6',
        star_allele: '*1xN',
        zygosity: 'heterozygous'
      }
    ],
    expectedHighlight: 'CYP2D6 *1xN/*1 Ultrarapid Metabolizer — Severe opioid toxicity risk. Codeine contraindicated.'
  },
  {
    id: 'case_oncology_dpyd',
    title: 'Colorectal Oncology Case',
    category: 'Oncology',
    patientId: 103,
    patientName: 'Robert Johnson',
    age: 62,
    gender: 'Male',
    clinicalContext: 'Stage III Colorectal adenocarcinoma candidate for FOLFOX chemotherapy (Fluorouracil / Capecitabine).',
    medications: ['Fluorouracil', 'Capecitabine'],
    variants: [
      {
        gene: 'DPYD',
        rsid: 'rs3918290',
        hgvs_c: 'c.1905+1G>A',
        zygosity: 'heterozygous',
        star_allele: '*2A'
      }
    ],
    expectedHighlight: 'DPYD *2A/*1 Intermediate Metabolizer — High risk of fatal toxicity. 50% dose reduction required.'
  },
  {
    id: 'case_hiv_hlab',
    title: 'Infectious Disease / Antiretroviral',
    category: 'Infectious Disease',
    patientId: 104,
    patientName: 'Elena Rostova',
    age: 41,
    gender: 'Female',
    clinicalContext: 'Initiating antiretroviral therapy for HIV-1 infection with Abacavir-containing regimen (Triumeq).',
    medications: ['Abacavir'],
    variants: [
      {
        gene: 'HLA-B',
        star_allele: '*57:01',
        zygosity: 'heterozygous'
      }
    ],
    expectedHighlight: 'HLA-B*57:01 Positive — Life-threatening hypersensitivity risk. Abacavir is strictly contraindicated.'
  },
  {
    id: 'case_polypharmacy',
    title: 'Complex Multi-Drug / Polypharmacy',
    category: 'Multi-Drug',
    patientId: 105,
    patientName: 'Arthur Pendelton',
    age: 71,
    gender: 'Male',
    clinicalContext: 'Atrial fibrillation and hypercholesterolemia. Prescribed Simvastatin (Zocor) and Warfarin (Coumadin).',
    medications: ['Simvastatin', 'Warfarin'],
    variants: [
      {
        gene: 'SLCO1B1',
        rsid: 'rs4149056',
        hgvs_c: 'c.521T>C',
        zygosity: 'homozygous_alt',
        star_allele: '*5'
      },
      {
        gene: 'CYP2C9',
        rsid: 'rs1057910',
        hgvs_c: 'c.1075A>C',
        zygosity: 'heterozygous',
        star_allele: '*3'
      },
      {
        gene: 'VKORC1',
        rsid: 'rs9923231',
        hgvs_c: 'c.-1639G>A',
        zygosity: 'homozygous'
      }
    ],
    expectedHighlight: 'Simvastatin *5/*5 Poor Function (High Myopathy Risk) + Warfarin High Sensitivity (Major Dose Reduction).'
  }
];

export const MOCK_GENE_DRUG_DATABASE: GeneDrugPairInfo[] = [
  {
    drug_name: 'Clopidogrel',
    brand_names: ['Plavix', 'Iscover'],
    primary_gene: 'CYP2C19',
    secondary_genes: ['PON1', 'ABCB1'],
    therapeutic_area: 'Cardiovascular / Antiplatelet',
    cpic_level: 'A',
    pharmgkb_level: '1A',
    fda_label_status: 'Boxed Warning'
  },
  {
    drug_name: 'Warfarin',
    brand_names: ['Coumadin', 'Jantoven'],
    primary_gene: 'CYP2C9',
    secondary_genes: ['VKORC1', 'CYP4F2'],
    therapeutic_area: 'Cardiovascular / Anticoagulant',
    cpic_level: 'A',
    pharmgkb_level: '1A',
    fda_label_status: 'Actionable PGx'
  },
  {
    drug_name: 'Simvastatin',
    brand_names: ['Zocor', 'Vytorin'],
    primary_gene: 'SLCO1B1',
    secondary_genes: ['CYP3A4', 'ABCG2'],
    therapeutic_area: 'Cardiovascular / Statin',
    cpic_level: 'A',
    pharmgkb_level: '1A',
    fda_label_status: 'Actionable PGx'
  },
  {
    drug_name: 'Codeine',
    brand_names: ['Tylenol with Codeine'],
    primary_gene: 'CYP2D6',
    secondary_genes: [],
    therapeutic_area: 'Analgesia / Opioid',
    cpic_level: 'A',
    pharmgkb_level: '1A',
    fda_label_status: 'Boxed Warning'
  },
  {
    drug_name: 'Tramadol',
    brand_names: ['Ultram', 'ConZip'],
    primary_gene: 'CYP2D6',
    secondary_genes: [],
    therapeutic_area: 'Analgesia / Opioid',
    cpic_level: 'A',
    pharmgkb_level: '1A',
    fda_label_status: 'Boxed Warning'
  },
  {
    drug_name: 'Tamoxifen',
    brand_names: ['Nolvadex', 'Soltamox'],
    primary_gene: 'CYP2D6',
    secondary_genes: [],
    therapeutic_area: 'Oncology / SERM',
    cpic_level: 'A',
    pharmgkb_level: '1A',
    fda_label_status: 'Actionable PGx'
  },
  {
    drug_name: 'Fluorouracil',
    brand_names: ['5-FU', 'Adrucil', 'Efudex'],
    primary_gene: 'DPYD',
    secondary_genes: ['TYMS'],
    therapeutic_area: 'Oncology / Antimetabolite',
    cpic_level: 'A',
    pharmgkb_level: '1A',
    fda_label_status: 'Boxed Warning'
  },
  {
    drug_name: 'Capecitabine',
    brand_names: ['Xeloda'],
    primary_gene: 'DPYD',
    secondary_genes: [],
    therapeutic_area: 'Oncology / Antimetabolite',
    cpic_level: 'A',
    pharmgkb_level: '1A',
    fda_label_status: 'Boxed Warning'
  },
  {
    drug_name: 'Azathioprine',
    brand_names: ['Imuran', 'Azasan'],
    primary_gene: 'TPMT',
    secondary_genes: ['NUDT15'],
    therapeutic_area: 'Immunology / Antirheumatic',
    cpic_level: 'A',
    pharmgkb_level: '1A',
    fda_label_status: 'Actionable PGx'
  },
  {
    drug_name: 'Abacavir',
    brand_names: ['Ziagen', 'Epzicom', 'Triumeq'],
    primary_gene: 'HLA-B',
    secondary_genes: [],
    therapeutic_area: 'Infectious Disease / Antiretroviral',
    cpic_level: 'A',
    pharmgkb_level: '1A',
    fda_label_status: 'Boxed Warning'
  },
  {
    drug_name: 'Allopurinol',
    brand_names: ['Zyloprim', 'Aloprim'],
    primary_gene: 'HLA-B',
    secondary_genes: [],
    therapeutic_area: 'Rheumatology / Xanthine Oxidase Inhibitor',
    cpic_level: 'A',
    pharmgkb_level: '1A',
    fda_label_status: 'Actionable PGx'
  },
  {
    drug_name: 'Carbamazepine',
    brand_names: ['Tegretol', 'Carbatrol'],
    primary_gene: 'HLA-B',
    secondary_genes: ['HLA-A', 'CYP3A4'],
    therapeutic_area: 'Neurology / Anticonvulsant',
    cpic_level: 'A',
    pharmgkb_level: '1A',
    fda_label_status: 'Boxed Warning'
  },
  {
    drug_name: 'Tacrolimus',
    brand_names: ['Prograf', 'Advagraf'],
    primary_gene: 'CYP3A5',
    secondary_genes: [],
    therapeutic_area: 'Transplantation / Immunosuppressant',
    cpic_level: 'A',
    pharmgkb_level: '1A',
    fda_label_status: 'Actionable PGx'
  }
];
