from django.contrib import admin
from django.contrib.admin import AdminSite
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from .models import Book,Page,Announcement


class cvitAdmin(AdminSite):
    site_header = 'CVIT Search Administration'
    site_title = 'CVIT Search Admin'
    index_title = 'CVIT Search Site Admin'
    site_url = '/' 


#add the group and user based authorization admin page
admin_site = cvitAdmin(name='admin')
admin_site.register(Group, GroupAdmin)
admin_site.register(User, UserAdmin)



#add the models
admin_site.register(Book)
admin_site.register(Page)
admin_site.register(Announcement)

