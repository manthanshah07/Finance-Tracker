from django.urls import path
from .views import goal_list, goal_add, goal_edit, goal_delete

urlpatterns = [
    path('', goal_list, name='goal_list'),
    path('add/', goal_add, name='goal_add'),
    path('edit/<int:pk>/', goal_edit, name='goal_edit'),
    path('delete/<int:pk>/', goal_delete, name='goal_delete'),
]
