from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserProfileForm
from properties.models import Property 

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваши данные успешно обновлены.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    favorite_properties = Property.objects.filter(
        favorited_by__user=request.user
    ).prefetch_related('images', 'translations')

    context = {
        'form': form,
        'properties': favorite_properties,
    }
    return render(request, 'account/profile.html', context)