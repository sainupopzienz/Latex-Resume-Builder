from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors
from io import BytesIO

def generate_resume_pdf(resume_data):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    contact_style = ParagraphStyle(
        'Contact',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=12
    )

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=6,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=colors.HexColor('#2c3e50'),
        borderPadding=0,
        leftIndent=0
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_LEFT
    )

    story.append(Paragraph(resume_data.get('full_name', ''), title_style))

    contact_info = []
    if resume_data.get('phone'):
        contact_info.append(resume_data['phone'])
    if resume_data.get('user_email'):
        contact_info.append(resume_data['user_email'])

    social_links = resume_data.get('social_links', {})
    for platform, url in social_links.items():
        if url:
            contact_info.append(f"{platform}: {url}")

    if contact_info:
        story.append(Paragraph(' | '.join(contact_info), contact_style))

    story.append(Spacer(1, 0.1*inch))

    if resume_data.get('profile_summary'):
        story.append(Paragraph('PROFESSIONAL SUMMARY', heading_style))
        story.append(Paragraph(resume_data['profile_summary'], body_style))
        story.append(Spacer(1, 0.1*inch))

    education = resume_data.get('education', [])
    if education:
        story.append(Paragraph('EDUCATION', heading_style))
        for edu in education:
            if isinstance(edu, dict):
                degree = edu.get('degree', '')
                institution = edu.get('institution', '')
                year = edu.get('year', '')
                gpa = edu.get('gpa', '')

                edu_text = f"<b>{degree}</b> - {institution}"
                if year:
                    edu_text += f" ({year})"
                if gpa:
                    edu_text += f" | GPA: {gpa}"

                story.append(Paragraph(edu_text, body_style))
        story.append(Spacer(1, 0.1*inch))

    technical_skills = resume_data.get('technical_skills', {})
    if technical_skills:
        story.append(Paragraph('TECHNICAL SKILLS', heading_style))
        for category, skills in technical_skills.items():
            if isinstance(skills, list):
                skills_text = ', '.join(skills)
            else:
                skills_text = str(skills)
            story.append(Paragraph(f"<b>{category}:</b> {skills_text}", body_style))
        story.append(Spacer(1, 0.1*inch))

    work_experience = resume_data.get('work_experience', [])
    if work_experience:
        story.append(Paragraph('WORK EXPERIENCE', heading_style))
        for work in work_experience:
            if isinstance(work, dict):
                title = work.get('title', '')
                company = work.get('company', '')
                period = work.get('period', '')
                description = work.get('description', '')

                work_header = f"<b>{title}</b> - {company}"
                if period:
                    work_header += f" | {period}"

                story.append(Paragraph(work_header, body_style))
                if description:
                    story.append(Paragraph(description, body_style))
                story.append(Spacer(1, 0.05*inch))
        story.append(Spacer(1, 0.05*inch))

    projects = resume_data.get('projects', [])
    if projects:
        story.append(Paragraph('PROJECTS', heading_style))
        for project in projects:
            if isinstance(project, dict):
                name = project.get('name', '')
                description = project.get('description', '')
                technologies = project.get('technologies', '')

                project_text = f"<b>{name}</b>"
                if technologies:
                    project_text += f" | {technologies}"

                story.append(Paragraph(project_text, body_style))
                if description:
                    story.append(Paragraph(description, body_style))
                story.append(Spacer(1, 0.05*inch))
        story.append(Spacer(1, 0.05*inch))

    languages = resume_data.get('languages', [])
    if languages:
        story.append(Paragraph('LANGUAGES', heading_style))
        lang_list = []
        for lang in languages:
            if isinstance(lang, dict):
                lang_name = lang.get('language', '')
                proficiency = lang.get('proficiency', '')
                lang_list.append(f"{lang_name} ({proficiency})")
            else:
                lang_list.append(str(lang))
        story.append(Paragraph(', '.join(lang_list), body_style))
        story.append(Spacer(1, 0.1*inch))

    certifications = resume_data.get('certifications', [])
    if certifications:
        story.append(Paragraph('CERTIFICATIONS', heading_style))
        for cert in certifications:
            if isinstance(cert, dict):
                cert_name = cert.get('name', '')
                issuer = cert.get('issuer', '')
                year = cert.get('year', '')

                cert_text = f"<b>{cert_name}</b>"
                if issuer:
                    cert_text += f" - {issuer}"
                if year:
                    cert_text += f" ({year})"

                story.append(Paragraph(cert_text, body_style))
            else:
                story.append(Paragraph(str(cert), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
