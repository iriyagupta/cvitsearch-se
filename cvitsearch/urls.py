"""cvitsearch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from home.admin import admin_site
from home import views as home_views


#adding url patterns for now

urlpatterns = [
	url(r'^$', home_views.index, name='home'),
    url(r'^contact$', home_views.contact, name='contact'),
    url(r'^search$', home_views.search, name='search'),
    url(r'^list1$', home_views.list1, name='list1'),
    url(r'^list2$', home_views.list2, name='list2'),
    url(r'^list3$', home_views.list3, name='list3'),
    # url(r'^register$', home_views.RegisterView.as_view(), name='register'),
    url(r'^line_segment$', home_views.line_segment, name='line_segment'),
    url(r'^stats$', home_views.stats, name='stats'),
    url(r'^books$', home_views.books, name='books'),
    url(r'^ajax/search/', home_views.ajax_search, name='ajax_search'),
    url(r'^admin/', admin_site.urls),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
