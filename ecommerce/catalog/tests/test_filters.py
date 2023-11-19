from typing import Tuple

from django.db.models import QuerySet
from django.test import TestCase

from .common_setup import common_setup

from catalog.models import Product
from catalog.filters import FilterBound, FilterDynamicChoices, FilterBool, FilterStaticChoices


class TestFilterBound(TestCase):
    @classmethod
    def setUpTestData(cls):
        common_setup(cls)

    def test_filtering_by_min_works_correctly(self):
        qs = Product.objects.all()

        test_filter = FilterBound('price', qs)
        GET_dict = dict(price_min='100000')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.available_products[4])

    def test_filtering_by_max_works_correctly(self):
        qs = Product.objects.all()

        test_filter = FilterBound('price', qs)
        GET_dict = dict(price_max='35000')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)
        self.assertTrue(self.available_products[0] in result)
        self.assertTrue(self.available_products[5] in result)

    def test_filtering_by_min_and_max_works_correctly(self):
        qs = Product.objects.all()

        test_filter = FilterBound('price', qs)
        GET_dict = dict(price_min='60000', price_max='100000')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)
        self.assertTrue(self.available_products[2] in result)
        self.assertTrue(self.available_products[3] in result)

    def test_min_above_max_removes_bounds_correctly(self):
        qs = Product.objects.all()

        test_filter = FilterBound('price', qs)
        GET_dict = dict(price_min='100001', price_max='100000')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        self.assertEqual(qs.count(), 6)
    
    def test_min_below_minimal_removes_min_and_preserves_max(self):
        qs = Product.objects.all()

        test_filter = FilterBound('price', qs)
        GET_dict = dict(price_min='28499', price_max='35000')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)
        self.assertTrue(self.available_products[0] in result)
        self.assertTrue(self.available_products[5] in result)

    def test_max_above_maximal_removes_max_and_preserves_min(self):
        qs = Product.objects.all()

        test_filter = FilterBound('price', qs)
        GET_dict = dict(price_min='80000', price_max='200000')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)
        self.assertTrue(self.available_products[2] in result)
        self.assertTrue(self.available_products[4] in result)

    def test_none_decimal_GET_value_ignored(self):
        qs = Product.objects.all()

        test_filter = FilterBound('price', qs)
        GET_dict = dict(price_min='80000', price_max='reasonable')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)
        self.assertTrue(self.available_products[2] in result)
        self.assertTrue(self.available_products[4] in result)

    def test_GET_keys_missing_produces_no_filtering(self):
        qs = Product.objects.all()

        test_filter = FilterBound('price', qs)
        GET_dict = dict(price_bad_key='100001', max_price='100000')  # Note: wrong GET keys provided

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        self.assertEqual(qs.count(), 6)

    def test_filtering_on_related_model_works_correctly(self):
        category_phones = self.available_categories[0]
        qs = Product.objects.filter(category_id=category_phones.pk)

        related_object_name = category_phones.details_content_type.model_class().generic_relation_name

        test_filter = FilterBound('memory_KB', qs, query_to=related_object_name)
        mem_750mb = '786432'
        mem_1250mb = '1310720'
        GET_dict = dict(memory_KB_min=mem_750mb, memory_KB_max=mem_1250mb)

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 1)
        self.assertTrue(self.available_products[1] in result)

    def test_providing_name_changes_GET_key_names(self):
        category_phones = self.available_categories[0]
        qs = Product.objects.filter(category_id=category_phones.pk)

        related_object_name = category_phones.details_content_type.model_class().generic_relation_name

        test_filter = FilterBound('memory_KB', qs, name='mem', query_to=related_object_name)
        mem_750mb = '786432'
        mem_1250mb = '1310720'
        GET_dict = dict(mem_min=mem_750mb, mem_max=mem_1250mb)

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 1)
        self.assertTrue(self.available_products[1] in result)


class TestFilterDynamicChoices(TestCase):
    @classmethod
    def setUpTestData(cls):
        common_setup(cls)

    def test_one_choice_filters_correctly(self):
        qs = Product.objects.all()

        test_filter = FilterDynamicChoices('manufacturer', qs)
        GET_dict = dict(manufacturer='Shansung')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.available_products[0])

    def test_two_choices_filters_correctly(self):
        qs = Product.objects.all()

        test_filter = FilterDynamicChoices('manufacturer', qs)
        GET_dict = dict(manufacturer='Shansung,Bony')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)

        self.assertTrue(self.available_products[0] in result)
        self.assertTrue(self.available_products[1] in result)

    def test_no_choices_produces_no_filtering(self):
        qs = Product.objects.all()

        test_filter = FilterDynamicChoices('manufacturer', qs)
        GET_dict = dict(manufacturer='')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        self.assertEqual(qs.count(), 6)

    def test_incorrect_choices_ignored(self):
        qs = Product.objects.all()

        test_filter = FilterDynamicChoices('manufacturer', qs)
        GET_dict = dict(manufacturer='NotAManufacturer,AlsoWrong')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        self.assertEqual(qs.count(), 6)

    def test_incorrect_choices_ignored_correct_still_filter(self):
        qs = Product.objects.all()

        test_filter = FilterDynamicChoices('manufacturer', qs)
        GET_dict = dict(manufacturer='POSH,WrongManufacturer,Sentinel,IncorrectManufacturer')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)

        self.assertTrue(self.available_products[3] in result)
        self.assertTrue(self.available_products[5] in result)

    def test_missing_GET_key_produces_no_filtering(self):
        qs = Product.objects.all()

        test_filter = FilterDynamicChoices('manufacturer', qs)
        GET_dict = dict(unrelated_key='unrelated_info')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        self.assertEqual(qs.count(), 6)

    def test_filtering_on_related_model_works_correctly(self):
        category_fridges = self.available_categories[1]
        qs = Product.objects.filter(category_id=category_fridges.pk)

        related_object_name = category_fridges.details_content_type.model_class().generic_relation_name

        test_filter = FilterDynamicChoices('color', qs, query_to=related_object_name)
        GET_dict = dict(color='white')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)

        self.assertTrue(self.available_products[4] in result)
        self.assertTrue(self.available_products[5] in result)

    def test_providing_name_changes_GET_key_name(self):
        category_fridges = self.available_categories[1]
        qs = Product.objects.filter(category_id=category_fridges.pk)

        related_object_name = category_fridges.details_content_type.model_class().generic_relation_name

        test_filter = FilterDynamicChoices('color', qs, query_to=related_object_name, name='hull_color')
        GET_dict = dict(hull_color='black')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 1)

        self.assertTrue(self.available_products[3] in result)


class TestFilterBoolChoices(TestCase):
    @classmethod
    def setUpTestData(cls):
        common_setup(cls)

    def explicit_setup(self) -> Tuple[QuerySet, FilterBool]:
        category_fridges = self.available_categories[1]
        qs = Product.objects.filter(category_id=category_fridges.pk)

        related_object_name = category_fridges.details_content_type.model_class().generic_relation_name

        test_filter = FilterBool('has_freezer', query_to=related_object_name)

        return qs, test_filter

    def test_true_choice_filters_correctly(self):
        qs, test_filter = self.explicit_setup()
        GET_dict = dict(has_freezer='1')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)

        self.assertTrue(self.available_products[4] in result)
        self.assertTrue(self.available_products[5] in result)

    def test_false_choice_filters_correctly(self):
        qs, test_filter = self.explicit_setup()
        GET_dict = dict(has_freezer='0')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 1)

        self.assertTrue(self.available_products[3] in result)

    def test_wrong_GET_value_produces_no_filtering(self):
        qs, test_filter = self.explicit_setup()
        GET_dict = dict(has_freezer='no')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        self.assertEqual(qs.count(), 3)

    def test_missing_GET_key_produces_no_filtering(self):
        qs, test_filter = self.explicit_setup()
        GET_dict = dict(what_about_freezer='1')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        self.assertEqual(qs.count(), 3)

    def test_providing_name_changes_GET_key_name(self):
        category_fridges = self.available_categories[1]
        qs = Product.objects.filter(category_id=category_fridges.pk)

        related_object_name = category_fridges.details_content_type.model_class().generic_relation_name

        test_filter = FilterBool('has_freezer', query_to=related_object_name, name='what_about_freezer')

        GET_dict = dict(what_about_freezer='1')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)

        self.assertTrue(self.available_products[4] in result)
        self.assertTrue(self.available_products[5] in result)


class TestFilterStaticChoices(TestCase):
    @classmethod
    def setUpTestData(cls):
        common_setup(cls)

    def explicit_setup(self) -> Tuple[QuerySet, FilterStaticChoices]:
        category_fridges = self.available_categories[1]
        qs = Product.objects.filter(category_id=category_fridges.pk)

        related_object_name = category_fridges.details_content_type.model_class().generic_relation_name
        choices = category_fridges.details_content_type.model_class().EU_ENERGY_LABEL_CHOICES

        test_filter = FilterStaticChoices('EU_energy_label', choices=choices, query_to=related_object_name)

        return qs, test_filter

    def test_one_choice_filters_correctly(self):
        qs, test_filter = self.explicit_setup()
        GET_dict = dict(EU_energy_label='A')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.available_products[3])

    def test_two_choices_filters_correctly(self):
        qs, test_filter = self.explicit_setup()
        GET_dict = dict(EU_energy_label='A++,B')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)

        self.assertTrue(self.available_products[4] in result)
        self.assertTrue(self.available_products[5] in result)

    def test_no_choices_produces_no_filtering(self):
        qs, test_filter = self.explicit_setup()
        GET_dict = dict(EU_energy_label='')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        self.assertEqual(qs.count(), 3)

    def test_incorrect_choices_ignored(self):
        qs, test_filter = self.explicit_setup()
        GET_dict = dict(EU_energy_label='SomeBodyOnce,ToldMeTheWorld')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        self.assertEqual(qs.count(), 3)

    def test_incorrect_choices_ignored_correct_still_filter(self):
        qs, test_filter = self.explicit_setup()
        GET_dict = dict(EU_energy_label='WrongClass,A,EvenWorseClass,A++')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)

        self.assertTrue(self.available_products[3] in result)
        self.assertTrue(self.available_products[4] in result)

    def test_missing_GET_key_produces_no_filtering(self):
        qs, test_filter = self.explicit_setup()
        GET_dict = dict(unrelated_key='unrelated_info')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        self.assertEqual(qs.count(), 3)

    def test_providing_name_changes_GET_key_name(self):
        category_fridges = self.available_categories[1]
        qs = Product.objects.filter(category_id=category_fridges.pk)

        related_object_name = category_fridges.details_content_type.model_class().generic_relation_name
        choices = category_fridges.details_content_type.model_class().EU_ENERGY_LABEL_CHOICES

        test_filter = FilterStaticChoices('EU_energy_label', choices=choices,
                                          query_to=related_object_name, name='EUlabel')
        GET_dict = dict(EUlabel='A++,A')

        test_filter.parse(GET_dict)
        qs = test_filter.filter(qs)

        result = list(qs)
        self.assertEqual(len(result), 2)

        self.assertTrue(self.available_products[3] in result)
        self.assertTrue(self.available_products[4] in result)
