import re
import typing as t


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


def deep_merge(d1: dict[str, t.Any], d2: dict[str, t.Any]) -> dict[str, t.Any]:
    """Deep merge two dictionaries.

    Parameters
    ----------
    d1 : dict[str, t.Any]
        The first dictionary.
    d2 : dict[str, t.Any]
        The second dictionary.

    Returns
    -------
    dict[str, t.Any]
        The merged dictionaries.
    """
    for k, v in d2.items():
        if isinstance(v, dict):
            d1[k] = deep_merge(d1.get(k, {}), v)
        else:
            d1[k] = v
    return d1
