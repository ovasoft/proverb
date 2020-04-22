import nltk
from nltk.corpus import wordnet as wn
import os
from django.conf import settings
from arango import ArangoClient
from nltk.corpus import stopwords
import multiprocessing
from multiprocessing import Process
from nltk.stem import WordNetLemmatizer
#settings.configure()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

client = ArangoClient(protocol='http', host='localhost', port=8529)

db = client.db('proverbs_net', username='root', password='21adelaku&N')

stop_words = set(stopwords.words('english'))

clear = lambda: os.system('clear')

def destination_file(file_name):
	return os.path.join(os.path.join(BASE_DIR,'data'),file_name)


def get_raw_lemmas(synset):
	lemmas = []
	dd = []
	if type(synset) is list:
		for syn in synset:
			dd.append(syn.name())
			for lemma in syn.lemmas():
				lemmas.append(lemma)
	else:
		dd.append(synset.name())
		lemmas=  [lemma for lemma in synset.lemmas()]
	return [lemmas,dd]

def create_lemmas_and_lemma_groups():
	done = [] # synset treated
	lemma_groups = [] # name of synset and associated lemmas come here; 
	# for every lemma get the synset of the antonym if available
	# add the synset to done and add the the lemmas to lemma_group
	counter = 0
	#get all sense in synsets
	for ss in wn.all_synsets():
		if ss.name() in done:
			continue
		if counter == 5:
			break
		# create a lemma group
		lemma_group = {'name':ss.name()}
		print("definition: %s;    POS:%s"%(ss.definition(),ss.pos()))
		#create a list of lemmas
		raw_lemmas,dr = get_raw_lemmas(ss)
		lemmas = []
		for lm in raw_lemmas:
			print("%s, pos:%s"%(lm.name(),lm.topic_domains()))
			if lm.antonyms():
				synt = wn.synsets(lm.antonyms()[0].name())
				s_r_l,dd = get_raw_lemmas(synt)
				done+=dd
				for ll in s_r_l:
					lemmas.append(ll.name())
					
			lemmas.append(lm.name())
		done+=dr
		lemma_group['lemmas'] = set(lemmas)
		lemma_groups.append(lemma_group)
		counter+=1
		state = (counter/117559)*100
		print("%d of %d lemma groups created -------------------%d %s" % (counter,117659,state,'%'))	
	return lemma_groups

def new_groupings():
	lem_col = create_or_get_collection('lemmas')
	syns_col = create_or_get_collection('syns')
	lemm_in_group = create_or_get_collection('lemma_in_syn')
	total = len(list(wn.all_synsets()))

	counter = 0
	for ss in wn.all_synsets():
		#dump in the db
		sg = insert_document(syns_col,{'name':ss.name(),'definition':ss.definition(),'pos':ss.pos()})
		for lm in ss.lemmas():
			#dump in db
			ll = insert_document(lem_col,{'name':lm.name(),'pos':ss.pos()})
			#create relationship
			op = insert_document(lemm_in_group,{'_from':ll['_id'],'_to':sg['_id']})
		print("Synset %d ----------------------------- %d %s"%(counter,(counter/total)*100,'%'))
		counter+=1

def define_syns_by_lemmas(cursor):
	wk = multiprocessing.current_process()
	lem_col = create_or_get_collection('lemmas')
	edge = create_or_get_collection('lem_defines_syn')
	for cur in cursor:
		print("%s is working on syn %s"%(wk.name,cur['name']))
		definition_tokens = nltk.word_tokenize(cur['definition'])
		pos = nltk.pos_tag(definition_tokens)
		for item in pos:
			cc = ''
			px = tags_map(item[1])
			if px == 'z':
				cc = salvation(item[0],'s')
			else:
				cc = db.aql.execute('for doc in lemmas filter doc.name=="%s" and doc.pos=="%s" return doc'%(item[0],px))
				if cc.empty() == True:
					cc = db.aql.execute('for doc in lemmas filter doc.name=="%s" limit 1 return doc'%(item[0]))
				if cc.empty() == True:
					cc = salvation(item[0],px)
			try:
				if cc.empty() is False:
					for c in cc:
						meta = insert_document(edge,{'_from':c['_id'],'_to':cur['_id']})
						print("%s inserted an edge with id %s"%(wk.name,meta['_id']))
			except:
				print('No salvation')
		print('---------------------------------------------------------------')


def salvation(lem,pos):
	returned = None
	cc = salt(lem,pos)
	if cc.empty() == False:
		return cc
	poss = ['s','n','a','v','r']
	poss.remove(pos)
	for px in poss:
		cc = salt(lem,px)
		if cc.empty() == False:
			returned = cc
			break
	return returned
def salt(lem,pos):
	lemmatizer = WordNetLemmatizer()
	#print("pos: %s, lmzing: %s "% (pos,lemmatizer.lemmatize(lem,pos)))
	return db.aql.execute('for doc in lemmas filter doc.name=="%s" limit 1 return doc'%(lemmatizer.lemmatize(lem,pos)))



def tags_map(tag):
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


def clean_name(name):
	sp =  name.split('.')
	return sp[0]

def create_or_get_collection(name):
	if db.has_collection(name):
		return db.collection(name)
	else:
		return db.create_collection(name)

def insert_document(collection,documents):
	if type(documents) is list:
		meta = collection.import_bulk(documents)
	else:
		meta = collection.insert(documents)
	return meta
#{'_id': 'lemmas/3520', '_key': '3520', '_rev': '_ZJcTdYW---'}

def append_lemma(l_col,li_col,lemma,lg_id):
	lm_meta = insert_document(l_col,{'name':lemma})
	insert_document(li_col,{'_from':lm_meta['_id'],'_to':lg_id})

def populate_and_link_llg():
	lemma_col = create_or_get_collection('lemmas')
	lemma_group_col = create_or_get_collection('lemma_groups')
	lemma_in_group = create_or_get_collection('lemma_in_group')
	counter = 0
	lemma_groups = create_lemmas_and_lemma_groups()
	llen = len(lemma_groups)
	for lg in lemma_groups:
		if clean_name(lg['name']) in stop_words:
			print("%s is in stopword"%clean_name(lg['name']))
			continue
		lg_meta = insert_document(lemma_group_col,{'name':lg['name']})
		for lm in lg['lemmas']:
			if lm in stop_words:
				print("%s is in stopword"%lm)
				continue
			lm_meta = insert_document(lemma_col,{'name':lm})
			insert_document(lemma_in_group,{'_from':lm_meta['_id'],'_to':lg_meta['_id']})
		counter+=1
		print("%d of %d inserted-----%d remaining"%(counter,llen,llen-counter))

def meaing():
	#cake_synsets = wn.synsets("human")
	counter = 5
	for synset in wn.all_synsets():
		if counter == 0:
			break
		print(synset.definition())
		counter-=1

def eee():
	synset = wn.synsets('naive')
	for sense in synset:
		print('Sense: %s; Definition: %s; POS: %s'%(sense.name(),sense.definition(),sense.pos()))

#======================================================================================================
#								Handle Inputs
#
#======================================================================================================

def test(tup):
	osise = multiprocessing.current_process()
	print("name %s"% osise.name)
	limit,offset = tup[0],tup[1]
	print(limit*offset)
	
	#nltk.download('punkt')
	#offset,limit
	#print(salvation('mitigating','s'))
	#define_syns_by_lemmas((20,5))
	#new_groupings()
	#eee()
	#create_lemmas_and_lemma_groups()

if __name__ == '__main__':
	syns_col = create_or_get_collection('syns')
	lem_col = create_or_get_collection('lemmas')
	docs = list(syns_col.all())
	x = int(len(docs)/50)
	splice = [(x*i,(i+1)*x) for i in range(50)]
	print(splice)
	jobs = []
	for i in splice:
		cur = docs[i[0]:i[1]]
		p = Process(target=define_syns_by_lemmas,args=(cur,))
		jobs.append(p)
	for job in jobs:
		job.start()
		job.join()

	#define_syns_by_lemmas((0,syns_col.count()))
	'''p1 = Process(target=define_syns_by_lemmas,args=((0,2000),))
	p2 = Process(target=define_syns_by_lemmas,args=((4000,2000),))
	p3 = Process(target=define_syns_by_lemmas,args=((4000,2000),))

	p1.start()
	p1.join()
	p2.start()
	p2.join()
	p3.start()
	p3.join()
	
	syns_col = create_or_get_collection('syns')
	x = int(syns_col.count()/5)
	ll = [(x,i*x) for i in range(6)]

	jobs = []
	for i in range(len(ll)):
		p = Process(target=define_syns_by_lemmas,args=(ll[i],))
		p.start()
		jobs.append(p)
	for k in jobs:
		
		k.join()'''



