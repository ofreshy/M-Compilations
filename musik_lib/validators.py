from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


current_year = timezone.now().year


def validate_year(value):
    """

    :param value:
    :return: Validation error if year is greater than this year
    """
    if value > current_year:
        raise ValidationError(
            _('%(value)s cannot exceed current year %(current_year)'),
            params={'value': value, 'current_year':current_year},
        )