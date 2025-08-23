import logging
from datetime import datetime
from typing import Dict
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph,
                                Spacer, PageBreak)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER

logger = logging.getLogger(__name__)

def create_dashboard(analysis: Dict):
    """Create interactive visualization dashboard"""

    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Monthly Savings by Strategy', 'Machine Type Distribution',
                       'Risk Assessment', 'Savings by Machine Type'),
        specs=[[{'type': 'bar'}, {'type': 'pie'}],
               [{'type': 'bar'}, {'type': 'bar'}]]
    )

    # 1. Monthly Savings by Strategy
    strategies = ['1-Year Resource', '3-Year Resource', '1-Year Flex', '3-Year Flex', 'Optimal Mix']
    monthly_savings = [
        analysis['total_savings_summary']['1_year_resource'],
        analysis['total_savings_summary']['3_year_resource'],
        analysis['total_savings_summary']['1_year_flex'],
        analysis['total_savings_summary']['3_year_flex'],
        analysis['total_savings_summary']['optimal_mix']
    ]

    fig.add_trace(
        go.Bar(x=strategies, y=monthly_savings,
               text=[f'${s:,.0f}' for s in monthly_savings],
               textposition='auto',
               marker_color=['#3B82F6', '#1E3A8A', '#10B981', '#059669', '#F59E0B']),
        row=1, col=1
    )

    # 2. Machine Type Distribution (Top 8)
    top_machines = sorted(analysis['machine_spend_distribution'].items(),
                         key=lambda x: x[1], reverse=True)[:8]

    fig.add_trace(
        go.Pie(labels=[m[0].upper() for m in top_machines],
               values=[m[1] for m in top_machines],
               hole=0.3),
        row=1, col=2
    )

    # 3. Risk Distribution
    risk_dist = analysis['risk_assessment']['risk_distribution']
    fig.add_trace(
        go.Bar(x=['Low Risk', 'Medium Risk', 'High Risk'],
               y=[risk_dist['low'], risk_dist['medium'], risk_dist['high']],
               text=[risk_dist['low'], risk_dist['medium'], risk_dist['high']],
               textposition='auto',
               marker_color=['#10B981', '#F59E0B', '#EF4444']),
        row=2, col=1
    )

    # 4. Top Savings Opportunities
    top_savings = sorted(analysis['savings_by_machine'].items(),
                        key=lambda x: x[1]['resource_cud_3yr']['monthly_savings'],
                        reverse=True)[:10]

    fig.add_trace(
        go.Bar(x=[s[0].upper() for s in top_savings],
               y=[s[1]['resource_cud_3yr']['monthly_savings'] for s in top_savings],
               text=[f"${s[1]['resource_cud_3yr']['monthly_savings']:,.0f}" for s in top_savings],
               textposition='auto',
               marker_color='#3B82F6'),
        row=2, col=2
    )

    # Update layout
    fig.update_layout(
        title_text="Cloud FinOps CUD Analysis Dashboard",
        showlegend=False,
        height=800
    )

    # Update axes
    fig.update_yaxes(title_text="Monthly Savings ($)", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    fig.update_yaxes(title_text="Monthly Savings ($)", row=2, col=2)
    fig.update_xaxes(tickangle=45, row=2, col=2)

    fig.show()

    return fig


class PDFReportGenerator:
    """Generate professional PDF reports for executive presentation"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1E3A8A'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#1E3A8A'),
            spaceAfter=12,
            spaceBefore=12
        ))

    def generate_report(self, analysis: Dict, filename: str = None) -> str:
        """Generate comprehensive PDF report"""
        if filename is None:
            filename = f"cfo_cud_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []

        # Title Page
        company_name = self.config_manager.get('company', {}).get('name', 'Your Company')
        story.append(Paragraph("Cloud FinOps CUD Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"{company_name}", self.styles['Title']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal']))
        story.append(PageBreak())

        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))

        total_spend = sum(analysis['machine_spend_distribution'].values())
        optimal_savings = analysis['total_savings_summary']['optimal_mix']
        savings_percentage = (optimal_savings / total_spend * 100) if total_spend > 0 else 0

        summary_data = [
            ['Metric', 'Value'],
            ['Total Monthly Spend', f"${total_spend:,.2f}"],
            ['Optimal Monthly Savings', f"${optimal_savings:,.2f}"],
            ['Annual Savings Potential', f"${optimal_savings * 12:,.2f}"],
            ['Effective Discount Rate', f"{savings_percentage:.1f}%"],
            ['Machine Types Analyzed', str(len(analysis['machine_spend_distribution']))],
            ['Risk Assessment', analysis['risk_assessment']['overall_risk']]
        ]

        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 20))

        # Top Recommendations
        story.append(Paragraph("Top Recommendations", self.styles['SectionHeader']))

        top_machines = sorted(analysis['savings_by_machine'].items(),
                            key=lambda x: x[1]['resource_cud_3yr']['monthly_savings'],
                            reverse=True)[:5]

        rec_data = [['Machine Type', 'Monthly Spend', 'Recommended Strategy', 'Monthly Savings']]
        for machine_type, savings in top_machines:
            rec_data.append([
                machine_type.upper(),
                f"${savings['monthly_spend']:,.2f}",
                savings['recommendation'],
                f"${savings['resource_cud_3yr']['monthly_savings']:,.2f}"
            ])

        rec_table = Table(rec_data)
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#10B981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(rec_table)
        story.append(PageBreak())

        # Risk Assessment
        story.append(Paragraph("Risk Assessment", self.styles['SectionHeader']))
        story.append(Paragraph(analysis['risk_assessment']['overall_recommendation'], self.styles['Normal']))
        story.append(Spacer(1, 12))

        # Next Steps
        story.append(Paragraph("Next Steps", self.styles['SectionHeader']))
        next_steps = [
            "1. Review machine-specific recommendations in detail",
            "2. Validate utilization patterns for high-value machine types",
            "3. Start with low-risk, high-savings opportunities",
            "4. Implement monitoring before committing to long-term CUDs",
            "5. Consider Flex CUDs for variable workloads"
        ]

        for step in next_steps:
            story.append(Paragraph(step, self.styles['Normal']))
            story.append(Spacer(1, 6))

        # Build PDF
        doc.build(story)

        logger.info(f"✅ PDF Report generated: {filename}")
        return filename
