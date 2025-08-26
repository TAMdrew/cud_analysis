"""Generates visual reports, including Plotly dashboards and PDF reports.

This module provides functions to create interactive dashboards and detailed,
professional PDF reports for CUD analysis, suitable for executive presentation.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .config_manager import ConfigManager

logger = logging.getLogger(__name__)


def create_dashboard(analysis: Dict[str, Any], config_manager: ConfigManager):
    """Creates an interactive Plotly dashboard for CUD analysis."""
    theme = config_manager.get(
        "reporting.theme_colors",
        {
            "primary": "#3B82F6",
            "secondary": "#1E3A8A",
            "accent": "#F59E0B",
            "success": "#10B981",
            "danger": "#EF4444",
        },
    )

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Monthly Savings by Strategy",
            "Machine Type Spend Distribution",
            "Risk Assessment",
            "Top Savings by Machine Type",
        ),
        specs=[[{"type": "bar"}, {"type": "pie"}], [{"type": "bar"}, {"type": "bar"}]],
    )

    # 1. Savings by Strategy
    savings_summary = analysis["total_savings_summary"]
    strategies = [
        "1-Yr Resource",
        "3-Yr Resource",
        "1-Yr Flex",
        "3-Yr Flex",
        "Optimal Mix",
    ]
    savings = [
        savings_summary.get("1_year_resource", 0),
        savings_summary.get("3_year_resource", 0),
        savings_summary.get("1_year_flex", 0),
        savings_summary.get("3_year_flex", 0),
        savings_summary.get("optimal_mix", 0),
    ]
    fig.add_trace(
        go.Bar(
            x=strategies,
            y=savings,
            text=[f"${s:,.0f}" for s in savings],
            textposition="auto",
            marker_color=[
                theme["primary"],
                theme["secondary"],
                theme["success"],
                theme["accent"],
                theme["danger"],
            ],
        ),
        row=1,
        col=1,
    )

    # 2. Machine Spend Distribution
    top_machines = sorted(
        analysis["machine_spend_distribution"].items(), key=lambda x: x[1], reverse=True
    )[:8]
    fig.add_trace(
        go.Pie(
            labels=[m[0].upper() for m in top_machines],
            values=[m[1] for m in top_machines],
            hole=0.3,
        ),
        row=1,
        col=2,
    )

    # 3. Risk Distribution
    risk_dist = analysis["risk_assessment"]["risk_distribution"]
    risk_values = [
        risk_dist.get("low", 0),
        risk_dist.get("medium", 0),
        risk_dist.get("high", 0),
    ]
    fig.add_trace(
        go.Bar(
            x=["Low", "Medium", "High"],
            y=risk_values,
            marker_color=[theme["success"], theme["accent"], theme["danger"]],
        ),
        row=2,
        col=1,
    )

    # 4. Top Savings Opportunities
    portfolio_layers = analysis["portfolio_recommendation"]["layers"][:10]
    savings_values = [layer["monthly_savings"] for layer in portfolio_layers]
    fig.add_trace(
        go.Bar(
            x=[layer["machine_type"].upper() for layer in portfolio_layers],
            y=savings_values,
            text=[f"${s:,.0f}" for s in savings_values],
            textposition="auto",
            marker_color=theme["primary"],
        ),
        row=2,
        col=2,
    )

    fig.update_layout(
        title_text="Cloud FinOps CUD Analysis Dashboard", showlegend=False, height=800
    )
    return fig


# pylint: disable=too-few-public-methods
class PDFReportGenerator:
    """Generates professional, customizable PDF reports."""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.styles = getSampleStyleSheet()
        self.theme = self.config_manager.get(
            "reporting.theme_colors",
            {
                "primary": "#1E3A8A",
                "secondary": "#10B981",
                "accent": "#F59E0B",
                "background": "#F3F4F6",
                "text": "#111827",
            },
        )
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Sets up custom paragraph and table styles using the theme."""
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                fontSize=24,
                textColor=HexColor(self.theme["primary"]),
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                fontSize=16,
                textColor=HexColor(self.theme["primary"]),
                spaceAfter=12,
                spaceBefore=12,
                fontName="Helvetica-Bold",
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="NormalLeft", parent=self.styles["Normal"], alignment=TA_LEFT
            )
        )

    def generate_report(
        self, analysis: Dict[str, Any], filename: Optional[str] = None
    ) -> str:
        """
        Generates a comprehensive, multi-page PDF report.

        Args:
            analysis: The analysis results dictionary.
            filename: The desired filename for the report. If None, a default
                      is used.

        Returns:
            The filename of the generated report.
        """
        if filename is None:
            filename = f"CFO_CUD_Report_{datetime.now().strftime('%Y%m%d')}.pdf"

        doc = SimpleDocTemplate(filename, pagesize=letter)
        story: List[Any] = []

        self._build_title_page(story)
        self._build_executive_summary(story, analysis)
        story.append(PageBreak())
        self._build_portfolio_recommendation(story, analysis)
        story.append(PageBreak())
        self._build_risk_assessment(story, analysis)
        self._build_next_steps(story)

        doc.build(story)
        logger.info("PDF Report generated: %s", filename)
        return filename

    def _build_title_page(self, story: List[Any]):
        """Builds the title page of the report."""
        logo_path = self.config_manager.get("reporting.company_logo_path")
        if logo_path and Path(logo_path).is_file():
            img = Image(logo_path, width=100, height=100)
            img.hAlign = "CENTER"
            story.append(img)
            story.append(Spacer(1, 20))

        story.append(
            Paragraph("Cloud FinOps CUD Analysis Report", self.styles["CustomTitle"])
        )
        company_name = self.config_manager.get("company.name", "Your Company")
        story.append(Paragraph(company_name, self.styles["Title"]))
        story.append(Spacer(1, 12))
        story.append(
            Paragraph(
                f"Generated: {datetime.now().strftime('%B %d, %Y')}",
                self.styles["Normal"],
            )
        )

    def _build_executive_summary(self, story: List[Any], analysis: Dict[str, Any]):
        """Builds the executive summary section with a key metrics table."""
        story.append(Paragraph("Executive Summary", self.styles["SectionHeader"]))
        total_spend = sum(analysis["machine_spend_distribution"].values())
        optimal_savings = analysis["total_savings_summary"]["optimal_mix"]
        savings_pct = (optimal_savings / total_spend * 100) if total_spend > 0 else 0

        data = [
            ["Metric", "Value"],
            ["Total Monthly Spend Analyzed", f"${total_spend:,.2f}"],
            ["Optimal Monthly Savings", f"${optimal_savings:,.2f}"],
            ["Annual Savings Potential", f"${optimal_savings * 12:,.2f}"],
            ["Effective Blended Discount", f"{savings_pct:.1f}%"],
            ["Overall Risk Assessment", analysis["risk_assessment"]["overall_risk"]],
        ]
        table = Table(data, colWidths=[200, 200])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), HexColor(self.theme["primary"])),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        HexColor(self.theme["background"]),
                    ),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(table)

    def _build_portfolio_recommendation(
        self, story: List[Any], analysis: Dict[str, Any]
    ):
        """Builds the top recommendations table."""
        story.append(
            Paragraph("Top Portfolio Recommendations", self.styles["SectionHeader"])
        )
        top_layers = analysis["portfolio_recommendation"]["layers"][:10]

        data = [["Machine Type", "Strategy", "Committed Spend", "Monthly Savings"]]
        for layer in top_layers:
            data.append(
                [
                    layer["machine_type"].upper(),
                    layer["strategy"].replace("_", " ").title(),
                    f"${layer['monthly_spend']:,.2f}",
                    f"${layer['monthly_savings']:,.2f}",
                ]
            )
        table = Table(data, colWidths=[100, 150, 120, 120])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), HexColor(self.theme["secondary"])),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        HexColor(self.theme["background"]),
                    ),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(table)

    def _build_risk_assessment(self, story: List[Any], analysis: Dict[str, Any]):
        """Builds the risk assessment section."""
        story.append(Paragraph("Risk Assessment", self.styles["SectionHeader"]))
        story.append(
            Paragraph(
                f"<b>Overall Risk:</b> {analysis['risk_assessment']['overall_risk']}",
                self.styles["NormalLeft"],
            )
        )
        story.append(
            Paragraph(
                f"<b>Recommendation:</b> "
                f"{analysis['risk_assessment']['recommendation']}",
                self.styles["NormalLeft"],
            )
        )
        story.append(Spacer(1, 12))

    def _build_next_steps(self, story: List[Any]):
        """Builds the next steps section."""
        story.append(Paragraph("Actionable Next Steps", self.styles["SectionHeader"]))
        steps = [
            "<b>1. Validate Spend:</b> Review the machine-specific spend "
            "distribution to confirm stability.",
            "<b>2. Start Conservatively:</b> Implement the top 3-5 "
            "recommendations for high-spend, low-risk machine types.",
            "<b>3. Monitor Utilization:</b> Set up monitoring for CUD "
            "utilization before expanding commitments.",
            "<b>4. Consider Flex CUDs:</b> Use Flex CUDs for workloads "
            "with less predictable usage patterns.",
            "<b>5. Quarterly Review:</b> Establish a quarterly cadence to "
            "review this report and adjust your CUD portfolio.",
        ]
        for step in steps:
            story.append(Paragraph(step, self.styles["NormalLeft"]))
            story.append(Spacer(1, 6))
