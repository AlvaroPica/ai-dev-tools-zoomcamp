from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_todo, name='create_todo'),
    path('edit/<int:todo_id>/', views.edit_todo, name='edit_todo'),
    path('delete/<int:todo_id>/', views.delete_todo, name='delete_todo'),
    path('toggle/<int:todo_id>/', views.toggle_resolved, name='toggle_resolved'),
]
