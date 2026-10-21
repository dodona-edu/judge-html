import unittest

from utils.color_converter import Color, UnresolvedColor


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
        self.assertEqual(correct, Color("rgb(100%,0%,0%)"), "test rgb")

        self.assertEqual(correct, Color("rgba(255,0,0,1)"), "test rgba")
        self.assertEqual(correct, Color("rgba(100%,0%,0%,1)"), "test rgba")

        self.assertEqual(correct, Color("hsl(0, 100%, 50%)"), "test hsl")

        self.assertEqual(correct, Color("hsla(0, 100%, 50%,1)"), "test hsla")

    def test_alpha_is_kept_from_rgba_and_hsla(self):
        """rgba() and hsla() carry an alpha, and it has to survive parsing"""
        # The alpha was parsed and then dropped, so these all looked fully opaque
        self.assertAlmostEqual(Color("rgba(0,0,0,0.5)").alpha, 0.5, delta=1 / 255)
        self.assertAlmostEqual(Color("hsla(0,0%,0%,0.25)").alpha, 0.25, delta=1 / 255)

        # Which made a half-transparent black compare equal to an opaque one
        self.assertNotEqual(Color("rgba(0,0,0,0.5)"), Color("rgb(0,0,0)"))

        # An alpha of 1 still means the same colour as the triple form
        self.assertEqual(Color("rgba(0,0,0,1)"), Color("rgb(0,0,0)"))

        # Forms without an alpha are unaffected and stay opaque
        self.assertAlmostEqual(Color("rgb(1,2,3)").alpha, 1.0)
        self.assertAlmostEqual(Color("#ff0000").alpha, 1.0)

    def test_hsl_hue_is_an_angle(self):
        self.assertEqual(Color("hsl(120, 100%, 50%)"), Color("lime"))
        self.assertEqual(Color("hsl(240, 100%, 50%)"), Color("blue"))
        self.assertEqual(Color("hsl(480, 100%, 50%)"), Color("lime"))
        self.assertEqual(Color("hsl(-240, 100%, 50%)"), Color("lime"))
        for hue in ("120deg", "0.3333333333turn", "133.3333333grad", "2.0943951rad"):
            self.assertEqual(Color(f"hsl({hue}, 100%, 50%)"), Color("lime"), hue)

    def test_rgb_numbers_are_always_out_of_255(self):
        self.assertEqual(Color("rgb(255, 0, 0)"), Color("red"))
        self.assertEqual(Color("rgb(0, 0, 1)"), Color("#000001"))
        self.assertEqual(Color("rgb(0.5, 0, 0)"), Color("black"))
        self.assertEqual(Color("rgb(50%, 0%, 0%)"), Color("rgb(127.5, 0, 0)"))
        self.assertEqual(Color("rgb(300, -5, 0)"), Color("red"))

    def test_alpha_number_or_percentage(self):
        self.assertAlmostEqual(Color("rgba(0,0,0,50%)").alpha, 0.5, delta=1 / 255)
        self.assertAlmostEqual(Color("hsla(0,0%,0%,.25)").alpha, 0.25, delta=1 / 255)
        self.assertEqual(Color("rgba(0,0,0,50%)"), Color("rgba(0,0,0,0.5)"))

    def test_space_separated_syntax(self):
        self.assertEqual(Color("rgb(255 0 0)"), Color("red"))
        self.assertEqual(Color("rgb(255 0 0 / 50%)"), Color("rgba(255,0,0,0.5)"))
        self.assertEqual(Color("rgb(255 0 0/.5)"), Color("rgba(255,0,0,0.5)"))
        self.assertEqual(Color("hsl(120deg 100% 50% / .5)"), Color("hsla(120,100%,50%,0.5)"))
        self.assertEqual(Color("rgb(255, 0, 0, 0.5)"), Color("rgba(255,0,0,0.5)"))
        self.assertEqual(Color("rgba(255, 0, 0)"), Color("red"))
        self.assertEqual(Color("hsla(0, 100%, 50%)"), Color("hsl(0, 100%, 50%)"))

    def test_case_insensitive(self):
        self.assertEqual(Color("RGB(255, 0, 0)"), Color("red"))
        self.assertEqual(Color("HSLA(0, 100%, 50%, 1)"), Color("red"))
        self.assertEqual(Color("#FFF"), Color("white"))
        self.assertEqual(Color("#FF0000FF"), Color("red"))
        self.assertEqual(Color("Red"), Color("red"))
        self.assertEqual(Color("Hsl(120deg 100% 50%)"), Color("lime"))

    def test_transparent(self):
        self.assertEqual(Color("transparent"), Color("rgba(0,0,0,0)"))
        self.assertEqual(Color("TRANSPARENT").alpha, 0.0)
        self.assertNotEqual(Color("transparent"), Color("black"))

    def test_css_names_missing_from_colour_package(self):
        self.assertEqual(Color("teal"), Color("#008080"))
        self.assertEqual(Color("rebeccapurple"), Color("#663399"))

    def test_names_browsers_reject(self):
        for name in ("navyblue", "lightslateblue", "violetred", "lightgoldenrod"):
            with self.subTest(name=name), self.assertRaises(ValueError) as raised:
                Color(name)
            self.assertNotIsInstance(raised.exception, UnresolvedColor, name)

    def test_channels_are_rounded_to_8_bit(self):
        # tinycss2 converts this hue to a green channel of 0.9999999999999998
        self.assertEqual(Color("hsl(0.5turn 100% 50%)"), Color("#00ffff"))
        self.assertEqual(Color("rgb(0.5, 0, 0)"), Color("black"))

    def test_hex_with_alpha(self):
        self.assertEqual(Color("#f008").rgba, (255, 0, 0, 136))
        self.assertEqual(Color("#f008"), Color("rgba(255, 0, 0, 0.5333333333)"))
        self.assertNotEqual(Color("#f008"), Color("red"))

    def test_hwb(self):
        self.assertEqual(Color("hwb(120 0% 0%)"), Color("lime"))
        self.assertEqual(Color("hwb(0 100% 0%)"), Color("white"))

    def test_not_equal_to_other_types(self):
        self.assertNotEqual(Color("red"), None)
        self.assertNotEqual(Color("red"), "red")

    def test_unresolved_values(self):
        for value in (
            "inherit",
            "INITIAL",
            "unset",
            "revert",
            "revert-layer",
            "currentcolor",
            "currentColor",
            "var(--main)",
            "lab(50% 40 59)",
            "lch(50% 40 59)",
            "oklab(60% 0.1 0.1)",
            "oklch(60% 0.15 50)",
            "color-mix(in srgb, red, blue)",
            "light-dark(red, blue)",
            "rgb(var(--r) 0 0)",
            "rgb(from red r g b)",
        ):
            with self.subTest(value=value), self.assertRaises(UnresolvedColor):
                Color(value)

    def test_invalid_values(self):
        for value in (
            "banana",
            "",
            "#12345",
            "#1234567",
            "#ggg",
            "#+f0",
            "rgb(1,2)",
            "rgb(1,2,3,4,5)",
            "rgb(1 2 3 / )",
            "rgb(1, 2 3)",
            "rgb(a, b, c)",
            "rgb(1_0, 0, 0)",
            "hsl(0xyz, 100%, 50%)",
            "foo(1, 2, 3)",
            "red blue",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError) as raised:
                Color(value)
            self.assertNotIsInstance(raised.exception, UnresolvedColor, value)
