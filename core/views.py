from django.shortcuts import render

# Create your views here.

def homepage(request):
    """Renders the homepage template."""
    return render(request, 'core/home/homepage.html')
