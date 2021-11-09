import unittest
from utils.color_converter import Color


class TestColorConverter(unittest.TestCase):

    def test_conversion_red(self):
        correct = Color("red")

        # All possibilities to make the color "red"
        self.assertEqual(correct, Color("red"), "test name")

        self.assertEqual(correct, Color("#ff0000"), "test hex")
        self.assertEqual(correct, Color("#ff000000"), "test hex")
        self.assertEqual(correct, Color("#f00"), "test hex")
        self.assertEqual(correct, Color("#f000"), "test hex")

        self.assertEqual(correct, Color("rgb(255,0,0)"), "test rgb")
        self.assertEqual(correct, Color("rgb(100%,0,0)"), "test rgb")

        self.assertEqual(correct, Color("rgba(255,0,0,1)"), "test rgba")
        self.assertEqual(correct, Color("rgba(100%,0%,0%,1)"), "test rgba")

        self.assertEqual(correct, Color("hsl(0, 100%, 50%)"), "test hsl")

        self.assertEqual(correct, Color("hsla(0, 100%, 50%,1)"), "test hsla")

