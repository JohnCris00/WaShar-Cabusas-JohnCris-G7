from django.urls import path

from . import views

app_name = "reservations"

urlpatterns = [
    path("book/<int:shop_pk>/", views.reservation_create, name="create"),
    path("mine/", views.my_reservations, name="my_reservations"),
    path("<int:pk>/edit/", views.reservation_update, name="update"),
    path("<int:pk>/cancel/", views.reservation_cancel, name="cancel"),
    path("<int:pk>/delete/", views.reservation_delete, name="delete"),
    path("manage/", views.shop_reservations, name="shop_reservations"),
    path("<int:pk>/status/<str:action>/", views.reservation_set_status, name="set_status"),
]