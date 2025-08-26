import unittest

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

        self.assertIn("overall_risk", risk_assessment)
        self.assertEqual(risk_assessment["overall_risk"], "MEDIUM")


if __name__ == "__main__":
    unittest.main()
