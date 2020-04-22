import random
import math
from .prophet import Prophet
from home.models import Baale
from arangoclient.models import Client
import re
from spacy.lang.en import English
import en_core_web_sm
from spacy import displacy

class Learner:
	def __init__(self,data):
		self.client = Client()
		learn = self.client.create_or_get_collection('learn')
		self.client.insert_document(learn,data)

class AProverb:
	def __init__(self,data):
		self.content = self.pap(data['proverb'].get('content'))
		self.actor_advice = self.pap(data['proverb'].get('actor_advice'))
		self.victim_advice = self.pap(data['proverb'].get('victim_advice'))
		self.observer_advice = self.pap(data['proverb'].get('observer_advice'))
		#self.kernel = data.get('kernel')
		self.interpretations = self.pap(data.get('interpretations'))
		self.id = self.pap(data['proverb'].get('_id'))
		self.key = self.pap(data['proverb'].get('_key'))
		self.story=self.pap(data['proverb'].get('narative'))
		#self.translations = data.get('translations')
		#self.words = data.get('words')
		#self.questions = data['questions'].split(';')
	def pap(self,val):
		return '' if val is None else val
	def get_key(self):
		return self.key
	def get_advice(self,role):
		advice = self.story

		if role == 'actor':
			advice += self.actor_advice
		elif role == 'victim':
			advice += self.victim_advice
		elif role == 'observer':
			advice += self.observer_advice
		return advice

	def get_other_advice(self,st,role):
		if st == 0:
			response = "A Yoruba proverb says {};".format(self.content)
		if st == 1:
			response = "Another proverb says {};".format(self.content)
		if st== 2:
			response = "The last proverb i have for you says {};".format(self.content)

		add = self.get_advice(role)
		if add is "":
			response+="Some data yet to be loaded"
		else:
			response+=add
		return response

class Core:
	def __init__(self,data):
		self.update(data)
		self.client = Client()
	def package(self):
		return{'depth':self.depth,
		'repeat':self.repeat,'stage':self.stage,'complaints':self.complaints,
		'response':self.response,'predictions':self.predictions,'u_occ':self.u_occ,
		'u_name':self.u_name,'ascertained':self.ascertained,
		'current_prediction':self.current_prediction,'choice':self.choice,
		'proper_predictions':self.proper_predictions,'proverbs':self.proverbs,
		'pop_data':self.pop_data,'evaluations':self.evaluations,'r_a':self.r_a}
	def reset(self):
		self.update({
			'complaints':'','predictions':{},
			'ascertained':{},
			'current_prediction':'','choice':'','proper_predictions':{},
			'proverbs':{},'pop_data':{},'evaluations':{},'r_a':{}
		})
	def update(self,data):
		for key,val in data.items():
			setattr(self,key,val)
		self.name = 'Sumonu'
	def save_chat(self):
		chats = self.client.create_or_get_collection('chats')
		self.client.insert_document(chats,self.package())



class Chatter(Core):
	def __init__(self,state={}):
		super().__init__(state)
		self.gad = Prophet()
		self.expresser = ExpressionHandler(self.name)
		self.baale = Baale()
		self.gps = ['daring','coolness','tenacity','humility','candour','patience','persevere',
		'honesty','acumen','consideration','genuiness',
		'kindness','moderation','recklessness','timidity','cruelty','greed','laziness',
		'indiscipline','pride','hypocrisy']
		self.domains = ['family','finance','nutrition','community','safety','career','emotion','spiritual']
		self.sdts  = ['autonomy','relatedness','competence']
		self.maslows = ['physiological','safety','belongingness','esteem','self_actualization']

	def compute_pop_content(self):
		ret = {}
		for key,vals in self.predictions.items():
			print(vals)
			if 'domain' in key:
				ret[key] = list(set(self.domains).difference(set(vals)))
			if 'sdt' in key:
				ret[key] = list(set(self.sdts).difference(set(vals)))
			if 'maslow' in key:
				ret[key] = list(set(self.maslows).difference(set(vals)))
			if 'gp' in key:
				ret[key] = list(set(self.gps).difference(set(vals)))
		ret['response'] = []
		print(ret)
		return ret
			

			
	def respond(self,message = 'default'):
		if self.stage == 'introduction':
			#check message and determine depth
			# switches to body automatically
			self.update(self.expresser.express_introduction(message,self.package()))
		
		if self.stage == 'body':
			# access expresprint(message)
			res = self.expresser.express_body(message,self.package())
			self.update(res)
			if self.depth == 2 and self.repeat == '00':
				self.predictions = self.gad.super_predict(self.complaint_string())
				print(self.spurious_prediction())

			if self.depth == 2 and self.repeat == '10':
				# reprocess
				self.reprocess(message)
			if self.depth == 3 and self.repeat == '01':
				self.pop_data = self.compute_pop_content()

			if self.depth == 4 and self.repeat == '01':
				#get proverbs
				#combine selects
				self.perfect_pro_pred()
				self.proverbs = self.baale.special_query(self.proper_predictions,self.complaint_string())
				self.reprocess(message)
		if self.stage == 'conclusion':
			self.update(self.expresser.express_conclusion(message,self.package()))

		return self.package()
	def perfect_pro_pred(self):
		for item in self.predictions.keys():
			if not item in self.proper_predictions.keys():
				self.proper_predictions.setdefault(item,[])
		for item in self.pop_data['response']:
			if item in self.gps:
				self.proper_predictions['gp_prediction'].append(item)
			elif item in self.maslows:
				self.proper_predictions['maslow_prediction'].append(item)
			elif item in self.sdts:
				self.proper_predictions['sdt_prediction'].append(item)
			elif item in self.domains:
				self.proper_predictions['domain_prediction'].append(item)
		


	def reprocess(self,message):
		res = self.expresser.express_body(message,self.package())
		self.update(res)


	def spurious_prediction(self):
		super_predictions = {}
		real_p = {}
		for idx, com in enumerate(self.complaints.split('**')):
			super_predictions['pred{}'.format(idx)] = self.gad.super_predict(com)
		for key in super_predictions['pred0'].keys():
			preds = []
			for pred in super_predictions:
				preds+=super_predictions[pred][key]
			real_p[key] = list(set(preds))
		return real_p




	def complaint_string(self):
		return self.complaints.replace('**','.')


class GeneralHandler(Core):
	def __init__(self,data):
		super().__init__(data)
		self.affirmative = ['good','alright','great','interesting','nice','okay','ok',
		'yes','yep','yea','true','exactly','correct','ofcourse','of','course','can','you','sure']
		self.res_to_affirmative = ['alright','okay','cool']
		self.descenting = ['nope','no','na','nay',"can't",'can','not','may','you']
		self.stage = data['stage']
	def message_is_affirmative(self,mul=0.6):
		cd = len(self.message['set'].intersection(set(self.affirmative))) 
		dd = math.ceil(mul*self.message['len'])
		#yy = 'yes' in self.message['message']
		return True if cd>=dd else False
	def message_is_descenting(self,mul=0.6):
		cd = len(self.message['set'].intersection(set(self.descenting))) 
		dd = math.ceil(mul*self.message['len'])
		#nn = 'no' in self.message['message']
		return True if cd>=dd else False

	def add_response(self,wh='none',message=""):
		if wh == 'turn':
			message = random.sample(self.turn,1)[0]
		elif wh == 'rta':
			message = random.sample(self.res_to_affirmative,1)[0]
		elif wh == 'aot':
			message = random.sample(self.aot,1)[0]
		elif wh == 'ae':
			message = random.sample(self.listening,1)[0]
		self.response.append(message)



class BodyHandler(GeneralHandler):
	def __init__(self,message,data):
		super().__init__(data)
		self.message = {'message':message.lower(),'len':len(message.split(' ')),
		'set':set(message.split(' '))}
		self.turn = ['May we move unto your complaint now?',
		"If you don't mind, I'll assume subsequent inputs are regarding your complaint",
		"Shall we discuss that which you'd like me to apply a proverb to?",
		" What is it you'd like me to apply a proverb to?",
		"I know you have stuff to do, may we go to your complaint?"]
		self.aot = ['is there any other thing i should know?',
		'any other relevant information?',
		'any other info to aid my knowledge of this subject matter?']
		self.listening = ["i'm listening"," okay, all ears",'say on then']

	
	def add_complaint(self):
		self.complaints+=' ** {} '.format(self.message['message'])

	def ask_questions(self):
		if self.current_prediction != "":
			if self.r_a[self.current_prediction] is True:
				#change prdiction
				options = set(self.predictions.keys()).difference(set(self.r_a.keys()))
				if len(options)>0:
					self.current_prediction = random.sample(options,1)[0]
				else:
					#ascertaining ends
					self.current_prediction = None
			#else:
				# not yet handled
		else:
			self.current_prediction =  random.sample(self.predictions.keys(),1)[0]

	def _in_message(self,pred,mess):
		expr = ""
		for idx,c in enumerate(pred):
			if idx!=0:
				expr+='{}*'.format(c)
			else:
				expr+=c
		expr = expr.strip('*')
		#print(expr)
		return True if len(re.findall(expr,mess))>0 else False
	def retrieve_selections(self):
		r_p = []
		for pred in self.predictions[self.current_prediction]:
			if self._in_message(pred,self.message['message']):
				r_p.append(pred)
		return r_p



	def determine_choice_and_prediction(self):
		if self.current_prediction != "":
			if self.ascertained[self.current_prediction][self.choice] is True:
				# change choice
				options = set(self.predictions[self.current_prediction]).difference(
					set(self.ascertained[self.current_prediction].keys()))
				if len(options)>0:
					self.choice = random.sample(options,1)[0]
				else:
					# change prediction
					options = set(self.predictions.keys()).difference(set(self.ascertained.keys()))

					if len(options)>0:
						self.current_prediction = random.sample(options,1)[0]
						self.choice = random.sample(self.predictions[self.current_prediction],1)[0]
					else:
						#ascertaining ends
						self.current_prediction = None
						self.choice = None
		else:
			self.current_prediction =  random.sample(self.predictions.keys(),1)[0]
			self.choice = random.sample(self.predictions[self.current_prediction],1)[0]
	def pick_response(self):
		self.determine_next_values()
		return self.package()

	def determine_next_values(self):
		next_depth = self.depth
		next_rep = self.repeat
		if self.depth == 0:
			self.add_response('turn')
			next_depth = 1
			# evaluate message
			#check if message is complaint or not
		if self.depth == 1:
			cd = not self.message_is_affirmative() 
			dd =  not self.message_is_descenting()			
			iscom = True if cd and  dd else False
			print(iscom,cd,dd)
			print(self.message['message'])
			if iscom:
				self.add_complaint()
				next_rep = '01'
				next_depth = 1
				self.add_response('aot')
			elif self.repeat == '00':
				self.add_response(message="I'll assume subsequent responses are about your complaint")
				self.add_response('ae')
				next_depth = 1
				next_rep = '01'
			elif self.message_is_descenting():
				self.add_response(message="I'll ask you some questions in order to make more accurate predictions")
				self.add_response(message='may I please?')
				next_depth = 2
				next_rep = '00'
			else:
				next_rep = '01'
				next_depth = 1
				self.add_response('ae')

				
		if self.depth == 2:
			if self.repeat == '00':
				if self.message_is_affirmative() or self.message['message'] in self.affirmative:
					self.add_response('rta')
					#take silence as ascent
					next_depth = 2
					next_rep = '10'
				elif self.message_is_descenting() or self.message['message'] in self.descenting:
					self.add_response(message='i percieve you are not in good mood')
					#at this point give a proverb that might suit this mood
					# manage this latter
					next_rep = '50'
					next_depth = 2
			if self.repeat == '10':
				# time to ascertain
				#ascertain domain
				#ch = self.choice
				c_p = self.current_prediction
				#self.determine_choice_and_prediction()
				self.ask_questions()
				print(self.current_prediction)
				if not self.current_prediction is None:
					#not self.choice is None and 
					#self.ascertained.setdefault(self.current_prediction,{})
					self.r_a.setdefault(self.current_prediction,False)
					#self.ascertained[self.current_prediction].setdefault(self.choice,False)
					#generate expression for choice, current_prediction
					#present expression
					next_depth =2
					next_rep =  '11'
				else:
					#ascertaining ends
					self.depth = 3 
					self.repeat = '00'
					# pop up to select other relevant options
				'''if  self.current_prediction == c_p:
					#self.choice == ch and
					# message was not affirmative
					self.repeat = '12'
					next_depth = 2'''
			if self.repeat == '11':
				# retreive selections from message
				sels = self.retrieve_selections()
				self.r_a[self.current_prediction] = True
				self.proper_predictions.setdefault(self.current_prediction,sels)
				next_depth = 2
				next_rep = '10'
				
		if self.depth == 3:
			if self.repeat == '00':
				#compute modal pop data
				self.add_response(message="A modal will show upon your subsequent response; kindly select 3 other relevant options; You may type 'okay'")
				next_depth = 3
				next_rep = '01'
			if self.repeat == '01':
				self.add_response(message="It's up")
				# when this value i.e 3,02 gets to ajax, trigger modal before chatting and chat after submission
				next_depth = 3
				next_rep = '02'
			if self.repeat == '02':
				# form result must be contained
				self.add_response(message='Thanks for your responses thus far')
				self.depth = 4
				self.repeat = '00'

		if self.depth == 4:
			if self.repeat == '00':
				# note characters
				# ela l'oro
				self.add_response(message="i'll speak to you  as the {} ".format(self.u_occ))
				#self.add_response(message="Please wait while i think")
				next_depth = 4
				next_rep = '01'
				#must be reprocessed
			if self.repeat == '01':
				#ascertain proverbs have been retrieved
				if len(self.proverbs['ranked']) > 0:
					self.repeat = '02'
					#next_rep = '02'
				else:
					# try another means to retrieve proverb
					print('try another means to retreive proverb')
					# i can't help you
					next_depth = 4
					next_rep = '01'
			if self.repeat == '02':
				print('here')
				prov = AProverb(self.proverbs['ranked'][0])
				self.add_response(message=prov.get_other_advice(0,self.u_occ))
				self.add_response(message='Hope it helps')
				next_rep = '03'
				next_depth = 4
			if self.repeat == '03':
				if self.message_is_descenting():
					self.add_response(message="Alright, I'm only speaking within the ambit of my knowledge")
				if self.message_is_affirmative():
					self.add_response(message = "I'm glad it does;")
				prov = AProverb(self.proverbs['ranked'][1])
				self.add_response(message=prov.get_other_advice(1,self.u_occ))
				self.add_response(message='does this help?')
				next_rep = '04'
				next_depth = 4
			if self.repeat == '04':
				if self.message_is_descenting():
					self.add_response(message='One last proverb for you')
				if self.message_is_affirmative():
					self.add_response(message = "I'm glad it does;")
				prov = AProverb(self.proverbs['ranked'][2])
				self.add_response(message=prov.get_other_advice(2,self.u_occ))
				self.add_response(message='Hope this does help you')
				next_rep = '05'
				next_depth = 4
			if self.repeat == '05':
				if self.message_is_descenting():
					self.add_response(message='Really?; I am still learning; And i will improve')
				if self.message_is_affirmative():
					self.add_response(message = "I'm glad it does;")
				self.stage = 'conclusion'
				next_rep = '00'
				next_depth = 0

		self.depth = next_depth
		self.repeat = next_rep

			#ascertain has ended


class IntroductionHandler(GeneralHandler):
	def __init__(self,message,data):
		super().__init__(data)
		self.message = {'message':message.lower(),'len':len(message.split(' ')),
		'set':set(message.split(' '))}
		self.hello = (['hello','hi','hey','sup'],
			set(['how','are','you','is','doing','faring','everything','going','fine','good']))
		self.welcome = (['welcome to my platform','Nice to have you here','Nice to meet you'],
			set(['thanks','thank','you','alright','my','pleasure','same','here','nice','meet','too','ok','okay']))
		self.intro = (['I am {}.;A robot learning to apply indigenous proverbs to human complaints.'.format(self.name),
		'You can call me {}.;I seek to learning the art of applying indigenous proverbs to human supplied contexts.'.format(self.name),
		"My name is {}. I am taking my time to understand the art of applying indigenous proverbs to human complaints.".format(self.name)
		],
		set(['good','alright','great','interesting','nice','okay','ok']))
		self.request_name = ['May I know your name?','What is your name please?']
		self.request_occ = ['Regarding your complaint, are you the accused, victim or an observer?',
		'Which of the these best describe your role in the context you are about to describe ?;Accused, victim or observer ']

	def pick_response(self):
		self.determine_next_depth()	
		print(self.depth)
		if not self.repeat in ['10','20'] and self.stage !='body':
			if self.depth == 0:
				self.add_response(random.sample(self.hello[0],1)[0])
			if self.depth == 1:
				self.add_response(random.sample(self.welcome[0],1)[0])
			if self.depth == 2:
				self.add_response(random.sample(self.intro[0],1)[0])
			if self.depth == 3:
				self.add_response(random.sample(self.request_name,1)[0])
			if self.depth == 4:
				self.add_response(random.sample(self.request_occ,1)[0])
		return self.package()
	
		
	def add_response(self,response):
		self.response.append(response)

	def extract_names(self,text):
		nlp = en_core_web_sm.load()
		nnt = nlp(text)
		ents = [i.text for i in nnt if i.pos_ == 'PROPN']
		exprs = []
		print(ents)
		for j,i in enumerate(ents):
			expr = ""
			for idx,c in enumerate(i):
				if idx == 0:
					expr+='[!@#~%^&]*{}*'.format(c)
				else:
					expr+='{}*'.format(c)
			'''if j == len(ents)-1:
				expr = expr.strip('*')'''

			exprs.append(expr)	
		names = []
		print(exprs)
		for expr in exprs:
			names+=re.findall(expr,text)

		rname = ""
		for name in ents:
			rname+=name
		return rname


	def determine_next_depth(self):
		#print(self.depth)
		next_depth = 0
		next_rep = '00'
		#print(int(self.depth) == 0 )
		if self.message['message'] == 'default':
			print('here pppp')
			next_depth = 0
			next_rep = '00'

		if self.depth == 0 and self.message['message'] != 'default':
			cd = len(self.message['set'].intersection(self.hello[1]))
			ed = self.message['message'] in self.hello[0]
			
			if cd >= math.ceil(0.7*self.message['len']) or ed is True :
				self.response.append('fine. Thanks')
				
			else:
				self.response.append('i do not understand your response.; But i assume all is well')
			
			next_depth = 1

		if self.depth == 1: 
			if len(self.message['set'].intersection(self.welcome[1])) >= math.ceil(0.7*self.message['len']) :
				self.response.append('great')
			next_depth = 2

		if self.depth == 2: 
			if len(self.message['set'].intersection(self.intro[1])) >= math.ceil(0.7*self.message['len']) :
				self.response.append('yeah')
			next_depth = 3

		if self.depth == 3:
			rname = self.extract_names(self.message['message'])
			if self.repeat == '00':
				if not rname:
					self.add_response("I couldn't tag your name; Kindly leave it as the only content of your message")
					next_rep = '10'
					next_depth = 3
				else:
					self.add_response("{} right?".format(rname))
					self.u_name = rname
					next_rep = '20'
					next_depth = 3
			elif self.repeat == '10':
				if self.message['len'] <=2 :
					self.add_response("{} right?".format(self.message['message']))
					self.u_name = self.message['message']
					next_rep = '20'
					next_depth = 3
				else:
					self.repeat = '00'
					next_depth = 3
					# what should dept be?
					#self.determine_next_depth()
			elif self.repeat == '20':
				if self.message['message'] in ['yes','yep','yea','true','exactly']:
					next_depth = 4
					next_rep = '00'
					self.add_response('Okay')
				elif self.message['message'] in ['no','nope','na','not at all','nay']:
					self.repeat == '00'
					next_depth = 3
					#self.determine_next_depth()
				else:
					next_depth = 4
					next_rep = '00'
					self.add_response("I'll stick to {} as your name please".format(self.u_name))
		if self.depth == 4:
			er = False
			if bool(re.match('ac+us+e',self.message['message'])):
				self.u_occ = 'actor'
				er = True
			if 'victim' in self.message['message']:
				self.u_occ = 'victim'
				er = True
			if 'observer' in self.message['message']:
				self.u_occ = 'observer'
				er = True

			if er == True:
				next_depth = 0
				thanks = ['Thanks for your responses thus far.',
				'I really appreciate your response.','Thanks for the info.']
				self.add_response(random.sample(thanks,1)[0])
				self.stage = 'body'
			else:
				self.add_response('Kindly specify one of actor, observer or victim')
				next_depth = 4

		self.depth = next_depth
		self.repeat = next_rep


class ConclusionHandler(GeneralHandler):
	def __init__(self,message,data):
		super().__init__(data)
		self.message = {'message':message.lower(),'len':len(message.split(' ')),
		'set':set(message.split(' '))}
		self.greetings = {'English':['bye','goodbye'],
		'Afrikaans':['totsiens'],'Yoruba':['O dabọ'],'Spanish':['adiós'],
		'Zulu':['Hamba kahle'],'Swahili':['kwaheri'],'Southern Sotho':['Sala hantle'],
		'Dutch':['Vaarwel'],'German':['Auf Wiedersehen'],'French':['Au revoir']}

	def get_result(self,key):
		grade = re.findall(r'\d+',self.message['message'])
		if len(grade) == 1:
			self.evaluations.setdefault(key,grade[0])
			return True
		else:
			self.add_response(message='Kind specify a rating between 1 and 5')
			return False
	def say_bye(self):
		lang = random.sample(list(self.greetings),1)
		lang = lang[0]
		message = random.sample(self.greetings[lang],1)[0]
		meaning = 'That is goodbye in {}'.format(lang)
		self.add_response(message=message)
		self.add_response(message=meaning)
	def is_bye(self):
		byes = [i  for bs in self.greetings.values() for i in bs]
		print(byes)
		return True if self.message['message'] in byes else False

	def pick_response(self):
		self.determine_next_values()
		return self.package()


	def determine_next_values(self):
		next_depth = self.depth
		next_rep = self.repeat
		if self.depth == 0:
			if self.repeat == '00':
				self.add_response(message='Thanks for your responses thus far')
				self.add_response(message='On a scale of 1-5, 1 being lowest, how related was the first proverb to your complaint')
				next_depth = 0
				next_rep = '01'
			if self.repeat == '01':
				wh = self.get_result('p1')
				if wh:
					self.depth = 1
					self.repeat = '00'
				else:
					next_depth = 0
					next_rep = '01'
		if self.depth == 1:
			if self.repeat == '00':
				self.add_response(message='Kindly rate the second proverb as you did the first')
				next_rep = '01'
				next_depth = 1
			if self.repeat == '01':
				wh = self.get_result('p2')
				if wh:
					self.depth = 2
					self.repeat = '00'
				else:
					next_depth = 1
					next_rep = '01'
		if self.depth == 2:
			if self.repeat == '00':
				self.add_response(message='Finally rate the third proverb on a scale of 1 to 5')
				next_rep = '01'
				next_depth = 2
			if self.repeat == '01':
				wh = self.get_result('p3')
				if wh:
					self.depth = 3
					self.repeat = '00'
					self.save_chat()
				else:
					next_depth = 2
					next_rep = '01'
		if self.depth == 3:
			if self.repeat == '00':
				self.add_response(message = 'Would you kindly teach me some stuff by?')
				next_depth = 3
				next_rep = '01'
			if self.repeat == '01':
				print('caught')
				if self.message_is_affirmative():
					self.add_response(message='Thanks; You will be redirected shortly')
					next_depth = 3
					next_rep = '10'
				elif self.message_is_descenting():
					self.add_response(message='Alright; Do you have another complaint?')
					#self.say_bye()
					next_depth = 3
					next_rep = '02'
			if self.repeat == '02':
				if self.message_is_affirmative():
					self.add_response('rta')
					self.stage = 'body'
					next_depth = 1
					next_rep = '01'
				else:
					self.repeat = '03'
					self.add_response(message='Thanks for your time')

			if self.repeat == '03':
				self.say_bye()
				#if self.is_bye():
				next_depth = 3
				next_rep = '03'
				# capture desire to do other things
		self.depth = next_depth
		self.repeat = next_rep


class ExpressionHandler:
	def __init__(self,name):
		self.name = name
		self.pos = ['daring','coolness','tenacity','humility','candour','patience','persevere',
		'honesty','acumen','consideration','genuiness','kindness','moderation']
		self.neg = ['recklessness','timidity','cruelty','greed','laziness',
		'indiscipline','pride','hypocrisy']
		self.presentations = [
		'will i be right to say * ?', 'i suspect * , is that true?',
		'may you clarify my doubt by ascertaining  that * ?',
		'if i assume  * , am i correct?',
		'could it be that * ?', 'shall we say * ?',
		'* . I presume. Is that right?',
		"i think *, i'm i right?"
		]
		self.thesaurus = {
		'event':['matter','experience','event','episode','occasion','occurence','issue'],
		'happened':['arose','took effect','occured','happened','transpired','took place','came about'],
		'casual':['adventitious','accidental','erratic','casual'],
		'close':['dear','attached','very familiar','close','intimate','bosom','cherished','confidential'],
		'elements':['gestures','signs','proofs','traces','elements'],
		'issue':['subject','matter','issue'],
		'lacking':['missing','needed','lacking'],
		'demonstrated':['manifested','demonstrated','expressed','displayed','indicated'],
		'someone':['someone','somebody'],
		'character':['someone','somebody','character'],
		'exhibited':['revealed','displayed','evinced','exhibited'],
		'lacked':['needed','is short of','lacked'],
		'suspect':['believe','consider','speculate','feel','suspect'],
		'clarify':['resolve','clear up','clarify'],
		'ascertaining':['confirming','verifying','ascertaining'],
		'assume':['conclude','guess','think'],
		'correct':['true','accurate','appropriate']
		}
	
	def express_introduction(self,message,data):
		intro = IntroductionHandler(message,data)
		ret = intro.pick_response()
		response = self.straighten(ret['response'])
		ret['response'] = response
		return ret

	def express_body(self,message,data):
		body = BodyHandler(message,data)
		ret = body.pick_response()
		#generate expressions
		if ret['depth'] == 2 and ret['repeat'] == '11':
			response = self.generate_presentation(self.generate_expression(ret['current_prediction'],ret['predictions'][ret['current_prediction']])) 

			ret['response']+=response
		response = self.straighten(ret['response'])

		ret['response'] = response

		if ret['depth'] == 4 and ret['repeat'] == '02':
			# start asking questions from proverbs
			print(ret['predictions'])
			print(ret['proverbs'])
		return ret

	def express_conclusion(self,message,data):
		conclusion = ConclusionHandler(message,data)
		ret = conclusion.pick_response()
		response = self.straighten(ret['response'])
		ret['response'] = response
		return ret




	def generate_expression(self,mtype,value):
		if 'domain' in mtype:
			return self.generate_domain_expr(value)
		if 'gp' in mtype:
			return self.generate_gp_expr(value)
		if 'sdt' in mtype:
			return self.generate_sdt_expr(value)
		if 'maslow' in mtype:
			return self.generate_maslow_expr(value)


	def generate_domain_expr(self,domain):
		expr = self.stringed_list(domain)
		ker = []
		res1 = ['which of * were affected by the event?; Let your selections be in a message',
		'which of the following aspects of life were affected by  the event;*;Kindly respond with a single message']
		ker+=random.sample(res1,1)
		return [i.replace('*', expr) for i in ker]

	def generate_gp_expr(self,gp):
		expr = self.stringed_list(gp)
		ker = []
		res1 = ['which of * are exhibited  in the event described?; Let your selections be in a message',
		'which of the following attributes are related to the event;*;Kindly respond with a single message']
		ker+=random.sample(res1,1)
		return [i.replace('*', expr) for i in ker]

	def stringed_list(self,ls):
		expr = ''
		for l in ls:
			expr+=' {}, '.format(l)
		return expr.strip(',')

	def generate_maslow_expr(self,maslow):
		expr = self.stringed_list(maslow)
		res1 = ['which of * were affected by the event?; Let your selections be in a message',
		'which of the following aspects of life were affected by  the event;*;Kindly respond with a single message']
		ker = []
		ker+=random.sample(res1,1)
		return [i.replace('*', expr) for i in ker]

	def generate_sdt_expr(self,sdt):
		expr = self.stringed_list(sdt)
		sdt = 'relationship' if sdt == 'belongingness' else sdt
		res = ['someone needs to improve his or her *']
		res1 = ['Which of * needs to be improved by any of the individuals in the event']

		return [i.replace('*', expr) for i in random.sample(res1,1) ]



	def generate_presentation(self,expr):
		#pres = random.sample(self.presentations,1)[0]
		#return [pres.replace('*', i) for i in expr]
		return expr

	def variate(self,presentation):
		kw = presentation.split(' ')
		for w in kw:
			syns = self.thesaurus.get(w,None)
			if not syns is None:
				presentation.replace(w,random.sample(syns,1))
		return presentation
	def straighten(self,responses):
		res = []
		for re in responses:
			res+=re.split(';')
		return res
