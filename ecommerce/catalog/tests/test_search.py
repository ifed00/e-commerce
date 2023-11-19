from .common_setup import common_setup

from django.test import TestCase

from catalog.models import Category, Product
from ..search import SearchCategory, SearchCatalog, SearchBase


class TestSearchBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        common_setup(cls)

    def test_multiple_search_tokens_concatenated_with_or_logic(self):
        cat_fridges = Category.objects.get(pk=2)
        qs = cat_fridges.product_set.all()

        search_engine = SearchBase(['name'])
        qs = search_engine.filter('Freeze choice', qs)

        result = list(qs)
        self.assertEqual(len(result), 2)

        self.assertTrue(self.available_products[3] in result)
        self.assertTrue(self.available_products[5] in result)

    def test_multiple_fields_concatenated_with_or_logic(self):
        cat_fridges = Category.objects.get(pk=2)
        qs = cat_fridges.product_set.all()

        search_engine = SearchBase(['name', 'description'])
        qs = search_engine.filter('ee', qs)

        result = list(qs)
        self.assertEqual(len(result), 2)

        self.assertTrue(self.available_products[3] in result)
        self.assertTrue(self.available_products[5] in result)


class TestSearchCategory(TestCase):
    @classmethod
    def setUpTestData(cls):
        common_setup(cls)

    def test_no_query_produces_no_filtering(self):
        cat_fridges = Category.objects.get(pk=2)
        qs = cat_fridges.product_set.all()

        search_engine = SearchCategory(['name'])
        qs = search_engine.filter('', qs)

        self.assertEqual(qs.count(), 3)


class TestSearchCatalog(TestCase):
    @classmethod
    def setUpTestData(cls):
        common_setup(cls)

    def test_no_query_raises_NoQuerySpecified_exception(self):
        qs = Product.published.all()

        search_engine = SearchCatalog(['name'])
        with self.assertRaises(SearchCatalog.NoQuerySpecified):
            search_engine.filter('', qs)

    def test_show_first_parameter_restricts_showed_products(self):
        qs = Product.published.all()

        search_engine = SearchCatalog(['name'], show_first=1)
        result = search_engine.filter('l', qs)

        self.assertEqual(len(result), 2)

        phones_cat = Category.objects.get(pk=1)
        fridges_cat = Category.objects.get(pk=2)

        for r in result:
            if r['category'] == phones_cat:
                self.assertEqual(r['found'], 2)
                self.assertEqual(len(r['first_found']), 1)
            elif r['category'] == fridges_cat:
                self.assertEqual(r['found'], 1)
                self.assertEqual(len(r['first_found']), 1)
            else:
                self.assertTrue(False)


