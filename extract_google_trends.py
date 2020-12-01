"""
@author: Arijit Gayen
-------------------------------------------------------------

The following Python script will extract Google Trends Data

-------------------------------------------------------------

Documentation: https://pypi.org/project/pytrends/

-------------------------------------------------------------

Future Scope: 
1. Better Optimized
2. More Generalised
3. Methods for Plotting TIME SERIES

"""


class Trends:

	def __init__(self, kw, timeframe = None):
		"""
		An object of Trends Class receives 2 parameters:
		1. kw -> a list containing keywords in the form of string (maximum: 5, 
			recommended: 1)

		2. timeframe -> a string determining the time in which data is to be extracted
			Valis formats of timeframe string
				(i) 'today 5-y': Last 5 years
				(ii) 'all': Whole
				(iii) 'today 10-m': Last 10 months
				(iv) '2019-10-30 2020-03-20': 30th October 2019 to 20th March 2020
				(v) 'now 9-d': last 9 days
				(vi) 'now 10-H': laqst 10 hours
				(vii) '2019-10-30T10 2020-03-20T20': 10 AM 30th October 2019 to 8 PM 20th March 2020
		

		"""

		import pandas as pd
		import numpy as np
		from pytrends.request import TrendReq
		import urllib3
		import time
		import math

		self.trend = TrendReq(hl = 'en-US', tz = 690)
		self.kw = kw

		self.trend.build_payload(kw, geo = 'IN', timeframe = timeframe)




	def get_normalised_interest(self):
		"""
		This Method Fucntion returns interest score over given timeframe jumping over
		a period of 7 days. The score is normalized between 0 and 100.

		"""
		df = self.trend.interest_over_time()
		df = df.drop(columns = ["isPartial"])

		return df



	def get_hourly_normalised_interest(self, gprop = None):
		"""
		This method returns normalized interest score on a period of hours
		Score normalized between 0 and 100
		It takes a parameter gprop which is one of the following strings:
		'images'
		'youtube'
		'news'
		'froogle' (for shopping)
		Default Parameter is None, which returns normal search results.

		"""
		year_start = 0
		month_start = 0
		day_start = 0
		hour_start = 0

		year_end = 0
		month_end = 0
		day_end
		hour_end = 0

		print("\nEnter space seperated starting year[20XX], month[1-12], day[1-31], hour[0-24]")
		year_start, month_start, day_start, hour_start = (int(x) for x in in input().split())


		print("\nEnter space seperated ending year[20XX], month[1-12], day[1-31], hour[0-24]")
		year_end, month_end, day_end, hour_end = (int(x) for x in in input().split())



		urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
		df = trend.get_historical_interest(self.kw, year_start, month_start, day_start, hour_start,
											year_end, month_end, day_end, hour_end, geo='IN', gprop = gprop)

		df = df.drop(columns = ['isPartial'])
		return df




	def trend_by_region(self, region, include_low = False):
		"""
		This function returns normalized interest scores divided into sections
		of given geo-location (which in our case in INDIA)
		Score normalized between 0 and 100
		Takes 2 arguments:
		1. region which is one of the following: "COUNTRY", "CITY", "DMA", "REGION"
		2. include_low which determines whether regions with very low interest scores
		are to be included or not, default to False

		"""
		
		df = trend.interest_by_region(resolution = code, inc_low_vol = include_low, inc_geo_code = True)

		return df




	def get_related_queries(self):
		"""
		This method function returns 2 Pandas Dataframes, rising and top
		rising contains the queries related to the given queries whose trend scores are increasing
		top contains the queries related to the given queries whose trend scores are currently maximum

		"""
		d = list(trend.related_queries().values())[0]

		rising = d['rising']
		top = d['top']

		return rising, top



	def trend_real_time(self):
		"""
		This method function returns the currently trending searches across INDIA

		"""
		df = trend.trending_searches(pn = 'india')

		return df




	def get_related_topics(self):
		"""
		This method function returns 2 Pandas Dataframes, rising and top
		rising contains the topics related to the topic of given queries whose trend scores are increasing
		top contains the topics related to the topics of given queries whose trend scores are currently maximum

		"""
		d = list(trend.related_topics().values())[0]

		rising = d['rising']
		top = d['top']

		return rising, top




	def get_suggestions(self):
		"""
		This method function returns the suggestions given by Google
		for given keyword searches.

		"""

		result = []
		for kewyword in self.kw:
			d = trend.suggestions(keyword)
			temp = []
			for i in d:
				temp.append((i['title'], i['type']))
			result.append(temp)

		return result






