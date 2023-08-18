# # ===========================================================================
# #                            Default Scraper
# # ===========================================================================
# # See https://requests.readthedocs.io/en/latest/

# from .scraper import Scraper, CappedException
# from schemas.results import ScrapingResult
# from logging import Logger
# from http import cookiejar
# from charset_normalizer import detect
# import requests
# import time
# import random


# # ---------------------------------------------------------------------------
# #                            COOKIE POLICY
# # ---------------------------------------------------------------------------

# class BlockAll(cookiejar.CookiePolicy):
#     """Defining a cookie policy to reject all cookies"""

#     return_ok = (
#         set_ok
#     ) = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
#     netscape = True
#     rfc2965 = hide_cookie2 = False

# # ---------------------------------------------------------------------------
# #                            SCRAPER
# # ---------------------------------------------------------------------------


# class DefaultParser(Scraper):
#     """Use request package to fetch webpage content"""

#     def __init__(
#         self,
#         name: str = "",
#         logger: Logger = Logger(__name__),
#         timeout: float = 5.0,
#         allow_cookies=False,
#         user_agent=None,
#         proxies=None,
#         max_content_length=52_428_800,  # 50MB
#         max_download_time=300,  # 5 minutes
#         chunk_size=1024,
#     ):
#         self.name = name
#         self.logger = logger
#         self.timeout = timeout
#         self.max_content_length = max_content_length
#         self.max_download_time = max_download_time
#         self.chunk_size = chunk_size

#         # if a user agent is given, then that is the only option in the list
#         if user_agent:
#             self.user_agents = [user_agent]
#         else:
#             self.load_user_agents()
#         self.session = requests.Session()

#         if not allow_cookies:
#             self.session.cookies.set_policy(BlockAll())
#             self.logger.info(f"Worker {name} configured to block all cookies!")

#         if proxies:
#             self.session.proxies.update(proxies)
#             self.logger.info(f"Worker {name} uses proxies: {proxies}")

#     def load_user_agents(self):
#         """Load the user gents file"""

#         # Open the list of user agents
#         with open("user_agents.txt", "r") as file:
#             self.user_agents = [line.strip() for line in file.readlines()]

#     def get(self, result: ScrapingResult) -> ScrapingResult:
#         """Fetch webpage content"""

#         # ------------------- User Agent -------------------

#         # Randomly pull a user agent
#         self.session.headers.update(
#             {"User-Agent": random.choice(self.user_agents)})

#         # ------------------- Request -------------------

#         # Request webpage content
#         request = self.session.get(
#             result.target_url, allow_redirects=True, timeout=self.timeout, stream=True
#         )

#         # ------------------- Check Headers -------------------

#         # Check response size via header:
#         # "Content-Length" is length of content in bytes
#         content_length = request.headers.get("Content-Length")
#         if content_length:
#             if int(content_length) > self.max_content_length:
#                 raise CappedException("Content-Length headers too large : " +
#                                       content_length + " bytes", CappedException.HEADERS_TOO_LARGE)

#         # Check contenty type via header:
#         # "Content-Type" is length of content in bytes
#         content_type = request.headers.get('Content-Type')
#         if content_type:
#             if content_type.startswith('audio/'):
#                 raise CappedException(
#                     "Content-Type is audio: " + content_type + " bytes", CappedException.CONTENT_AUDIO)
#             elif content_type.startswith('video/'):
#                 raise CappedException(
#                     "Content-Type is video: " + content_type + " bytes", CappedException.CONTENT_VIDEO)

#         # ------------------- Read Content Stream  -------------------

#         content_size = 0
#         start_time = time.time()
#         chunks = []

#         # Read stream of webpage content in chunks
#         for chunk in request.iter_content(self.chunk_size):

#             # Abort if response takes to long
#             if time.time() - start_time > self.max_download_time:
#                 raise CappedException(
#                     "Response takes too long to download!", CappedException.TOO_LONG)

#             # Abort if response is too large
#             content_size += len(chunk)
#             if content_size > self.max_content_length:
#                 raise CappedException(
#                     "Response too large: " + content_size + " bytes", CappedException.TOO_LARGE)

#             chunks.append(chunk)

#         # Decode content stream to string
#         joined_chunks = b"".join(chunks)
#         encoding = request.encoding if request.encoding is not None else detect(joined_chunks)[
#             'encoding']

#         try:
#             # if fails (e.g., it could be None), then try recognizing it
#             response_content = joined_chunks.decode(encoding)
#         except:
#             try:
#                 # try utf-8, the most likely
#                 encoding = "utf-8"
#                 response_content = joined_chunks.decode("utf-8")
#             except Exception as e:
#                 # just point there was a decoding error (but this is not a "FAILED",
#                 # request) - maybe there is a way of saving joined_chunks?
#                 response_content = 'DECODING_ERROR'

#         # ------------------- Store Results -------------------

#         result.landing_url = request.url
#         result.status_code = request.status_code
#         result.content_html = response_content  # static.content
#         result.encoding = encoding
#         result.elapsed = request.elapsed.total_seconds()
#         result.headers = request.headers

#         return result
