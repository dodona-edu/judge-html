def is_empty_document(document: str) -> bool:
    """Check if a document is empty, not allowing comments"""
    document = document.strip()

    # Completely empty (barring whitespace)
    if not document:
        return True

    # Allow multiline comments
    in_comment = False

    for line in document.splitlines():
        line = line.strip()

        # Line is empty
        if not line:
            continue

        # New comment started
        if line.startswith("<!--"):
            in_comment = True
        elif line.endswith("-->"):
            in_comment = False
        elif not in_comment and line.startswith("<"):
            # At least one line was not a comment
            return False

    # Not a single line was found
    return True
