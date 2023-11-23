import unittest
from decimal import Decimal

from django.core.exceptions import ValidationError

from ..validators import non_zero_validator


class TestNonZeroValidator(unittest.TestCase):
    def test_zero_raises_ValidaitonError(self):
        with self.assertRaises(ValidationError):
            non_zero_validator(Decimal(0))

    def test_non_zero_doesnt_raises(self):
        non_zero_validator(Decimal(0.01))
        self.assertTrue(True)
