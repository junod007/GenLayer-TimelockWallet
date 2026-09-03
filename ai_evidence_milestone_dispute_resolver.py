# {
#   "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6"
# }

from genlayer import *
import json


class AIEvidenceMilestoneDisputeResolver(gl.Contract):
    client: Address
    provider: Address

    requirement: str
    evidence_url: str

    evidence_submitted: bool
    dispute_open: bool
    resolved: bool

    decision: str
    reasoning: str
    resolution: str

    def __init__(
        self,
        provider: str,
        requirement: str
    ):
        self.client = gl.message.sender_address
        self.provider = Address(provider)

        self.requirement = requirement
        self.evidence_url = ""

        self.evidence_submitted = False
        self.dispute_open = False
        self.resolved = False

        self.decision = ""
        self.reasoning = ""
        self.resolution = ""

    @gl.public.write
    def submit_evidence(
        self,
        evidence_url: str
    ) -> None:
        if gl.message.sender_address != self.provider:
            raise gl.vm.UserError(
                "Only the provider can submit evidence."
            )

        if self.evidence_submitted:
            raise gl.vm.UserError(
                "Evidence has already been submitted."
            )

        if evidence_url == "":
            raise gl.vm.UserError(
                "Evidence URL cannot be empty."
            )

        self.evidence_url = evidence_url
        self.evidence_submitted = True

    @gl.public.write
    def open_dispute(self) -> None:
        if gl.message.sender_address != self.client:
            raise gl.vm.UserError(
                "Only the client can open a dispute."
            )

        if not self.evidence_submitted:
            raise gl.vm.UserError(
                "No evidence has been submitted yet."
            )

        if self.dispute_open:
            raise gl.vm.UserError(
                "Dispute is already open."
            )

        if self.resolved:
            raise gl.vm.UserError(
                "Dispute has already been resolved."
            )

        self.dispute_open = True

    @gl.public.write
    def resolve_dispute(self) -> None:
        if not self.dispute_open:
            raise gl.vm.UserError(
                "No dispute is currently open."
            )

        if self.resolved:
            raise gl.vm.UserError(
                "Dispute has already been resolved."
            )

        requirement = self.requirement
        evidence_url = self.evidence_url

        def evaluate_evidence():
            response = gl.nondet.web.get(
                evidence_url
            )

            evidence = response.body.decode(
                "utf-8"
            )

            prompt = f"""
You are an impartial milestone dispute evaluator.

Requirement:
{requirement}

Evidence source:
{evidence_url}

Evidence content:
{evidence[:12000]}

Determine whether the evidence satisfies the requirement.

Return valid JSON only using exactly this structure:

{{
    "decision": "APPROVE",
    "reasoning": "brief evidence-based explanation",
    "resolution": "RELEASE_TO_PROVIDER"
}}

Use one of these decision values:
- APPROVE
- REJECT

Use one of these resolution values:
- RELEASE_TO_PROVIDER
- REFUND_TO_CLIENT

Rules:
- If the evidence satisfies the requirement, use APPROVE and RELEASE_TO_PROVIDER.
- If the evidence does not satisfy the requirement, use REJECT and REFUND_TO_CLIENT.
"""

            result = gl.nondet.exec_prompt(
                prompt,
                response_format="json"
            )

            if isinstance(result, str):
                data = json.loads(result)
            else:
                data = result

            if not isinstance(data, dict):
                raise gl.vm.UserError(
                    "AI returned an invalid result."
                )

            if "decision" not in data:
                raise gl.vm.UserError(
                    "AI result is missing decision."
                )

            if "reasoning" not in data:
                raise gl.vm.UserError(
                    "AI result is missing reasoning."
                )

            if "resolution" not in data:
                raise gl.vm.UserError(
                    "AI result is missing resolution."
                )

            return {
                "decision": str(data["decision"]),
                "reasoning": str(data["reasoning"]),
                "resolution": str(data["resolution"])
            }

        def validate_result(
            leader_result
        ) -> bool:
            if not isinstance(
                leader_result,
                gl.vm.Return
            ):
                return False

            leader_data = leader_result.calldata

            if not isinstance(
                leader_data,
                dict
            ):
                return False

            if (
                "decision" not in leader_data
                or "reasoning" not in leader_data
                or "resolution" not in leader_data
            ):
                return False

            if (
                leader_data["decision"]
                not in ["APPROVE", "REJECT"]
            ):
                return False

            if (
                leader_data["resolution"]
                not in [
                    "RELEASE_TO_PROVIDER",
                    "REFUND_TO_CLIENT"
                ]
            ):
                return False

            validator_data = evaluate_evidence()

            return (
                leader_data["decision"]
                == validator_data["decision"]
                and
                leader_data["resolution"]
                == validator_data["resolution"]
            )

        result = gl.vm.run_nondet_unsafe(
            evaluate_evidence,
            validate_result
        )

        self.decision = result["decision"]
        self.reasoning = result["reasoning"]
        self.resolution = result["resolution"]

        self.resolved = True
        self.dispute_open = False

    @gl.public.view
    def get_contract_state(
        self
    ) -> dict[str, str]:
        return {
            "client": self.client.as_hex,
            "provider": self.provider.as_hex,
            "requirement": self.requirement,
            "evidence_url": self.evidence_url,
            "evidence_submitted": str(
                self.evidence_submitted
            ),
            "dispute_open": str(
                self.dispute_open
            ),
            "resolved": str(
                self.resolved
            ),
            "decision": self.decision,
            "reasoning": self.reasoning,
            "resolution": self.resolution
        }
