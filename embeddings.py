from gensim.models import Word2Vec
import csv
import numpy as np
from sklearn.linear_model import LinearRegression
from bs4 import BeautifulSoup
from hi_to_eng import transliterate,_setup

# fd = open('parallel/IITB.en-hi.hi', 'r')
# lines = fd.read().splitlines()
# sentences = [line.split(' ') for line in lines]
# print(sentences[:10])
# print('Training word2vec ....')
# model = Word2Vec(sentences, min_count=2, size=300)
# print('training done ...')
# model.save('model/word2vec-hi.bin')
# print(len(model))
model_en = Word2Vec.load('model/word2vec-eng.bin')
# model_hi = Word2Vec.load('model/word2vec-hi.bin')
model_hi = Word2Vec.load('../hi/hi.bin')
words = list(model_hi.wv.vocab)
# print(len(words))
# # print((model['स्थिति']))
# sim = model_hi.wv.similar_by_vector(model_hi['मंदिर'], topn=10, restrict_vocab=None)
# print(sim)

dictionary = []
with open('English-Hindi Dictionary.csv') as csvfile:
	file = csv.reader(csvfile)
	for row in file:
		if row[0]=='eword' and row[1]=='hword':
			continue
		if row[0]!='' and row[1]!='':
			dictionary.append([row[0], row[1]])

print('Dictionary loaded ...')

hindi = np.zeros((len(dictionary),300))
english = np.zeros((len(dictionary),300))

# print(dictionary[0])
i = 0
for d in dictionary:
	tmp = np.zeros(300)
	temp = d[1].split(' ')
	li = [x for x in temp if x!='']
	# print(li)
	if li==[]:
		continue
	# print(li)
	for item in li:
		try:
			tmp += np.array(model_hi[item])
		except:
			continue
	# print(type(hindi[i]), type(tmp))
	hindi[i] = tmp/len(li)

	tmp = np.zeros(300)
	temp = d[0].split(' ')
	li = [x for x in temp if x!='']
	# print(li)
	if li==[]:
		continue
	for item in li:
		try:
			tmp += np.array(model_en[item])
		except:
			continue
	english[i] = tmp/len(li)
	i += 1

hindi = hindi[:i]
english = english[:i]

print(hindi.shape, english.shape, i)
# print(len(hindi[np.nonzero(hindi)]))


regr = LinearRegression()
regr.fit(hindi, english)
# print(model_en['episode'])

hi = model_hi['लालू'].reshape(1,-1)
en = regr.predict(hi)
print(en.shape, type(en), type(model_hi['मंदिर']), model_hi['मंदिर'].shape)
sim = model_en.wv.similar_by_vector(en.reshape(300,), topn=10, restrict_vocab=None)
print(sim)

fd = open('queries-modified.txt', 'r')
st = fd.read()
fd.close()
soup = BeautifulSoup(st, "html5lib")

titles = soup.find_all('title')
string = ""

_setup()

for title in titles:
    if title is not None:
        string = string+'\n'+str(title)

queries = BeautifulSoup(string, "html5lib").text

query = queries.split('\n')

list = []
for q in query:
	tee = q.split(' ')
	translated_query = ''
	for term in tee:
		try:
			hi = model_hi[term].reshape(1,-1)
			en = regr.predict(hi)
			trans = model_en.wv.similar_by_vector(en.reshape(300,), topn=1, restrict_vocab=None)
			if trans[0][1] >= 0.4:
				translated_query += ' ' + trans[0][0]
			else:
				trans = transliterate(term, 'devanagari', 'hk').lower()
				translated_query += ' ' + trans
		except:
			trans = transliterate(term, 'devanagari', 'hk').lower()
			translated_query += ' ' + trans
		# print(trans[0][0])
		
	list.append(translated_query)

print(list)

f = open("expanded-queries.txt", "w+")
f.write("<topics>\n")
num = 76
for line in list:
    f.write('\n<top>\n<num>'+str(num)+'</num>\n<title>'+line+'</title>\n</top>\n')
    num = num+1
f.write('</topics>\n')
f.close()


	