# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *


@gl.evm.contract_interface
class Recipient:
    class View:
        pass

    class Write:
        pass


class GenLayerMilestoneEscrow(gl.Contract):

    client: Address
    provider: Address
    milestone_requirement: str

    readme_url: str
    source_code_url: str

    locked_amount: u256

    decision: str
    evaluation_reason: str

    evidence_submitted: bool
    reviewed: bool
    released: bool
    refunded: bool

    def __init__(
        self,
        provider_address: str,
        milestone_requirement: str
    ):
        self.client = gl.message.sender_address
        self.provider = Address(provider_address)
        self.milestone_requirement = milestone_requirement

        self.readme_url = ""
        self.source_code_url = ""

        self.locked_amount = u256(0)

        self.decision = "PENDING"
        self.evaluation_reason = ""

        self.evidence_submitted = False
        self.reviewed = False
        self.released = False
        self.refunded = False


    # ---------------------------------------------------------
    # DEPOSIT / CUSTODY
    # ---------------------------------------------------------

    @gl.public.write.payable
    def deposit(self) -> None:
        amount = gl.message.value

        if amount == u256(0):
            raise gl.vm.UserError(
                "Deposit must be greater than zero"
            )

        if self.reviewed:
            raise gl.vm.UserError(
                "Milestone has already been reviewed"
            )

        self.locked_amount = (
            self.locked_amount + amount
        )


    # ---------------------------------------------------------
    # SUBMIT EVIDENCE
    # ---------------------------------------------------------

    @gl.public.write
    def submit_evidence(
        self,
        readme_url: str,
        source_code_url: str
    ) -> None:

        if gl.message.sender_address != self.client:
            raise gl.vm.UserError(
                "Only the client can submit evidence"
            )

        if self.locked_amount == u256(0):
            raise gl.vm.UserError(
                "No funds are locked"
            )

        if self.reviewed:
            raise gl.vm.UserError(
                "Milestone has already been reviewed"
            )

        if readme_url == "":
            raise gl.vm.UserError(
                "README URL is required"
            )

        if source_code_url == "":
            raise gl.vm.UserError(
                "Source code URL is required"
            )

        self.readme_url = readme_url
        self.source_code_url = source_code_url

        self.evidence_submitted = True
        self.decision = "PENDING"
        self.evaluation_reason = ""


    # ---------------------------------------------------------
    # GENLAYER CONSENSUS REVIEW
    # ---------------------------------------------------------

    @gl.public.write
    def evaluate_milestone(self) -> None:

        if gl.message.sender_address != self.client:
            raise gl.vm.UserError(
                "Only the client can request evaluation"
            )

        if self.locked_amount == u256(0):
            raise gl.vm.UserError(
                "No funds are locked"
            )

        if not self.evidence_submitted:
            raise gl.vm.UserError(
                "No milestone evidence submitted"
            )

        if self.reviewed:
            raise gl.vm.UserError(
                "Milestone has already been reviewed"
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
                    f"Could not fetch README: "
                    f"{readme_response.status_code}"
                )

            if source_response.status_code >= 400:
                raise gl.vm.UserError(
                    f"Could not fetch source code: "
                    f"{source_response.status_code}"
                )

            readme_content = (
                readme_response.body
                .decode("utf-8")[:8000]
            )

            source_content = (
                source_response.body
                .decode("utf-8")[:16000]
            )

            prompt = f"""
You are an independent GenLayer milestone reviewer.

MILESTONE REQUIREMENT:
{requirement}

PROJECT README:
{readme_content}

SOURCE CODE:
{source_content}

The project uses this escrow contract to hold GEN
until a milestone has been independently evaluated.

Evaluate whether the submitted implementation
actually satisfies the milestone requirement.

Check carefully:

1. The milestone requirement is addressed.
2. The submitted source code implements the claimed functionality.
3. Persistent contract state is present where required.
4. Relevant public methods are implemented.
5. GenLayer-specific functionality is genuinely present.
6. The README claims are supported by the source code.
7. The implementation provides a coherent milestone
   workflow involving evidence, evaluation, and settlement.

Do not approve based only on documentation claims.

Return ONLY a JSON object in exactly this format:

{{
    "decision": "APPROVED" or "REJECTED",
    "reason": "brief evidence-based explanation"
}}

Rules:

- APPROVED only when the evidence reasonably demonstrates
  that the milestone requirement is satisfied.
- REJECTED when evidence is missing, inaccessible,
  incomplete, irrelevant, or insufficient.
- The decision must be exactly APPROVED or REJECTED.
- The reason must be a non-empty string.
"""

            result = gl.nondet.exec_prompt(
                prompt,
                response_format="json"
            )

            if not isinstance(result, dict):
                raise gl.vm.UserError(
                    "Invalid consensus response"
                )

            decision = result.get("decision")
            reason = result.get("reason")

            if decision not in (
                "APPROVED",
                "REJECTED"
            ):
                raise gl.vm.UserError(
                    "Invalid consensus decision"
                )

            if not isinstance(reason, str):
                raise gl.vm.UserError(
                    "Invalid consensus reason"
                )

            if len(reason.strip()) == 0:
                raise gl.vm.UserError(
                    "Empty consensus reason"
                )

            return {
                "decision": decision,
                "reason": reason
            }


        def validator_fn(
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

            leader_decision = (
                leader_data.get("decision")
            )

            leader_reason = (
                leader_data.get("reason")
            )

            if leader_decision not in (
                "APPROVED",
                "REJECTED"
            ):
                return False

            if not isinstance(
                leader_reason,
                str
            ):
                return False

            if len(
                leader_reason.strip()
            ) == 0:
                return False

            # Independent validator evaluation
            validator_result = leader_fn()

            validator_decision = (
                validator_result.get("decision")
            )

            if validator_decision not in (
                "APPROVED",
                "REJECTED"
            ):
                return False

            # Consensus is based on the stable decision.
            return (
                validator_decision
                == leader_decision
            )


        result = gl.vm.run_nondet_unsafe(
            leader_fn,
            validator_fn
        )

        self.decision = result["decision"]
        self.evaluation_reason = result["reason"]
        self.reviewed = True


    # ---------------------------------------------------------
    # SETTLEMENT
    # ---------------------------------------------------------

    @gl.public.write
    def settle(self) -> None:

        if not self.reviewed:
            raise gl.vm.UserError(
                "Milestone has not been reviewed"
            )

        if self.locked_amount == u256(0):
            raise gl.vm.UserError(
                "No funds available for settlement"
            )

        if self.released or self.refunded:
            raise gl.vm.UserError(
                "Escrow has already been settled"
            )

        amount = self.locked_amount

        if self.decision == "APPROVED":

            Recipient(
                self.provider
            ).emit_transfer(
                value=amount
            )

            self.released = True
            self.locked_amount = u256(0)

        elif self.decision == "REJECTED":

            Recipient(
                self.client
            ).emit_transfer(
                value=amount
            )

            self.refunded = True
            self.locked_amount = u256(0)

        else:
            raise gl.vm.UserError(
                "Invalid milestone decision"
            )


    # ---------------------------------------------------------
    # VIEWS
    # ---------------------------------------------------------

    @gl.public.view
    def get_client(self) -> str:
        return self.client.as_hex


    @gl.public.view
    def get_provider(self) -> str:
        return self.provider.as_hex


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
    def get_locked_amount(self) -> u256:
        return self.locked_amount


    @gl.public.view
    def get_contract_balance(self) -> u256:
        return self.balance


    @gl.public.view
    def get_decision(self) -> str:
        return self.decision


    @gl.public.view
    def get_evaluation_reason(self) -> str:
        return self.evaluation_reason


    @gl.public.view
    def get_status(self) -> str:

        if self.released:
            return "RELEASED"

        if self.refunded:
            return "REFUNDED"

        if not self.evidence_submitted:
            return "AWAITING_EVIDENCE"

        if not self.reviewed:
            return "AWAITING_REVIEW"

        if self.decision == "APPROVED":
            return "APPROVED_AWAITING_SETTLEMENT"

        if self.decision == "REJECTED":
            return "REJECTED_AWAITING_REFUND"

        return "PENDING"
