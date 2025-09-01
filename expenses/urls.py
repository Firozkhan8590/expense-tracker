
from django.urls import path
from . import views 

urlpatterns = [
   path('', views.home, name='home'),
   path('register-expense/', views.register, name='register'),
   path('login/',views.login_view, name='login'),
   path('dashboard/',views.dashboard, name='user_dashboard'),
   path('add-expense/',views.add_expense, name='add_expense'),
   path('edit-expense/<int:expense_id>/', views.edit_expense_user, name='edit_expense_user'),
   path('delete-expense/<int:expense_id>/', views.delete_expense_user, name='delete_expense_user'),
   path('logout/', views.logout_view, name='logout'),

   #admin
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('manage-users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('manage-expenses/', views.manage_expenses, name='manage_expenses'),
    path('manage-expenses/edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('manage-expenses/delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('download-report/', views.download_expense_report, name='download_report'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
]