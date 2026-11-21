from django.urls import path
from . import views

from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
        path('add/', views.add_employee, name='add_employee'),
        path('update/<int:id>/', views.update_employee, name='update_employee'),
        path('delete/<int:id>/', views.delete_employee, name='delete_employee'),
       
        path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
