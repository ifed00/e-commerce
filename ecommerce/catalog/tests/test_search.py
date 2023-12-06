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
        qs = search_engine._filter('Freeze choice', qs)

        result = list(qs)
        self.assertEqual(len(result), 2)

        self.assertTrue(self.available_products[3] in result)
        self.assertTrue(self.available_products[5] in result)

    def test_multiple_fields_concatenated_with_or_logic(self):
        cat_fridges = Category.objects.get(pk=2)
        qs = cat_fridges.product_set.all()

        search_engine = SearchBase(['name', 'description'])
        qs = search_engine._filter('ee', qs)

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
        search_engine = SearchCatalog()
        with self.assertRaises(SearchCatalog.NoQuerySpecified):
            search_engine.filter('')

    def test_tokens_concatenated_using_or_logic(self):
        search_engine = SearchCatalog()

        result = search_engine.filter('icall galaxy')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].found, 2)

    def test_searches_in_product_name_and_category_name(self):
        search_engine = SearchCatalog()

        result = search_engine.filter('i')

        self.assertEqual(len(result), 2)
        for entry in result:
            if entry.category == Category.objects.get(name='phones'):
                self.assertFalse(entry.whole_category)
            elif entry.category == Category.objects.get(name='fridges'):
                self.assertTrue(entry.whole_category)
            else:
                self.assertFalse(True)

    def test_whole_category_match_produce_no_in_category_filtering(self):
        search_engine = SearchCatalog(show_first=10)

        result = search_engine.filter('phones')

        self.assertTrue(result[0].whole_category)
        self.assertEqual(len(result[0].first_found_products), 3)

    def test_show_first_parameter_restricts_showed_products(self):
        search_engine = SearchCatalog(show_first=1)
        result = search_engine.filter('l')

        self.assertEqual(len(result), 2)

        phones_cat = Category.objects.get(pk=1)
        fridges_cat = Category.objects.get(pk=2)

        for r in result:
            if r.category == phones_cat:
                self.assertNotEqual(len(r.first_found_products), r.found)
            elif r.category == fridges_cat:
                self.assertEqual(len(r.first_found_products), r.found)
            else:
                self.assertTrue(False)


