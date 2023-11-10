import unittest
from decimal import Decimal

from django.core.exceptions import ValidationError

from catalog.validators import validate_percent, validate_resolution


class ValidatePercent(unittest.TestCase):
    def test_negative_number_raises_ValidationError(self):
        with self.assertRaises(ValidationError):
            validate_percent(Decimal(-0.01))

    def test_number_above_hundred_raises_ValidationError(self):
        with self.assertRaises(ValidationError):
            validate_percent(Decimal(100.01))

    def test_okay_number_passes(self):
        validate_percent(Decimal(33.33))
        self.assertTrue(True)


class ValidateResolution(unittest.TestCase):
    def test_HD_passes(self):
        validate_resolution('1980x720')
        self.assertTrue(True)

    def test_wrong_delimiter_format_raises_ValidationError(self):
        for delimiter in ['_', '-', 'X', 'm']:
            with self.subTest(delimiter=delimiter):
                with self.assertRaises(ValidationError):
                    validate_resolution(f'1980{delimiter}720')

    def test_empty_value_raises_ValidationError(self):
        with self.assertRaises(ValidationError):
            validate_resolution('')

    def test_negative_number_raises_ValidationError(self):
        for negative_resolution in ['-1920x720', '-1920x-720', '-1920x-720']:
            with self.subTest(resolution=negative_resolution):
                with self.assertRaises(ValidationError):
                    validate_resolution(negative_resolution)

    def test_non_decimal_raises_ValidationError(self):
        for res in ['0x16x720', '1.8x77', '2.34e6x6.99']:
            with self.subTest(resolution=res):
                with self.assertRaises(ValidationError):
                    validate_resolution(res)

    def test_zero_raises_ValidationError(self):
        for res in ['0x1280', '0x720', '0x0']:
            with self.subTest(resolution=res):
                with self.assertRaises(ValidationError):
                    validate_resolution(res)

    def test_missing_resolution_part_raises_ValidationError(self):
        for res in ['1920x', 'x720']:
            with self.subTest(resolution=res):
                with self.assertRaises(ValidationError):
                    validate_resolution(res)

    def test_leading_zero_raises_ValidationError(self):
        for res in ['000256x1920', '180x00180']:
            with self.subTest(resolution=res):
                with self.assertRaises(ValidationError):
                    validate_resolution(res)
