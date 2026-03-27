from crewai.tools import BaseTool
from typing import Optional, List, Type
from duckduckgo_search import DDGS
from pydantic import BaseModel, Field, model_validator
from i18n import t

class DuckDuckGoSearchToolInputSchema(BaseModel):
    query: str = Field(..., description=t('tool.search_query'))
    max_results: int = Field(5, description=t('tool.max_results'))
    region: str = Field("fr-fr", description=t('tool.search_region'))
    safesearch: str = Field("moderate", description=t('tool.safesearch'))

class DuckDuckGoSearchToolInputSchemaFull(DuckDuckGoSearchToolInputSchema):
    domains: Optional[List[str]] = Field(default=None, description=t('tool.search_domains'))
    time: Optional[str] = Field(None, description=t('tool.search_time_range'))


class DuckDuckGoSearchTool(BaseTool):
    name: str = t('tool.duckduckgo_search')
    description: str = t('tool.duckduckgo_search_desc')
    args_schema: Type[BaseModel] = DuckDuckGoSearchToolInputSchema

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._generate_description()

    def _run(self, query: str, max_results: int = 5, region: str = "fr-fr",
             safesearch: str = "moderate", time: Optional[str] = None,
             domains: Optional[List[str]] = None) -> str:
        """
        Search the web using DuckDuckGo and return formatted results.

        Args:
            query: The search query string
            max_results: Maximum number of results to return (default: 5)
            region: Region code for localized results (default: wt-wt for worldwide)
            safesearch: SafeSearch setting (off, moderate, strict)
            time: Time range for results (d=day, w=week, m=month, y=year)
            domains: List of domains to filter results by (e.g. ["wikipedia.org", "github.com"])

        Returns:
            A string containing the search results with titles, snippets, and URLs
        """
        try:
            # Initialize the DuckDuckGo Search client
            ddgs = DDGS()

            # Format domains for the query if provided
            domain_filter = ""
            if domains:
                domain_filter = " " + " ".join(f"site:{domain}" for domain in domains)

            # Perform the search with parameters
            results = list(ddgs.text(
                query + domain_filter,
                region=region,
                safesearch=safesearch,
                timelimit=time,
                max_results=max_results
            ))

            # Format the results
            if not results:
                return t('tool.no_results')

            formatted_results = t('tool.search_results_header') + "\n\n"
            for i, result in enumerate(results, 1):
                formatted_results += f"{i}. {result['title']}\n"
                formatted_results += f"   {result['body']}\n"
                formatted_results += f"   URL: {result['href']}\n\n"

            return formatted_results

        except Exception as e:
            return t('tool.error_search', error=str(e))

    def run(self, inputs: DuckDuckGoSearchToolInputSchema):
        return self._run(
            inputs.query,
            inputs.max_results,
            inputs.region,
            inputs.safesearch
        )