from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

def generate_pdf(personal_info, education, experience, skills, template):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Custom styles based on template
    if template == "Professional":
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.navy,
            spaceAfter=30
        )
    elif template == "Modern":
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.darkgreen,
            spaceAfter=30
        )
    else:  # Classic
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.black,
            spaceAfter=30
        )

    # Personal Information
    if personal_info:
        story.append(Paragraph(f"{personal_info.get('name', '')}", title_style))
        story.append(Paragraph(f"Email: {personal_info.get('email', '')}", styles["Normal"]))
        story.append(Paragraph(f"Phone: {personal_info.get('phone', '')}", styles["Normal"]))
        story.append(Spacer(1, 20))

    # Education Section
    story.append(Paragraph("Education", styles["Heading2"]))
    for edu in education:
        if edu.get('institution'):
            story.append(Paragraph(f"<b>{edu.get('institution')}</b>", styles["Normal"]))
            story.append(Paragraph(f"{edu.get('degree')} - {edu.get('graduation_year')}", styles["Normal"]))
            story.append(Spacer(1, 10))

    # Experience Section
    story.append(Paragraph("Professional Experience", styles["Heading2"]))
    for exp in experience:
        if exp.get('company'):
            story.append(Paragraph(f"<b>{exp.get('company')}</b>", styles["Normal"]))
            story.append(Paragraph(f"{exp.get('position')} ({exp.get('duration')})", styles["Normal"]))
            story.append(Paragraph(f"{exp.get('description')}", styles["Normal"]))
            story.append(Spacer(1, 10))

    # Skills Section
    if skills:
        story.append(Paragraph("Skills", styles["Heading2"]))
        skills_text = ", ".join(skills)
        story.append(Paragraph(skills_text, styles["Normal"]))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
