from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from planner.views import AssociateRedirect, AssociateCallback, LoginCallback, LoginRedirect, account_initialize, test, fileuploader
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.contrib.auth.views import login, logout_then_login, password_change
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'churchplanner.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^planner/', include('planner.urls')),
    url(r'^associate/(?P<provider>(\w|-)+)/$', login_required(AssociateRedirect.as_view()), name='associate'),
    url(r'^associate-callback/(?P<provider>(\w|-)+)/$', login_required(AssociateCallback.as_view()), name='associate-callback'),
    url(r'^login/(?P<provider>(\w|-)+)/$', LoginRedirect.as_view(), name='login'),
    url(r'^login-callback/(?P<provider>(\w|-)+)/$', LoginCallback.as_view(), name='login-callback'),
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'^logout/$', logout_then_login),
    (r'^test/$', test),
    (r'account/change_password/$', password_change),
    (r'^account/initialize/$', account_initialize),
    (r'^$', login_required(TemplateView.as_view(template_name='main.html'))),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}),
    url( r"^fileuploader/(?P<pk>\d{1,6})/$", fileuploader),
    (r'^pdf_viewer$', login_required(TemplateView.as_view(template_name='pdf_viewer.html'))),
)


