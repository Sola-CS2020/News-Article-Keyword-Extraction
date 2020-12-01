"""
@author: Arijit Gayen
----------------------------------------------------------------------

Extract Keywords from articles using TF-IDF method

----------------------------------------------------------------------

Future Scope: 
1. Explore and add Stemmer and Lemmatizer for better pre processing of Text
2. Method to plot TIME SERIES
"""


class Tfidf:

	def __init__(self):
		"""

		The only Method Function of use to the user is extract.
		The others are helper functions.

		"""

		import numpy as np
		import pandas as pd
		import re
		import nltk
		from sklearn.feature_extraction.text import CountVectorizer
		from sklearn.feature_extraction.text import TfidfTransformer

		self.df = None



	def preprocess_text(self, text):
		text = text.lower()

		text = re.sub("</?.*?>"," <> ",text)
		text=re.sub("(\\d|\\W)+"," ",text)

		return text


	def sort_coo(self, coo_matrix):
		tuples = zip(coo_matrix.col, coo_matrix.data)
		return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)




	def extract_topn_from_vector(self, feature_names, sorted_items, topn):

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



	def get_stop_words(self):
		f = open("stop_words.txt")
		stop_words = f.readlines()

		for i in range(len(stop_words)):
			stop_words[i] = stop_words[i][:-1]


		return stop_words


	def get_text(self, df):
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


	def extract_keywords_util(self, cv, transformer, documents, n):
		tfidf_vector = transformer.transform(cv.transform(documents))

		results = []
		for i in range(tfidf_vector.shape[0]):
			vector = tfidf_vector[i]
			sorted_items = sort_coo(vector.tocoo())

			keywords = extract_topn_from_vector(cv.get_feature_names(), sorted_items, n)
			results.append(keywords)

		return results




	def tfidf(self, documents, stop_words):
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


	def dataset_by_year(self, df, year):
		temp = df[df['Date'].dt.year == year]

		return temp


	def dataset_by_month(self, df, year, month):
		temp1 = self.dataset_by_year(df, year)

		temp = temp1[temp1['Date'].dt.month == month]

		return temp


	def dataset_by_week(self, df, year, week):
		temp1 = dataset_by_year(df, year)

		temp = temp1[temp1['Date'].dt.week == week]

		return temp


	def dataset_by_day(self, df, year, month, day):
		temp1 = self.dataset_by_month(df, year, month)
		temp = temp1[temp1['Date'].dt.day == day]

		return temp



	def extract(self, paths, interval = 'whole', no_of_keywords = 10): 
		"""
		This method function is of use to the User.
		Parameters received"
		1. paths -> A list of strings, each string determines the path of a .csv file
					containing the articles
		2. interval -> string determining the timeframe from which articles are to be
					taken. Following formates are approved:
					(i) "whole": Complete section (DEFAULT)
					(ii) "m-YYYY-MM": Articles from the month of March 2020 would be "m-2020-03"
					(iii) "y-YYYY": Articles from 2020 would be "y-2020"
					(iv) "d-YYYY-MM-DD" : Articles from 25th March 2020 would be "d-2020-03-25"
					(v) "w-YYYY-WW": Articles from 28th week of 2020 would be "w-2020-28"

		3. no_of_keywords -> integer determining number of keywords to be extracted (DEFAULT: 10)
		
		"""

		df = pd.read_csv(paths[0])

		for index in range(1,len(paths)):
			path = paths[index]
			temp = pd.read_csv(temp)
			df = pd.concat([df, temp], ignore_index = True)

		stop_words = self.get_stop_words()

		df = self.get_text(df)
		self.df = df

		documents = df["Text"].tolist()
		cv, transformer = self.tfidf(documents, stop_words)


		if interval[0] == 'y':
			year = int(interval[2:])

			temp = self.dataset_by_year(df, year)
			documents = temp["Text"].tolist()
			docs = ""

			for doc in documents:
				docs = docs + doc

			keywords = extract_keywords_util(cv, transformer, [docs], no_of_keywords)


		elif interval[0] == 'm':
			year = int(interval[2:6])
			month = int(interval[7:])

			temp = self.dataset_by_month(df, year, month)
			documents = temp["Text"].tolist()
			docs = ""

			for doc in documents:
				docs = docs + doc

			keywords = extract_keywords_util(cv, transformer, [docs], no_of_keywords)

		elif interval[0] == 'd':

			year = int(interval[2:6])
			month = int(interval[7:9])
			day = int(interval[10:])

			temp = self.dataset_by_day(df, year, month, day)
			documents = df["Text"].tolist()

			docs = ""

			for doc in documents:
				docs = docs + doc

			keywords = extract_keywords_util(cv, transformer, [docs], no_of_keywords)

		elif interval[0] == 'w':

			year = int(interval[2:6])
			week = int(interval[7:])

			temp = self.dataset_by_week(df, year, week)
			documents = df["Text"].tolist()

			docs = ""

			for doc in documents:
				docs = docs + doc

			keywords = extract_keywords_util(cv, transformer, [docs], no_of_keywords)


		else:
			keywords = self.extract_keywords_util(cv, transformer, documents, no_of_keywords)


		return keywords