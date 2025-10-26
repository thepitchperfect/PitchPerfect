from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Post, PostImage, Comment
from .forms import PostForm
from club_directories.models import Club, League, FavoriteClub
import json


def forum_home(request):
    """
    Forum homepage with filtering capabilities
    - Viewable by everyone (logged in or not)
    - Supports filtering by multiple clubs and league
    - Shows news carousel at top, discussions below
    """
    # Base queryset
    all_posts = Post.objects.select_related('author').prefetch_related('clubs', 'images').annotate(
        comment_count=Count('comments')
    ).order_by('-created_at')
    
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
    
    # Get favorite club
    user_favorite_clubs = []
    if request.user.is_authenticated:
        user_favorite_clubs = Club.objects.filter(favorited_by__user=request.user)

    # Separate news and discussions
    news_posts = filtered_posts.filter(post_type='news').order_by('-created_at')
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
        'form': PostForm(user=request.user),
        'current_filters': {
            'user_favorite_clubs': user_favorite_clubs,
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
def create_post(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)

    form = PostForm(request.POST, user=request.user)
    if not form.is_valid():
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    post_type = form.cleaned_data.get('post_type')
    if post_type == 'news' and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Only staff can create official news.'}, status=403)

    club_ids = request.POST.getlist('clubs')
    if len(club_ids) > 3:
        return JsonResponse({'success': False, 'error': 'Max 3 clubs allowed'}, status=400)

    image_urls = request.POST.getlist('image_urls')
    image_captions = request.POST.getlist('image_captions')

    post = form.save(commit=False)
    post.author = request.user
    post.save()

    if club_ids:
        post.clubs.set(club_ids)

    # Append images (image_url, caption)
    for idx, url in enumerate(image_urls):
        if not url:
            continue
        caption = image_captions[idx] if idx < len(image_captions) else ''
        PostImage.objects.create(post=post, image_url=url, caption=caption)

    return JsonResponse({'success': True})

@login_required
def update_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user != post.author and not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)

    if request.method in ['POST', 'PUT']:
        # handle text data
        post.title = request.POST.get('title', post.title)
        post.content = request.POST.get('content', post.content)
        post.post_type = request.POST.get('post_type', post.post_type)
        post.save()

        # handle new image uploads (append, not replace)
        for i, img_file in enumerate(request.FILES.getlist('images')):
            caption = request.POST.get(f'caption_{i}', '')
            PostImage.objects.create(post=post, image=img_file, caption=caption)

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)


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