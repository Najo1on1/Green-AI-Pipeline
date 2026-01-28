from reportlab.pdfgen import canvas

def create_policy_pdf(filename):
    c = canvas.Canvas(filename)
    c.setFont("Helvetica", 12)
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "Secure-Corp Data Handling Policy v1.0")
    
    # Content (Simulating Compliance Rules)
    c.setFont("Helvetica", 12)
    text_lines = [
        "1. All Engineers must use Multi-Factor Authentication (MFA).",
        "2. Production Data must be encrypted at rest using AES-256.",
        "3. The CTO is responsible for approving all Cloud Budgets.",
        "4. Customer PII (Personally Identifiable Information) must never be stored in logs.",
        "5. If a Data Breach occurs, the Security Team must be notified within 1 hour."
    ]
    
    y = 750
    for line in text_lines:
        c.drawString(50, y, line)
        y -= 30
        
    c.save()
    print(f"✅ Generated artifact: {filename}")

if __name__ == "__main__":
    create_policy_pdf("company_policy.pdf")