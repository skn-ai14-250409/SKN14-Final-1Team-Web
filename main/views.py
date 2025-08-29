from django.shortcuts import render

def home_view(request):
    return render(request, 'my_app/home.html')

def api_chatbot_view(request):
    return render(request, 'my_app/main_chatbot.html')

def internal_docs_view(request):
    return render(request, 'my_app/internal_docs.html')