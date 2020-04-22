from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def about_view(request,*args,**kwargs):
	context = {
	'title':"About"
	}
	return render(request,'about.html',context)
