from GenericTest.models import Video, TestCase, Test
from django.contrib import admin

class VideoAdmin(admin.ModelAdmin):
    fieldsets     = [
                     ('Method',      {'fields': ['description']}),
                     (None,          {'fields': ['filename'   ]}),
                     ('Included in', {'fields': ['test'   ]}),
                     ]
    list_display  = ('description', 'filename')
    search_fields = ['filename', 'description']
    
class TestCaseInline(admin.TabularInline):
    model  = TestCase
    extra  = 1
    fields = ['play_order', 'video', 'is_done']

class TestAdmin(admin.ModelAdmin):
    fieldsets      = [
                      (None,         {'fields': ['title', 'description']}),
                      ]
    inlines        = [TestCaseInline]
    list_display   = ('title', 'create_date', 'was_created_today')
    list_filter    = ['create_date']
    search_fields  = ['title', 'description']
    date_hierarchy = 'create_date'
    
admin.site.register(Test , TestAdmin)
admin.site.register(Video, VideoAdmin)