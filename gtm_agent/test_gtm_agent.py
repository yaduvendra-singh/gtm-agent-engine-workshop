import unittest
from unittest.mock import patch

from gtm_agent import gtm_agent


class ProspectToolPrivacyTests(unittest.TestCase):
    def test_prospect_tools_exclude_billing_fields(self):
        record = {
            "prospect_id": "LEAD-TEST",
            "name": "Test Prospect",
            "email": "test@example.com",
            "annual_revenue": 1_000_000,
            "enrichment_source": "Test",
            "disqualified": False,
            "billing_qualification": {
                "tax_id": "123-45-6789",
                "date_of_birth": "1990-01-01",
                "card_on_file": "4111111111111111",
                "credit_check_ref": "EXPN-TEST",
            },
            "engagement_history": [],
            "account_details": [],
            "tech_stack": [],
        }
        sensitive_keys = {
            "tax_id",
            "date_of_birth",
            "card_on_file",
            "credit_check_ref",
        }

        with patch.object(gtm_agent.data_service, "get_prospect_record", return_value=record), \
                patch.object(gtm_agent.data_service, "get_profile_from_db", return_value={"prospect_profile": None}), \
                patch.object(gtm_agent.data_service, "fetch_engagement_history", return_value=[]), \
                patch.object(gtm_agent.data_service, "fetch_account_details", return_value=[]), \
                patch.object(gtm_agent.data_service, "fetch_tech_stack", return_value=[]), \
                patch.object(gtm_agent.data_service, "save_profile_to_db"):
            contact_result = gtm_agent.get_prospect.invoke({"prospect_id": "LEAD-TEST"})
            profile_result = gtm_agent.build_prospect_profile.invoke({"prospect_id": "LEAD-TEST"})

        self.assertTrue(sensitive_keys.isdisjoint(contact_result["prospect"]))
        self.assertTrue(sensitive_keys.isdisjoint(profile_result["prospect_profile"]))


if __name__ == "__main__":
    unittest.main()
