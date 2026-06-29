from django.urls import path
from . import views
from . import search_views
from rest_framework.routers import DefaultRouter
from . import search_views

router = DefaultRouter()
#router.register(r'boards', views.BoardViewSet)
#router.register(r'lists', views.ListViewSet)
#router.register(r'cards', views.CardViewSet)

urlpatterns = [
    # Tableros
    path('', views.board_list, name='board_list'),
    path('create/', views.create_board, name='create_board'),
    path('<int:pk>/', views.board_detail, name='board_detail'),
    path('<int:pk>/edit/', views.edit_board, name='edit_board'),  
    path('<int:pk>/delete/', views.delete_board, name='delete_board'),
    path('<int:pk>/delete-permanent/', views.delete_board_permanent, name='delete_board_permanent'),
    path('api/user-owned-boards/', views.user_owned_boards_api, name='user_owned_boards_api'),
    
    # Listas
    path('<int:board_id>/lists/create/', views.create_list, name='create_list'),
    path('lists/<int:list_id>/edit/', views.edit_list, name='edit_list'),
    path('lists/<int:list_id>/delete/', views.delete_list, name='delete_list'),
    path('lists/update-position/', views.update_list_position, name='update_list_position'),
    
    # Tarjetas
    path('lists/<int:list_id>/cards/create/', views.create_card, name='create_card'),
    path('cards/<int:card_id>/edit/', views.edit_card, name='edit_card'),
    path('cards/update-position/', views.update_card_position, name='update_card_position'),
    path('cards/<int:card_id>/delete/', views.delete_card, name='delete_card'),
    
    # Miembros
    path('<int:board_id>/members/add/', views.add_member, name='add_member'),
    path('<int:board_id>/members/', views.board_members_api, name='board_members_api'),
    path('members/<int:membership_id>/remove/', views.remove_member, name='remove_member'),
    path('members/<int:membership_id>/permissions/', views.update_member_permissions, name='update_member_permissions'),

    path('search/', search_views.search_view, name='search'),
    path('search/api/', search_views.search_api, name='search_api'),
    path('calendar/', search_views.calendar_view, name='calendar'),
    path('panel/', search_views.panel_view, name='panel'),
    path('labels/', search_views.labels_view, name='labels'),
    path('labels/api/', search_views.labels_api, name='labels_api'),
    path('labels/create/', search_views.create_label, name='create_label'),
    path('labels/<int:label_id>/update/', search_views.update_label, name='update_label'),
    path('labels/<int:label_id>/delete/', search_views.delete_label, name='delete_label'),
    path('cards/<int:card_id>/labels/<int:label_id>/toggle/', search_views.toggle_card_label, name='toggle_card_label'),
]