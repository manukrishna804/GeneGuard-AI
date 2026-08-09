# Module 1: WES Analysis Backend (MVP)

## Purpose
This module handles Whole Exome Sequencing (WES) report processing. It automates the parsing of variant text from PDF reports, performs validation, and queries clinical annotations to return structured genomic evidence.

## Current Pipeline
1. **PDF Validation**: Ensures uploaded files are valid PDF formats.
2. **Text Extraction**: Uses `pdfplumber` to extract plain text from text-based PDFs.
3. **Variant Extraction**: Practical pattern matcher (regex) extracts Gene, Transcript, cDNA (HGVS), Protein change, rsID, and Zygosity.
4. **Variant Validation**: Performs sanity checks on the extracted fields.
5. **Ensembl REST API**: Queries `https://rest.ensembl.org` using HGVS annotations for transcript mappings or fallback gene symbol lookups.
6. **NCBI ClinVar / E-utilities**: Queries `https://eutils.ncbi.nlm.nih.gov` to fetch corresponding ClinVar UIDs (via `esearch`) and records (via `esummary`).
7. **Evidence Combination**: Assembles the clinical data into a unified JSON format.

## API Endpoints

### 1. Health Check
* **Endpoint**: `GET /api/v1/wes/health`
* **Response**:
  ```json
  {
      "module": "wes_analysis",
      "status": "healthy"
  }
  ```

### 2. Analyze PDF Report
* **Endpoint**: `POST /api/v1/wes/analyze`
* **Request Format**: `multipart/form-data`
* **Body Parameters**:
  * `file`: (Binary) The WES PDF report file.
* **Response**: `WESAnalysisResponse` schema containing extracted variants and annotations.

### 3. Test Single Variant
* **Endpoint**: `POST /api/v1/wes/test-variant`
* **Request Format**: `application/json`
* **Request Body**:
  ```json
  {
      "gene": "PAH",
      "transcript": "NM_000277.3",
      "cdna": "c.722G>A",
      "protein": "p.Arg241His",
      "rsid": null,
      "zygosity": "HET"
  }
  ```
* **Response**: Resolves annotations directly from Ensembl & ClinVar without requiring a PDF.

## Environment Variables
* `NCBI_API_KEY`: *(Optional)* NCBI E-utilities API key. Highly recommended to increase rate limit from 3 to 10 queries/second.

## Future Scope (Planned)
* OCR engine support for image-based/scanned PDF reports.
* Persistent database storage integrations.
* Additional genomic databases (gnomAD, HPO, OMIM, Orphanet, PubMed).
* ACMG classification and AI-driven clinical reasoning.

