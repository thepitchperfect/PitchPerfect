from django.urls import path
from . import views

urlpatterns = [
    # Page views (viewable by everyone)
    path('', views.forum_home, name='forum_home'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    
    # AJAX endpoints for posts (login required)
    path('api/post/create/', views.create_post, name='create_post'),
    path('api/post/<int:pk>/data/', views.get_post_data, name='get_post_data'),  # NEW: Get post data for editing
    path('api/post/<int:pk>/update/', views.update_post, name='update_post'),
    path('api/post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    
    # AJAX endpoints for comments (login required)
    path('api/post/<int:post_pk>/comment/create/', views.create_comment, name='create_comment'),
    path('api/comment/<int:pk>/update/', views.update_comment, name='update_comment'),
    path('api/comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
]