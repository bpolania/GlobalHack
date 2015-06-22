import nltk
from nltk.corpus import PlaintextCorpusReader
from nltk.corpus import wordnet as wn

import os
import sys
sys.path.append("../generic_app/")
sys.path.append("../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

import glob
import re

from demo.models import Relationship, Ontology

json = {}

# convert_pdf_to_txt
# input:  string
# return: string
#
# this method gets the path for a PDF file and returns all the parseable text in a string


def convert_pdf_to_txt(path):
	
	rsrcmgr = PDFResourceManager()
	retstr = StringIO()
	codec = 'utf-8'
	laparams = LAParams()
	device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
	fp = file(path, 'rb')
	interpreter = PDFPageInterpreter(rsrcmgr, device)
	password = ""
	maxpages = 0
	caching = True
	pagenos=set()
	
	for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
	    interpreter.process_page(page)
	fp.close()
	
	device.close()
	str = retstr.getvalue()
	retstr.close()
	return str

# process_csv
# input:  string
# return: string
#
# this method gets the path for a CSV file and returns all the relevant words in a string,
# basically it removes commas and replace it with spaces.

def process_csv(path):

	str = open(path, 'r').read()
	str = str.replace(',', ' ')

	return str


# getRoot
# input:  string
# return: string
#
# this method gets a domain string to identify a relative path looking for a set of documents,
# identifies the type of files, create a new folder if necessary and stores a processed version
# of each file whether in text format. It can process pdf or csv files. It returns the relative
# path of the folder with processed files.

def getRoot(domain):
	
	# identify pdf files
	if len(glob.glob( domain + "/*.pdf")) > 0:
		
		# If necessary, make new dir for the corpus.
		corpusdir = domain + '_to_text'
		if not os.path.isdir(corpusdir):
			os.mkdir(corpusdir)
			
		# each files is processes and converted into text
		for document in glob.glob( domain + "/*.pdf"):
			string = convert_pdf_to_txt(document)
			newFileName = document.split('/', 1 )[1]
			newFileName = newFileName.replace("pdf", "txt")
			text_file = open(corpusdir + "/" + newFileName, "w")
			text_file.write(string)
			text_file.close()
		
		return corpusdir
		
	
	# identify csv files
	if len(glob.glob( domain + "/*.csv")) > 0:
		
		# If necessary, Make new dir for the corpus.
		corpusdir = domain + '_to_text'
		if not os.path.isdir(corpusdir):
			os.mkdir(corpusdir)
		
		# each files is processes and converted into text
		for document in glob.glob( domain + "/*.csv"):
			string = process_csv(document)
			newFileName = document.split('/', 1 )[1]
			text_file = open(corpusdir + "/" + newFileName, "w")
			text_file.write(string)
			text_file.close()
			
		return corpusdir
	
	return domain

	
# setData
# input:  string
# return: list, list
#
# this method gets a domain so it can look for a specific relative address for files
# once the set of files are identified they are processed so all the relevant words are stored in a list.
# It return two(2) lists of words, one with the relevant words and the other with original corpus of words.



def setData(domain):
	
	# domain variable can take one of the following values
	#
	# "chicago_crime_data",
	# "economics",
	# "software_vulnerability",
	# "cyber_threat",
	# "articles",
	# "msds"

	
	corpus_root = getRoot(domain)					# based on the selected domain corpus root will hold the relative address of the corpus
	wordlists = PlaintextCorpusReader(corpus_root, '.*')		# NLTK's laintextCorpusReader load text files in the root
	words = wordlists.words()					# and extract all the words in each file 

	my_stopwords = nltk.corpus.stopwords.words('english')		# my_stopwords holds a list of non-relevant (stop) words in english
	content = [w for w in words if w.lower() not in my_stopwords]	# stop words are removed
	content = [w for w in content if len(w) > 2]			# words shorther than two(2) characters are removed
	content = [w for w in content if not w.isdigit()]		# digit only words (e.g. "10", "30", "450") are removed

	result = {}							
	
	# a list of related words is created for each word in the content variable
	
	for word in content:						
		result[word] = []
		for sset in wn.synsets(word):				# the first synonym of a set is selected, this can be expanded to the rest of the words in the set for more accuracy but at the cost of performace
			for synset in sset.hyponyms():			# a set of hyponyms is added for the main synonym
				result[word].append(synset.name[0:synset.name.find('.')])

	return result,content # both the synonyms and the original word corpus is returned 


# ontology
# input:  string
# return: json data
#
# this method gets a topic input from the user, calls the setData method, creates and onthology and
# returns JSON data.


def ontology(topic):
	
	tree,corpus = setData(topic);
	
	data = {}
	orderedKeys = []
	result = {}
	orderedResult = []
	used = []
	
	# all words in the processed corpus are compared against against each other
	# if two words have an hyponym in common it's assigned as children to both words
	# at the end of the process, each word in the corpus will have a list of the hyponyms
	# they share with the rest of the words
	
	for root in corpus:
		data[root] = []
		for word in corpus:
			if root != word:
				intersection = list(set(tree[root]).intersection(tree[word]))
				if len(intersection) > 0:
					data[root].append(word)
					
	
	# the corpus will be ordered so the word with the most hyponyms in common with the rest of the words in the corpus
	# is at the top of the list, the rest of the worlds are ranked from there down to the words with no common hyponyms,
	# the better ranked word will be that with more hyponyms, included duplicated ones, even when those duplicated words
	# will be eliminated later, this makes semantic sense because it means that a word is related with a single word more
	# than once so it's more relevant to the text, so for example between animal {dog, cat, cat, dog, duck, dog} and
	# car {automobile, racing, stereo, rental, truck} the word "animal" is the better ranked.
	
	for k in sorted(data, key=lambda k: len(data[k]), reverse=True):
		if len(data[k]) > 0:
			orderedKeys.append(k)
			
			
	
	# an ontology tree for each word (node) is created with all the words and its children, when two words share a children the better ranked word
	# will keep it as a children the other(s) will lose it.
	
	for key in orderedKeys:
		level = list(set(data[key]) - set(used))
		used += data[key]
		used.append(key)
		result[key] = level
		for node in level:
			data[node] = list(set(data[node]) - set(level).intersection(data[node]))
			
	
	# words are ordered based in the initial rank before duplicates hyponims are removed as children
	
	for k in sorted(result, key=lambda k: len(result[k]), reverse=True):
		orderedResult.append(k)
		
	db_values = [{
		"topic": topic,
		"userid": 0,
		"version": 0,
		"name": orderedKeys[0],
		"p_rel": "",
		"parent_name": ""
	}]
	
	# an ontology is created by building a tree with all available the nodes, starting from the most relevant down and
	# converted to a JSON format
	for r in result:
		for child in result[r]:
			db_values.append({
				"topic": topic,
				"userid": 0,
				"version": 0,
				"name": child,
				"p_rel": "is_a",
				"parent_name": r
			})
			
	Relationship.objects.bulk_create([Relationship(**x) for x in db_values])
	return db_values



#getRoot("articles")
#ontology("articles")
#getRoot("articles")


print "Processing articles..."
ontology("articles")
print "Processing economics..."
ontology("economics")
print "Processing software_vulnerability..."
ontology("software_vulnerability")
print "Processing cyber_threat..."
ontology("cyber_threat")
print "Processing msds..."
ontology("msds")

