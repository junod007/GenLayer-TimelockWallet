# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *


@gl.evm.contract_interface
class _Recipient:
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


    # ============================================================
    # DEPOSIT
    # ============================================================

    @gl.public.write.payable
    def deposit(self) -> None:

        if gl.message.sender_address != self.client:
            raise gl.vm.UserError(
                "Only the client can deposit"
            )

        if self.locked_amount != u256(0):
            raise gl.vm.UserError(
                "Escrow is already funded"
            )

        amount = gl.message.value

        if amount == u256(0):
            raise gl.vm.UserError(
                "Deposit must be greater than zero"
            )

        self.locked_amount = amount


    # ============================================================
    # SUBMIT EVIDENCE
    # ============================================================

    @gl.public.write
    def submit_evidence(
        self,
        readme_url: str,
        source_code_url: str
    ) -> None:

        if gl.message.sender_address != self.provider:
            raise gl.vm.UserError(
                "Only the provider can submit evidence"
            )

        if self.locked_amount == u256(0):
            raise gl.vm.UserError(
                "Escrow has not been funded"
            )

        if self.released:
            raise gl.vm.UserError(
                "Escrow already released"
            )

        if self.refunded:
            raise gl.vm.UserError(
                "Escrow already refunded"
            )

        if readme_url == "":
            raise gl.vm.UserError(
                "README URL cannot be empty"
            )

        if source_code_url == "":
            raise gl.vm.UserError(
                "Source code URL cannot be empty"
            )

        self.readme_url = readme_url
        self.source_code_url = source_code_url

        self.evidence_submitted = True
        self.reviewed = False

        self.decision = "PENDING"
        self.evaluation_reason = ""


    # ============================================================
    # MILESTONE EVALUATION
    # ============================================================

    @gl.public.write
    def evaluate_milestone(self) -> None:

        if self.locked_amount == u256(0):
            raise gl.vm.UserError(
                "Escrow has not been funded"
            )

        if not self.evidence_submitted:
            raise gl.vm.UserError(
                "No evidence submitted"
            )

        if self.released:
            raise gl.vm.UserError(
                "Escrow already released"
            )

        if self.refunded:
            raise gl.vm.UserError(
                "Escrow already refunded"
            )

        readme_url = self.readme_url
        source_code_url = self.source_code_url
        requirement = self.milestone_requirement


        def fetch_and_review():

            readme_response = gl.nondet.web.get(
                readme_url
            )

            source_response = gl.nondet.web.get(
                source_code_url
            )

            if readme_response.status_code >= 400:
                raise gl.vm.UserError(
                    "Could not fetch README evidence"
                )

            if source_response.status_code >= 400:
                raise gl.vm.UserError(
                    "Could not fetch source code evidence"
                )

            readme_content = (
                readme_response.body.decode("utf-8")[:10000]
            )

            source_content = (
                source_response.body.decode("utf-8")[:20000]
            )

            prompt = f"""
You are an independent GenLayer milestone escrow reviewer.

Your task is to determine whether the submitted project evidence
satisfies the milestone requirement.

MILESTONE REQUIREMENT:
{requirement}

README / PROJECT DOCUMENTATION:
{readme_content}

SOURCE CODE:
{source_content}

Evaluate the evidence conservatively.

The implementation should demonstrate:

1. The milestone requirement is actually addressed.
2. The source code implements the claimed functionality.
3. The contract contains persistent state relevant to the milestone.
4. Relevant public methods are implemented.
5. GenLayer-specific functionality is actually used.
6. Native GEN escrow custody is implemented when required.
7. The README claims are supported by the source code.
8. The submitted source code represents a coherent working workflow.

IMPORTANT:

APPROVED only when the evidence reasonably demonstrates
that the milestone requirement is satisfied.

REJECTED when evidence is missing, inaccessible, irrelevant,
incomplete, contradictory, or insufficient.

Do not approve based only on README claims.

Do not assume functionality that is not visible in the source code.

Return ONLY this JSON structure:

{{
    "decision": "APPROVED" or "REJECTED",
    "reason": "brief evidence-based explanation"
}}

The decision MUST be exactly one of:

APPROVED
REJECTED
"""

            result = gl.nondet.exec_prompt(
                prompt,
                response_format="json"
            )

            if not isinstance(result, dict):
                raise gl.vm.UserError(
                    "LLM returned invalid response"
                )

            decision = result.get("decision")
            reason = result.get("reason")

            if decision not in (
                "APPROVED",
                "REJECTED"
            ):
                raise gl.vm.UserError(
                    "Invalid milestone decision"
                )

            if not isinstance(reason, str):
                raise gl.vm.UserError(
                    "Invalid evaluation reason"
                )

            if len(reason.strip()) == 0:
                raise gl.vm.UserError(
                    "Empty evaluation reason"
                )

            return {
                "decision": decision,
                "reason": reason
            }


        # ========================================================
        # VALIDATOR
        # ========================================================

        def validator_fn(leader_result) -> bool:

            # Leader must have returned successfully.
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

            leader_decision = leader_data.get(
                "decision"
            )

            leader_reason = leader_data.get(
                "reason"
            )

            # Validate leader structure.
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


            # Independently reproduce the review.
            try:

                validator_result = fetch_and_review()

            except Exception:
                return False


            validator_decision = validator_result.get(
                "decision"
            )

            if validator_decision not in (
                "APPROVED",
                "REJECTED"
            ):
                return False


            # IMPORTANT:
            #
            # Do NOT compare the natural-language reason.
            #
            # LLM reasoning can legitimately differ between
            # validators.
            #
            # Only compare the stable settlement decision.

            return (
                validator_decision
                == leader_decision
            )


        # ========================================================
        # GENLAYER CONSENSUS
        # ========================================================

        result = gl.vm.run_nondet_unsafe(
            fetch_and_review,
            validator_fn
        )


        if result["decision"] not in (
            "APPROVED",
            "REJECTED"
        ):
            raise gl.vm.UserError(
                "Consensus returned invalid decision"
            )

        self.decision = result["decision"]
        self.evaluation_reason = result["reason"]
        self.reviewed = True


    # ============================================================
    # SETTLEMENT
    # ============================================================

    @gl.public.write
    def settle(self) -> None:

        if not self.reviewed:
            raise gl.vm.UserError(
                "Milestone has not been reviewed"
            )

        if self.locked_amount == u256(0):
            raise gl.vm.UserError(
                "No funds locked"
            )

        if self.released:
            raise gl.vm.UserError(
                "Escrow already released"
            )

        if self.refunded:
            raise gl.vm.UserError(
                "Escrow already refunded"
            )


        amount = self.locked_amount


        if self.decision == "APPROVED":

            # Mark state before emitting settlement.
            self.released = True
            self.locked_amount = u256(0)

            _Recipient(
                self.provider
            ).emit_transfer(
                value=amount
            )

            return


        if self.decision == "REJECTED":

            # Mark state before emitting refund.
            self.refunded = True
            self.locked_amount = u256(0)

            _Recipient(
                self.client
            ).emit_transfer(
                value=amount
            )

            return


        raise gl.vm.UserError(
            "Milestone decision is not settled"
        )


    # ============================================================
    # READ METHODS
    # ============================================================

    @gl.public.view
    def get_client(self) -> str:
        return self.client.as_hex


    @gl.public.view
    def get_provider(self) -> str:
        return self.provider.as_hex


    @gl.public.view
    def get_contract_balance(self) -> u256:
        return self.balance


    @gl.public.view
    def get_locked_amount(self) -> u256:
        return self.locked_amount


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
