from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Post, PostImage, Comment
from club_directories.models import Club, League
import json


def forum_home(request):
    """
    Forum homepage with filtering capabilities
    - Viewable by everyone (logged in or not)
    - Supports filtering by club, league, and hashtags
    """
    posts = Post.objects.select_related('author', 'club').prefetch_related('images').annotate(
        comment_count=Count('comments')
    )
    
    # Get filter parameters
    club_id = request.GET.get('club')
    league_id = request.GET.get('league')
    league_tag = request.GET.get('league_tag')
    club_tag = request.GET.get('club_tag')
    post_type = request.GET.get('type')  # 'news' or 'discussion'
    search = request.GET.get('search')
    
    # Apply filters
    if club_id:
        posts = posts.filter(club_id=club_id)
    
    if league_id:
        # Filter by direct league tag OR club's league
        posts = posts.filter(Q(league_id=league_id) | Q(club__league_id=league_id))
    
    if league_tag:
        posts = posts.filter(league_tags__icontains=league_tag)
    
    if club_tag:
        posts = posts.filter(club_tags__icontains=club_tag)
    
    if post_type:
        posts = posts.filter(post_type=post_type)
    
    if search:
        posts = posts.filter(
            Q(title__icontains=search) | 
            Q(content__icontains=search) |
            Q(league_tags__icontains=search) |
            Q(club_tags__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(posts, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all clubs and leagues for filter dropdowns
    clubs = Club.objects.select_related('league').all().order_by('name')
    leagues = League.objects.all().order_by('name')
    
    # Get popular hashtags (extract from recent posts)
    popular_league_tags = get_popular_tags('league_tags')
    popular_club_tags = get_popular_tags('club_tags')
    
    context = {
        'page_obj': page_obj,
        'clubs': clubs,
        'leagues': leagues,
        'popular_league_tags': popular_league_tags,
        'popular_club_tags': popular_club_tags,
        'current_filters': {
            'club': club_id,
            'league': league_id,
            'league_tag': league_tag,
            'club_tag': club_tag,
            'type': post_type,
            'search': search,
        }
    }
    
    return render(request, 'forum/home.html', context)


def get_popular_tags(field_name, limit=10):
    """Extract popular hashtags from posts"""
    posts = Post.objects.exclude(**{field_name: ''}).values_list(field_name, flat=True)[:100]
    
    tag_count = {}
    for tags_string in posts:
        tags = [tag.strip() for tag in tags_string.split(',') if tag.strip()]
        for tag in tags:
            tag_count[tag] = tag_count.get(tag, 0) + 1
    
    # Sort by count and return top tags
    sorted_tags = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)[:limit]
    return [tag for tag, count in sorted_tags]


def post_detail(request, pk):
    """
    Post detail page with comments
    - Viewable by everyone
    - Only logged-in users can see comment form
    """
    post = get_object_or_404(
        Post.objects.select_related('author', 'club').prefetch_related('images', 'comments__author'),
        pk=pk
    )
    comments = post.comments.all()
    
    context = {
        'post': post,
        'comments': comments,
    }
    
    return render(request, 'forum/post_detail.html', context)


@login_required
@require_http_methods(["POST"])
def create_post(request):
    """
    Create a new post (AJAX)
    - Only logged-in users can create posts
    - Only admins can create 'news' type posts
    """
    try:
        data = json.loads(request.body)
        
        post_type = data.get('post_type', 'discussion')
        
        # Check if user is admin for news posts
        if post_type == 'news' and not request.user.is_staff:
            return JsonResponse({
                'success': False, 
                'error': 'Only admins can post official news'
            }, status=403)
        
        # Create post
        post = Post.objects.create(
            title=data.get('title'),
            content=data.get('content'),
            author=request.user,
            post_type=post_type,
            club_id=data.get('club_id') if data.get('club_id') else None,
            league_id=data.get('league_id') if data.get('league_id') else None,
            league_tags=data.get('league_tags', ''),
            club_tags=data.get('club_tags', ''),
        )
        
        # Add images if provided
        images_data = data.get('images', [])
        for idx, img_data in enumerate(images_data):
            PostImage.objects.create(
                post=post,
                image_url=img_data.get('url'),
                caption=img_data.get('caption', ''),
                order=idx
            )
        
        return JsonResponse({
            'success': True,
            'post': {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'author': post.author.username,
                'post_type': post.get_post_type_display(),
                'created_at': post.created_at.strftime('%B %d, %Y %I:%M %p')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["PUT"])
def update_post(request, pk):
    """Update a post (AJAX) - author only"""
    post = get_object_or_404(Post, pk=pk)
    
    # Check if user is the author
    if post.author != request.user:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        post.title = data.get('title', post.title)
        post.content = data.get('content', post.content)
        post.club_id = data.get('club_id') if data.get('club_id') else None
        post.league_id = data.get('league_id') if data.get('league_id') else None
        post.league_tags = data.get('league_tags', post.league_tags)
        post.club_tags = data.get('club_tags', post.club_tags)
        post.save()
        
        # Update images if provided
        if 'images' in data:
            # Delete existing images
            post.images.all().delete()
            
            # Add new images
            images_data = data.get('images', [])
            for idx, img_data in enumerate(images_data):
                PostImage.objects.create(
                    post=post,
                    image_url=img_data.get('url'),
                    caption=img_data.get('caption', ''),
                    order=idx
                )
        
        return JsonResponse({
            'success': True,
            'post': {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'updated_at': post.updated_at.strftime('%B %d, %Y %I:%M %p')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["DELETE"])
def delete_post(request, pk):
    """Delete a post (AJAX) - author or admin only"""
    post = get_object_or_404(Post, pk=pk)
    
    # Check if user is the author or admin
    if post.author != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    post.delete()
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def create_comment(request, post_pk):
    """Create a comment (AJAX) - logged-in users only"""
    post = get_object_or_404(Post, pk=post_pk)
    
    try:
        data = json.loads(request.body)
        comment = Comment.objects.create(
            post=post,
            content=data.get('content'),
            author=request.user
        )
        
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'author': comment.author.username,
                'created_at': comment.created_at.strftime('%B %d, %Y %I:%M %p')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["PUT"])
def update_comment(request, pk):
    """Update a comment (AJAX) - author only"""
    comment = get_object_or_404(Comment, pk=pk)
    
    if comment.author != request.user:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        comment.content = data.get('content', comment.content)
        comment.save()
        
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'updated_at': comment.updated_at.strftime('%B %d, %Y %I:%M %p')
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["DELETE"])
def delete_comment(request, pk):
    """Delete a comment (AJAX) - author or admin only"""
    comment = get_object_or_404(Comment, pk=pk)
    
    if comment.author != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    comment.delete()
    return JsonResponse({'success': True})