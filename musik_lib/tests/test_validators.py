from django.core.exceptions import ValidationError
from django.test import TestCase

from musik_lib import validators


class CurrentYearTest(TestCase):

    def test_created_year(self):
        created_year = validators.current_year + 10
        self.assertRaises(
            ValidationError,
            validators.validate_year(created_year),
        )


