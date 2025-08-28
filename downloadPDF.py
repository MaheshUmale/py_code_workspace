# Import libraries
import requests
from bs4 import BeautifulSoup

# URL from which pdfs to be downloaded
pageURL = "https://www.geeksforgeeks.org/how-to-extract-pdf-tables-in-python/"

def dowlloadAllFilesFromURLPage(pageURL) :
	# Requests URL and get response object
	response = requests.get(pageURL)

	# Parse text obtained
	soup = BeautifulSoup(response.text, 'html.parser')

	# Find all hyperlinks present on webpage
	links = soup.find_all('a')

	i = 0

	# From all links check for pdf link and
	# if present download file
	for link in links:
		if ('.pdf' in link.get('href', [])):
			i += 1
			print("Downloading file: ", i)

			# Get response object for link
			response = requests.get(link.get('href'))

			# Write content in pdf file
			pdf = open("pdf"+str(i)+".pdf", 'wb')
			pdf.write(response.content)
			pdf.close()
			print("File ", i, " downloaded")

		print("All PDF files downloaded")


largeFileUrl = "https://download.library.lol/main/3134000/987aa4b8f2563feccb1f3e4695914fc3/Al%20Brooks%20-%20Reading%20Price%20Charts%20Bar%20by%20Bar_%20The%20Technical%20Analysis%20of%20Price%20Action%20for%20the%20Serious%20Trader-Wiley%20%282009%29.pdf"
largeFileName = "Al Brooks - Reading Price Charts Bar by Bar_ The Technical Analysis of Price Action for the Serious Trader-Wiley (2009).pdf"

url2 ="https://download.library.lol/main/4052000/59eb25984bfe262093bc02703d663863/Brandon%20Rosewag%20-%20The%20New%20Age%20of%20Technical%20Analysis.pdf"
name2 ="The New Age of Technical Analysis.pdf"
from bs4 import BeautifulSoup
def downloadLargeFile(url,name):
	# Import libraries
	import requests


#
	# response = requests.get( url)
	# pdf = open(url, 'wb')
	# pdf.write(response.content)
	# pdf.close()
	response = requests.get(url, stream=True)
	count = 0
	with open(name, mode="wb") as file:

		for chunk in response.iter_content(chunk_size=10 * 1024):
			file.write(chunk)
			count = count + 1
			#print(count)
			if count==10 :
				print("--in progress-")
				count=0

		print(" DOWNLOADED ---" + name)

downloadLargeFile(url2,name2)