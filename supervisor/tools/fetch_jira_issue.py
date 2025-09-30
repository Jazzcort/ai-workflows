from pydantic import BaseModel, Field
import logging

from beeai_framework.context import RunContext
from beeai_framework.emitter import Emitter
from beeai_framework.tools import ToolOutput, Tool, ToolRunOptions

from ..supervisor_types import Issue, FullIssue
from ..jira_utils import get_issue

logger = logging.getLogger(__name__)


class FetchJiraIssueInput(BaseModel):
    issue_id: str = Field(description="ID of the JIRA issue")
    full: bool = Field(
        description="Indicates whether to retrieve the full issue, including the comments section. If false, only the basic issue details are returned"
    )


class FetchJiraIssueOutput(BaseModel, ToolOutput):
    results: Issue | FullIssue

    def get_text_content(self) -> str:
        return self.model_dump_json(indent=2, exclude_unset=True)

    def is_empty(self) -> bool:
        return False


class FetchJiraIssueTool(
    Tool[FetchJiraIssueInput, ToolRunOptions, FetchJiraIssueOutput]
):
    """
    Tool to fetch JIRA issues.
    """

    name = "fetch_jira_issue"  # type: ignore
    description = "Fetch a JIRA issue"  # type: ignore
    input_schema = FetchJiraIssueInput  # type: ignore

    def _create_emitter(self) -> Emitter:
        return Emitter.root().child(
            namespace=["tool", "search_resultsdb"],
            creator=self,
        )

    async def _run(
        self,
        input: FetchJiraIssueInput,
        options: ToolRunOptions | None,
        context: RunContext,
    ) -> FetchJiraIssueOutput:
        try:
            return FetchJiraIssueOutput(results=get_issue(input.issue_id, input.full))
        except Exception as e:
            logger.exception("Error fetching or parsing JIRA issues: %s", e)
            raise e
