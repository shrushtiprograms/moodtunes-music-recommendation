#!/usr/bin/env python3
"""
accuracy_report_final.py
Generates high-quality evaluation outputs and a polished PDF report.
Confusion Matrix is COMPLETELY REMOVED in this version.
"""

import os
from pathlib import Path
import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
from sklearn.exceptions import UndefinedMetricWarning

warnings.filterwarnings("ignore", category=UndefinedMetricWarning)

from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    classification_report
)

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch

# ------------------- USER PATHS -------------------
PROJECT_ROOT = Path(".")
DATA_PATH = PROJECT_ROOT / "data" / "emotion_dataset.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "emotion_classifier.pkl"
LOGO_PATH = PROJECT_ROOT / "logo.png"
OUTPUT_DIR = PROJECT_ROOT / "final_evaluation_outputs"
# --------------------------------------------------

OUTPUT_DIR.mkdir(exist_ok=True)

# --- Load Data ---
df = pd.read_csv(DATA_PATH)
model = joblib.load(MODEL_PATH)

texts = df["text"].astype(str).tolist()
y_true = df["emotion"].astype(str).tolist()
y_pred = model.predict(texts)

# --- Metrics ---
acc = accuracy_score(y_true, y_pred)
prec_w, rec_w, f1_w, _ = precision_recall_fscore_support(
    y_true, y_pred, average="weighted", zero_division=0
)

summary = {
    "Accuracy": acc,
    "Precision (weighted)": prec_w,
    "Recall (weighted)": rec_w,
    "F1 (weighted)": f1_w
}

# --- Per Class Metrics ---
labels = sorted(list(set(y_true)))
prec, rec, f1, sup = precision_recall_fscore_support(
    y_true, y_pred, labels=labels, zero_division=0
)

per_class_df = pd.DataFrame({
    "label": labels,
    "precision": prec,
    "recall": rec,
    "f1-score": f1,
    "support": sup.astype(int)
})

# --- Save CSVs ---
pd.DataFrame([summary]).to_csv(OUTPUT_DIR / "metrics_summary.csv", index=False)
per_class_df.to_csv(OUTPUT_DIR / "per_class_metrics.csv", index=False)

# --- Metrics Bar Plot ---
metrics_names = ["Accuracy", "Precision", "Recall", "F1"]
metrics_values = [
    summary["Accuracy"],
    summary["Precision (weighted)"],
    summary["Recall (weighted)"],
    summary["F1 (weighted)"]
]

fig, ax = plt.subplots(figsize=(7, 4), dpi=200)
bars = ax.bar(metrics_names, metrics_values)
ax.set_ylim(0, 1)
ax.set_title("Model Summary Metrics")

for i, b in enumerate(bars):
    h = b.get_height()
    ax.text(
        b.get_x() + b.get_width()/2, h + 0.01,
        f"{h*100:.2f}%", ha="center", fontsize=9
    )

fig.tight_layout()
bar_path = OUTPUT_DIR / "metrics_bar_highres.png"
plt.savefig(bar_path, dpi=200, bbox_inches="tight")
plt.close()

# --- Classification Report ---
clf_report = classification_report(y_true, y_pred, digits=4, zero_division=0)

# --- PDF Build ---
pdf_path = OUTPUT_DIR / "Accuracy_Report_Final_Best.pdf"
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "title_style", parent=styles["Title"], alignment=1,
    fontSize=18, textColor=colors.HexColor("#0B3D91")
)

h2 = ParagraphStyle(
    "h2", parent=styles["Heading2"], textColor=colors.HexColor("#0B3D91")
)

normal = styles["BodyText"]

doc = SimpleDocTemplate(str(pdf_path), pagesize=A4,
                        rightMargin=40, leftMargin=40,
                        topMargin=40, bottomMargin=40)

story = []

# --- Logo ---
if LOGO_PATH.exists():
    story.append(RLImage(str(LOGO_PATH), width=2*inch, height=2*inch))

story.append(Spacer(1, 6))
story.append(Paragraph("<b>Emotion-Based Music Recommendation System</b>", title_style))
story.append(Spacer(1, 6))
story.append(Paragraph(f"<i>Evaluation Report — Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>", normal))
story.append(Spacer(1, 12))


# --- Summary Table ---
story.append(Paragraph("<b>Model Summary Metrics</b>", h2))
story.append(Spacer(1, 6))

table_data = [
    ["Metric", "Value", "Meaning"],
    ["Accuracy", f"{acc*100:.2f}%", "Overall correctness"],
    ["Precision", f"{prec_w*100:.2f}%", "Correctness of predicted labels"],
    ["Recall", f"{rec_w*100:.2f}%", "Model finding actual labels"],
    ["F1 Score", f"{f1_w*100:.2f}%", "Balanced precision & recall"],
]

table = Table(table_data, colWidths=[140, 100, 220])
table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#DCE6F1")),
    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ('ALIGN', (0,0), (-1,-1), 'CENTER')
]))
story.append(table)
story.append(Spacer(1, 12))


# --- Per Class Table ---
story.append(Paragraph("<b>Per-class Metrics</b>", h2))
story.append(Spacer(1, 6))

pc_data = [["Label", "Precision", "Recall", "F1-Score", "Support"]]
for _, r in per_class_df.iterrows():
    pc_data.append([
        r["label"],
        f"{r['precision']*100:.2f}%",
        f"{r['recall']*100:.2f}%",
        f"{r['f1-score']*100:.2f}%",
        str(int(r["support"]))
    ])

pc_table = Table(pc_data, colWidths=[100, 80, 80, 80, 80])
pc_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#DCE6F1")),
    ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
    ('ALIGN', (0,0), (-1,-1), 'CENTER')
]))

story.append(pc_table)
story.append(Spacer(1, 12))


# --- Bar Chart ---
story.append(Paragraph("<b>Metrics Bar Chart</b>", h2))
story.append(Spacer(1, 6))
story.append(RLImage(str(bar_path), width=6*inch, height=2.5*inch))
story.append(Spacer(1, 12))


# --- Classification Report ---
story.append(Paragraph("<b>Classification Report (detailed)</b>", h2))
story.append(Spacer(1, 6))

mono = ParagraphStyle("mono", fontName="Courier", fontSize=8)

for line in clf_report.splitlines():
    story.append(Paragraph(line.replace(" ", "&nbsp;"), mono))

story.append(Spacer(1, 12))

doc.build(story)

print("DONE! Your clean report is ready.")
print("PDF:", pdf_path)
print("Bar Chart:", bar_path)
print("CSVs inside:", OUTPUT_DIR)