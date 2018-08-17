from django.conf.urls import url
from . import views           # This line is new!


urlpatterns = [
    url(r'^$', views.index),
    url(r'^loginorregister/', views.loginorregister),
    url(r'^register/', views.register),
    url(r'^login/', views.login),
    url(r'^item/(?P<number>\d+)/$',views.itemDisplay),
    url(r'^create/', views.create),
    url(r'^findGPU/', views.findGPU),
    url(r'^additem/', views.additem),
    url(r'^delItem/(?P<number>\d+)/$',views.delItem),
    url(r'^cart/', views.cart),
    url(r'^purchase/', views.purchase),
    url(r'^checkout/', views.checkout),  # render checkout page
    url(r'^orderhistory/', views.orderhistory),
    url(r'^clear/', views.clear)
]