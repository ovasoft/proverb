'''import nltk
from nltk.corpus import wordnet as wn 
counter = 0
for ss in wn.all_synsets():
	print(ss.name())
	for lemma in ss.lemmas():
		print("synset: %s; sense: %s"%(ss,lemma.name()))
		if lemma.antonyms():
			print(wn.synsets(lemma.antonyms()[0].name()))

	counter+=1
	if counter == 11:
		break'''

		