class HtmlValidationError(Exception):
    """Base class for HTML related exceptions in this module."""
    pass


class LocatableHtmlValidationError(HtmlValidationError):
    def __init__(self, tag_location: [str]):
        self._tag_location = tag_location

    def tag_location(self) -> str:
        return f"located at: {' -> '.join(self._tag_location)}"


class MissingClosingTagError(LocatableHtmlValidationError):
    def __init__(self, tag: str, tag_location: [str]):
        super(MissingClosingTagError, self).__init__(tag_location)
        self.tag = tag

    def __str__(self):
        return f"Missing closing tag for tag <{self.tag}> ({self.tag_location()})"


class InvalidTagError(LocatableHtmlValidationError):
    def __init__(self, invalid_tag, tag_location: [str]):
        super(InvalidTagError, self).__init__(tag_location)
        self.invalid_tag = invalid_tag

    def __str__(self):
        return f"Invalid tag: <{self.invalid_tag}> (located at: {self.tag_location()})"


class InvalidAttributeError(LocatableHtmlValidationError):
    def __init__(self, tag, invalid_attribute, tag_location: [str]):
        super(InvalidAttributeError, self).__init__(tag_location)
        self.tag = tag
        self.invalid_attribute = invalid_attribute

    def __str__(self):
        return f"Invalid attribute for tag <{self.tag}>: {self.invalid_attribute} (located at: {self.tag_location()})"
