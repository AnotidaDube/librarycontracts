from django.urls import path
from . import views

urlpatterns = [
    # ==========================================
    # PUBLIC / HOMEPAGE
    # ==========================================
    # This is the landing page users see before logging in
    path('', views.welcome, name='welcome'),

    # ==========================================
    # AUTHENTICATION ROUTES
    # ==========================================
    # Maps to the custom auth views we created in views.py
    #path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ==========================================
    # DASHBOARD & CONTRACT MANAGEMENT
    # ==========================================
    path('list/', views.contract_list, name='contract_list'),
    path('add/', views.add_contract, name='add_contract'),
    path('edit/<int:contract_id>/', views.edit_contract, name='edit_contract'),
]