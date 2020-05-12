# Register your models here.
from django.contrib import admin

from musik_lib.models.stats import *


class LibraryAdmin(admin.ModelAdmin):
    actions = ['update_stats']

    def update_stats(self, request, queryset):
        library_stat = LibraryStat.load()
        library_stat.update()
        self.message_user(request, "Calculated Library Stats.")

    update_stats.short_description = "Updating Stats for all library"


class CollectionAdmin(admin.ModelAdmin):
    actions = ['update_stats']

    def update_stats(self, request, queryset):
        library_stat = LibraryStat.load()
        created_objects = 0
        for col in queryset.all():
            c, created = CollectionStat.objects.get_or_create(
                collection=col,
                library_stat=library_stat,
            )
            c.update()
            created_objects += int(created)

        self.message_user(request, "Created {} collection stats.".format(created_objects))

    update_stats.short_description = "Updating calculation stats"


admin.site.register(Artist)
admin.site.register(Track)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Library, LibraryAdmin)
admin.site.register(CollectionStat)
admin.site.register(LibraryStat)
admin.site.register(ArtistFrequencyLibrary)
admin.site.register(ArtistFrequencyCollection)
admin.site.register(DuplicateTrack)
