# -*- coding: utf-8 -*-
import os
import sys
import cPickle as pickle
import jieba
import random
import chardet

'''
Note:all the text before write into file must be unicode, include U1s, U2s, U1, U2
'''

def read_conversations(conv_file):
	'''
	read conversations from conv_file, and return U1s, U2s
	'''
	U1s = []
	U2s = []
	for index, line in enumerate(open(conv_file, 'r').readlines()):
		if (index+1) % 2 == 0:
			U2 = line.strip('U2').strip()
			U2s.append(U2)
		else:
			U1 = line.strip('U1').strip()
			U1s.append(U1)

	return U1s, U2s

def cut_words(U1):
	'''
	using jieba api to cut words
	jieba may not suitable for this task, cause sometimes jieba may cut the longest words into two words
	'''
	cutted_words_li = []
	if len(U1) <= 3:
		cutted_words_li.append(U1)
		return cutted_words_li

	words_li = jieba.cut(U1) 
	for cut_words in words_li:
		cutted_words_li.append(cut_words)
	return cutted_words_li

def build_hash(words, i, hash_table, U2):
	if i == len(words)-1:
		if hash_table.has_key(words[i]):
			if isinstance(hash_table[words[i]], list):
				hash_table[words[i]].insert(0, U2)
			else:
				hash_table[words[i]] = [U2, hash_table[words[i]]]
		else:
			hash_table[words[i]] = [U2, {}]
		return hash_table
	else:
		if hash_table.has_key(words[i]):
			if isinstance(hash_table[words[i]], list):
				hash_table[words[i]][-1] = build_hash(words, i+1, hash_table[words[i]][-1], U2)
			else:
				hash_table[words[i]] = build_hash(words, i+1, hash_table[words[i]], U2)
		else:
			hash_table[words[i]] = build_hash(words, i+1, {}, U2)
	return hash_table


def build_hash_table():
	dict_file = 'dict.txt'
	dict_file_fp = open(dict_file, 'w')
	hash_table_file = 'hash_table.pkl'
	hash_table_file_fp = open(hash_table_file, 'w')
	conv_file = 'format_conv.dat'
	hash_table = {}
	uni_words_li = []
	U1s, U2s = read_conversations(conv_file)
	n = 0
	for U1 in U1s:
		#print chardet.detect(U1)
		seg_words = cut_words(unicode(U1, 'utf-8')) #using jieba api
		max_len_word = 0
		max_len_words_li = []
		for word in seg_words:
			if len(word) >= max_len_word:
				if len(word) == max_len_word:
					max_len_words_li.append(word)	
				else:
					if len(max_len_words_li) > 0:
						max_len_words_li = [word]
					else:
						max_len_words_li.append(word)
				max_len_word = len(word)
				
		if max_len_word >= 2:
			for word in max_len_words_li:
				#print chardet.detect(word)
				#exit()
				build_hash(word, 0, hash_table, unicode(U2s[n], 'utf-8'))
				word = word.encode('utf-8')
				if word in uni_words_li:
					continue
				else:
					dict_file_fp.write(word+'\n')
					uni_words_li.append(word)
		n += 1

	pickle.dump(hash_table, hash_table_file_fp, True)
	dict_file_fp.close()
	hash_table_file_fp.close()
	print 'Write hash table to hash_tabel_file Successfully...'

def train_hash_table(U1, U2):
	'''
	train with hash_table, to add extra U1 and U2
	'''
	hash_table = load_hash_table()
	uni_words_li = load_dict_words()
	dict_file_fp = open('dict.txt', 'a')
	hash_table_file = 'hash_table.pkl'
	hash_table_file_fp = open(hash_table_file, 'w')
	seg_words = cut_words(unicode(U1, 'utf-8')) 
	max_len_word = 0
	max_len_words_li = []
	for word in seg_words:
		if len(word) >= max_len_word:
			if len(word) == max_len_word:
				max_len_words_li.append(word)	
			else:
				if len(max_len_words_li) > 0:
					max_len_words_li = [word]
				else:
					max_len_words_li.append(word)
			max_len_word = len(word)
				
	if max_len_word >= 2:
		for word in max_len_words_li:
			#print chardet.detect(word)
			#exit()
			build_hash(word, 0, hash_table, unicode(U2, 'utf-8'))
			word = word.encode('utf-8')
			if word in uni_words_li:
				continue
			else:
				dict_file_fp.write(word+'\n')
				uni_words_li.append(word)

	pickle.dump(hash_table, hash_table_file_fp, True)
	dict_file_fp.close()
	hash_table_file_fp.close()
	print 'Update hash table and dict Successfully...'


def load_hash_table():
	hash_table_file = 'hash_table.pkl'
	read_hash_table_fp = file(hash_table_file, 'r')
	hash_table = pickle.load(read_hash_table_fp)
	read_hash_table_fp.close()
	return hash_table

def load_dict_words():
	dict_file = 'dict.txt'
	dict_words_li = []
	for index, line in enumerate(open(dict_file, 'r').readlines()):
		dict_words_li.append(line.strip())

	return dict_words_li

def search_ans(word, hash_table):
	'''
	search the response from hash_table according to the key word
	'''
	ans_li = []
	if len(word) == 1:
		if hash_table.has_key(word[0]):
			if isinstance(hash_table[word[0]], list):
				j = 0
				while j < len(hash_table[word[0]])-1:       #may have more than one ans
					ans_li.append(hash_table[word[0]][j])
					j += 1
			else:
				ans_li.append(u'哈哈，您真有趣！')
		else:
			ans_li.append(u'哈哈，您真有趣！')
		return ans_li

	tmp_hash = {}
	i = 0 	
	while i < len(word):
		if i == 0:
			if hash_table.has_key(word[i]):
				tmp_hash = hash_table[word[i]]
			else:
				ans_li.append(u'哈哈，您真有趣！')
				return ans_li
		elif i == len(word)-1:
			if tmp_hash.has_key(word[i]):
				if isinstance(tmp_hash[word[i]], list):
					j = 0
					while j < len(tmp_hash[word[i]])-1:       #may have more than one ans
						ans_li.append(tmp_hash[word[i]][j])
						j += 1
				else:
					ans_li.append(u'哈哈，您真有趣！')
					return ans_li
			else:
				ans_li.append(u'哈哈，您真有趣！')
				return ans_li
		else:
			if tmp_hash.has_key(word[i]):
				if isinstance(tmp_hash[word[i]], list):
					tmp_hash = tmp_hash[word[i]][-1]
				else:
					tmp_hash = tmp_hash[word[i]]
			else:
				ans_li.append(u'哈哈，您真有趣！')
				return ans_li
		i += 1
	
	return ans_li

def get_all_ans(user_input, hash_table):
	cutted_words_li = cut_words(user_input) #user_input must be unicode
	max_len_words_li = []
	max_len_word = 0

	for cutted_word in cutted_words_li:
		if len(cutted_word) >= max_len_word:
			if len(cutted_word) == max_len_word:
				max_len_words_li.append(cutted_word)
			else:
				if len(max_len_words_li) > 0:
					max_len_words_li = [cutted_word]
				else:
					max_len_words_li.append(cutted_word)
			max_len_word = len(cutted_word)

	all_ans_li = []
	for word in max_len_words_li:
		#print word
		ans_li = search_ans(word, hash_table)
		all_ans_li.append(ans_li)
	return all_ans_li


def chat(user_input, hash_table = {}, flag = 0):
	if flag == 0:      #not use chat_multi mode
		user_input = unicode(user_input, 'utf-8') 
		hash_table = load_hash_table()
	all_ans_li = get_all_ans(user_input, hash_table) #user_input must be unicode
	#for ans_li in all_ans_li:
	#	for ans in ans_li:
	#		print ans
	seed_1 = random.randint(0, len(all_ans_li)-1)
	ans_li = all_ans_li[seed_1]
	seed_2 = random.randint(0, len(ans_li)-1)
	ans = ans_li[seed_2]
	if flag == 0:
		print u'You: '+user_input
		print u'小黄: '+ans
		print len(all_ans_li)
		print len(ans_li)
	
	return ans

def chat_multi(user_input):
	user_input = unicode(user_input, 'utf-8')
	hash_table = load_hash_table()
	i = 0
	while i < 30:
		ans = chat(user_input, hash_table, 1)
		if i == 0:
			print u'小黄1: '+user_input
			print u'小黄2: '+ans
			user_input = ans
			i += 1
			continue		 
		if i % 2 == 1:
			#print chardet.detect(ans)
			print u'小黄1: '+ans
		else:		
			#print chardet.detect(ans)
			print u'小黄2: '+ans
		user_input = ans
		i += 1


################################################
if __name__=="__main__":
	build_hash_table()    #when first use, execute this function ,then commented out this function
	#exit()
	
	if sys.argv[1] == 'chat':
		user_input = sys.argv[2]
		chat(user_input)
	elif sys.argv[1] == 'chat_multi':
		user_input = sys.argv[2]
		chat_multi(user_input)
	elif sys.argv[1] == 'train':
		U1 = sys.argv[2]
		U2 = sys.argv[3]
		train_hash_table(U1, U2)
	else:
		print 'Please see the usage...'
		print "Usage1: python main.py 'chat' [user_input]"
		print "Usage2: python main.py 'chat_multi' [user_input]"
		print "Usage3: python main.py 'train' [U1] [U2]"
		exit()
