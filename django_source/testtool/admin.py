from testtool.models import *
from django.contrib import admin

class VideoAdmin(admin.ModelAdmin):
    list_display = ('filename', 'test')
    
    
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'method', 'create_time')


class TestInstanceAdmin(admin.ModelAdmin):
    list_display = ('pk', 'test', 'owner', 'create_time')
    

class TestCaseItemAdmin(admin.ModelAdmin):
    list_display = ('test_case', 'play_order', 'video')


class TestCaseInstanceAdmin(admin.ModelAdmin):
    list_display = ('test_instance', 'play_order')

    
admin.site.register(Test, TestAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(TestInstance, TestInstanceAdmin)
admin.site.register(UserProfile)
admin.site.register(TestCase)
admin.site.register(TestCaseItem, TestCaseItemAdmin)
admin.site.register(TestCaseInstance, TestCaseInstanceAdmin)
admin.site.register(ScoreDSIS)
admin.site.register(ScoreSSCQE)