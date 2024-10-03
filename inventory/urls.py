# inventory/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Inventory URLs
    path('', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.inventory_add, name='inventory_add'),
    path('inventory/<str:sku>/edit/', views.inventory_edit, name='inventory_edit'),
    path('inventory/<str:sku>/delete/', views.inventory_delete, name='inventory_delete'),
    path('inventory/<str:sku>/', views.inventory_detail, name='inventory_detail'),

    # Inbound URLs
    path('inbound/', views.inbound_list, name='inbound_list'),
    path('inbound/add/', views.inbound_add, name='inbound_add'),
    path('inbound/<int:pk>/', views.inbound_detail, name='inbound_detail'),
    path('trigger_automated_inbound/', views.trigger_automated_inbound, name='trigger_automated_inbound'),
    
    # Outbound URLs
    path('outbound/', views.outbound_list, name='outbound_list'),
    path('outbound/add/', views.outbound_add, name='outbound_add'),
    path('outbound/<int:pk>/', views.outbound_detail, name='outbound_detail'),
    #path('outbound/generate_automated/', views.generate_automated_outbound, name='generate_automated_outbound'),
    path('outbound/update_status/<int:pk>/', views.outbound_update_status, name='outbound_update_status'),
    path('scheduled_outbounds/', views.scheduled_outbound_list, name='scheduled_outbound_list'),
    path('scheduled_outbounds/add/', views.scheduled_outbound_add, name='scheduled_outbound_add'),
    path('scheduled_outbounds/process/', views.trigger_scheduled_outbounds, name='trigger_scheduled_outbounds'),
    
    # User Management URLs
    path('users/', views.user_list, name='user_list'),
    path('users/create/<str:role>/', views.create_user, name='create_user'),
    path('users/<int:pk>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:pk>/delete/', views.delete_user, name='delete_user'),

    # Profile URL
    path('profile/', views.profile, name='profile'),
    #path('trigger_processes/', views.trigger_automated_processes, name='trigger_processes'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_add, name='customer_add'),
]
