# {
#   "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6"
# }

from genlayer import *


@gl.evm.contract_interface
class _Recipient:
    class View:
        pass

    class Write:
        pass


class GenLayerMilestoneEscrowV3(gl.Contract):

    client: Address
    provider: Address

    milestone_requirement: str

    readme_url: str
    source_code_url: str

    locked_amount: u256

    evidence_submitted: bool
    reviewed: bool
    released: bool
    refunded: bool

    decision: str
    evaluation_reason: str

    def __init__(
        self,
        client: Address,
        provider: Address,
        milestone_requirement: str,
        readme_url: str,
        source_code_url: str
    ) -> None:

        self.client = client
        self.provider = provider

        self.milestone_requirement = milestone_requirement

        self.readme_url = readme_url
        self.source_code_url = source_code_url

        self.locked_amount = u256(0)

        self.evidence_submitted = False
        self.reviewed = False
        self.released = False
        self.refunded = False

        self.decision = "PENDING"
        self.evaluation_reason = ""


    # ============================================================
    # DEPOSIT
    # ============================================================

    @gl.public.write.payable
    def deposit(self) -> None:

        amount = gl.message.value

        if amount == u256(0):
            raise gl.vm.UserError(
                "Deposit amount must be greater than zero"
            )

        if self.reviewed:
            raise gl.vm.UserError(
                "Milestone already reviewed"
            )

        self.locked_amount = (
            self.locked_amount + amount
        )


    # ============================================================
    # SUBMIT EVIDENCE
    # ============================================================

    @gl.public.write
    def submit_evidence(self) -> None:

        if self.locked_amount == u256(0):
            raise gl.vm.UserError(
                "Escrow has not been funded"
            )

        if self.reviewed:
            raise gl.vm.UserError(
                "Milestone already reviewed"
            )

        self.evidence_submitted = True


    # ============================================================
    # AI REVIEW
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

        if self.reviewed:
            raise gl.vm.UserError(
                "Milestone already reviewed"
            )


        requirement = self.milestone_requirement
        readme_url = self.readme_url
        source_code_url = self.source_code_url


        def review():

            # ----------------------------------------------------
            # FETCH README
            # ----------------------------------------------------

            readme_response = gl.nondet.web.get(
                readme_url
            )

            if readme_response.status_code >= 400:
                raise gl.vm.UserError(
                    "Could not fetch README evidence"
                )


            # ----------------------------------------------------
            # FETCH SOURCE CODE
            # ----------------------------------------------------

            source_response = gl.nondet.web.get(
                source_code_url
            )

            if source_response.status_code >= 400:
                raise gl.vm.UserError(
                    "Could not fetch source code evidence"
                )


            readme_content = (
                readme_response.body
                .decode("utf-8")
                [:12000]
            )

            source_content = (
                source_response.body
                .decode("utf-8")
                [:25000]
            )


            # ----------------------------------------------------
            # REVIEW PROMPT
            # ----------------------------------------------------

            prompt = f"""
You are an independent GenLayer milestone escrow reviewer.

Determine whether the submitted project evidence satisfies
the milestone requirement.

MILESTONE REQUIREMENT:
{requirement}

README:
{readme_content}

SOURCE CODE:
{source_content}

Evaluate conservatively.

APPROVE only if the evidence clearly demonstrates that the
milestone requirement has been implemented.

Check:

1. The milestone requirement is addressed.
2. The source code implements the claimed functionality.
3. Relevant persistent contract state exists.
4. Relevant public methods exist.
5. GenLayer-specific functionality is actually used.
6. Native GEN escrow functionality is implemented.
7. README claims are supported by the source code.
8. The workflow is coherent.

Do NOT approve based only on README claims.

Do NOT assume functionality that is not visible in the source.

Return ONLY this JSON object:

{{
    "decision": "APPROVED",
    "reason": "brief evidence-based explanation"
}}

OR:

{{
    "decision": "REJECTED",
    "reason": "brief evidence-based explanation"
}}

The decision MUST be exactly:

APPROVED

or:

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


            decision = result.get(
                "decision"
            )

            reason = result.get(
                "reason"
            )


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

        def validator_fn(
            leader_result
        ) -> bool:

            if not isinstance(
                leader_result,
                gl.vm.Return
            ):
                return False


            leader_data = (
                leader_result.calldata
            )


            if not isinstance(
                leader_data,
                dict
            ):
                return False


            leader_decision = (
                leader_data.get(
                    "decision"
                )
            )


            leader_reason = (
                leader_data.get(
                    "reason"
                )
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


            # Validator independently performs
            # the same evidence review.

            try:

                validator_result = review()

            except Exception:

                return False


            validator_decision = (
                validator_result.get(
                    "decision"
                )
            )


            if validator_decision not in (
                "APPROVED",
                "REJECTED"
            ):
                return False


            # IMPORTANT:
            #
            # Reason is NOT compared.
            #
            # Only the stable decision is compared.

            return (
                validator_decision
                == leader_decision
            )


        # ========================================================
        # GENLAYER CONSENSUS
        # ========================================================

        result = gl.vm.run_nondet_unsafe(
            review,
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

        self.evaluation_reason = (
            result["reason"]
        )

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

            self.released = True
            self.locked_amount = u256(0)

            _Recipient(
                self.provider
            ).emit_transfer(
                value=amount
            )

            return


        if self.decision == "REJECTED":

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
