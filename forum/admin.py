from django.contrib import admin
from .models import Post, PostImage, Comment

class PostImageInline(admin.TabularInline):
    """Show related images under a post """
    model = PostImage
    extra = 0
    readonly_fields = ('image_url', 'caption', 'order', 'uploaded_at')
    can_delete = False

class CommentInline(admin.TabularInline):
    """Show comments under a post """
    model = Comment
    extra = 0
    readonly_fields = ('author', 'content', 'created_at', 'updated_at')
    can_delete = False

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """ Display for forum posts. """
    list_display = ('title', 'author', 'post_type', 'created_at')
    list_filter = ('post_type', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('author', 'created_at', 'updated_at')
    inlines = [PostImageInline, CommentInline]
    ordering = ('-created_at',)
    filter_horizontal = ('clubs',)

@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    """Standalone view for post images """
    list_display = ('post', 'image_url', 'caption', 'order', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('caption',)
    readonly_fields = ('uploaded_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin view for comments ."""
    list_display = ('author', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('author__username', 'content', 'post__title')
    readonly_fields = ('author', 'post', 'created_at', 'updated_at')

