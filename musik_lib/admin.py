from django.contrib import admin

# Register your models here.
from django.contrib import admin

from musik_lib.models.base import *

admin.site.register(Artist)
admin.site.register(Track)
admin.site.register(Collection)
admin.site.register(Library)
