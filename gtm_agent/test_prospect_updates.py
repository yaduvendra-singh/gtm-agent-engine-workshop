import json
import os
import pathlib
import sys
import types

os.environ.setdefault("OPENAI_API_KEY", "test-key")
package = types.ModuleType("gtm_agent")
package.__path__ = [str(pathlib.Path(__file__).parent)]
sys.modules.setdefault("gtm_agent", package)

from gtm_agent import data_service
from gtm_agent import gtm_agent


class _ScoringResult:
    def model_dump(self):
        return {"score": 100.0, "max_score": 100, "justification": "Okta is present."}


class _ScoringStub:
    def __init__(self):
        self.user_content = None

    def invoke(self, messages):
        self.user_content = messages[1]["content"]
        return _ScoringResult()


def test_update_persists_and_scoring_uses_rebuilt_profile(monkeypatch):
    prospect_id = "LEAD-90001"
    technology = "Okta"
    record = data_service.PROSPECTS[prospect_id]
    original_stack = list(record["tech_stack"])
    data_service._PROFILES.pop(prospect_id, None)

    try:
        result = data_service.update_prospect_info(prospect_id, technology)
        assert result["updated"] is True
        assert technology in data_service.fetch_tech_stack(prospect_id)

        profile = gtm_agent.build_prospect_profile.invoke({"prospect_id": prospect_id})[
            "prospect_profile"
        ]
        scorer = _ScoringStub()
        monkeypatch.setattr(gtm_agent, "_scoring_llm", scorer)

        gtm_agent.score_prospect.invoke(
            {"prospect_profile": profile, "offering": data_service.OFFERINGS["OFFER-10007"]}
        )

        scored_profile = json.loads(scorer.user_content.split("\n\nProspect profile:\n", 1)[1])
        assert technology in scored_profile["tech_stack"]
        assert technology not in (
            set(data_service.OFFERINGS["OFFER-10007"]["required_tech_stack"])
            - set(scored_profile["tech_stack"])
        )
    finally:
        record["tech_stack"] = original_stack
        data_service._PROFILES.pop(prospect_id, None)
