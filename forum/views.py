from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Post, PostImage, Comment
from club_directories.models import Club, League
import json


def forum_home(request):
    """
    Forum homepage with filtering capabilities
    - Viewable by everyone (logged in or not)
    - Supports filtering by multiple clubs and league
    - Shows news carousel at top, discussions below
    """
    # Base queryset - removed 'league' from select_related since it might not exist yet
    all_posts = Post.objects.select_related('author').prefetch_related('clubs', 'images').annotate(
        comment_count=Count('comments')
    )
    
    # Get filter parameters
    club_ids = request.GET.getlist('clubs')  # Multiple clubs
    league_id = request.GET.get('league')
    search = request.GET.get('search')
    
    # Apply filters to all posts
    filtered_posts = all_posts
    
    if club_ids:
        filtered_posts = filtered_posts.filter(clubs__id__in=club_ids).distinct()
    
    if league_id:
        filtered_posts = filtered_posts.filter( Q(clubs__league_id=league_id)).distinct()
    
    if search:
        filtered_posts = filtered_posts.filter(
            Q(title__icontains=search) | 
            Q(content__icontains=search)
        )
    
    # Separate news and discussions
    news_posts = filtered_posts.filter(post_type='news').order_by('-created_at')[:3]  # Top 3 most recent news
    discussion_posts = filtered_posts.filter(post_type='discussion')
    
    # Pagination for discussions only
    paginator = Paginator(discussion_posts, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all clubs and leagues for filter dropdowns
    clubs = Club.objects.select_related('league').all().order_by('name')
    leagues = League.objects.all().order_by('name')
    
    context = {
        'news_posts': news_posts,
        'page_obj': page_obj,
        'clubs': clubs,
        'leagues': leagues,
        'current_filters': {
            'clubs': club_ids,
            'league': league_id,
            'search': search,
        }
    }
    
    return render(request, 'forum/home.html', context)


def post_detail(request, pk):
    """
    Post detail page with comments
    - Viewable by everyone
    - Only logged-in users can see comment form
    """
    post = get_object_or_404(
        Post.objects.select_related('author').prefetch_related('clubs', 'images', 'comments__author'),
        pk=pk
    )
    comments = post.comments.all()
    
    # Get user's favorite clubs if logged in (for potential actions)
    user_favorite_clubs = []
    if request.user.is_authenticated:
        user_favorite_clubs = Club.objects.filter(
            favorited_by__user=request.user
        ).select_related('league').order_by('name')
    
    context = {
        'post': post,
        'comments': comments,
        'user_favorite_clubs': user_favorite_clubs,
    }
    
    return render(request, 'forum/post_detail.html', context)


@login_required
@require_GET
def get_post_data(request, pk):
    """
    API endpoint to fetch post data for editing
    - Returns post data as JSON
    - Only author or admin can access
    """
    try:
        post = get_object_or_404(Post, pk=pk)
        
        # Check if user is the author or admin
        if post.author != request.user and not request.user.is_staff:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        
        # Get post images
        images = []
        for img in post.images.all().order_by('order'):
            images.append({
                'url': img.image_url,
                'caption': img.caption,
                'order': img.order
            })
        
        # Get tagged club IDs
        club_ids = list(post.clubs.values_list('id', flat=True))
        
        # Get league_id if field exists
        league_id = None
        if hasattr(post, 'league') and post.league:
            league_id = str(post.league.id)
        
        return JsonResponse({
            'success': True,
            'post': {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'post_type': post.post_type,
                'club_ids': [str(club_id) for club_id in club_ids],
                'league_id': league_id,
                'images': images,
            }
        })
    except Exception as e:
        import traceback
        print("Error in get_post_data:", traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


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
        
        # Create post (without league field since it doesn't exist in DB)
        post = Post.objects.create(
            title=data.get('title'),
            content=data.get('content'),
            author=request.user,
            post_type=post_type,
        )
        
        # Add club tags (multiple clubs)
        club_ids = data.get('club_ids', [])
        if club_ids:
            post.clubs.set(club_ids)
        
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
    """Update a post (AJAX) - author or admin only"""
    post = get_object_or_404(Post, pk=pk)
    
    # Check if user is the author or admin
    if post.author != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        post.title = data.get('title', post.title)
        post.content = data.get('content', post.content)
        post.save()
        
        # Update league if field exists
        if hasattr(Post, 'league'):
            league_id = data.get('league_id')
            post.league_id = league_id if league_id else None
            post.save()
        
        # Update club tags (multiple clubs)
        if 'club_ids' in data:
            post.clubs.set(data.get('club_ids', []))
        
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