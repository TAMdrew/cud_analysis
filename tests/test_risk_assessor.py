import unittest

from finops_analysis_platform.models import RiskAssessment
from finops_analysis_platform.risk_assessor import RiskAssessor


class TestRiskAssessor(unittest.TestCase):
    """Test suite for the RiskAssessor class."""

    def setUp(self):
        """Set up a test instance of the risk assessor."""
        self.risk_assessor = RiskAssessor()

    def test_assess_risk(self):
        """Test the risk assessment logic."""
        savings_by_machine = {
            "n1": {"monthly_spend": 300},
            "e2": {"monthly_spend": 50},
            "gpu": {"monthly_spend": 100},
        }
        risk_assessment = self.risk_assessor.assess_risk(savings_by_machine)

        self.assertIsInstance(risk_assessment, RiskAssessment)
        self.assertEqual(risk_assessment.overall_risk, "MEDIUM")

    def test_assess_risk_low(self):
        """Test the risk assessment logic for a low-risk outcome."""
        savings_by_machine = {
            "n1": {"monthly_spend": 300},
            "e2": {"monthly_spend": 50},
            "c2": {"monthly_spend": 100},
        }
        risk_assessment = self.risk_assessor.assess_risk(savings_by_machine)
        self.assertEqual(risk_assessment.overall_risk, "LOW")

    def test_assess_risk_high(self):
        """Test the risk assessment logic for a high-risk outcome."""
        savings_by_machine = {
            "n1": {"monthly_spend": 100},
            "gpu": {"monthly_spend": 300},
            "a2": {"monthly_spend": 100},
        }
        risk_assessment = self.risk_assessor.assess_risk(savings_by_machine)
        self.assertEqual(risk_assessment.overall_risk, "HIGH")

    def test_assess_risk_no_data(self):
        """Test the risk assessment with no input data."""
        risk_assessment = self.risk_assessor.assess_risk({})
        self.assertEqual(risk_assessment.overall_risk, "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
