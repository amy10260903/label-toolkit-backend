from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
class DemoView(TemplateView):
    template_name = "demo.html"