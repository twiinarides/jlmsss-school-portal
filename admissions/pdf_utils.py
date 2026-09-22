"""
admissions/pdf_utils.py — PDF generation for offer letters and payment receipts.
Uses ReportLab. Requires: pip install reportlab Pillow
"""

import io
import os
from django.conf import settings
from django.utils import timezone

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, Image,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

NAVY = (11 / 255, 31 / 255, 58 / 255)
GOLD = (212 / 255, 175 / 255, 55 / 255)
LIGHT_GRAY = (0.95, 0.95, 0.95)
BLACK = (0, 0, 0)
WHITE = (1, 1, 1)


def _get_logo_path():
    """Return absolute path to the school logo/badge."""
    return os.path.join(settings.BASE_DIR, 'static', 'img', 'school-badge.png')


def generate_offer_letter_pdf(application):
    """
    Generate a professional, watermarked PDF Offer Letter.
    Returns BytesIO object or None if reportlab is not available.
    """
    if not REPORTLAB_AVAILABLE:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f'Offer Letter — {application.application_number}',
        author='Janan Luwum Memorial SSS',
    )

    styles = getSampleStyleSheet()
    story = []

    # Watermark-style header band
    navy_rgb = colors.Color(*NAVY)
    gold_rgb = colors.Color(*GOLD)

    # School header table
    logo_path = _get_logo_path()
    header_data = []
    logo_cell = ''
    if os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=2.5 * cm, height=2.5 * cm)
            logo_cell = logo
        except Exception:
            logo_cell = ''

    school_name_style = ParagraphStyle(
        'SchoolName', fontName='Helvetica-Bold', fontSize=13,
        textColor=navy_rgb, spaceAfter=2, alignment=TA_CENTER,
    )
    school_sub_style = ParagraphStyle(
        'SchoolSub', fontName='Helvetica', fontSize=9,
        textColor=colors.Color(0.3, 0.3, 0.3), alignment=TA_CENTER,
    )

    school_info = [
        Paragraph('KAMUGANGUZI JANAN LUWUM MEMORIAL', school_name_style),
        Paragraph('SENIOR SECONDARY SCHOOL', school_name_style),
        Paragraph('P.O. Box — Kamuganguzi, Kabale District, Uganda', school_sub_style),
        Paragraph('admissions@jananluwummemorialsss.sc.ug | www.jananluwummemorialsss.sc.ug', school_sub_style),
    ]

    header_table_data = [[logo_cell, school_info]]
    header_table = Table(header_table_data, colWidths=[3 * cm, 13.5 * cm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width='100%', thickness=3, color=gold_rgb, spaceAfter=4))
    story.append(HRFlowable(width='100%', thickness=1, color=navy_rgb, spaceAfter=12))

    # OFFER LETTER title
    title_style = ParagraphStyle(
        'Title', fontName='Helvetica-Bold', fontSize=16,
        textColor=navy_rgb, alignment=TA_CENTER, spaceAfter=6,
    )
    story.append(Paragraph('ADMISSION OFFER LETTER', title_style))

    # Application ref + date
    ref_style = ParagraphStyle(
        'Ref', fontName='Helvetica', fontSize=10,
        textColor=colors.Color(0.3, 0.3, 0.3), alignment=TA_CENTER, spaceAfter=18,
    )
    today = timezone.now().strftime('%d %B %Y')
    story.append(Paragraph(f'Application Reference: <b>{application.application_number}</b> | Date: {today}', ref_style))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.Color(*LIGHT_GRAY), spaceAfter=16))

    body_style = ParagraphStyle(
        'Body', fontName='Helvetica', fontSize=11, leading=16,
        textColor=colors.Color(0.1, 0.1, 0.1), spaceAfter=10, alignment=TA_JUSTIFY,
    )
    bold_style = ParagraphStyle(
        'Bold', fontName='Helvetica-Bold', fontSize=11,
        textColor=navy_rgb, spaceAfter=4,
    )

    # Salutation
    student_name = application.student_name.upper()
    guardian_name = ''
    if application.student:
        guardian_name = application.student.guardian_name
    story.append(Paragraph(f'Dear {guardian_name or "Parent/Guardian"},', body_style))
    story.append(Spacer(1, 6))

    # Opening paragraph
    window_intro = ''
    if application.window.offer_letter_intro:
        window_intro = application.window.offer_letter_intro
    else:
        window_intro = (
            f'On behalf of the Headteacher, staff, and Board of Governors of Kamuganguzi Janan Luwum '
            f'Memorial Senior Secondary School, we are delighted to offer admission to:'
        )
    story.append(Paragraph(window_intro, body_style))
    story.append(Spacer(1, 8))

    # Student details box
    story.append(Paragraph(f'<b>{student_name}</b>', title_style))
    story.append(Spacer(1, 8))

    # Details table
    entry_class = application.entry_class_label
    details = [
        ['Application Number', application.application_number],
        ['Academic Year', application.window.academic_year],
        ['Class Admitted To', entry_class],
        ['Admission Type', 'Transfer Student' if application.is_transfer else 'New Entrant'],
    ]
    if application.student:
        details.insert(1, ['Date of Birth', application.student.date_of_birth.strftime('%d %B %Y')])

    detail_table = Table(details, colWidths=[6 * cm, 10.5 * cm])
    detail_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), navy_rgb),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.white, colors.Color(0.97, 0.97, 0.97)]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.85, 0.85, 0.85)),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(detail_table)
    story.append(Spacer(1, 16))

    # Body text
    story.append(Paragraph(
        'This offer is subject to the following conditions being met within <b>14 days</b> of this letter:',
        body_style,
    ))
    conditions = [
        '1. Presentation of original academic transcripts and certificates for verification.',
        '2. Completion of medical examination forms and submission of immunization records.',
        '3. Payment of the prescribed school fees for the first term.',
        "4. Signing of the school's code of conduct and community engagement agreement.",
        "5. Physical presentation at the school's admissions office with this letter.",
    ]
    for cond in conditions:
        story.append(Paragraph(f'&nbsp;&nbsp;&nbsp;{cond}', body_style))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        'We look forward to welcoming the student to our school community. Should you have any questions, '
        'please contact the Admissions Office at <b>admissions@jananluwummemorialsss.sc.ug</b> or visit '
        'our portal at <b>admission.jananluwummemorialsss.sc.ug</b>.',
        body_style,
    ))
    story.append(Spacer(1, 24))

    # Signature block
    story.append(Paragraph('Yours faithfully,', body_style))
    story.append(Spacer(1, 36))
    story.append(HRFlowable(width=8 * cm, thickness=1, color=navy_rgb))
    story.append(Paragraph('<b>The Headteacher</b>', bold_style))
    story.append(Paragraph('Kamuganguzi Janan Luwum Memorial Senior Secondary School', ref_style))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.Color(*LIGHT_GRAY)))

    # Footer
    footer_style = ParagraphStyle(
        'Footer', fontName='Helvetica-Oblique', fontSize=8,
        textColor=colors.Color(0.5, 0.5, 0.5), alignment=TA_CENTER, spaceBefore=8,
    )
    story.append(Paragraph(
        f'This is a computer-generated document. Generated on {today}. '
        f'Ref: {application.application_number}',
        footer_style,
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def generate_payment_receipt_pdf(application):
    """Generate a downloadable payment receipt PDF."""
    if not REPORTLAB_AVAILABLE:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2.5 * cm, leftMargin=2.5 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    navy_rgb = colors.Color(*NAVY)
    gold_rgb = colors.Color(*GOLD)
    story = []

    title_style = ParagraphStyle(
        'Title', fontName='Helvetica-Bold', fontSize=18,
        textColor=navy_rgb, alignment=TA_CENTER, spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        'Sub', fontName='Helvetica', fontSize=10,
        textColor=colors.Color(0.4, 0.4, 0.4), alignment=TA_CENTER, spaceAfter=16,
    )
    body_style = ParagraphStyle('Body', fontName='Helvetica', fontSize=11, leading=16, spaceAfter=6)

    story.append(Paragraph('PAYMENT RECEIPT', title_style))
    story.append(Paragraph('Kamuganguzi Janan Luwum Memorial Senior Secondary School', sub_style))
    story.append(HRFlowable(width='100%', thickness=2, color=gold_rgb, spaceAfter=16))

    today = timezone.now().strftime('%d %B %Y at %H:%M')
    story.append(Paragraph(f'Receipt generated: {today}', sub_style))

    details = [
        ['Application Number', application.application_number],
        ['Student Name', application.student_name],
        ['Class', application.entry_class_label],
        ['Admission Window', str(application.window)],
        ['Payment Reference', application.payment_reference or 'Pending'],
        ['Fee Amount (UGX)', str(application.window.application_fee or 'N/A')],
        ['Payment Status', 'VERIFIED' if application.payment_verified else 'PENDING VERIFICATION'],
    ]

    detail_table = Table(details, colWidths=[6 * cm, 10 * cm])
    detail_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), navy_rgb),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.white, colors.Color(0.97, 0.97, 0.97)]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.85, 0.85, 0.85)),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(detail_table)
    story.append(Spacer(1, 20))

    footer_style = ParagraphStyle(
        'Footer', fontName='Helvetica-Oblique', fontSize=8,
        textColor=colors.Color(0.5, 0.5, 0.5), alignment=TA_CENTER,
    )
    story.append(HRFlowable(width='100%', thickness=1, color=colors.Color(0.85, 0.85, 0.85)))
    story.append(Paragraph('This receipt is auto-generated. Keep this for your records.', footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
