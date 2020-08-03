from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^submit/expense/$', views.submit_expense, name = 'submit_expense'),
    url(r'^submit/income/$', views.submit_income, name = 'submit_income'),
    url(r'^register/?$', views.register, name = 'register'),
    url(r'^login/?$', views.login, name = 'login'),
    url(r'^$', views.index, name = 'index'),
    url(r'^logout/?$', views.logout, name = 'logout'),
    url(r'^q/generalstat/?$', views.generalstat, name = 'generalstat'),
]