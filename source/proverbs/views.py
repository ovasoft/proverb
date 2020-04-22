from django.shortcuts import render
from .models import Proverb
from django.http import HttpResponse, JsonResponse

# Create your views here.

def all_proverbs_view(request,*args):
	owe = Proverb()
	data = []
	context = {
	'title':'All Proverbs',
	}
	for cur in owe.get_all_proverbs():
		data.append({'content':cur['content'],'key' : cur['_key']})
	context['data'] = data
	return render(request,'all_proverbs.html',context)

def a_proverb_view(request,key):
	owe = Proverb()
	data = owe.get_a_proverb(key)
	context = {
	'title':'Detail'
	}
	if data == -1:
		context['data'] = 'No such Document'
	else:
		context['data'] = data
		context['key'] = owe.get_absolute_url(data['_key'])
	return render(request,'proverb_detail.html',context)


def create_proverb_view(request,*args,**kwargs):
	context = {
	'title':"Proverbs",
	'class':'alert-danger',
	'message':'Some errors occured!',
	'state':'invisible'
	}
	if request.POST:
		print(request.POST['proverbs'])
		context['state'] = 'visible'
		owe = Proverb()
		result = owe.create_proverb(request.POST['proverbs'])
		if result['errors'] == 0 and result['error'] is False:
			context['class'] = 'alert-success'
			context['message'] = 'Proverbs successfully created'

	return render(request,'proverb_create.html',context)


def update_proverb_view(data):
	return 'hello'

def add_proverb_attr(request,key):
	if request.POST:
		print(request.POST) 
		owe = Proverb()
		result = owe.save_proverb_attribute(request.POST,'proverbs/'+key)
	return JsonResponse(result)

def load_proverb_attr(request,key,load):
	print(request.POST)
	if request.POST:
		owe = Proverb()
		result = owe.load_proverb_attribute(key,load)
	return JsonResponse(result)



'''
let domain_proverbs = (for doc in domain filter doc.name in @domains
		let all_ = (for v in 1..2 any doc._id attr_to_proverb filter v._id like 'proverb%'  
		return distinct v )
		for prov in all_
		let meta = (for v in 1..2 any prov._id attr_to_proverb return v)
		let p_w = (for v in meta filter v._id like 'words%' return v)
		let inter = (for v in meta filter v._id like 'interpretations%' return v.content)
		let trans = (for v in meta filter v._id like 'translations%' return v.content)
		let bp_w = (for i in p_w let mm = (for v in 1..2 any i._id attr_to_word filter v._id 
		like 'metaphors%' return v.content) return {'word':i.content,'metaphors':mm})
		
		return distinct {'proverb':prov,'kernel':prov.kernel,'interpretations':inter,
		'translations':trans,'words':bp_w})

		let gp_proverbs = (for doc in domain filter doc.name in @gp
		let all_ = (for v in 1..2 any doc._id attr_to_proverb filter v._id like 'proverb%'  
		return distinct v )
		for prov in all_
		let meta = (for v in 1..2 any prov._id attr_to_proverb return v)
		let p_w = (for v in meta filter v._id like 'words%' return v)
		let inter = (for v in meta filter v._id like 'interpretations%' return v.content)
		let trans = (for v in meta filter v._id like 'translations%' return v.content)
		let bp_w = (for i in p_w let mm = (for v in 1..2 any i._id attr_to_word filter v._id 
		like 'metaphors%' return v.content) return {'word':i.content,'metaphors':mm})
		
		return distinct {'proverb':prov,'kernel':prov.kernel,'interpretations':inter,
		'translations':trans,'words':bp_w})

		let maslow_proverbs = (for doc in domain filter doc.name in @maslow
		let all_ = (for v in 1..2 any doc._id attr_to_proverb filter v._id like 'proverb%'  
		return distinct v )
		for prov in all_
		let meta = (for v in 1..2 any prov._id attr_to_proverb return v)
		let p_w = (for v in meta filter v._id like 'words%' return v)
		let inter = (for v in meta filter v._id like 'interpretations%' return v.content)
		let trans = (for v in meta filter v._id like 'translations%' return v.content)
		let bp_w = (for i in p_w let mm = (for v in 1..2 any i._id attr_to_word filter v._id 
		like 'metaphors%' return v.content) return {'word':i.content,'metaphors':mm})
		
		return distinct {'proverb':prov,'kernel':prov.kernel,'interpretations':inter,
		'translations':trans,'words':bp_w})

		let sdt_proverbs = (for doc in domain filter doc.name in @sdt
		let all_ = (for v in 1..2 any doc._id attr_to_proverb filter v._id like 'proverb%'  
		return distinct v )
		for prov in all_
		let meta = (for v in 1..2 any prov._id attr_to_proverb return v)
		let p_w = (for v in meta filter v._id like 'words%' return v)
		let inter = (for v in meta filter v._id like 'interpretations%' return v.content)
		let trans = (for v in meta filter v._id like 'translations%' return v.content)
		let bp_w = (for i in p_w let mm = (for v in 1..2 any i._id attr_to_word filter v._id 
		like 'metaphors%' return v.content) return {'word':i.content,'metaphors':mm})
		
		return distinct {'proverb':prov,'kernel':prov.kernel,'interpretations':inter,
		'translations':trans,'words':bp_w})

		let word_proverbs = (let ids = (let strids = (for i in @ln  return i)
		for id in strids return id)
		let result = (for id in ids
	 	for v in 1..4 outbound 
	 	id
	 	attr_to_proverb,attr_to_word,syn_defines_attr filter v._id like "proverbs%" return distinct v)
	 	for prov in result
		let meta = (for v in 1..2 any prov._id attr_to_proverb return v)
		let p_w = (for v in meta filter v._id like 'words%' return v)
		let inter = (for v in meta filter v._id like 'interpretations%' return v.content)
		let trans = (for v in meta filter v._id like 'translations%' return v.content)
		let bp_w = (for i in p_w let mm = (for v in 1..2 any i._id attr_to_word filter v._id 
		like 'metaphors%' return v.content) return {'word':i.content,'metaphors':mm})
		return distinct {'proverb':prov,'kernel':prov.kernel,
		'interpretations':inter,'translations':trans,'words':bp_w})

		return {'domain':domain_proverbs,'sdt':sdt_proverbs,'gp':gp_proverbs,
		'maslow':maslow_proverbs,'words':word_proverbs}
'''