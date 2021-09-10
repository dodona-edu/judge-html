class HtmlValidationError(Exception):
    """Base class for HTML related exceptions in this module."""
    pass


class LocatableHtmlValidationError(HtmlValidationError):
    def __init__(self, tag_location: [str], position: (int, int)):
        self._tag_location = tag_location
        self.position = position

    def tag_location(self) -> str:
        if self._tag_location:
            return f"located at: {self.fpos()} | {' -> '.join([f'<{x}>' for x in self._tag_location])}"
        else:
            return f"located at: {self.fpos()}"

    def fpos(self) -> str:
        return f"line {self.position[0]} position {self.position[1]}"


class MissingClosingTagError(LocatableHtmlValidationError):
    def __init__(self, tag: str, tag_location: [str], position: (int, int)):
        super(MissingClosingTagError, self).__init__(tag_location, position)
        self.tag = tag

    def __str__(self):
        return f"Missing closing tag for tag <{self.tag}> ({self.tag_location()})"


class InvalidTagError(LocatableHtmlValidationError):
    def __init__(self, invalid_tag: str, tag_location: [str], position: (int, int)):
        super(InvalidTagError, self).__init__(tag_location, position)
        self.invalid_tag = invalid_tag

    def __str__(self):
        return f"Invalid tag: <{self.invalid_tag}> ({self.tag_location()})"


class InvalidAttributeError(LocatableHtmlValidationError):
    def __init__(self, tag: str, invalid_attribute: str, tag_location: [str], position: (int, int)):
        super(InvalidAttributeError, self).__init__(tag_location, position)
        self.tag = tag
        self.invalid_attribute = invalid_attribute

    def __str__(self):
        return f"Invalid attribute for tag <{self.tag}>: {self.invalid_attribute} ({self.tag_location()})"


class MissingRequiredAttributeError(LocatableHtmlValidationError):
    def __init__(self, tag: str, missing_attributes: str, tag_location: [str], position: (int, int)):
        super(MissingRequiredAttributeError, self).__init__(tag_location, position)
        self.tag = tag
        self.missing_attributes = missing_attributes

    def __str__(self):
        return f"Missing required attribute(s) for tag <{self.tag}>: {self.missing_attributes} ({self.tag_location()})"


class MissingRecommendedAttributesWarning(LocatableHtmlValidationError):
    """
    this is a warning, warnings will only be raised at the end
    """
    def __init__(self, tag: str, missing_attributes: str, tag_location: [str], position: (int, int)):
        super(MissingRecommendedAttributesWarning, self).__init__(tag_location, position)
        self.tag = tag
        self.missing_attributes = missing_attributes

    def __str__(self):
        return f"Missing recommended attribute(s) for tag <{self.tag}>: {self.missing_attributes} ({self.tag_location()})"


class Warnings(Exception):
    """
    class made to gather multiple warnings
    """
    def __init__(self):
        self.warnings = []

    def __int__(self, warnings: [Exception]):
        self.warnings = warnings

    def __len__(self):
        return len(self.warnings)

    def __bool__(self):
        return len(self) != 0

    def add(self, warning: Exception):
        self.warnings.append(warning)

    def __str__(self):
        return f"Warnings ({len(self)}):\n{self._print_warnings()}"

    def _print_warnings(self) -> str:
        return "\n".join([str(x) for x in self.warnings])
