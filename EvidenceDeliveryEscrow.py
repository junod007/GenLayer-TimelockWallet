# {
#   "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6"
# }

from genlayer import *
import json


class EvidenceDeliveryEscrow(gl.Contract):

    client: str
    provider: str
    amount: u256

    requirement: str
    evidence_url: str
    decision: str

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
        self.decision = "pending"

        self.evidence_submitted = False
        self.reviewed = False
        self.released = False
        self.refunded = False


    @gl.public.view
    def get_status(self) -> str:
        return self.decision


    @gl.public.view
    def get_evidence(self) -> str:
        return self.evidence_url


    @gl.public.view
    def get_amount(self) -> u256:
        return self.amount


    @gl.public.write
    def submit_evidence(self, url: str) -> str:
        if str(gl.message.sender_address).lower() != self.provider.lower():
            raise Exception("Only provider can submit evidence")

        if self.released or self.refunded:
            raise Exception("Escrow is already settled")

        if len(url) == 0:
            raise Exception("Evidence URL cannot be empty")

        self.evidence_url = url
        self.evidence_submitted = True
        self.reviewed = False
        self.decision = "evidence_submitted"

        return "Evidence submitted"


    @gl.public.write
    def review_evidence(self) -> str:
        if not self.evidence_submitted:
            raise Exception("No evidence submitted")

        if self.released or self.refunded:
            raise Exception("Escrow is already settled")

        requirement = self.requirement
        evidence_url = self.evidence_url


        def evaluate():
            prompt = f"""
You are reviewing delivery evidence for an escrow contract.

Contract requirement:
{requirement}

Evidence URL:
{evidence_url}

Visit and analyze the evidence URL when possible.

Decide whether the evidence meaningfully demonstrates that the provider
has satisfied the stated requirement.

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
The decision must be based on the submitted evidence and the escrow
requirement. Approve only when the evidence reasonably demonstrates
that the requirement has been satisfied. Reject evidence that is
missing, irrelevant, inaccessible, or insufficient.
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

        if not self.reviewed:
            raise Exception("Evidence has not been reviewed")

        if self.decision != "approved":
            raise Exception("Evidence was not approved")

        if self.released or self.refunded:
            raise Exception("Escrow is already settled")

        self.released = True

        return "Payment approved for release"


    @gl.public.write
    def refund_client(self) -> str:
        if str(gl.message.sender_address).lower() != self.client.lower():
            raise Exception("Only client can request refund")

        if self.released or self.refunded:
            raise Exception("Escrow is already settled")

        self.refunded = True
        self.decision = "refunded"

        return "Refund approved"
