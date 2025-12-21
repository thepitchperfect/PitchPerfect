from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.http import require_http_methods, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import strip_tags
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import Post, PostImage, Comment
from .forms import PostForm
from club_directories.models import Club, League, LeaguePick
from main.models import CustomUser
import requests, base64, json, traceback
from urllib.parse import unquote


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
    club_ids = [cid for cid in club_ids if cid.strip()]

    league_id = request.GET.get('league')
    league_id = league_id if league_id else None  
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
        user_favorite_clubs = Club.objects.filter(picked_in_leagues__user=request.user)

    # Separate news and discussions
    news_posts = filtered_posts.filter(post_type='news').order_by('-created_at')
    discussion_posts = filtered_posts.filter(post_type='discussion')
    
    # Pagination for discussions only
    paginator = Paginator(discussion_posts, 200)
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
        'user_favorite_clubs': user_favorite_clubs,
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
    
    context = {
        'post': post,
        'comments': comments,
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
        post = get_object_or_404(
            Post.objects.select_related('author').prefetch_related('clubs', 'images'), 
            pk=pk
        ) 

        if post.author != request.user and not request.user.is_staff:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        
        images = []
        for img in post.images.all().order_by('order'):
            images.append({
                'url': img.image_url,
                'caption': img.caption,
                'order': img.order
            })
        
        club_ids = list(post.clubs.values_list('id', flat=True))
        
        league_id = None 
            
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
    except Http404:
        return JsonResponse({'success': False, 'error': 'Post not found.'}, status=404)
    except Exception as e:
        print("Error in get_post_data:", traceback.format_exc()) # Keep for debugging
        return JsonResponse({'success': False, 'error': 'An internal server error occurred.'}, status=500)

def show_json(request):
    posts = Post.objects.all()

    data = []
    
    for post in posts:
        data.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "post_type": post.post_type,
            "author": post.author.username,    
            "created_at": post.created_at.isoformat(),
            "updated_at": post.updated_at.isoformat(),
            
            "clubs": list(
                post.clubs.values(
                    "id",
                    "name",
                    "logo_url",
                )
            )[:3],

            # Nested related images
            "images": [
                {
                    "url": img.image_url,
                    "caption": img.caption,
                    "order": img.order,
                }
                for img in post.images.all()
            ],

            # Nested comments
            "comments": [
                {
                    "author": c.author.username,
                    "content": c.content,
                    "created_at": c.created_at.isoformat()
                }
                for c in post.comments.all()
            ]
        })

    return JsonResponse(data, safe=False)

def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    # double encoding
    decoded = image_url
    while True:
        new = unquote(decoded)
        if new == decoded:
            break
        decoded = new

    image_url = decoded

    # CASE 1: base64 data URI => data:image/png;base64,....
    if image_url.startswith("data:"):
        try:
            header, encoded = image_url.split(",", 1)

            # header example: "data:image/png;base64"
            try:
                mime = header.split(";")[0].split(":")[1]   # extracts image/png
            except Exception:
                mime = "image/png"   # fallback

            img_bytes = base64.b64decode(encoded)

            return HttpResponse(
                img_bytes,
                content_type=mime
            )
        except Exception:
            return HttpResponse("Invalid base64 image", status=400)

    # CASE 2: URL fetch
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0 Safari/537.36"
            )
        }

        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()

        return HttpResponse(
            response.content,
            content_type=response.headers.get("Content-Type", "image/png")
        )
    except requests.RequestException as e:
        return HttpResponse(f"Error fetching image!: {str(e)}", status=500)

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

        # handle new image uploads 
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

@csrf_exempt
@login_required 
def create_comment_flutter(request, post_pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # required fields
            content = strip_tags(data.get("content", ""))
            author = request.user

            # test
            # try: 
            #     author = CustomUser.objects.get(username='ayshia.la')
            # except CustomUser.DoesNotExist:
            #     author = CustomUser.objects.first()

            # if not author:
            #     return JsonResponse({"status": "error", "message": "No default user found for testing. Please create a user."}, status=500)

            if not content:
                return JsonResponse({"status": "error", "message": "Content required"}, status=400)

            # fetch objects
            post = get_object_or_404(Post, pk=post_pk)

            # create comment
            comment = Comment.objects.create(
                post=post,
                author=author,
                content=content
            )

            new_comment_data = {
                'author': comment.author.username,
                'content': comment.content,
                'created_at': comment.created_at.isoformat()
            }

            return JsonResponse({"status": "success", "comment": new_comment_data}, status=200)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "POST required"}, status=405)

@csrf_exempt
@login_required
def create_post_flutter(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        title = strip_tags(data.get("title", ""))
        content = strip_tags(data.get("content", ""))
        post_type = data.get("post_type", "").lower() 
        author = request.user  
        
        #  test  
        # try: 
        #     author = CustomUser.objects.get(username='admin')
        # except CustomUser.DoesNotExist:
        #     author = CustomUser.objects.first()

        if not author:
            return JsonResponse({"status": "error", "message": "No default user found for testing. Please create a user."}, status=500)

        if not content:
            return JsonResponse({"status": "error", "message": "Content required"}, status=400)

        # Staff check for news posts
        if post_type == "news" and not author.is_staff:
            return JsonResponse({"success": False, "error": "Only staff can create official news."}, status=403)

        # clubs 
        club_ids = data.get("clubs", [])
        if len(club_ids) > 3:
            return JsonResponse({"success": False, "error": "Max 3 clubs allowed"}, status=400)

        # images + captions 
        image_urls = data.get("image_urls", [])
        image_captions = data.get("image_captions", [])

        post = Post.objects.create(
            title=title,
            content=content,
            post_type=post_type,
            author=author
        )

        # attach clubs
        if club_ids:
            post.clubs.set(club_ids)

        # attach images
        for idx, url in enumerate(image_urls):
            if not url:
                continue
            caption = (
                image_captions[idx] if idx < len(image_captions) else ""
            )
            PostImage.objects.create(
                post=post,
                image_url=url,
                caption=caption
            )

        return JsonResponse({
            "success": True,
            "post_id": post.id
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
 
def get_user_favorite_clubs_flutter(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "User not authenticated"}, status=401)
    
    user_favorite_clubs = Club.objects.filter(picked_in_leagues__user=request.user).distinct()
    
    clubs_data = [
        {
            "id": club.id,
            "name": club.name,
        }
        for club in user_favorite_clubs
    ]

    return JsonResponse({"status": "success", "clubs": clubs_data})