# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *


class AIMilestoneEscrow(gl.Contract):
    client_name: str
    milestone_requirement: str
    evidence_url: str
    decision: str
    evaluation_reason: str
    reviewed: bool

    def __init__(
        self,
        client_name: str,
        milestone_requirement: str
    ):
        self.client_name = client_name
        self.milestone_requirement = milestone_requirement
        self.evidence_url = ""
        self.decision = "PENDING"
        self.evaluation_reason = ""
        self.reviewed = False

    @gl.public.write
    def submit_evidence(self, url: str) -> None:
        self.evidence_url = url
        self.decision = "PENDING"
        self.evaluation_reason = ""
        self.reviewed = False

    @gl.public.write
    def evaluate_milestone(self) -> None:
        if self.evidence_url == "":
            raise gl.vm.UserError("No evidence URL submitted")

        url = self.evidence_url
        requirement = self.milestone_requirement

        def leader_fn():
            response = gl.nondet.web.get(url)

            if response.status_code >= 400:
                raise gl.vm.UserError(
                    f"Could not fetch evidence: {response.status_code}"
                )

            content = response.body.decode("utf-8")

            # Batasi konten agar prompt tidak terlalu besar
            evidence = content[:12000]

            prompt = f"""
You are an independent project milestone reviewer.

MILESTONE REQUIREMENT:
{requirement}

SUBMITTED EVIDENCE:
{evidence}

Evaluate whether the submitted evidence reasonably demonstrates
that the milestone requirement has been satisfied.

Return ONLY a JSON object in this exact structure:

{{
    "decision": "APPROVED" or "REJECTED",
    "reason": "brief explanation"
}}

Rules:
1. APPROVED only when the evidence reasonably demonstrates
   that the requirement has been satisfied.
2. REJECTED when the evidence is missing, irrelevant,
   incomplete, inaccessible, or insufficient.
3. Do not assume features that are not visible in the evidence.
4. The decision must be exactly APPROVED or REJECTED.
"""

            result = gl.nondet.exec_prompt(
                prompt,
                response_format="json"
            )

            if not isinstance(result, dict):
                raise gl.vm.UserError("Invalid LLM response")

            if result.get("decision") not in (
                "APPROVED",
                "REJECTED"
            ):
                raise gl.vm.UserError("Invalid decision")

            if not isinstance(result.get("reason"), str):
                raise gl.vm.UserError("Invalid reason")

            return result

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False

            leader_data = leader_result.calldata

            if not isinstance(leader_data, dict):
                return False

            leader_decision = leader_data.get("decision")

            if leader_decision not in (
                "APPROVED",
                "REJECTED"
            ):
                return False

            # Validator melakukan evaluasi independen:
            # fetch evidence + LLM review ulang
            validator_data = leader_fn()

            validator_decision = validator_data.get("decision")

            if validator_decision not in (
                "APPROVED",
                "REJECTED"
            ):
                return False

            # Consensus hanya membutuhkan keputusan utama sama.
            # Reason boleh berbeda antar model/validator.
            return validator_decision == leader_decision

        result = gl.vm.run_nondet_unsafe(
            leader_fn,
            validator_fn
        )

        self.decision = result["decision"]
        self.evaluation_reason = result["reason"]
        self.reviewed = True

    @gl.public.view
    def get_milestone(self) -> str:
        return self.milestone_requirement

    @gl.public.view
    def get_evidence_url(self) -> str:
        return self.evidence_url

    @gl.public.view
    def get_decision(self) -> str:
        return self.decision

    @gl.public.view
    def get_evaluation_reason(self) -> str:
        return self.evaluation_reason

    @gl.public.view
    def get_status(self) -> str:
        if not self.reviewed:
            return "PENDING"

        return self.decision
