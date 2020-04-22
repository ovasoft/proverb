from django.db import models
from django.conf import settings
from arangoclient.models import Client
from django.urls import reverse
#from prophet.prophet import Prophet
#from data_processing.utils import cleaner
# Create your models here.

class Proverb(Client):
	
	def __init__(self):
		super().__init__()
		self.collection = self.create_or_get_collection('proverbs')

	def __load_data(self,id):
		if self.collection.has(id):
			return self.collection.get(id)
		else:
			return -1

	def create_proverb(self,data):
		#validate the data
		clean = []
		if '**' in data:
			data = data.split('**')
			for prov in data:
				clean.append({'content':prov})
		else:
			clean.append({'content':data})

		return self.insert_document(self.collection,clean)

	def get_all_proverbs(self):
		return self.collection.all()

	def __validate_data(self,data):
		errors = []
		if data['content'] == '' or data['content'] ==' ':
			errors.append('Content must be valid')
		return errors
	def get_a_proverb(self,id):
		if self.collection.has(id):
			return self.collection.get(id)
		else:
			return -1

	def ssofe(self,attr,data,proverb_id):
		result = []
		attr_to_proverb = self.create_or_get_collection('attr_to_proverb')
		syn_def_attr = self.create_or_get_collection('syn_defines_attr')
		sos = data[attr].split('**')
		label = 'syn_to_%s'%attr
		trans_doc = self.create_or_get_collection(attr)
		relationships = []
		prov_tran_rel = []
		for trans in sos:
			rel_syns = self.get_sentence_synsets(trans)
			trans_meta = self.insert_document(trans_doc,{'content':trans})
			for rel in rel_syns:
				relationships.append({'_from':rel,'_to':trans_meta['_id'],'label':label})
			prov_tran_rel.append({'_from':trans_meta['_id'],'_to':proverb_id,
				'label':'%s_to_proverb'%attr})
		result.append(self.insert_document(attr_to_proverb,prov_tran_rel))
		result.append(self.insert_document(syn_def_attr,relationships))
		return {'result':result}

	def save_proverb_attribute(self,data,proverb_id):
		attr_type = data['attr_type']
		attr_to_proverb = self.create_or_get_collection('attr_to_proverb')
		syn_def_attr = self.create_or_get_collection('syn_defines_attr')
		if attr_type == 'words':
			word = data['words']
			metaphors = data['wmm'].split(',')
			meaning = data['wm']
			word_doc = self.create_or_get_collection('words')
			met_doc = self.create_or_get_collection('metaphors')
			attr_to_word_doc = self.create_or_get_collection('attr_to_word')
			word_meta = self.insert_document(word_doc,{'content':word,'meaning':meaning})
			self.insert_document(attr_to_proverb,{'_from':word_meta['_id']
				,'_to':proverb_id,'label':'word_to_proverb'})
			#link meanining to synsets
			synsets_id = self.get_sentence_synsets(meaning)
			relationships = []
			for syn in synsets_id:
				relationships.append({'_from':syn,'_to':word_meta['_id'],'label':'syn_to_word'})
			for met in metaphors:
				w_m_rel = []
				met_meta = self.insert_document(met_doc,{'content':met})
				w_m_rel.append({'_from':met_meta['_id'],'_to':word_meta['_id']})
				synset_id = self.get_sentence_synsets(met)
				for syn in synset_id:
					relationships.append({'_from':syn,'_to':met_meta['_id'],'label':'syn_to_metaphor'})
				self.insert_document(attr_to_word_doc,w_m_rel)
			return (self.insert_document
				(syn_def_attr,relationships))
		elif attr_type == 'translations':
			return self.ssofe('translations',data,proverb_id)
		elif attr_type == 'interpretations':
			return self.ssofe('interpretations',data,proverb_id)
		elif attr_type == 'saveg':
			#return self.safe_domain()
			return self.link_proverb_to_groupings(data,proverb_id)
		elif attr_type == 'updateProverb':
			return self.update_proverb_attribute(data,proverb_id)

	
	def load_proverb_attribute(self,key,type):
		result = []
		aql = """with words,proverbs,metaphors,domain,sdt,good_person,maslow,syns for v in 1..10 inbound 
		@proverb attr_to_proverb, attr_to_word, syn_defines_attr,lemma_in_syn return DISTINCT v"""
		cursor = self.db.aql.execute(aql,bind_vars={'proverb':'proverbs/'+key})
		for cur in cursor:
			result.append(cur)
		return {'result':result}
	def load_rich_proverb(self,keys):
		return 'ko'

	def get_absolute_url(self,key):
		return reverse('proverb_detail',kwargs={'key':key})

	def link_others(self,sentences,proverb_id):
		relationships = []
		for sent in sentences:
			syn = self.get_sentence_synsets(sent)
			for s in syn:
				relationships.append({'_from':s,'_to':proverb_id,'label':'syn_to_proverb'})
		attr_to_proverb = self.create_or_get_collection('attr_to_proverb')
		return self.insert_document(attr_to_proverb,relationships)



		return syns
	def update_proverb_attribute(self,data,proverb_id):
		sents = [data['observer_advice'],data['victim_advice'],data['actor_advice']]
		self.link_others(sents,proverb_id)
		ex = self.collection.get(proverb_id)
		ex['content'] = data['proverb']
		ex['kernel'] = data['kernel']
		ex['observer_advice'] = data['observer_advice']
		ex['victim_advice'] = data['victim_advice']
		ex['actor_advice'] = data['actor_advice']
		ex['story'] = data['story']
		return self.db.update_document(ex)




        




		



