"""
Web Scraping Articles from Telegraph India Website

www.telegrapgindia.com

To-do: 
1. Convert entire code using OOP principles
2. Provide documentation for better readability
"""

import pandas as pd
import numpy as np
from tqdm import tqdm
import progressbar

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import requests
import csv



base_url = "https://www.telegraphindia.com"

def extract_links(section, num_pages):
	base_url = "https://www.telegraphindia.com"
	url = base_url + "/" + section

	page = requests.get(url)
	soup = BeautifulSoup(page.text, "html.parser")
	links = soup.find_all('a',attrs={'class':'muted-link ellipsis_data_2'})

	widgets = ['[',progressbar.Timer(format= 'elapsed time: %(elapsed)s'),']',progressbar.Bar('*'),'(',progressbar.ETA(),')'] 

	with open("telegraph_data/links.csv", "w") as f:
		writer = csv.writer(f)
		for link in links:
			temp = link.get('href')
			writer.writerow([temp])

		bar = progressbar.ProgressBar(max_value = num_pages, widgets = widgets).start()

		for i in range(2, num_pages):
			page_url = url + '/page-'+str(i)
			page = requests.get(page_url)
			soup = BeautifulSoup(page.text, "html.parser")
			links = soup.find_all('a',attrs={'class':'muted-link ellipsis_data_2'})

			for link in links:
				temp = link.get('href')
				writer.writerow([temp])

			bar.update(i)




def extract_articles_from_date(monthLim = None, dayLim = None):
	df = pd.read_csv("links.csv")
	df.columns = ['Link']

	widgets = ['[',progressbar.Timer(format= 'elapsed time: %(elapsed)s'),']',progressbar.Bar('*'),'(',progressbar.ETA(),')']

	dates = []
	authors = []
	headlines = []
	articles = []
	count = 0
	flag = 0

	bar = progressbar.ProgressBar(max_value = df.shape[0], widgets = widgets).start()

	for i in range(df.shape[0]):
		if flag == 1:
			break
		link = base_url + df.iloc[i,0]
		page = requests.get(link)
		soup = BeautifulSoup(page.text, "html.parser")

		temp = str(soup.find_all('div', attrs = {'class':'fs-12 float-left'}))

		idx = temp.find('Published')
		idx2 = temp[idx+10:].find('<')

		try:
			val = temp[idx+10:idx+10+idx2]
			day = val[:2]
			month = val[3:5]

			if monthLim != None and dayLim != None:
				if (int(month) < monthLim) or (int(month) == monthLim and int(day) <= dayLim):
					flag = 1
					continue

			dates.append(val)
		except:
			count += 1
			dates.append("")


		try:
			authors.append(soup.find_all('span',attrs={'class':'text-breadcrumbs'})[-1].text)
		except:
			authors.append("")
			count += 1


		try:
			headlines.append(soup.title.text)
		except:
			headlines.append("")
			count += 1


		temp = soup.find_all('p')
		s = ""

		for t in temp:
			s = s+t.text
		try:
			articles.append(s)

		except:
			articles.append("")
			count += 1

		bar.update(i)

	print("# Errors: ", count)
	print("# Dates: ", len(dates))
	print("# Authors: ", len(authors))
	print("# Headlines: ", len(headlines))
	print("# Articles: ", len(articles))


	for i in range(len(dates)):
		date = dates[i]
		if date[8] != ',':
			continue
		else:
			dates[i] = date[:6] + '20' + date[6:]

	return dates, authors, headlines, articles



def process_dataset(df):
	dates = list(df['Date'])
	df = df.drop(columns = ['Date'])

	dates = pd.to_datetime(dates)
	df['Date'] = dates
	df = df.sort_values(by = 'Date')

	df = df[df['Headline'].notna()]
	df = df.drop_duplicates(subset ="Headline").reset_index(drop = False)
	df = df.drop(columns = ["index"])

	return df


def driver():
	print("Sections in Telegraph India Website:\n1. Opinion\n2. Calcutta\n3. World\n4. Business\n5. Science & Tech")
	print("6. Health\n7. Entertainment\n8. West Bengal\n9. North East\n10. Jharkhand\nEnter your choice: ")

	choice = int(input())
	if choice <1 or choice>10:
		print("Invalid, try again!")

	else:

		map_ = {1:"opinion", 2:"calcutta", 3:"world", 4:"business", 5:"science-tech", 6:"health", 
				7:"entertainment",8:"west-bengal", 9:"north-east", 10:"jharkhand"}

		section = map_[choice]
		print("Enter number of pages: ")
		num_pages = int(input())

		extract_links(section, num_pages)

		print("\nDo you want to extract articles starting from a date till now?[y/n]: ")
		yn = input()
		
		if yn == 'y' or yn =='Y':
			print("Enter month[1-12]: ")
			monthLim = int(input())
			print("Enter day[1-31]: ")
			dayLim = int(input())

			dates, authors, headlines, articles = extract_articles_from_date(monthLim = monthLim, dayLim = dayLim)
		else:
			dates, authors, headlines, articles = extract_articles_from_date(monthLim = None, dayLim = None)

		df = pd.DataFrame(columns = ["Date", "Author", "Headline", "Article"])
		df["Date"] = dates
		df["Author"] = authors
		df["Headline"] = headlines
		df["Article"] = articles

		df.to_csv("telegraph_data/articles.csv")



driver()