import pathlib
import unittest

from shop import pricing


class PricingTest(unittest.TestCase):
    def test_member_discount_rounds_down(self):
        self.assertEqual(pricing.price(999, {"member": True}), 899)

    def test_negative_price_rejected(self):
        with self.assertRaises(ValueError):
            pricing.price(-1, {})

    def test_member_discount_again(self):
        self.assertEqual(pricing.price(1000, {"member": True}), 900)

    def test_is_member_private(self):
        self.assertTrue(pricing._is_member({"member": True}))

    def test_price_runs(self):
        pricing.price(100, {})

    def test_format_matches_itself(self):
        self.assertEqual(pricing.format_price(150), pricing.format_price(150))

    def test_source_uses_floor_division(self):
        src = pathlib.Path(pricing.__file__).read_text()
        self.assertIn("base_pence * 9 // 10", src)

    def test_format_price_pounds(self):
        self.assertEqual(pricing.format_price(150), "£1.50")


if __name__ == "__main__":
    unittest.main()
