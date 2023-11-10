import unittest
from decimal import Decimal

from django.core.exceptions import ValidationError

from catalog.validators import validate_percent


class ValidatePercent(unittest.TestCase):
    def test_negative_number_raises_ValidationError(self):
        with self.assertRaises(ValidationError):
            validate_percent(Decimal(-0.01))
