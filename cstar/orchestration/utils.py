import re


def slugify(source: str) -> str:
    """Convert a source string into a URL-safe slug.

    Parameters
    ----------
    source : str
        The string to be converted.

    Returns
    -------
    str
        The slugified version of the source string.
    """
    if not source:
        raise ValueError

    alphanumeric = re.sub(r"\W", "", source.casefold())
    return re.sub(r"\s+", "-", alphanumeric)
