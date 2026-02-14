from django.urls import path

from product.views import home_page

urlpatterns = [
    path("<int:user_id>/", home_page, name="home"),
]
