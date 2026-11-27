from django.urls import path

from . import views

app_name = "shops"

urlpatterns = [
    path("mine/", views.my_shops, name="my_shops"),
    path("new/", views.shop_create, name="shop_create"),
    path("<int:pk>/", views.shop_detail, name="shop_detail"),
    path("<int:pk>/edit/", views.shop_update, name="shop_update"),
    path("<int:pk>/delete/", views.shop_delete, name="shop_delete"),
    path("<int:shop_pk>/services/new/", views.service_create, name="service_create"),
    path("services/<int:pk>/edit/", views.service_update, name="service_update"),
    path("services/<int:pk>/delete/", views.service_delete, name="service_delete"),
    path("find/", views.shop_finder, name="shop_finder"),
    path("find/<int:pk>/", views.shop_public_detail, name="shop_public_detail"),
]