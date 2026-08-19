# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *


class MilestoneReviewer(gl.Contract):
    client_name: str
    milestone_requirement: str
    readme_url: str
    source_code_url: str
    status: str
    evaluation_reason: str

    def __init__(
        self,
        client_name: str,
        milestone_requirement: str
    ):
        self.client_name = client_name
        self.milestone_requirement = milestone_requirement
        self.readme_url = ""
        self.source_code_url = ""
        self.status = "PENDING"
        self.evaluation_reason = ""

    @gl.public.write
    def submit_evidence(
        self,
        readme_url: str,
        source_code_url: str
    ) -> None:
        self.readme_url = readme_url
        self.source_code_url = source_code_url
        self.status = "SUBMITTED"
        self.evaluation_reason = ""

    @gl.public.write
    def review_evidence(self) -> None:
        if self.readme_url == "":
            raise gl.vm.UserError(
                "No README evidence submitted"
            )

        if self.source_code_url == "":
            raise gl.vm.UserError(
                "No source code evidence submitted"
            )

        readme_url = self.readme_url
        source_code_url = self.source_code_url
        requirement = self.milestone_requirement

        def leader_fn():
            readme_response = gl.nondet.web.get(
                readme_url
            )

            source_response = gl.nondet.web.get(
                source_code_url
            )

            if readme_response.status_code >= 400:
                raise gl.vm.UserError(
                    "Could not fetch README"
                )

            if source_response.status_code >= 400:
                raise gl.vm.UserError(
                    "Could not fetch source code"
                )

            readme_content = readme_response.body.decode(
                "utf-8"
            )[:8000]

            source_content = source_response.body.decode(
                "utf-8"
            )[:16000]

            prompt = f"""
You are an independent project milestone reviewer.

MILESTONE REQUIREMENT:
{requirement}

PROJECT DOCUMENTATION:
{readme_content}

SOURCE CODE:
{source_content}

Evaluate whether the submitted evidence reasonably
demonstrates that the milestone requirement has been satisfied.

Return ONLY a JSON object with this structure:

{{
    "decision": "APPROVED" or "REJECTED",
    "reason": "brief explanation"
}}

Rules:
1. APPROVED only when the evidence reasonably demonstrates
that the milestone requirement is satisfied.
2. REJECTED when the evidence is missing, irrelevant,
incomplete, inaccessible, or insufficient.
3. Do not assume functionality that is not visible
in the submitted evidence.
4. The decision must be exactly APPROVED or REJECTED.
"""

            return gl.nondet.exec_prompt(
                prompt,
                response_format="json"
            )

        def validator_fn(leader_result) -> bool:
            if not isinstance(
                leader_result,
                gl.vm.Return
            ):
                return False

            leader_data = leader_result.calldata

            if not isinstance(leader_data, dict):
                return False

            decision = leader_data.get(
                "decision"
            )

            reason = leader_data.get(
                "reason"
            )

            if decision not in (
                "APPROVED",
                "REJECTED"
            ):
                return False

            if not isinstance(reason, str):
                return False

            if len(reason.strip()) == 0:
                return False

            return True

        result = gl.vm.run_nondet_unsafe(
            leader_fn,
            validator_fn
        )

        self.status = result["decision"]
        self.evaluation_reason = result["reason"]

    @gl.public.view
    def get_client_name(self) -> str:
        return self.client_name

    @gl.public.view
    def get_milestone(self) -> str:
        return self.milestone_requirement

    @gl.public.view
    def get_readme_url(self) -> str:
        return self.readme_url

    @gl.public.view
    def get_source_code_url(self) -> str:
        return self.source_code_url

    @gl.public.view
    def get_status(self) -> str:
        return self.status

    @gl.public.view
    def get_evaluation_reason(self) -> str:
        return self.evaluation_reason
