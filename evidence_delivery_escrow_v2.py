# {
#   "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6"
# }

from genlayer import *
import json


@gl.evm.contract_interface
class _Recipient:
    class View:
        pass

    class Write:
        pass


class EvidenceDeliveryEscrowV2(gl.Contract):

    client: str
    provider: str
    amount: u256

    requirement: str
    evidence_url: str
    evidence_content: str
    decision: str

    deposited: bool
    evidence_submitted: bool
    reviewed: bool
    released: bool
    refunded: bool


    def __init__(
        self,
        provider: str,
        amount: u256,
        requirement: str
    ):
        self.client = str(gl.message.sender_address)
        self.provider = provider
        self.amount = amount

        self.requirement = requirement
        self.evidence_url = ""
        self.evidence_content = ""
        self.decision = "pending"

        self.deposited = False
        self.evidence_submitted = False
        self.reviewed = False
        self.released = False
        self.refunded = False


    @gl.public.view
    def get_contract_balance(self) -> u256:
        return self.balance


    @gl.public.write.payable
    def deposit(self) -> str:
        if self.deposited:
            raise Exception("Deposit already made")

        if gl.message.value != self.amount:
            raise Exception("Incorrect deposit amount")

        self.deposited = True
        self.decision = "deposited"

        return "Deposit received"


    @gl.public.write
    def submit_evidence(self, url: str) -> str:
        if str(gl.message.sender_address).lower() != self.provider.lower():
            raise Exception("Only provider can submit evidence")

        if not self.deposited:
            raise Exception("Deposit is required first")

        if self.released or self.refunded:
            raise Exception("Escrow is already settled")

        if len(url) == 0:
            raise Exception("Evidence URL cannot be empty")

        self.evidence_url = url
        self.evidence_content = ""
        self.evidence_submitted = True
        self.reviewed = False
        self.decision = "evidence_submitted"

        return "Evidence submitted"


    @gl.public.write
    def review_evidence(self) -> str:
        if not self.deposited:
            raise Exception("Deposit is required first")

        if not self.evidence_submitted:
            raise Exception("No evidence submitted")

        if self.released or self.refunded:
            raise Exception("Escrow is already settled")

        requirement = self.requirement
        evidence_url = self.evidence_url

        def evaluate():
            response = gl.nondet.web.get(evidence_url)

            if response.status_code >= 400:
                raise Exception(
                    f"Evidence URL returned HTTP {response.status_code}"
                )

            evidence_content = response.body.decode("utf-8")

            if len(evidence_content.strip()) == 0:
                raise Exception("Evidence URL returned empty content")

            evidence_content = evidence_content[:12000]

            prompt = f"""
You are reviewing delivery evidence for an escrow contract.

Contract requirement:
{requirement}

Evidence URL:
{evidence_url}

Retrieved evidence content:
{evidence_content}

Decide whether the retrieved evidence meaningfully demonstrates
that the provider has satisfied the stated requirement.

Return ONLY valid JSON in this exact format:

{{
  "decision": "approved" or "rejected",
  "reason": "short explanation"
}}
"""

            result = gl.nondet.exec_prompt(prompt)

            return json.dumps(
                json.loads(result),
                sort_keys=True
            )

        result = gl.eq_principle.prompt_comparative(
            evaluate,
            principle="""
The decision must be based on the retrieved evidence content
and the escrow requirement.

Approve only when the retrieved evidence reasonably demonstrates
that the requirement has been satisfied.

Reject evidence that is missing, inaccessible, irrelevant,
or insufficient.

Both the web retrieval and the final decision must be grounded
in the submitted evidence URL.
"""
        )

        data = json.loads(result)

        if data["decision"] == "approved":
            self.decision = "approved"
        else:
            self.decision = "rejected"

        self.reviewed = True

        return self.decision


    @gl.public.write
    def release_payment(self) -> str:
        if str(gl.message.sender_address).lower() != self.client.lower():
            raise Exception("Only client can release payment")

        if not self.deposited:
            raise Exception("Deposit is required first")

        if not self.reviewed:
            raise Exception("Evidence has not been reviewed")

        if self.decision != "approved":
            raise Exception("Evidence was not approved")

        if self.released or self.refunded:
            raise Exception("Escrow is already settled")

        if self.balance < self.amount:
            raise Exception("Insufficient escrow balance")

        _Recipient(Address(self.provider)).emit_transfer(
            value=self.amount
        )

        self.released = True
        self.decision = "released"

        return "Payment released"


    @gl.public.write
    def refund_client(self) -> str:
        if str(gl.message.sender_address).lower() != self.client.lower():
            raise Exception("Only client can request refund")

        if not self.deposited:
            raise Exception("Deposit is required first")

        if self.released or self.refunded:
            raise Exception("Escrow is already settled")

        if self.decision != "rejected":
            raise Exception("Refund is only available after rejection")

        if self.balance < self.amount:
            raise Exception("Insufficient escrow balance")

        _Recipient(Address(self.client)).emit_transfer(
            value=self.amount
        )

        self.refunded = True
        self.decision = "refunded"

        return "Refund completed"
