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
    def __init__(self, invalid_tag: str, tag_location: [str]):
        super(InvalidTagError, self).__init__(tag_location)
        self.invalid_tag = invalid_tag

    def __str__(self):
        return f"Invalid tag: <{self.invalid_tag}> ({self.tag_location()})"


class InvalidAttributeError(LocatableHtmlValidationError):
    def __init__(self, tag: str, invalid_attribute: str, tag_location: [str]):
        super(InvalidAttributeError, self).__init__(tag_location)
        self.tag = tag
        self.invalid_attribute = invalid_attribute

    def __str__(self):
        return f"Invalid attribute for tag <{self.tag}>: {self.invalid_attribute} ({self.tag_location()})"


class MissingRequiredAttributeError(LocatableHtmlValidationError):
    def __init__(self, tag: str, missing_attributes: str, tag_location: [str]):
        super(MissingRequiredAttributeError, self).__init__(tag_location)
        self.tag = tag
        self.missing_attributes = missing_attributes

    def __str__(self):
        return f"Missing required attribute(s) for tag <{self.tag}>: {self.missing_attributes} ({self.tag_location()})"


class MissingRecommendedAttributeError(LocatableHtmlValidationError):
    def __init__(self, tag: str, missing_attributes: str, tag_location: [str]):
        super(MissingRecommendedAttributeError, self).__init__(tag_location)
        self.tag = tag
        self.missing_attributes = missing_attributes

    def __str__(self):
        return f"Missing recommended attribute(s) for tag <{self.tag}>: {self.missing_attributes} ({self.tag_location()})"
