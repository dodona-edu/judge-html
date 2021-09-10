import json
from html.parser import HTMLParser
from exceptions.htmlExceptions import *
from os import path

# Location of this test file
base_path = path.dirname(__file__)
# keynames for the json
REQUIRED_ATR_KEY = "required_attributes"
RECOMMENDED_ATR_KEY = "recommended_attributes"


class HtmlValidator(HTMLParser):
    """
    this class checks the following:
      * each tag that opens must have a corresponding closing tag
      * is the tag a valid tag
      * required attributes (to be completed in the json)
      * recommended attributes (to be completed in the json)
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.warnings = Warnings()
        self.tag_stack = []
        with open(path.abspath(path.join(base_path, "html_tags_attributes.json")), "r") as f:
            self.valid_dict = json.load(f)

        self.check_required = kwargs.get("required", True)
        self.check_recommended = kwargs.get("recommended", True)

    def validate_fpath(self, source_filepath: str):
        with open(source_filepath, "r") as f:
            self._validate(f.read())
            if self.warnings:
                raise self.warnings

    def validate_content(self, content: str):
        self._validate(content)
        if self.warnings:
            raise self.warnings

    def _validate(self, text: str):
        self.reset()
        self.feed(text)

    def error(self, error: HtmlValidationError):  # make exception classes and throw these instead
        raise error

    def warning(self, warning: HtmlValidationError):
        self.warnings.add(warning)

    def handle_starttag(self, tag: str, attributes: [(str, str)]):
        if tag == "meta":
            return
        self._valid_tag(tag)
        # already append, because the tag is valid,
        #  this way the tag stack is updated for a more accurate location of the error messages
        self.tag_stack.append(tag)
        self._valid_attributes(tag, set(a[0] for a in attributes))

    def handle_endtag(self, tag: str):
        self._validate_corresponding_tag(tag)
        self.tag_stack.pop()

    def handle_data(self, data: str):
        pass  # we don't need to ook at data

    def _validate_corresponding_tag(self, tag: str):
        """validate that each tag that opens has a corresponding closing tag
        """
        if tag != self.tag_stack[-1]:
            self.error(MissingClosingTagError(self.tag_stack[-1], self.tag_stack, self.getpos()))

    def _valid_tag(self, tag: str):
        """validate that a tag is a valid HTML tag"""
        if tag not in self.valid_dict:
            self.error(InvalidTagError(tag, self.tag_stack, self.getpos()))

    def _valid_attributes(self, tag: str, attributes: set[str]):
        """validate attributes"""
        tag_info = self.valid_dict[tag]

        if self.check_required:
            required = set(tag_info[REQUIRED_ATR_KEY]) if REQUIRED_ATR_KEY in tag_info else set()
            if missing_req := (required - attributes):
                self.error(MissingRequiredAttributeError(tag, ", ".join(missing_req), self.tag_stack, self.getpos()))

        if self.check_recommended:
            recommended = set(tag_info[RECOMMENDED_ATR_KEY]) if RECOMMENDED_ATR_KEY in tag_info else set()
            if missing_rec := (recommended - attributes):
                self.warning(MissingRecommendedAttributesWarning(tag, ", ".join(missing_rec), self.tag_stack.copy(), self.getpos()))
