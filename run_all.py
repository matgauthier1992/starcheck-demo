from pipeline import run_pipeline
from reports.generate_report import generate_pdf

def main():
    # 1. Run pipeline
    results = run_pipeline("data/sample_input.txt")

    # 2. Generate PDF report
    generate_pdf(results, "reports/compliance_report.pdf")

    print("✅ Compliance analysis complete. Report saved to reports/compliance_report.pdf")

if __name__ == "__main__":
    main()
