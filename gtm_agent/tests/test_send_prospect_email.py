import os
from unittest.mock import Mock, patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent.gtm_agent import send_prospect_email


def test_disqualified_prospect_is_blocked_without_message_id():
    runtime = Mock(config={"metadata": {}})
    prospect = {
        "prospect_id": "LEAD-50001",
        "name": "Priya Nair",
        "email": "priya.nair@brightwaveapps.com",
    }

    with patch(
        "gtm_agent.gtm_agent.data_service.get_prospect_record",
        return_value={"prospect_id": "LEAD-50001", "disqualified": True},
    ):
        result = send_prospect_email.func(
            prospect,
            "Invitation to Book a Demo",
            "Please book a demo.",
            runtime,
            from_rep={"name": "Marco Rossi", "email": "marco.rossi@northpoint.com"},
        )

    assert result == {"status": "blocked", "reason": "prospect is flagged disqualified"}


def test_override_sends_to_disqualified_prospect():
    runtime = Mock(config={"metadata": {}})
    prospect = {
        "prospect_id": "LEAD-50001",
        "name": "Priya Nair",
        "email": "priya.nair@brightwaveapps.com",
    }

    with patch(
        "gtm_agent.gtm_agent.data_service.get_prospect_record",
        return_value={"prospect_id": "LEAD-50001", "disqualified": True},
    ):
        result = send_prospect_email.func(
            prospect,
            "Invitation to Book a Demo",
            "Please book a demo.",
            runtime,
            from_rep={"name": "Marco Rossi", "email": "marco.rossi@northpoint.com"},
            override=True,
        )

    assert result["status"] == "sent"
    assert result["message_id"].startswith("msg-")
