from django.urls import path
from . import views

app_name = "matchpredictions"  # 👈 this is required for namespacing

urlpatterns = [
    # 🏠 Home page
    path("", views.main_view, name="main"),

    # 🟢 Match list & detail
    path("main/", views.main_view, name="main"),
    path("match/<uuid:match_id>/", views.match_detail, name="match_detail"),

    # 🗳️ Voting endpoint
    path("vote/<uuid:match_id>/", views.vote_match, name="vote_match"),

    # 🛠️ Admin-only actions
    path("add/", views.match_create, name="match_create"),
    path("edit/<uuid:match_id>/", views.match_update, name="match_update"),
    path("delete/<uuid:match_id>/", views.match_delete, name="match_delete"),

    # ⚙️ AJAX endpoint for loading clubs dynamically
    path("ajax/load-clubs/", views.load_clubs, name="ajax_load_clubs"),

    path('<uuid:match_id>/edit_vote/', views.edit_vote, name='edit_vote'),
    path('<uuid:match_id>/delete_vote/', views.delete_vote, name='delete_vote'),

]



