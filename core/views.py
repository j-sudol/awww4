from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
from backgrounds.models import Background

@login_required
def home(request):
    background = Background.objects.all()
    routes = request.user.route_set.all()
    return render(request, 'home.html', {'background_list': background, 'routes': routes})
