import unittest

from utils.color_converter import Color


class TestColorConverter(unittest.TestCase):
    def test_conversion_red(self):
        correct = Color("red")

        # All possibilities to make the color "red"
        self.assertEqual(correct, Color("red"), "test name")

        self.assertEqual(correct, Color("#ff0000"), "test hex")
        self.assertEqual(correct, Color("#ff0000ff"), "test hex")
        self.assertEqual(correct, Color("#f00"), "test hex")
        self.assertEqual(correct, Color("#f00f"), "test hex")

        self.assertEqual(correct, Color("rgb(255,0,0)"), "test rgb")
        self.assertEqual(correct, Color("rgb(100%,0,0)"), "test rgb")

        self.assertEqual(correct, Color("rgba(255,0,0,1)"), "test rgba")
        self.assertEqual(correct, Color("rgba(100%,0%,0%,1)"), "test rgba")

        self.assertEqual(correct, Color("hsl(0, 100%, 50%)"), "test hsl")

        self.assertEqual(correct, Color("hsla(0, 100%, 50%,1)"), "test hsla")

    def test_alpha_is_kept_from_rgba_and_hsla(self):
        """rgba() and hsla() carry an alpha, and it has to survive parsing"""
        # The alpha was parsed and then dropped, so these all looked fully opaque
        self.assertAlmostEqual(Color("rgba(0,0,0,0.5)").alpha, 0.5)
        self.assertAlmostEqual(Color("hsla(0,0%,0%,0.25)").alpha, 0.25)

        # Which made a half-transparent black compare equal to an opaque one
        self.assertNotEqual(Color("rgba(0,0,0,0.5)"), Color("rgb(0,0,0)"))

        # An alpha of 1 still means the same colour as the triple form
        self.assertEqual(Color("rgba(0,0,0,1)"), Color("rgb(0,0,0)"))

        # Forms without an alpha are unaffected and stay opaque
        self.assertAlmostEqual(Color("rgb(1,2,3)").alpha, 1.0)
        self.assertAlmostEqual(Color("#ff0000").alpha, 1.0)
