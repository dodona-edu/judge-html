import json
from html.parser import HTMLParser
from exceptions.htmlExceptions import *

REQUIRED_ATR_KEY = "required"
ALL_ATR_KEY = "all"


class HtmlValidator(HTMLParser):
    """
    this class checks the following when text is fed to it (.feed(text)):
      IMPLEMENTED
      * each tag that opens must have a corresponding closing tag
      * valid tag
      NOT IMPLEMENTED
      * each tag has valid attributes
    """

    def __init__(self):
        super().__init__()
        self.tag_stack = []
        with open("html_tags_attributes.json", "r") as f:
            self.valid_dict = json.load(f)

    def validate(self, text: str):
        self.reset()
        self.feed(text)

    def error(self, error: HtmlValidationError):  # make exception classes and throw these instead
        raise error

    def handle_starttag(self, tag: str, attributes: [(str, str)]):
        self._valid_tag(tag)
        # already append, because the tag is valid,
        #  this way the tag stack is updated for a more accurate location of the error messages
        self.tag_stack.append(tag)
        self._valid_attributes(tag, attributes)

    def handle_endtag(self, tag: str):
        self._validate_corresponding_tag(tag)
        self.tag_stack.pop()

    def handle_data(self, data: str):
        pass  # we don't need to ook at data

    def _validate_corresponding_tag(self, tag: str):
        """validate that each tag that opens has a corresponding closing tag
        """
        if tag != self.tag_stack[-1]:
            self.error(MissingClosingTagError(self.tag_stack[-1], self.tag_stack))

    def _valid_tag(self, tag: str):
        """validate that a tag is a valid HTML tag"""
        if tag not in self.valid_dict:
            self.error(InvalidTagError(tag, self.tag_stack))

    def _valid_attributes(self, tag: str, attributes: [(str, str)]):
        """validate that each attribute is a valid attribute for its tag"""

        tag_info = self.valid_dict[tag]
        atrs = [a[0] for a in attributes]  # only the attribute names, not the values

        if REQUIRED_ATR_KEY in tag_info:  # there are required attributes, check if they are present
            for key in tag_info[REQUIRED_ATR_KEY]:
                if key not in atrs:
                    self.error(MissingRequiredAttributeError(tag, key, self.tag_stack))

        if ALL_ATR_KEY in tag_info:  # there are no valid attributes set in the json
            for atr in attributes:  # check if every attribute is a valid attribute
                if not atr[0] in tag_info[ALL_ATR_KEY]:
                    self.error(InvalidAttributeError(tag, atr[0], self.tag_stack))


validator = HtmlValidator()
validator.validate(
    '<!DOCTYPE html><html lang="en"><body><h1>My First Heading</h1><p>My first paragraph.</p></body></html>')
