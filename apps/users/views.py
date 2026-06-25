from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileEditForm, RegistrationForm


def register(request):
    """Self-service registration. Logs the user in immediately on success."""
    if request.user.is_authenticated:
        return redirect('users:profile_detail_self')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Annsana, {user.username}.')
            return redirect('users:profile_detail_self')
    else:
        form = RegistrationForm()

    return render(request, 'users/register.html', {'form': form})


def profile_detail(request, username):
    """Public profile view. Anyone can view; only the owner sees the edit link."""
    profile_user = get_object_or_404(User, username=username)
    return render(request, 'users/profile.html', {
        'profile_user': profile_user,
        'profile': profile_user.profile,
        'is_own_profile': request.user.is_authenticated and request.user == profile_user,
    })


@login_required
def profile_detail_self(request):
    """Convenience redirect target after login/registration: /profile/me/."""
    return redirect('users:profile_detail', username=request.user.username)


@login_required
def profile_edit(request):
    """Lets the logged-in user edit their own profile."""
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('users:profile_detail', username=request.user.username)
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'users/profile_edit.html', {'form': form})
