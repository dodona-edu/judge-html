from html.parser import HTMLParser

from dodona.translator import Translator
from exceptions.html_exceptions import *
from os import path
from utils.file_loaders import json_loader, html_loader
from validators.double_chars_validator import DoubleCharsValidator
from functools import lru_cache

# Location of this test file
base_path = path.dirname(__file__)
# keynames for the json
REQUIRED_ATR_KEY = "required_attributes"
RECOMMENDED_ATR_KEY = "recommended_attributes"
PERMITTED_PARENTS_KEY = "permitted_parents"
VOID_KEY = "void_tag"


class HtmlValidator(HTMLParser):
    """
    parses & validates the html
      the html doesn't need to start with <!DOCTYPE html>, if it is present it will just be ignored
    this class checks the following:
      * each tag that opens must have a corresponding closing tag
        * tags starting with </ are omitted
        * tags that dont need a closing tag (see json) can bit omitted (like <meta>)
        * tags that can self-close like <meta/>
      * is the tag a valid tag
      * does the tag have valid nesting (it checks the permitted parents)
          for example a head tag has the html tag as permitted parent but nothing else
      * required attributes (to be completed in the json)
      * recommended attributes (to be completed in the json)
      * invalid attributes (style attribute is not allowed)
    """

    def __init__(self, translator: Translator, **kwargs):
        """
        kwargs:
        * required: whether or not to check required arguments
        * recommended: whether or not to check recommended arguments
        * nesting: whether or not to check the nesting of tags
µ        """
        super().__init__()
        self.translator = translator
        self.warnings = Warnings(self.translator)
        self.tag_stack = []
        self.double_chars_validator = DoubleCharsValidator(translator)
        self.valid_dict = json_loader(path.abspath(path.join(base_path, "html_tags_attributes.json")))
        self.check_required = kwargs.get("required", True)
        self.check_recommended = kwargs.get("recommended", True)
        self.check_nesting = kwargs.get("nesting", True)

    def set_check_required(self, b: bool):
        self.check_required = b

    def set_check_recommended(self, b: bool):
        self.check_recommended = b

    def set_check_nesting(self, b: bool):
        self.check_nesting = b

    def error(self, error: HtmlValidationError):  # make exception classes and throw these instead
        raise error

    def warning(self, warning: MissingRecommendedAttributesWarning):
        """gathers the warnings,
            these will be thrown at the end if no Errors occur
        """
        self.warnings.add(warning)

    def validate_file(self, source_filepath: str):
        self._validate(html_loader(source_filepath, shorted=False))

    def validate_content(self, content: str):
        self._validate(content)

    def _validate(self, text: str):
        """here the actual validation occurs"""
        self.tag_stack.clear()
        self.warnings.clear()
        self.reset()
        # check brackets and stuff ( '(', '"', '{', '[', '<')
        self._valid_double_chars(text)
        # check html syntax
        self.feed(text)
        # clear tag stack
        if self.tag_stack:
            raise MissingClosingTagError(translator=self.translator, tag_location=self.tag_stack,
                                         position=self.getpos(), tag=self.tag_stack.pop())
        # show warnings if any
        if self.warnings:
            raise self.warnings

    def _valid_double_chars(self, text):
        """check whether every opening char has a corresponding closing char"""
        self.double_chars_validator.validate_content(text)

    def handle_starttag(self, tag: str, attributes: [(str, str)]):
        """handles a html tag that opens, like <body>
            attributes hold the (name, value) of the attributes supplied in the tag"""
        tag = tag.lower()
        self._valid_tag(tag)
        if self.check_nesting:
            self._valid_nesting(tag)
        if not self._is_void_tag(tag):
            self.tag_stack.append(tag)
        self._valid_attributes(tag, set(a[0].lower() for a in attributes))

    def handle_endtag(self, tag: str):
        """handles a html tag that closes, like <body/>"""
        tag = tag.lower()
        self._validate_corresponding_tag(tag)
        if not self._is_void_tag(tag):
            self.tag_stack.pop()

    def handle_startendtag(self, tag, attrs):
        """handles a html tag that opens and instantly closes, like <meta/>"""
        tag = tag.lower()
        if not self._is_void_tag(tag):
            self.error(NoSelfClosingTagError(translator=self.translator, tag_location=self.tag_stack,
                                             position=self.getpos(), tag=tag))
        else:
            self.handle_starttag(tag, attrs)

    def _validate_corresponding_tag(self, tag: str):
        """validate that each tag that opens has a corresponding closing tag
        """
        if not (self.tag_stack and self.tag_stack[-1] == tag):
            self.error(MissingClosingTagError(translator=self.translator, tag_location=self.tag_stack,
                                              position=self.getpos(), tag=tag))

    @lru_cache()
    def _is_void_tag(self, tag: str) -> bool:
        """indicates whether the tag its corresponding closing tag is omittable or not"""
        return VOID_KEY in self.valid_dict[tag] and self.valid_dict[tag][VOID_KEY]

    @lru_cache()
    def _valid_tag(self, tag: str):
        """validate that a tag is a valid HTML tag (if a tag isn't allowed, this wil also raise an exception"""
        if tag not in self.valid_dict:
            self.error(InvalidTagError(translator=self.translator, tag_location=self.tag_stack, position=self.getpos(),
                                       tag=tag))

    def _valid_attributes(self, tag: str, attributes: set[str]):
        """validate attributes
            check whether all required attributes are there, if not, raise an error
            check whether all recommended attributes are there, if not, add a warning
        """
        # no inline css allowed
        if "style" in attributes:
            self.error(InvalidAttributeError(translator=self.translator, tag_location=self.tag_stack,
                                             position=self.getpos(), tag=tag, attribute="style"))

        tag_info = self.valid_dict[tag]

        if self.check_required:
            required = set(tag_info[REQUIRED_ATR_KEY]) if REQUIRED_ATR_KEY in tag_info else set()
            if missing_req := (required - attributes):
                self.error(MissingRequiredAttributesError(translator=self.translator, tag_location=self.tag_stack,
                                                          position=self.getpos(), tag=tag,
                                                          attribute=", ".join(missing_req)))

        if self.check_recommended:
            recommended = set(tag_info[RECOMMENDED_ATR_KEY]) if RECOMMENDED_ATR_KEY in tag_info else set()
            if missing_rec := (recommended - attributes):
                self.warning(MissingRecommendedAttributesWarning(translator=self.translator,
                                                                 tag_location=self.tag_stack.copy(),
                                                                 position=self.getpos(), tag=tag,
                                                                 attribute=", ".join(missing_rec)))

    def _valid_nesting(self, tag):
        """check whether the nesting is html-approved,
            some tags can only have specific parent tags
        """
        tag_info = self.valid_dict[tag]
        if PERMITTED_PARENTS_KEY in tag_info:
            # check if the prev tag is in the permitted parents field of the current tag
            prev_tag = self.tag_stack[-1] if self.tag_stack else None
            # prev tag can be None when tag is <html>, you don't expect it has a parent,
            #   if you want a tag without a parent you need to add "permitted_parent: []" in the json for that tag
            if not tag_info[PERMITTED_PARENTS_KEY]:
                if prev_tag is not None:
                    self.error(UnexpectedTagError(translator=self.translator, tag_location=self.tag_stack,
                                                  position=self.getpos(), tag=tag))
            elif prev_tag is not None and prev_tag not in tag_info[PERMITTED_PARENTS_KEY]:
                self.error(UnexpectedTagError(translator=self.translator, tag_location=self.tag_stack,
                                              position=self.getpos(), tag=tag))
