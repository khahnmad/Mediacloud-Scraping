# ===========================================================================
#                            Generic Scraper Class
# ===========================================================================

from abc import ABC, abstractmethod


class CappedException(Exception):
    TOO_LARGE = "TOO_LARGE"
    TOO_LONG = "TOO_LONG"
    HEADERS_TOO_LARGE = "HEADERS_TOO_LARGE"
    CONTENT_AUDIO = "CONTENT_AUDIO"
    CONTENT_VIDEO = "CONTENT_VIDEO"

    def __init__(self, message, capped_type):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Capped type
        self.capped_type = capped_type


class Scraper(ABC):
    """Abstract scraper class"""

    def __init__(self):
        pass

    @abstractmethod
    def get(self, url):
        pass
