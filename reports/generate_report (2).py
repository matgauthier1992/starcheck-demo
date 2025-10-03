from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf(results, output_path):
    c = canvas.Canvas(output_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, "Billion Dollar Jet Software – Compliance Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, 720, f"Document: {results.get('document', 'N/A')}")
    c.drawString(50, 700, f"Risk Score: {results.get('risk_score', 0)}% compliant")

    c.drawString(50, 670, "Violations Found:")
    y = 650
    for v in results.get("violations", []):
        c.drawString(70, y, f"- {v}")
        y -= 20

    c.drawString(50, y, "Suggested Fixes:")
    y -= 20
    for s in results.get("suggestions", []):
        c.drawString(70, y, f"- {s}")
        y -= 20

    c.save()
