from unittest import TestCase

from leadmacro import Color


class TestColor(TestCase):
    def test_color_returns_int_when_created_with_int(self):
        color = Color(123456)
        self.assertEquals(123456, color.color)

    def test_color_returns_rgb_tuple(self):
        color = Color(0x00bfff)
        self.assertEqual((0, 191, 255), color.rgb)
