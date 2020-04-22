from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from .models import Baale
import jsonpickle
from prophet.chatter import Chatter,Core,AProverb,Learner
import json

# Create your views here.

def home_view(request,*args,**kwargs):
	context = {
		'title':"Home"
		}
	if(request.POST):
		
		return redirect('response',complaint=request.POST['complaint'])
	return render(request,'home.html',context)

def response_view(request,**kwargs):
	sumonu = Baale()
	res = sumonu.query(kwargs['complaint'])
	
	return render(request,'response.html',{'title':'Response','context':jsonpickle.encode(res)}) 
def end_view(request):
	return render(request,'end.html',{})
def learn_view(request):
	if request.POST:
		if not request.POST.get('tp') is None:
			data = jsonpickle.decode(request.POST['data'])
			l = Learner({'data':data['values'],'complaint':data['complaint']})
			return JsonResponse(jsonpickle.encode({'res':'end'}),safe=False)
		sumonu = Baale()
		#print(request.POST['stringed']['complaints'])
		we = jsonpickle.decode(request.POST['stringed'])
		res = sumonu.special_query(we['proper_predictions'],we['complaints'],norm=False)
		proverbs = []
		
		for prov in res:
			p = AProverb(prov)
			proverbs.append({'aa':p.get_advice('actor'),'va':p.get_advice('victim'),
				'oa':p.get_advice('observer'),'key':p.get_key()})
		return render(request,'learn.html',{'proverbs':jsonpickle.encode(proverbs),
			'complaints':we['complaints'].replace('**',' '),'bulk':request.POST['stringed']})
	


def chat_view(request,*args,**kwargs):
	context = {
		'title':"Home"
		}
	if(request.POST):
		state = {}
		defaults = {
			'stage':'introduction','depth': 0,
			'repeat': '00','complaints':'','predictions':{},
			'response':[],'u_name':'','u_occ':'','ascertained':{},
			'current_prediction':'','choice':'','proper_predictions':{},
			'proverbs':{},'pop_data':{},'evaluations':{},'r_a':{}
		}
		we = jsonpickle.decode(request.POST['stringed'])
		#print(we)
		#print(jsonpickle.decode(request.POST['complaint']))
		for param in defaults:
			#print()
			if we.get(param) is None:
				#setattr(state,param,defaults[param])
				state.setdefault(param,defaults[param])
			else:
				#setattr(state,param,)
				if param == 'depth':
					state.setdefault(param,int(request.POST[param]))
				else:
					state.setdefault(param,we[param])
		state['name'] = 'Sumonu'
		bot = Chatter(state)

		ret = bot.respond(request.POST['complaint'])
		#print(ret)
		return JsonResponse(jsonpickle.encode(ret),safe=False)
	return render(request,'chat.html',context)
