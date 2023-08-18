# ===========================================================================
#                            Scraper ScrapingResult
# ===========================================================================
# See:
# - Pydantic Schema - https://docs.pydantic.dev/usage/schema/

from pydantic import BaseModel, Field
import datetime


class ScrapingResult(BaseModel):
    """Scraping results"""

    target_url: str = Field(default=None, description="target URL")
    landing_url: str = Field(default=None, description="landing URL")
    content_html: str = Field(
        default=None, description="reference to static content"
    )
    content_text: str = Field(
        default=None, description="reference to extracted content"
    )
    elapsed: float = Field(
        default=None, description="Request: time until request finished"
    )
    encoding: str = Field(
        default=None, description="Request: content encoding")
    headers: list = Field(default=None, description="Request: content headers")
    status_code: int = Field(
        default=None, description="Request: HTTP status code")
    scraped_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        description="Request: request timestemp",
    )


if __name__ == "__main__":
    result = ScrapingResult(
        target_url="www.example.de", landing_url="www.example.de/different"
    )
    print(result)
    print(result.model_dump())
