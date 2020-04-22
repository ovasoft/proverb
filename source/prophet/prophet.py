from collections import Counter
import csv
from django.conf import settings
import os
# Create your models here.

#from nltk.tokenize import sent_tokenize,word_tokenize
import warnings
warnings.filterwarnings(action = 'ignore')

import gensim

from gensim.models import Word2Vec

from .sentiment import sentiment

from data_processing.Elijah import predict 


class Prophet:
	"""docstring for Prophet"""
	
	def __init__(self):
		this_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		data_dir = os.path.join(this_dir,'data')

	
	def super_predict(self,sentence):
		eli_pred = predict(sentence)
		#print(eli_pred)
		return {
		'domain_prediction':self.normalise_domain(eli_pred['domains']),
		'sdt_prediction': self.normalise_sdt(eli_pred['sdt']),
		'maslow_prediction': self.normalise_maslow(eli_pred['maslow']),
		'gp_prediction': eli_pred['gp']
		}

	def lemmalise(self,word):
		#get word 
		cake_synset = wn.synsets(word)
		print(cake_synset)

	def get_sentiment(self,complaint):
		return sentiment(complaint)

	def normalise_domain(self,vals):
		res = []
		for val in vals:
			if val in ['finance','financial security']:
				res.append('finance')
			if val in ['physiological','health']:
				res.append('nutrition')
			if val == 'psychological':
				res.append('emotion')
			if val == 'work':
				res.append('career')
			if val in ['community','safety','family','spiritual']:
				res.append(val)
		return list(set(res))

	def normalise_sdt(self,vals):
		return list(set(['relatedness' if i== 'belongingness' else i for i in vals]))

	def normalise_maslow(self,vals):
		return list(set(['self_actualization' if i == 'self actualisation' else i for i in vals]))

'''Isiah = Prophet()
res = Isiah.super_predict('pride goes before a fall')
print(res)

for item in res:
	print('%s :'%item,res[item])'''
