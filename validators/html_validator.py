from html.parser import HTMLParser
from exceptions.htmlExceptions import *


class Validator(HTMLParser):
    """
    this class checks the following when text is fed to it (.feed(text)):
      IMPLEMENTED
      * each tag that opens must have a corresponding closing tag
      NOT IMPLEMENTED
      * valid tag with possibly has valid attributes

    """

    def __init__(self, text: str):
        super().__init__()
        self.tag_stack = []
        self.text = text
        self.feed(self.text)

    def error(self, error: HtmlValidationError):  # make exception classes and throw these instead
        raise error

    def handle_starttag(self, tag, attrs):
        self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        open_tag = self.tag_stack[-1]

        if open_tag != tag:
            self.error(MissingClosingTagError(open_tag, self.tag_stack))

        self.tag_stack.pop()

    def handle_data(self, data):
        # we don't need to ook at data
        pass

    def _validate_corresponding_tag(self):
        """validate that each tag that opens has a corresponding closing tag
        """
        pass

    def _valid_tag_and_attributes(self, tag: str, attributes: [(str, str)]) -> bool:
        """validate that each tag is a valid tag and has valid attributes"""
        pass


validated = Validator('<html><head><title>Test</title></head>'
                      '<body><h1>Parse me!</body></html>')
