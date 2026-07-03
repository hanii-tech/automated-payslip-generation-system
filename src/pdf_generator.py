"""
pdf_generator.py
-----------------
Builds a professional-looking PDF payslip for a single employee using
reportlab's platypus (high-level) API — tables, paragraphs, and styles.
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)

# Change these to whatever you'd like the payslip to display.
COMPANY_NAME = "NovaTech Corporation"
COMPANY_SUBTITLE = "Payroll & Human Resources Division"


def _build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="CompanyTitle", fontSize=16, leading=20,
        textColor=colors.HexColor("#1F3864"), fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="CompanySubtitle", fontSize=10, leading=14,
        textColor=colors.HexColor("#555555"),
    ))
    styles.add(ParagraphStyle(
        name="PayslipTitle", fontSize=13, leading=16,
        textColor=colors.white, fontName="Helvetica-Bold",
        alignment=1,  # center
    ))
    styles.add(ParagraphStyle(
        name="SectionLabel", fontSize=9, leading=12,
        textColor=colors.HexColor("#777777"),
    ))
    styles.add(ParagraphStyle(
        name="SectionValue", fontSize=11, leading=14,
        textColor=colors.HexColor("#1a1a1a"), fontName="Helvetica-Bold",
    ))
    return styles


def generate_payslip_pdf(employee: dict, month: str, year: str, output_dir: str) -> str:
    """
    Generate a single payslip PDF for one employee.

    Args:
        employee: dict with keys Employee_ID, Employee_Name, Email, Department,
                  Designation, Basic_Salary, HRA, DA, Other_Allowance, Bonus,
                  Tax_Percentage, PF_Percentage, Gross_Earnings, PF_Amount,
                  Tax_Amount, NetPay
        month: e.g. "June"
        year: e.g. "2026"
        output_dir: folder to save the PDF into

    Returns:
        The full file path of the generated PDF.
    """
    os.makedirs(output_dir, exist_ok=True)

    safe_name = str(employee["Employee_Name"]).replace(" ", "_")
    file_name = f"{employee['Employee_ID']}_{safe_name}_{month}_{year}.pdf"
    file_path = os.path.join(output_dir, file_name)

    doc = SimpleDocTemplate(
        file_path, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm,
    )
    styles = _build_styles()
    elements = []

    # --- Header: Company name + payslip banner ---
    elements.append(Paragraph(COMPANY_NAME, styles["CompanyTitle"]))
    elements.append(Paragraph(COMPANY_SUBTITLE, styles["CompanySubtitle"]))
    elements.append(Spacer(1, 10))

    banner = Table(
        [[Paragraph(f"PAYSLIP FOR {month.upper()} {year}", styles["PayslipTitle"])]],
        colWidths=[doc.width],
    )
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1F3864")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(banner)
    elements.append(Spacer(1, 14))

    # --- Employee details block ---
    emp_info = [
        [Paragraph("Employee Name", styles["SectionLabel"]),
         Paragraph("Employee ID", styles["SectionLabel"])],
        [Paragraph(str(employee["Employee_Name"]), styles["SectionValue"]),
         Paragraph(str(employee["Employee_ID"]), styles["SectionValue"])],
        [Paragraph("Department", styles["SectionLabel"]),
         Paragraph("Designation", styles["SectionLabel"])],
        [Paragraph(str(employee["Department"]), styles["SectionValue"]),
         Paragraph(str(employee["Designation"]), styles["SectionValue"])],
        [Paragraph("Email", styles["SectionLabel"]), ""],
        [Paragraph(str(employee["Email"]), styles["SectionValue"]), ""],
    ]
    emp_table = Table(emp_info, colWidths=[doc.width / 2, doc.width / 2])
    emp_table.setStyle(TableStyle([
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("LINEBELOW", (0, 5), (-1, 5), 0.5, colors.HexColor("#dddddd")),
    ]))
    elements.append(emp_table)
    elements.append(Spacer(1, 18))

    # --- Salary breakdown table ---
    basic = float(employee["Basic_Salary"])
    hra = float(employee["HRA"])
    da = float(employee["DA"])
    other_allow = float(employee["Other_Allowance"])
    bonus = float(employee["Bonus"])
    pf = float(employee["PF_Amount"])
    tax = float(employee["Tax_Amount"])
    net_pay = float(employee["NetPay"])
    total_earnings = basic + hra + da + other_allow + bonus
    total_deductions = pf + tax

    data = [
        ["Earnings", "Amount (Rs.)", "Deductions", "Amount (Rs.)"],
        ["Basic Salary", f"{basic:,.2f}", f"Provident Fund ({employee['PF_Percentage']}%)", f"{pf:,.2f}"],
        ["HRA", f"{hra:,.2f}", f"Tax ({employee['Tax_Percentage']}%)", f"{tax:,.2f}"],
        ["DA", f"{da:,.2f}", "", ""],
        ["Other Allowance", f"{other_allow:,.2f}", "", ""],
        ["Bonus", f"{bonus:,.2f}", "", ""],
        ["Total Earnings", f"{total_earnings:,.2f}", "Total Deductions", f"{total_deductions:,.2f}"],
    ]
    salary_table = Table(data, colWidths=[doc.width * 0.3, doc.width * 0.2,
                                           doc.width * 0.3, doc.width * 0.2])
    salary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3864")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#EDEDED")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("ALIGN", (3, 0), (3, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(salary_table)
    elements.append(Spacer(1, 18))

    # --- Net pay highlight ---
    net_table = Table([["NET PAY", f"Rs. {net_pay:,.2f}"]], colWidths=[doc.width * 0.5, doc.width * 0.5])
    net_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#2E7D32")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 13),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (0, 0), 10),
        ("RIGHTPADDING", (1, 0), (1, 0), 10),
    ]))
    elements.append(net_table)
    elements.append(Spacer(1, 24))

    # --- Footer note ---
    elements.append(Paragraph(
        "This is a system-generated payslip and does not require a signature.",
        styles["SectionLabel"],
    ))

    doc.build(elements)
    return file_path
