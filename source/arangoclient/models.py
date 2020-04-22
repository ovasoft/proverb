from django.db import models
from arango import ArangoClient
import nltk
from nltk.stem import WordNetLemmatizer
# Create your models here.

class Client():

	def __init__(self):
		self.__client = ArangoClient(protocol='http', host='localhost', port=8529)

		self.db = self.__client.db('proverbs_net', username='root', password='21adelaku&N')

	def create_or_get_collection(self,name):
		if self.db.has_collection(name):
			return self.db.collection(name)
		else:
			return self.db.create_collection(name)

	def insert_document(self,collection,documents):
		#print(documents)
		if type(documents) is list:
			meta = collection.import_bulk(documents)
		else:
			meta = collection.insert(documents)
		return meta

	def tokenise(self,sentence):
		sentence_tokens = nltk.word_tokenize(sentence)
		return nltk.pos_tag(sentence_tokens) 

	def lemmalise(self,word,pos):
		lemmatizer = WordNetLemmatizer()
		return lemmatizer.lemmatize(word,pos)

	def get_sentence_synsets(self,sentence):
		return self.transverse_to_get_synsets(
			self.get_db_representation(sentence))

	def get_db_representation(self,sentence):
		words = sentence.split(' ')
		tokens = self.tokenise(sentence)
		representations = []
		append = lambda q:representations.append(q)
		for item in tokens:
			pos = self.tags_map(item[1])
			pps = item[1]
			lem = item[0]
			if pos == 'z':
				continue
			cc = self.salt(lem,pos)
			if cc.empty() == False:
				for c in cc:
					append(c['_id'])
				continue
			poss = ['s','n','a','v','r']
			poss.remove(pos)
			for px in poss:
				cc = self.salt(lem,px)
				if cc.empty() == False:
					for c in cc:
						append(c['_id'])
					continue
		return representations

	def salt(self,lem,pos):
	#print("pos: %s, lmzing: %s "% (pos,lemmatizer.lemmatize(lem,pos)))
		return self.db.aql.execute('for doc in lemmas filter doc.name=="%s" limit 1 return doc'%
			(self.lemmalise(lem,pos)),count=True)

	def get_all_collection_doc(self,coll):
		aql = 'for doc in @@coll return doc'
		return self.db.aql.execute(aql,bind_vars={'@coll':coll},count=True)

	def link_proverb_to_groupings(self,groupings,proverb_id):
		'''domains_col = self.create_or_get_collection('domain')
		sdt_col = self.create_or_get_collection('domain')
		maslow_col = self.create_or_get_collection('domain')
		good_person_col = self.create_or_get_collection('good_person')'''
		domains = self.get_all_collection_doc('domain')
		sdt = self.get_all_collection_doc('sdt')
		maslow = self.get_all_collection_doc('maslow')
		good_person = self.get_all_collection_doc('good_person')
		relationships = []

		for dom in domains:
			if dom['name'] in groupings.keys():
				relationships.append({'_from':dom['_id'],'_to':proverb_id,'label':'domain_to_proverb'})
		for sd in sdt:
			if sd['name'] in groupings.keys():
				relationships.append({'_from':sd['_id'],'_to':proverb_id,'label':'sdt_to_proverb'})
		for mas in maslow:
			if mas['name'] in groupings.keys():
				relationships.append({'_from':mas['_id'],'_to':proverb_id,'label':'maslow_to_proverb'})
		for gp in good_person:
			if gp['name'] in groupings.keys():
				relationships.append({'_from':gp['_id'],'_to':proverb_id,'label':'good_person_to_proverb'})
		print(relationships)
		return self.insert_document(self.create_or_get_collection('attr_to_proverb'),relationships)





	def tags_map(self,tag):
		tag = tag.lower()
		if tag in ['jj','jjr','jjs']:
			return 'a'
		elif tag in ['nn','nns','nnp','nnps']:
			return 'n'
		elif tag in ['rb','rbs']:
			return 'r'
		elif tag in ['vb','vbd','vbg','vbn','vbp','vbz']:
			return 'v'
		else:
			return 'z'


	def transverse_to_get_synsets(self,db_representation):
		# this should later get higher order cluster
		#do salvaql = 
		synsets = []
		for rep in db_representation:
			aql = 'for v in 1..2 outbound "%s" lemma_in_syn return v'%rep
			cursor = self.db.aql.execute(aql)
			for cur in cursor:
				synsets.append(cur['_id'])
		#print(synsets)
		return synsets
		

		



