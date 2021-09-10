import json
from html.parser import HTMLParser
from exceptions.htmlExceptions import *

REQUIRED_ATR_KEY = "required_attributes"
RECOMMENDED_ATR_KEY = "recommended_attributes"


class HtmlValidator(HTMLParser):
    """
    this class checks the following when text is fed to it (.feed(text)):
      IMPLEMENTED
      * each tag that opens must have a corresponding closing tag
      * valid tag
      * required attributes (to be completed in the json)
      * recommended attributes (to be completed in the json)
      NOT IMPLEMENTED
    """

    def __init__(self, judge_filepath: str, **kwargs):
        super().__init__()
        self.tag_stack = []
        with open(f"{judge_filepath}/validators/html_tags_attributes.json", "r") as f:
            self.valid_dict = json.load(f)

        self.check_required = kwargs.get("required", True)
        self.check_recommended = kwargs.get("recommended", True)

    def validate(self, source_filepath: str):
        with open(source_filepath, "r") as f:
            self._validate(f.read())

    def _validate(self, text: str):
        self.reset()
        self.feed(text)

    def error(self, error: HtmlValidationError):  # make exception classes and throw these instead
        raise error

    def handle_starttag(self, tag: str, attributes: [(str, str)]):
        if tag == "meta":
            return
        self._valid_tag(tag)
        # already append, because the tag is valid,
        #  this way the tag stack is updated for a more accurate location of the error messages
        self.tag_stack.append(tag)
        self._valid_attributes(tag, set(a[0] for a in attributes))
        # print(self.getpos())

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

    def _valid_attributes(self, tag: str, attributes: set[str]):
        """validate attributes"""
        tag_info = self.valid_dict[tag]

        if self.check_required:
            required = set(tag_info[REQUIRED_ATR_KEY]) if REQUIRED_ATR_KEY in tag_info else set()
            if missing_req := (required - attributes):
                self.error(MissingRequiredAttributeError(tag, ", ".join(missing_req), self.tag_stack))

        if self.check_recommended:
            recommended = set(tag_info[RECOMMENDED_ATR_KEY]) if RECOMMENDED_ATR_KEY in tag_info else set()
            if missing_rec := (recommended - attributes):
                self.error(MissingRecommendedAttributeError(tag, ", ".join(missing_rec), self.tag_stack))


validator = HtmlValidator("..")
#validator._validate('<!DOCTYPE html><html lang="en"><body><img/><h1> My First Heading</h1><p> My first paragraph.</p></body></html>')
validator.validate("simple.html")
