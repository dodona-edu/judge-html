import json
from html.parser import HTMLParser
from exceptions.htmlExceptions import *


class Validator(HTMLParser):
    """
    this class checks the following when text is fed to it (.feed(text)):
      IMPLEMENTED
      * each tag that opens must have a corresponding closing tag
      NOT IMPLEMENTED
      * valid tag (with valid attributes)

    """

    def __init__(self, text: str):
        super().__init__()
        self.tag_stack = []
        self.text = text
        with open("html_tags_attributes.json", "r") as f:
            self.valid_dict = json.load(f)
        self.feed(self.text)

    def error(self, error: HtmlValidationError):  # make exception classes and throw these instead
        raise error

    def handle_starttag(self, tag: str, attributes: [(str, str)]):
        self._valid_tag(tag)
        # self._valid_attributes(tag, attributes)  # always throws an exception because the dicts in the json for the attributes are still empty
        self.tag_stack.append(tag)

    def handle_endtag(self, tag: str):
        self._validate_corresponding_tag(tag)
        self.tag_stack.pop()

    def handle_data(self, data: str):
        # we don't need to ook at data
        pass

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
        valid_attributes = self.valid_dict[tag]
        for atr in attributes:
            if not atr[0] in valid_attributes:
                self.error(InvalidAttributeError(tag, atr[0], self.tag_stack))


validated = Validator('<!DOCTYPE html><html><body><h1>My First Heading</h1><p>My first paragraph.</p></body></html>')
