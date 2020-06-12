from django.core.exceptions import ValidationError
from django.test import TestCase

from musik_lib import validators


class CurrentYearTest(TestCase):

    def test_created_year(self):
        future_year = validators.current_year + 10
        with self.assertRaises(ValidationError):
            validators.validate_year(future_year)



