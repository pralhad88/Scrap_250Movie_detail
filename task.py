from bs4 import BeautifulSoup
import urllib.request
import re 
import json 
import random 
import time 
import os

# Task 1:- (Top Rated Indian Movies wale IMDB page se saari top rated movies ki list nikaalni hai)
def scrape_top_list():
	top_movies = []
	dic = {}
	second_time = random.randint(1, 3)
	time.sleep(second_time) 
	source = urllib.request.urlopen("https://www.imdb.com/india/top-rated-indian-movies/").read()
	soup = BeautifulSoup(source,'lxml')

	main = soup.find('div',{'class':'lister'})
	a = main.find('tbody',{'class':"lister-list"})

	movie_rank = []
	movie_name=[]
	movie_year=[]
	movie_rating=[]
	movie_url=[]

	for tr in a.find_all("tr"):
		position = tr.find('td',{'class':'titleColumn'}).text.strip()
		rank = ''
		for j in position:
			if "." not in j:
				rank = rank + j
			else:
				break
		movie_rank.append(rank)
		
		name = tr.find('td',{'class':'titleColumn'}).a.text
		movie_name.append(name)
		
		year = tr.find('td',{'class':'titleColumn'}).span.text
		movie_year.append(year)
		
		rating = tr.find('td',{'class':'ratingColumn imdbRating'}).strong.text
		movie_rating.append(rating)
		
		url = tr.find('td',{'class':'titleColumn'}).a['href']
		link = "https://www.imdb.com" + url
		movie_url.append(link)

	for i in range(len(movie_rank)):
		dic['Name'] = movie_name[i]
		dic['Year'] = int(movie_year[i][1:5])
		dic['Position'] = int(movie_rank[i])
		dic['Rating'] = float(movie_rating[i])
		dic['url'] = movie_url[i]  
		top_movies.append(dic)
		dic = {}

	return top_movies
movies = scrape_top_list()
#print(movies)

#Task 2:- (Separate movies, according to the year of release)
def group_by_year(year):
	years=[]
	for i in year:
		if i['Year'] not in years:
			years.append(i['Year'])
	years.sort()
	movies_dic = {i:[] for i in years}

	for i in year:
		year = i["Year"]
		for j in movies_dic:
			if str(j) == str(year):
				movies_dic[j].append(i)
	return movies_dic
#print(group_by_year(movies))

#Task 3:- (Divied movies according to the Decade wise)
def group_by_decade(decade):
	movies_dec = []
	for i in decade:
		mod = i['Year']%10
		dec = i['Year']-mod
		if dec not in movies_dec:
			movies_dec.append(dec)
	movies_dec.sort()
	dec_movies = {i:[] for i in movies_dec}
	for i in dec_movies:
		group_year = group_by_year(movies)
		for year, movie in group_year.items():
			if i <= year and year <= i+9:
				for k in movie:
					dec_movies[i].append(k)
	return dec_movies

#print(group_by_decade(movies))

#Task 12 & 13:-(find out coactore from a movie)
def scrape_movie_casts(movie_detail):
	cast_data = []
	dic = {}
	for i in movie_detail:
		url = i['url']

		if os.path.exists("./movie_cast/"+url[27:36]+'_cast'+".json"):
			f = open("./movie_cast/"+url[27:36]+'_cast'+".json","r+")
			read_file = f.read()
			read_file = json.loads(read_file)
			cast_data.append(read_file)
			
		else:
			f = open("./movie_cast/"+url[27:36]+'_cast'+".json", "w+")
			source = urllib.request.urlopen(url).read()
			soup = BeautifulSoup(source,'lxml')
			soup = soup.find('div',{'id':'titleCast'})
			soup = soup.find('div',{'class':'see-more'}).a['href']
			
			new_url = url[0:37] + soup
			open_link = urllib.request.urlopen(new_url).read()
			soup2 = BeautifulSoup(open_link,'lxml')
			soup2 = soup2.find('div',{'id':'fullcredits_content'})
			soup2 = soup2.find('table',{'class':"cast_list"})
			sopu2 = soup2.find('tbody')
			
			for i in soup2.find_all('tr'):
				for j in i.find_all('td'):
					for k in j.find_all('a'):
						if "name" in k['href'] and (k.text !=""):
							dic['imdb_id'] = k['href'][6:15]
							name = k.text.strip()
							dic['name'] = name
							cast_data.append(dic)
							dic={}
			with open("./movie_cast/"+url[27:36]+'_cast'+".json",'w+') as fp:
				json.dump(cast_data,fp)
			cast_data.append(dic)
			cast_data = []
			dic = {}
	#return cast_data
	return read_file
	
#print(scrape_movie_casts(movies))


# Task 4 & 5:- (Scrap all movie detailed like actor, director etc)
def scrape_movie_details(movies):
	stored_data = []
	dic = {}

	for i in movies:
		url = i['url']
		file_name = url[27:36] + '.json'
		# Task 8:- memory cache
		if os.path.exists('./movie/' + file_name):
			with open('./movie/' + file_name, "r+") as read_file:
				#read_file = f.read()
				read_file = json.load(read_file)
			#stored_data.append(read_file)


			#Task 13:- (Adding cast information into movie detailed file)
			cast_data = scrape_movie_casts([i])
			read_file['cast'] = cast_data
			with open('./movie/' + file_name,"w+") as data: 
				json.dump(read_file,data)
			stored_data.append(read_file)
		else:

			f = open("./movie/"+url[27:36]+".json", "w+")
			#Task 9:-(blockage priventer task from a web server provider)
			second_time = random.randint(1, 3) 
			time.sleep(second_time) 
			
			source = urllib.request.urlopen(url).read()
			soup = BeautifulSoup(source,'lxml')
			main = soup.find('div',{'class':'title_wrapper'})
			name = list(main.find('h1').text)
			movie_name = ""
			for i in name:
				if "\xa0" == i:
					break
				else:
					movie_name+=i	
			
			sepa_h_m = re.findall("\d+", main.time.text.strip())
			if len(sepa_h_m) == 1:
				runtime = int(sepa_h_m[0]) * 60 
			else:
				runtime = int(sepa_h_m[0]) * 60 + int(sepa_h_m[1])
			
			genre_list = main.find_all('div',{'class':'subtext'})
			genre = []
			for k in genre_list:
				for p in k.find_all('a'):
					if p.text.isalnum() == True:
						genre.append(p.text)
					else:
						break

			poster_url = soup.find('div',{'class':'poster'}).a.img['src']

			
			sumary = soup.find('div',{'class':'summary_text'}).text.strip()
			
			director = soup.find('div',{'class':'credit_summary_item'})
			directors = []
			for i in director.find_all('a'):
				directors.append(i.text)
			
			lang = soup.find('div',{'id':'titleDetails'})
			language = []
			for j in lang.find_all('div',{'class':'txt-block'}):
				if "Country" in (j.text):
					country = j.a.text
				if "Language" in (j.text):
					for i in j.find_all('a'):
						language.append(i.text)
		
			dic['Name'] = movie_name
			dic['Director'] = directors
			dic['Country'] = country
			dic['Language'] = language
			dic['poster_image_url'] = poster_url
			dic['bio'] = sumary
			dic['runtime'] = runtime
			dic['genre'] = genre
			#Task 13
			cast_data = scrape_movie_casts(i)
			dic['cast'] = cast_data
			stored_data.append(dic)
			with open("./movie/"+url[27:36]+".json",'w+') as fp:
				json.dump(dic,fp)
			dic = {}

	return stored_data

data = scrape_movie_details(movies)
#print(data)

#Task 6:-(scrap how many languages ​​have I been used the movie to the released)
def analyse_movies_language(movies):
	language = {}
	for i in movies:
		languages = i['Language']
		count = 0
		for j in languages:
			if j not in language:
				language[j] = count + 1
			else:
				language[j] = language[j] + 1
	return language

#print(analyse_movies_language(data))

#Task 7:-(how many movies are directed by one particular director)
def analyse_movies_directors(movies):
	director = {}
	for i in movies:
		directors = i['Director']
		count = 0
		for j in directors:
			if j not in director:
				director[j] = count + 1
			else:
				director[j] = director[j] + 1
	return director

#print(analyse_movies_directors(data))

#Task 10:-(According to the director in how many language they are directed movie)
def analyse_language_and_directors(movie_detail):
	dic1 = {}
	count = 0
	for i in movie_detail:
		language = i["Language"]
		for k in i['Director']:
			if k not in dic1:
				dic1[k] = {}
			for j in language:
				if j not in dic1[k]:
					dic1[k][j] = count + 1
				else:
					dic1[k][j] = dic1[k][j] + 1
	return dic1

#print(analyse_language_and_directors(data))

#Task 11:- (Separate genre and count the type of genre for all movies)
def analyse_movies_genre(movie_detail):
	genre = {}
	for i in movie_detail:
		genres = i['genre']
		count = 0
		for j in genres:
			if j not in genre:
				genre[j] = count + 1
			else:
				genre[j] = genre[j] + 1
	return genre
#print(analyse_movies_genre(data))

# Task 14:- (In how much movies work coactore with leading actor, only first 5 coactor)
def analyse_co_actors(movie):
	all_co_actor = []
	dic = {}
	
	for i in movie:
		cast = i['cast']
		count = 0
		co_actor = []
		for j in cast:
			if count == 0:
				id1=j['imdb_id']
				dic[id1] = {}
				dic[id1]['name'] = j['name']
				dic[id1]['frequent_co_actors'] = []
			else:
				co_actor.append(j['name'])
			count += 1
			if count == 6:
				break	
		#print(dic)

		for i in co_actor:
			total = 0
			dic1 = {}
			for j in movie:
				cast1 = j['cast']
				for k in cast1:
					if (dic[id1]['name'] and i) in k['name']:
						total+=1
						dic1['imdb_id'] = k['imdb_id']
						dic1['name'] = k ['name']
			dic1['num_movies'] = total
			dic[id1]['frequent_co_actors'].append(dic1)
			dic1={}
		all_co_actor.append(dic)
		#print(dic)
		dic = {}
	return all_co_actor
#print(analyse_co_actors(data))

#Task 15:- (If actor is work more than in one movie then calculate in how many movies he/she is work)
def analyse_actors(movie):
	num_movies_act_work = {}
	for i in movie:
		cast = i['cast']
		for j in cast:
			num_movie = 0
			for l in movie:
				cast1 = l['cast']
				for k in cast1:
					if j['name'] in k['name']:
						num_movie+=1
			if num_movie > 1:
				id1 = j['imdb_id']
				num_movies_act_work[id1] = {}
				num_movies_act_work[id1]['name'] = j['name']
				num_movies_act_work[id1]['num_movies'] = total
	return num_movies_act_work
#print(analyse_actors(data))