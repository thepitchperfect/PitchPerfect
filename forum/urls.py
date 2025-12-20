from django.urls import path
from . import views
from main.views import login_user

app_name = 'forum'

urlpatterns = [
    path('', views.forum_home, name='forum_home'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('login/', login_user, name='login'),
    path('api/post/create/', views.create_post, name='create_post'),
    path('api/post/<int:pk>/data/', views.get_post_data, name='get_post_data'), 
    path('api/post/<int:pk>/update/', views.update_post, name='update_post'),
    path('api/post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('api/post/<int:post_pk>/comment/create/', views.create_comment, name='create_comment'),
    path('api/comment/<int:pk>/update/', views.update_comment, name='update_comment'),
    path('api/comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('json/', views.show_json, name='show_json'),
    path('proxy-image/', views.proxy_image, name='proxy_image'),
    path('api/post/<int:post_pk>/comment/create/flutter/', views.create_comment_flutter, name='create_comment_flutter'),
    path('api/post/create/flutter/', views.create_post_flutter, name='create_post_flutter'),
]