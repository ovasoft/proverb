from django.db import models
from prophet.prophet import Prophet
from arangoclient.models import Client
from data_processing.utils import cleaner

# Create your models here.
class Baale(object):
	"""docstring for Baale"""
	def __init__(self):
		self.__client = Client()
		self.__prophet = Prophet()
		self.__predictions = {}

		self.__query = '''
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

		let gp_proverbs = (for doc in good_person filter doc.name in @gp
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

		let maslow_proverbs = (for doc in maslow filter doc.name in @maslow
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

		let sdt_proverbs = (for doc in sdt filter doc.name in @sdt
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

		let word_proverbs = (let result = (for id in @ln
		for v in 1..4 any  concat('syns/',id)	attr_to_proverb,
		attr_to_word,syn_defines_attr filter v._id like "proverbs%" return distinct v)
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
		self.__query1  = '''
		let domain_proverbs = (for doc in domain filter doc.name in @domains
		let all_ = (for v in 1..2 inbound doc._id attr_to_proverb filter v._id like 'proverb%'  
		return distinct v )
		for prov in all_
		let meta = (for v in 1..2 inbound prov._id attr_to_proverb return v)
		let p_w = (for v in meta filter v._id like 'words%' return v)
		let inter = (for v in meta filter v._id like 'interpretations%' return v.content)
		let trans = (for v in meta filter v._id like 'translations%' return v.content)
		let bp_w = (for i in p_w let mm = (for v in 1..2 any i._id attr_to_word filter v._id 
		like 'metaphors%' return v.content) return {'word':i.content,'metaphors':mm})
		
		return distinct {'proverb':prov,'kernel':prov.kernel,'interpretations':inter,
		'translations':trans,'words':bp_w})

		let gp_proverbs = (for doc in good_person filter doc.name in @gp
		let all_ = (for v in 1..2 inbound doc._id attr_to_proverb filter v._id like 'proverb%'  
		return distinct v )
		for prov in all_
		let meta = (for v in 1..2 inbound prov._id attr_to_proverb return v)
		let p_w = (for v in meta filter v._id like 'words%' return v)
		let inter = (for v in meta filter v._id like 'interpretations%' return v.content)
		let trans = (for v in meta filter v._id like 'translations%' return v.content)
		let bp_w = (for i in p_w let mm = (for v in 1..2 any i._id attr_to_word filter v._id 
		like 'metaphors%' return v.content) return {'word':i.content,'metaphors':mm})
		
		return distinct {'proverb':prov,'kernel':prov.kernel,'interpretations':inter,
		'translations':trans,'words':bp_w})

		let word_proverbs = (let result = (for id in @ln
		for v in 1..4 any  concat('syns/',id)	attr_to_proverb,
		attr_to_word,syn_defines_attr filter v._id like "proverbs%" return distinct v)
	 	for prov in result
		let meta = (for v in 1..2 inbound prov._id attr_to_proverb return v)
		let p_w = (for v in meta filter v._id like 'words%' return v)
		let inter = (for v in meta filter v._id like 'interpretations%' return v.content)
		let trans = (for v in meta filter v._id like 'translations%' return v.content)
		let bp_w = (for i in p_w let mm = (for v in 1..2 any i._id attr_to_word filter v._id 
		like 'metaphors%' return v.content) return {'word':i.content,'metaphors':mm})
		return distinct {'proverb':prov,'kernel':prov.kernel,
		'interpretations':inter,'translations':trans,'words':bp_w})

		return {'domain':domain_proverbs,'gp':gp_proverbs,
		'words':word_proverbs}

	'''		
	def special_query(self,predictions,complaint,norm=True):
		syns = set(self.__client.get_sentence_synsets(cleaner(complaint)))
		result = self.__client.db.aql.execute(self.__query,bind_vars={
			'domains':list(predictions['domain_prediction']),
			'sdt': list(predictions['sdt_prediction']),
			'maslow':list(predictions['maslow_prediction']),
			'gp':list(predictions['gp_prediction']),
			'ln':list(syns)
			})
		res = []
		for cur in result:
			res.append(cur)
		ranked =  self.rank1(res)
		confidence = (len(ranked['r1']),len(ranked['r2']),len(ranked['r3']),len(ranked['r4']),len(ranked['r5']))
		ranked = ranked['r1']+ranked['r2']+ranked['r3']+ranked['r4']+ranked['r5']
		if norm:
			ranked = ranked[0:3]
			return {'ranked':ranked,'confidence':confidence}
		else:
			return ranked




	def query(self,complaint):

		syns = set(self.__client.get_sentence_synsets(cleaner(complaint)))
		self.predictions = self.__prophet.super_predict(cleaner(complaint))
		self.predictions['domain_prediction'] = self.predictions['domain_prediction']
		#self.predictions['gp_prediction'] = ['perseverance','tenacity','daring','acumen']
		print('prediction is : {}'.format(self.predictions))
		
		result = self.__client.db.aql.execute(self.__query,bind_vars={
			'domains':list(self.predictions['domain_prediction']),
			'sdt': list(self.predictions['sdt_prediction']),
			'maslow':list(self.predictions['maslow_prediction']),
			'gp':list(self.predictions['gp_prediction']),
			'ln':list(syns)
			})
		#result = self.__client.db.aql.execute(qua)
		res = []
		for cur in result:
			res.append(cur)
		return self.rank1(res)

	def query1(self,complaint):
		syns = set(self.__client.get_sentence_synsets(cleaner(complaint)))
		self.predictions = self.__prophet.super_predict(cleaner(complaint))
		self.predictions['domain_prediction'] = self.predictions['domain_prediction']
		#self.predictions['gp_prediction'] = ['perseverance','tenacity','daring','acumen']
		print('prediction is : {}'.format(self.predictions))
		
		result = self.__client.db.aql.execute(self.__query1,bind_vars={
			'domains':list(self.predictions['domain_prediction']),
			'gp':list(self.predictions['gp_prediction']),
			'ln':list(syns)
			})
		#result = self.__client.db.aql.execute(qua)
		res = []
		for cur in result:
			res.append(cur)
		return self.rank1(res)

	def rank1(self,result):
		domain = result[0]['domain']
		sdt = result[0]['sdt']
		gp = result[0]['gp']
		maslow = result[0]['maslow']
		words = result[0]['words']
		total = domain+sdt+gp+maslow+words
		total = list({item['proverb']['_key']:item for item in total}.values())

		a = set([item['proverb']['_key'] for item in domain])
		b = set([item['proverb']['_key'] for item in sdt])
		c = set([item['proverb']['_key'] for item in gp])
		d = set([item['proverb']['_key'] for item in maslow])
		e = set([item['proverb']['_key'] for item in words])

		abcde = set.intersection(a,b,c,d,e)			#100
		abcd = set.intersection(a,b,c,d) #l75
		abce = set.intersection(a,b,c,e) #l80
		acde = set.intersection(a,c,d,e) #l80
		bcde = set.intersection(b,c,d,e) #l90
		abde = set.intersection(a,b,d,e) #l75
		abc = set.intersection(a,b,c) 	#l55
		abd = set.intersection(a,b,d)	#50
		abe = set.intersection(a,b,e)	#55
		acd = set.intersection(a,c,d)	#55
		ace = set.intersection(a,c,e)	#60
		ade = set.intersection(a,d,e)	#55
		bcd = set.intersection(b,c,d)	#65
		bce = set.intersection(b,c,e)	#70
		bde = set.intersection(b,d,e)	#65
		cde = set.intersection(c,d,e)	#70
		ab = set.intersection(a,b)		#30
		ac = set.intersection(a,c)		#35
		ad = set.intersection(a,d)		#30
		ae = set.intersection(a,e)		#35
		bc = set.intersection(b,c)		#45
		de = set.intersection(d,e)		#45
		bd = set.intersection(b,d)		#40
		be = set.intersection(b,e)		#45
		cd = set.intersection(c,d)		#45
		ce = set.intersection(c,e)		#50
		ao = set.difference(a,abcde,abcd,abce,acde,abde,abc,abd,abe,acd,ace,ab,ac,ad,ae) # 10
		bo = set.difference(b,abcde,abcd,abce,bcde,abc,abd,abe,bcd,bce,bde,ab,bc,bd,be)  #20
		co = set.difference(c,abcde,abcd,abce,acde,bcde,abc,acd,ace,bcd,bce,cde,ac,bc,cd,ce) #25
		do = set.difference(d,abcde,abcd,acde,bcde,abd,acd,ade,bcd,bde,cde,ad,de,bd,cd) # 20
		eo = set.difference(e,abcde,abce,acde,bcde,abe,ace,ade,bce,bde,cde,ae,de,be,ce) #25
		
		ranks = {100:[],90:[],80:[],75:[],70:[],65:[],
		60:[],55:[],50:[],45:[],40:[],35:[],30:[],25:[],20:[],10:[]}

		for item in total:
			if item['proverb']['_key'] in abcde:
				ranks.setdefault(100,[]).append(item)
			elif item['proverb']['_key'] in bcde:
				ranks.setdefault(90,[]).append(item)

			elif item['proverb']['_key'] in abce or item['proverb']['_key'] in acde:
				ranks.setdefault(80,[]).append(item)
			elif item['proverb']['_key'] in abcd or item['proverb']['_key'] in abde:
				ranks.setdefault(75,[]).append(item)
			elif item['proverb']['_key'] in bce or item['proverb']['_key'] in cde:
				ranks.setdefault(70,[]).append(item)
			elif item['proverb']['_key'] in bcd or item['proverb']['_key'] in bde:
				ranks.setdefault(65,[]).append(item)
			elif item['proverb']['_key'] in ace:
				ranks.setdefault(60,[]).append(item)
			elif item['proverb']['_key'] in abc or item['proverb']['_key'] in abe or item['proverb']['_key'] in acd or item['proverb']['_key'] in ade :

				ranks.setdefault(55,[]).append(item)
			elif item['proverb']['_key'] in ce or item['proverb']['_key'] in abd:
				ranks.setdefault(50,[]).append(item)
			elif item['proverb']['_key'] in cd or item['proverb']['_key'] in be or item['proverb']['_key'] in de or item['proverb']['_key'] in bc :
				ranks.setdefault(45,[]).append(item)
			elif item['proverb']['_key'] in bd :
				ranks.setdefault(40,[]).append(item)
			elif item['proverb']['_key'] in ac or item['proverb']['_key'] in ae:
				ranks.setdefault(35,[]).append(item)
			elif item['proverb']['_key'] in ad or item['proverb']['_key'] in ab:
				ranks[30].append(item)

			elif item['proverb']['_key'] in co or item['proverb']['_key'] in eo:
				ranks.setdefault(25,[]).append(item)
			elif item['proverb']['_key'] in bo or item['proverb']['_key'] in do:
				ranks.setdefault(20,[]).append(item)
			elif item['proverb']['_key'] in ao:
				ranks.setdefault(10,[]).append(item)

		return {'r1':ranks[100]+ranks[90],'r2':ranks[80]+ranks[75]+ranks[70],
		'r3':ranks[65]+ranks[60]+ranks[55],'r4':ranks[50]+ranks[45]+ranks[40],
		'r5':ranks[35]+ranks[30]+ranks[25]+ranks[20]+ranks[10]}






	def rank(self,result):
		domain = result[0]['domain']
		sdt = result[0]['sdt']
		gp = result[0]['gp']
		maslow = result[0]['maslow']
		words = result[0]['words']
		total = result[0]['domain']+result[0]['sdt']+result[0]['gp']+result[0]['maslow']+result[0]['words']
		
		#print(domain[0])
		a = [] #domain
		b = [] 	#sdt
		c = []	#gp
		d = []	#maslow
		e = []	#words
		for item in domain:
			a.append(item['proverb']['_key'])
		for item in sdt:
			b.append(item['proverb']['_key'])
		for item in gp:
			c.append(item['proverb']['_key'])
		for item in maslow:
			d.append(item['proverb']['_key'])
		for item in words:
			e.append(item['proverb']['_key'])

		a = set(a)
		b = set(b)
		c = set(c)
		d = set(d)
		e = set(e)


		r1 = a.intersection(b).intersection(c).intersection(d).intersection(e)
		r2 = a.intersection(b).intersection(c).intersection(d).union(
			a.intersection(b).intersection(c).intersection(e)).union(
			a.intersection(c).intersection(d).intersection(e)).union(
			b.intersection(c).intersection(d).intersection(e)).union(
			a.intersection(b).intersection(d).intersection(e))
		
		r3 = a.intersection(b).intersection(c).union(a.intersection(b).intersection(d)).union(
			a.intersection(b).intersection(e)).union(a.intersection(c).intersection(d)).union(
			a.intersection(c).intersection(e)).union(a.intersection(d).intersection(e)).union(
			b.intersection(c).intersection(d)).union(b.intersection(c).intersection(e)).union(
			b.intersection(d).intersection(e)).union(c.intersection(d).intersection(e))
		
		r4 = a.intersection(b).union(a.intersection(c)).union(a.intersection(d)).union(
			a.intersection(e)).union(b.intersection(c)).union(b.intersection(d)).union(
			b.intersection(e)).union(c.intersection(d)).union(c.intersection(e)).union(d.intersection(e)
			)
		r5 = a.union(b).union(c).union(d).union(e)
		


		tto = r5.difference(r4).union(r3).difference(r2).union(r1)
		print(tto)
		xtotal = []
		
		for item in total:
			if item['proverb']['_key'] in tto:
				xtotal.append(item)
				tto.remove(item['proverb']['_key'])
		

		rank1,rank2,rank3,rank4,rank5 = [],[],[],[],[]
		print('len of xtotal is {}'.format(len(xtotal)))
		print('length  of domain is {}'.format(len(domain)))
		print('length  of sdt is {}'.format(len(sdt)))
		print('length  of maslow is {}'.format(len(maslow)))
		print('length  of words is {}'.format(len(words)))
		print('length  of gp is {}'.format(len(gp)))
		for item in xtotal:

			#metmake = MakeMetaphors(item)
			#mets = metmake.fit_metaphor_to_context(self.predictions)
			#item['metaphors'] = mets
			if item['proverb']['_key'] in r1:
				rank1.append(item)
			elif item['proverb']['_key'] in r2:
				
				rank2.append(item)
			elif item['proverb']['_key'] in r3:
				
				rank3.append(item)
			elif item['proverb']['_key'] in r4:
				
				rank4.append(item)
			else:
			
				rank5.append(item)

		return{'r1':rank1,'r2':rank2,'r3':rank3,'r4':rank4,'r5':rank5}

	def abr(self,vals):
		res = []
		for val in vals:
			if val in ['finance','financial security']:
				res.append('finance')
			if val in ['physiological','health']:
				res.append('nutrition')
			if val == 'psychological':
				res.append('emotion')
			if val in ['community','work','safety','family','spiritual']:
				res.append(val)
		return res
	

class MakeMetaphors():
	def __init__(self,proverb):
		#print(proverb)
		if proverb['kernel']:
			self.kernels = []
			self.finished = []
			self.words = proverb['words']
			self.kernels+= self.xyz(proverb['kernel'])
			self.prophet = Prophet()
			ph = []
			while len(self.kernels)>0:
				for ker in self.kernels:
					ph+=self.xyz(ker)
					self.kernels.clear()
					self.kernels+=ph
					ph.clear()
			self.finished = list(set(self.finished))

		#print(self.finished)

	def isFinished(self,ss):
		if '{' in ss:
			return False
		else:
			return True

	def xyz(self,kernel):
		ker = []
		if not self.words:
			return ker
		for word in self.words:
			for met in word['metaphors']:
				a = kernel
				if not word['word'] in a:
					continue
				re = a.replace('{{{}}}'.format(word['word']),met)
				if self.isFinished(re):
					self.finished.append(re)
				else:
					ker.append(re)
		return ker 
	def group_compare(self,pred1,pred2):
		cmps = {}
		nt = 0
		keys = ['domain_prediction','sdt_prediction','maslow_prediction','gp_prediction']
		for key in keys:
			cp = self.compare(pred1[key],pred2[key])
			nt+=cp
			cmps[key] = cp
		return (cmps,nt/4)
		#return nt/4

	def compare(self,pred1,pred2):
		ef1 = set(pred1)
		ef2 = set(pred2)
		return len(ef1.intersection(ef2))/len(pred1)


	def fit_metaphor_to_context(self,complaint_predictions):
		fittings = {}
		try:

			for i in self.finished:
				ipred = self.prophet.super_predict(cleaner(i))
				res,tot = self.group_compare(ipred,complaint_predictions)
				#domain based comparison
				fittings[i] = res['domain_prediction']
			sorted_x = sorted(fittings.items(), key=lambda kv: kv[1],reverse=True)
			er = sorted_x[:int(0.5*len(self.finished))]
			#print(sorted_x)
			return [i[0] for i in er]
		except:
			return []