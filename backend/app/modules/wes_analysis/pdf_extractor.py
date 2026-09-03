import pdfplumber


def extract_text_from_pdf(pdf_path):
    """
    Extract all text from a PDF.

    Returns:
        str: Combined text from all pages.
    """

    text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    pdf_path = "medgenome_report.pdf"

    text = extract_text_from_pdf(pdf_path)

    print(text)