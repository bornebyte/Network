from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json

from .models import *


def index(request):
    all_posts = Post.objects.all().order_by('-date_created')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number == None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = []
    suggestions = []
    if request.user.is_authenticated:
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
    return render(request, "network/index.html", {
        "posts": posts,
        "suggestions": suggestions,
        "page": "all_posts",
        'profile': False
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        fname = request.POST["firstname"]
        lname = request.POST["lastname"]
        profile = request.FILES.get("profile")
        cover = request.FILES.get('cover')

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = fname
            user.last_name = lname
            if profile is not None:
                user.profile_pic = profile
            # Note: If no profile pic is provided, it will remain empty (ImageField allows blank=True)
            if cover is not None:
                user.cover = cover           
            user.save()
            Follower.objects.create(user=user)
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")



def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse("User not found", status=404)
    
    all_posts = Post.objects.filter(creater=user).order_by('-date_created')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number == None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = []
    suggestions = []
    follower = False
    if request.user.is_authenticated:
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]

        follower_obj = Follower.objects.filter(user=user).first()
        if follower_obj and request.user in follower_obj.followers.all():
            follower = True
    
    follower_obj = Follower.objects.filter(user=user).first()
    follower_count = follower_obj.followers.all().count() if follower_obj else 0
    following_count = Follower.objects.filter(followers=user).count()
    return render(request, 'network/profile.html', {
        "username": user,
        "posts": posts,
        "posts_count": all_posts.count(),
        "suggestions": suggestions,
        "page": "profile",
        "is_follower": follower,
        "follower_count": follower_count,
        "following_count": following_count
    })

def following(request):
    if request.user.is_authenticated:
        following_user = Follower.objects.filter(followers=request.user).values('user')
        all_posts = Post.objects.filter(creater__in=following_user).order_by('-date_created')
        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
        return render(request, "network/index.html", {
            "posts": posts,
            "suggestions": suggestions,
            "page": "following"
        })
    else:
        return HttpResponseRedirect(reverse('login'))

def saved(request):
    if request.user.is_authenticated:
        all_posts = Post.objects.filter(savers=request.user).order_by('-date_created')

        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)

        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).order_by("?")[:6]
        return render(request, "network/index.html", {
            "posts": posts,
            "suggestions": suggestions,
            "page": "saved"
        })
    else:
        return HttpResponseRedirect(reverse('login'))
        


@login_required
def create_post(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        try:
            post = Post.objects.create(creater=request.user, content_text=text, content_image=pic)
            return HttpResponseRedirect(reverse('index'))
        except Exception as e:
            return HttpResponse(str(e), status=500)
    else:
        return HttpResponse("Method must be 'POST'", status=405)

@login_required
@csrf_exempt
def edit_post(request, post_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        img_chg = request.POST.get('img_change')
        post_id = request.POST.get('id')
        try:
            post = Post.objects.get(id=post_id)
            if post.creater != request.user:
                return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)
            
            post.content_text = text
            if img_chg != 'false':
                post.content_image = pic
            post.save()
            
            post_text = post.content_text if post.content_text else False
            post_image = post.img_url() if post.content_image else False
            
            return JsonResponse({
                "success": True,
                "text": post_text,
                "picture": post_image
            })
        except Post.DoesNotExist:
            return JsonResponse({"success": False, "error": "Post not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    else:
        return HttpResponse("Method must be 'POST'", status=405)

@csrf_exempt
def like_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            try:
                post = Post.objects.get(pk=id)
                post.likers.add(request.user)
                post.save()
                return HttpResponse(status=204)
            except Post.DoesNotExist:
                return HttpResponse("Post not found", status=404)
            except Exception as e:
                return HttpResponse(str(e), status=500)
        else:
            return HttpResponse("Method must be 'PUT'", status=405)
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def unlike_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            try:
                post = Post.objects.get(pk=id)
                post.likers.remove(request.user)
                post.save()
                return HttpResponse(status=204)
            except Post.DoesNotExist:
                return HttpResponse("Post not found", status=404)
            except Exception as e:
                return HttpResponse(str(e), status=500)
        else:
            return HttpResponse("Method must be 'PUT'", status=405)
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def save_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            try:
                post = Post.objects.get(pk=id)
                post.savers.add(request.user)
                post.save()
                return HttpResponse(status=204)
            except Post.DoesNotExist:
                return HttpResponse("Post not found", status=404)
            except Exception as e:
                return HttpResponse(str(e), status=500)
        else:
            return HttpResponse("Method must be 'PUT'", status=405)
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def unsave_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            try:
                post = Post.objects.get(pk=id)
                post.savers.remove(request.user)
                post.save()
                return HttpResponse(status=204)
            except Post.DoesNotExist:
                return HttpResponse("Post not found", status=404)
            except Exception as e:
                return HttpResponse(str(e), status=500)
        else:
            return HttpResponse("Method must be 'PUT'", status=405)
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def follow(request, username):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            try:
                user = User.objects.get(username=username)
                (follower, create) = Follower.objects.get_or_create(user=user)
                follower.followers.add(request.user)
                follower.save()
                return HttpResponse(status=204)
            except User.DoesNotExist:
                return HttpResponse("User not found", status=404)
            except Exception as e:
                return HttpResponse(str(e), status=500)
        else:
            return HttpResponse("Method must be 'PUT'", status=405)
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def unfollow(request, username):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            try:
                user = User.objects.get(username=username)
                follower = Follower.objects.get(user=user)
                follower.followers.remove(request.user)
                follower.save()
                return HttpResponse(status=204)
            except User.DoesNotExist:
                return HttpResponse("User not found", status=404)
            except Follower.DoesNotExist:
                return HttpResponse("Follower relationship not found", status=404)
            except Exception as e:
                return HttpResponse(str(e), status=500)
        else:
            return HttpResponse("Method must be 'PUT'", status=405)
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def comment(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                comment_text = data.get('comment_text')
                post = Post.objects.get(id=post_id)
                newcomment = Comment.objects.create(
                    post=post,
                    commenter=request.user,
                    comment_content=comment_text
                )
                post.comment_count += 1
                post.save()
                return JsonResponse([newcomment.serialize()], safe=False, status=201)
            except Post.DoesNotExist:
                return HttpResponse("Post not found", status=404)
            except Exception as e:
                return HttpResponse(str(e), status=500)
    
        try:
            post = Post.objects.get(id=post_id)
            comments = Comment.objects.filter(post=post).order_by('-comment_time').all()
            return JsonResponse([comment.serialize() for comment in comments], safe=False)
        except Post.DoesNotExist:
            return JsonResponse([], safe=False)
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def delete_post(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            try:
                post = Post.objects.get(id=post_id)
                if request.user == post.creater:
                    post.delete()
                    return HttpResponse(status=204)
                else:
                    return HttpResponse("Unauthorized", status=403)
            except Post.DoesNotExist:
                return HttpResponse("Post not found", status=404)
            except Exception as e:
                return HttpResponse(str(e), status=500)
        else:
            return HttpResponse("Method must be 'PUT'", status=405)
    else:
        return HttpResponseRedirect(reverse('login'))
