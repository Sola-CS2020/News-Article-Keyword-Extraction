"""

Extract Keywords from articles
using TF-IDF method

To-do: 
1. Convert entire Code using OOP principles
2. Provide documentation for better Readability
3. Explore and add Stemmer and Lemmatizer for better pre processing of Text
"""



import numpy as np
import pandas as pd
import re
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer



def preprocess_text(text):
	text = text.lower()

	text = re.sub("</?.*?>"," <> ",text)
	text=re.sub("(\\d|\\W)+"," ",text)

	return text


def sort_coo(coo_matrix):
	tuples = zip(coo_matrix.col, coo_matrix.data)
	return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)




def extract_topn_from_vector(feature_names, sorted_items, topn):

	sorted_items = sorted_items[:topn]

	score_vals = []
	feature_vals = []

	for idx, score in sorted_items:
	    fname = feature_names[idx]
		score_vals.append(round(score, 3))
		feature_vals.append(feature_names[idx])

	results= {}
	for idx in range(len(feature_vals)):
		results[feature_vals[idx]]=score_vals[idx]

	return results



def get_stop_words():
	f = open("stop_words.txt")
	stop_words = f.readlines()

	for i in range(len(stop_words)):
		stop_words[i] = stop_words[i][:-1]


	return stop_words


def get_text(df):
	texts = []

	for i in range(df.shape[0]):
		if type(df.iloc[i,2]) == float:
			head = ""
		else:
			head = df.iloc[i,2]


		if type(df.iloc[i,3]) == float:
			article = ""
		else:
			article = df.iloc[i,3]


		text = head + " " + article
		text = preprocess_text(text)
		texts.append(text)

	df["Text"] = texts

	return df


def extract_keywords_whole(cv, transformer, documents, n):
	tfidf_vector = transformer.transform(cv.transform(documents))

	results = []
	for i in range(tfidf_vector.shape[0]):
		vector = tfidf_vector[i]
		sorted_items = sort_coo(vector.tocoo())

		keywords = extract_topn_from_vector(cv.get_feature_names(), sorted_items, n)
		results.append(keywords)

	return results



def extract_keywords_single(cv, transformer, doc, n):
	tfidf_vector = transformer.transform(cv.transform([doc]))

	sorted_items = sort_coo(tfidf_vector.tocoo())
	keywords = extract_topn_from_vector(cv.get_feature_names(), sorted_items, n)

	return keywords



def tfidf(documents, stop_words):
	cv = CountVectorizer(stop_words = stop_words)

	word_count_vector = cv.fit_transform(documents)
	print("Length of Stop Words: ", len(stop_words))
	print("Size of Vocabulary [excluding stopwords]: ", word_count_vector.shape[1])

	print("\n\nEnter maximum size of Features [-1 for keeping size intact]: ")
	max_features = int(input())

	if max_features != -1:
		cv = CountVectorizer(stop_words = stop_words, max_features = max_features)
		word_count_vector = cv.fit_transform(documents)

	transformer = TfidfTransformer(smooth_idf = True, use_idf = True)
	transformer.fit(word_count_vector)

	return cv, transformer



def dataset_by_month(df, month):
	temp = df[df['Date'].dt.month == month]

	return temp


def dataset_by_week(df, month, week):
	temp1 = dataset_by_month(df, month)
	days = []
	for i in range(((week-1)*7+1),(week*7+1)):
		days.append(i)

	
	temp = temp1[temp1['Date'].dt.day == days[0]]
	for i in range(1,len(days)):
		temp = pd.concat([temp, temp1[temp1['Date'].dt.day == days[i]]], ignore_index = True)


	return temp



def driver():
	print("Extract keywords across a single section or multiple sections?\nEnter s for single, m for multiple: ")
	choice = input().lower()

	if choice not in ["s", "m"]:
		print("Invalid Input, try again!")
	else:
		if choice == "s":
			print("Enter path of Article file: ")
			path = input()
			df = pd.read_csv(path)

		else:
			print("Enter comma seperated paths of Article files: ")
			paths = input().split(',')
			df = pd.read_csv(paths[0])

			for index in range(1,len(paths)):
				path = paths[index]
				temp = pd.read_csv(temp)
				df = pd.concat([df, temp], ignore_index = True)

		stop_words = get_stop_words()

		df = get_text(df)

		documents = df["Text"].tolist()
		cv, transformer = tfidf(documents, stop_words)

		print("Extract Articles:\n1. Monthly\n2. Weekly\n3. Section as a whole\n4. Section by Articles\nEnter choice: ")
		choice = int(input())

		if choice == 1:
			print("Enter Month value[1-12]: ")
			month = int(input())

			if month < 1 or month >12:
				print("Invalid input, try again!")
			else:
				print("Number of keywords for individual Articles (press -1 for default which is 10): ")
				n = int(input())
				if n == -1:
					n = 10

				temp = dataset_by_month(df, month)
				documents = temp["Text"].tolist()
				docs = ""

				for doc in documents:
					docs = docs + doc

				keywords = extract_keywords_single(cv, transformer, docs, n)
				for k in keywords:
					print(k, keywords[k])


		elif choice == 2:
			print("Enter Month value[1-12]: ")
			month = int(input())

			if month < 1 or month >12:
				print("Invalid input, try again!")
			else:
				print("Enter Week Number[1-5]: ")
				week = int(input())

				if week<1 or week>5:
					print("Invalid input, try again!")

				else:

					temp = dataset_by_week(df, month, week)
					print("Number of keywords for individual Articles (press -1 for default which is 10): ")
					n = int(input())
					if n == -1:
						n = 10

					
					documents = temp["Text"].tolist()
					docs = ""

					for doc in documents:
						docs = docs + doc

					keywords = extract_keywords_single(cv, transformer, docs, n)
					for k in keywords:
						print(k, keywords[k])

		elif choice == 3:
			documents = df["Text"].tolist()

			print("Number of keywords for individual Articles (press -1 for default which is 10): ")
			n = int(input())
			if n == -1:
				n = 10
			results = extract_keywords_whole(cv, transformer, documents, n)

			return results

		elif choice == 4:
			print("Number of Articles in Data Frame: ", df.shape[0], ".............")
			print("Enter index number of Article: ")
			index = int(input())-1

			documents = df["Text"].tolist()
			doc = documents[index]

			print("Number of keywords for individual Articles (press -1 for default which is 10): ")
			n = int(input())
			if n == -1:
				n = 10


			keywords = extract_keywords_single(cv, transformer, docs, n)
			for k in keywords:
				print(k, keywords[k])


		else:
			print("Invalid Input, try again!")