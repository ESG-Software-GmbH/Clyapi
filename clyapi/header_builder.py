def build_headers(env_setup, overrides=None, remove=None):
    """
    Build standardized headers for requests, with optional overrides.
    Automatically includes Authorization and EntityId (if needed).

    :param env_setup: dict returned by env_setup fixture
    :param overrides: dict of additional or overriding headers
    :return: dict of headers
    """
    headers = {
        "Authorization": f"Bearer {env_setup['token']}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Add EntityId only for parent institutions acting on a child
    if env_setup["institution_type"] == "parent" and env_setup["entity_type"]:
        headers["EntityId"] = env_setup["entity_type"]

    # Apply custom overrides (e.g. Accept header, Content-Type etc.)
    if overrides:
        headers.update(overrides)
    # Remove specific keys
    if remove:
        for key in remove:
            headers.pop(key, None)

    return headers
