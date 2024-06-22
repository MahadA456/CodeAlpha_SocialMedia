from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from .models import Post, Comment, Follow, Block, Story, Message, Profile
from .forms import PostForm, CommentForm, StoryForm, MessageForm, ProfileForm, SignUpForm

def home(request):
    return redirect('login')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)  # Create a Profile for the user
            login(request, user)
            return redirect('view_posts')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('view_posts')
    else:
        form = PostForm()
    return render(request, 'core/create_post.html', {'form': form})

@login_required
def view_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'core/view_posts.html', {'posts': posts})

@login_required
def create_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('view_posts')
    else:
        form = CommentForm()
    return render(request, 'core/create_comment.html', {'form': form, 'post': post})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('view_posts')
    return render(request, 'core/delete_comment.html', {'comment': comment})

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    return redirect('view_posts')

@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    return redirect('view_posts')

@login_required
def block_user(request, user_id):
    user_to_block = get_object_or_404(User, id=user_id)
    Block.objects.get_or_create(blocker=request.user, blocked=user_to_block)
    return redirect('view_posts')

@login_required
def unblock_user(request, user_id):
    user_to_unblock = get_object_or_404(User, id=user_id)
    Block.objects.filter(blocker=request.user, blocked=user_to_unblock).delete()
    return redirect('view_posts')

@login_required
def create_story(request):
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.user = request.user
            story.save()
            return redirect('view_stories')
    else:
        form = StoryForm()
    return render(request, 'core/create_story.html', {'form': form})

@login_required
def view_stories(request):
    current_time = timezone.now()
    stories = Story.objects.filter(expires_at__gt=current_time).order_by('-created_at')
    return render(request, 'core/view_stories.html', {'stories': stories})

@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('inbox')
    else:
        form = MessageForm()
    return render(request, 'core/send_message.html', {'form': form})

@login_required
def inbox(request):
    messages = Message.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'core/inbox.html', {'messages': messages})

@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    posts = Post.objects.filter(user=user).order_by('-created_at')
    return render(request, 'core/profile.html', {'profile': profile, 'posts': posts})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'core/edit_profile.html', {'form': form})
@login_required
def logout_view(request):
    logout(request)
    return redirect('login') 