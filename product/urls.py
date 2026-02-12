from django.urls import path

from product.views import home_page

urlpatterns = [
    path("", home_page, name="home"),
]
