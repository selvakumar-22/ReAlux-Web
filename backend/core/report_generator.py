import os, math
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

def generate_report(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    styles=getSampleStyleSheet()
    title=ParagraphStyle("Title2", parent=styles["Title"], alignment=TA_CENTER, fontSize=20, spaceAfter=12)
    doc=SimpleDocTemplate(filepath,pagesize=A4,rightMargin=36,leftMargin=36,topMargin=36,bottomMargin=36)
    story=[Paragraph("ReAlux — Aluminium Dross Recovery Analysis", title),
           Paragraph(f"<b>Sample:</b> {data.get('sample_id','-')} &nbsp;&nbsp; <b>Test:</b> {data.get('test_method','-')}", styles["Normal"]),
           Spacer(1,12)]
    comp=data.get("composition",{})
    rows=[["Component","Value (%)"]]+[[k,f"{float(v):.2f}"] for k,v in comp.items()]
    story.append(KeepTogether([Paragraph("<b>Composition</b>",styles["Heading2"]),
                               Table(rows, colWidths=[160,100], style=TableStyle([
                                   ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#dbeafe")),
                                   ("GRID",(0,0),(-1,-1),0.5,colors.grey),
                                   ("ALIGN",(1,1),(-1,-1),"RIGHT")
                               ]))]))
    story.append(Spacer(1,12))
    result_rows=[
        ["Result","Value"],
        ["Metal recovery",f"{data.get('metal_recovery',0):.2f}%"],
        ["Alumina recovery",f"{data.get('alumina_recovery',0):.2f}%"],
        ["Recovery category",str(data.get("recovery_category","-"))],
        ["Best recovery method",str(data.get("best_method","-"))],
        ["Risk level",str((data.get("safety_summary") or {}).get("risk_level","-"))],
        ["Model",str(data.get("model_used","-"))],
    ]
    story.append(KeepTogether([Paragraph("<b>Analysis Results</b>",styles["Heading2"]),
                               Table(result_rows, colWidths=[190,260], style=TableStyle([
                                   ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#dcfce7")),
                                   ("GRID",(0,0),(-1,-1),0.5,colors.grey)
                               ]))]))
    story.append(Spacer(1,12))
    story.append(Paragraph("<b>Method recommendation</b>",styles["Heading2"]))
    story.append(Paragraph(str(data.get("method_reason","-")),styles["BodyText"]))
    safety=data.get("safety_summary") or {}
    story.append(Spacer(1,8))
    story.append(Paragraph("<b>Safety / handling advice</b>",styles["Heading2"]))
    for key in ["classification_note","handling_advice","storage_advice","ppe_advice","disposal_advice"]:
        if safety.get(key): story.append(Paragraph(str(safety[key]),styles["BodyText"]))
    story.append(Spacer(1,8))
    metrics=[
        ["Model performance","R²","MAE","RMSE"],
        ["Metal",fmt(data.get("r2_metal")),fmt(data.get("mae_metal")),fmt(data.get("rmse_metal"))],
        ["Alumina",fmt(data.get("r2_alumina")),fmt(data.get("mae_alumina")),fmt(data.get("rmse_alumina"))],
    ]
    story.append(KeepTogether([Paragraph("<b>Model performance</b>",styles["Heading2"]),
        Table(metrics,colWidths=[150,90,90,90],style=TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#fef3c7")),
            ("GRID",(0,0),(-1,-1),0.5,colors.grey)
        ]))]))
    story.append(Spacer(1,10))
    story.append(Paragraph("<b>Note:</b> This report is a decision-support output. Safety classifications and process recommendations should be verified by qualified personnel and site-specific procedures.", styles["BodyText"]))
    doc.build(story)

def fmt(x):
    return "-" if x is None else f"{float(x):.3f}"
