from urllib.parse import urlencode


def get_error_redirect(path: str, error: str, message: str) -> str:
    """Create an error redirect URL with query parameters.

    Args:
        path (str): Base path to redirect to
        error (str): Error message or code
        message (str): User-friendly error message

    Returns:
        str: URL with error parameters
    """
    query_params = {"error": error, "message": message}

    # Ensure path starts with /
    if not path.startswith("/"):
        path = f"/{path}"

    return f"{path}?{urlencode(query_params)}"
