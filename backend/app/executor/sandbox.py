def validate_language(language: str):

    supported = [
        "python"
    ]

    if language not in supported:
        return False

    return True
