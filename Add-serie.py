#==============================================================================#
#Title           :Add-serie 	                                               #
#Date            :14/09/2017                                                   #
#Version         :1.1                                                          #
#Usage           :Python                                                       #
#Python version  :3.5                                                          #
#==============================================================================#

import os, errno
import http.client
import json
import glob	#import glob module
import datetime #import date and time module
import pathlib #import filesystem module

# ------------------------------------------------------------------------------------------------------------------ #

##
## @brief      Convert date to a specific date format
## @return     Returns converted date format
##
def convertDate():
	date = datetime.date.today().strftime("%d/%m/%Y") #convert date to a string "dd/mm/yy format"
	return date #return date to main program
	            
##
## @brief      Convert time to a specific time format
## @return     Returns converted time format
##
def convertTime():
	time = datetime.datetime.now().time().strftime("%H:%M:%S") #convert time to a string ("24h-min-sec")
	return time #return time to main program

##
## @brief      Writes data to a file
## @param      root      Root to location where file will be stored
## @param      filename  Name of the file
## @param      data      Data that will be stored in the file
## @param      date      Current date
## @param      time      Current time
## @return     None
##
def writeFile(root,filename,data,date,time): 
	path = "{}/{}".format(root,filename)
	write = "[{}][{}]\t[{}]\n".format(date,time,data) #initialize time string to a variable
	fop = open(path,"a") #open file in writing mode, we append information to log file
	fop.write(write) #write date,time and filenames text to file as one string 
	fop.close() #close file to prevent other data is written to this file

##
## @brief      Get content from specified file
## @param      path  Path to file
## @return     Returns content from specified file
##
def readFile(path):
	path = open(path,'r')
	return path.read()

##
## @brief      Print all key and values from a JSON object
## @param      json  JSON object
## @return     None
##
def printJSON(json):
	for key, value in json.items():
		print("{} - {}".format(key,value))

##
## @brief      Connects to server
## @param      request  Request you want to ask server
## @return     Returns data as a JSON object
##
def connectToServer(request):
	conn = http.client.HTTPSConnection("api.themoviedb.org") #connect to db
	payload = "{}" #init payload
	conn.request("GET", request, payload) #get payload from server

	response = conn.getresponse() #get response from server
	data = response.read().decode("utf-8") #read and decode data to 'utf-8'
	return data #return decoded data

##
## @brief      Get serie ID from server, needed to obtain more detailed serie information
## @param      api    API key needed to acces data from server
## @param      serie  Serie you want to get ID from  
## @return     returns id from server
##
def fetchSerieID(api,serie):
	serie = serie.replace(" ", "%20") #replace 'space' with '%20'
	req = "/3/search/tv?page=1&query={}&language=en-US&api_key={}".format(serie,api) #format request string with according data
	data = connectToServer(req) #Get data from server
	
	check = jsonQuery(data,'total_results') #check if serie exsists

	#if serie doesn't exsist then we return 0
	if check == 0:
		return 0

	id = jsonComplexQuery(data,'results','id') #get ID from JSON object
	return id

##
## @brief      Get amount of seasons from a specied serie
## @param      api 	API key needed to acces data from server
## @param      id   Serie ID, needed to obtain more detailed serie information
## @return     Returns amount of seasons
##
def fetchSerieSeasons(api,id):
	req = "/3/tv/{}?api_key={}".format(id,api)
	#print(req)
	data = connectToServer(req)
	seasons = jsonQuery(data,'number_of_seasons')
	return seasons

##
## @brief      Get associated value from key
## @param      data  JSON object
## @param      key   Key you want to get value from
## @return     returns value
##
def jsonQuery(data,key):
	raw = json.loads(data)  #concert string to a dict
	query = raw[key]
#	printJSON(raw)
	return query

##
## @brief      Get associated value from key containing a list	
## @param      data           JSON object
## @param      primairyKey    Key containing a list
## @param      secondairyKey  Key inside list where you want to get the value from
## @return     Returns value
##
def jsonComplexQuery(data,primairyKey,secondairyKey):
	primairyQuery = json.loads(data)  #concert string to a dict
	listResults = json.dumps(primairyQuery[primairyKey]) #get list from 'results' and convert them to a JSON string
	secondairyQuery = json.loads(listResults)[0] #convert list to a dict
	query = secondairyQuery[secondairyKey] #get id 
	return query

##
## @brief      Create directories
## @param      path  Path where you want to created directories
## @return     None
##
def createDir(path):
	try:
		os.makedirs(path)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise

# ------------------------------------------------------------------------------------------------------------------ #

root = readFile("root.txt") #Get root path
api = readFile("API.txt") #get API key

serie = input("Please enter serie: ") #enter tv show and replace space with %20

id = fetchSerieID(api,serie) #get serie ID

#if the serie doesn't, then we ask to re-enter the show
while id == 0:
	serie = input("Serie doesn't exsist: ") #enter tv show and replace space with '%20'
	id = fetchSerieID(api,serie) #get serie ID
	                             
seasons = fetchSerieSeasons(api,id) #get amount of seasons

path = "{}\{}".format(root,serie.title()) #Path to serie folder and capitalize 1st letter of every word

checkDirectory = os.path.isdir(path) #check if file path already exsist

#if path exsist keep asking for serie to enter thus other files would not override
while checkDirectory == True:
	serie = input("Serie already exists: ") #enter tv show and replace space with %20

	id = fetchSerieID(api,serie) #get serie ID
	seasons = fetchSerieSeasons(api,id) #get amount of seasons

	path = "{}\{}".format(root,serie.title()) #Path to serie folder and capitalize 1st letter of every word
	checkDirectory = os.path.isdir(path)

print(path) #print path

#create all folders containing season numbers
for i in range(1,int(seasons) + 1):	
	fullPath = "{}\Season {}".format(path,str(i).zfill(2))
	print(fullPath)
	createDir(fullPath)

if seasons == 1:
	logData = "{} - {} season".format(serie.title(),seasons)
	print(logData)
else:
	logData = "{} - {} seasons".format(serie.title(),seasons)
	print(logData)


date = convertDate() #getting date from convertDate function 
time = convertTime() #getting time from convertDate function
writeFile("D:\Programs\Serie-Directory","Add_log.txt",logData,date,time)
