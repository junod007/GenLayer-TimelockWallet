# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *


class MilestoneReviewer(gl.Contract):
    client_name: str
    milestone_requirement: str
    readme_url: str
    source_code_url: str
    status: str

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

    @gl.public.write
    def submit_evidence(
        self,
        readme_url: str,
        source_code_url: str
    ) -> None:
        self.readme_url = readme_url
        self.source_code_url = source_code_url
        self.status = "SUBMITTED"

    @gl.public.write
    def approve(self) -> None:
        self.status = "APPROVED"
