from django.urls import path

from .views import anketa_page, SaveClientView

urlpatterns = [

    # Bu manzil orqali Web App ochiladi: https://domeningiz.uz/webapp/
    path('anketa/', anketa_page, name='anketa_page'),

    # Bu manzilga JavaScript ma'lumot yuboradi
    path('api/save-client/', SaveClientView.as_view(), name='save_client'),
]
