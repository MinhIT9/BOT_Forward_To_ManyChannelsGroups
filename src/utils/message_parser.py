# src/utils/message_parser.py
import re
from typing import Tuple, Optional

URL_REGEX = r'(https?://[^\s]+)'

def parse_admin_message(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Parses the admin's message to extract the key, title, and URL.
    Returns (key, title, url)
    """
    lines = text.splitlines()
    if not lines:
        return None, None, None

    # Key is always the first line
    key = lines[0].strip()
    if not key.startswith('!'):
        # If the first line is not a key, assume there is no key
        key = '!' # Default to all
        content_lines = lines
    else:
        content_lines = lines[1:]

    url_found = None
    title_lines = []

    # Find the URL and separate it from the title
    for line in content_lines:
        match = re.search(URL_REGEX, line)
        if match and not url_found:
            url_found = match.group(0)
        else:
            title_lines.append(line)

    title = "\n".join(title_lines).strip()

    return key, title, url_found