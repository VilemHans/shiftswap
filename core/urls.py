from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('offer/<int:shift_id>/', views.offer_shift, name='offer_shift'),
    path('cancel-offer/<int:shift_id>/', views.cancel_offer, name='cancel_offer'),
    path('request/<int:shift_id>/', views.request_shift, name='request_shift'),
    path('approve/<int:request_id>/', views.approve_request, name='approve_request'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]