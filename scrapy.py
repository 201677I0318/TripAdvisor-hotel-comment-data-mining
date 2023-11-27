# -*- coding: utf-8 -*-
import csv
import requests
from bs4 import BeautifulSoup

# Remove emoji symbols
import re
def remove_emoji(string):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U0001F1F2-\U0001F1F4"  # Macau flag
                           u"\U000024C2-\U0001F251"
                           u"\U0001f926-\U0001f937"
                           u"\U0001F1F2"
                           u"\U0001F1F4"
                           u"\U0001F620"
                           u"\u200d"
                           u"\u2640-\u2642"
                           u"\u2600-\u2B55"
                           u"\u23cf"
                           u"\u23e9"
                           u"\u231a"
                           u"\u3030"
                           u"\ufe0f"
                           u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                           u"\U00002702-\U000027B0"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

# Set headers to simulate browser access
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.48'
    }

# Change URL here to crawl hotel reviews from different regions
homeurl = 'https://www.tripadvisor.com'
baseurl = 'https://www.tripadvisor.com/Hotels-g34438-oa'
lasturl='-Miami_Florida-Hotels.html'


# Get hotel review links

# Create an empty list to store hotel review links
links = []

# Loop to get all hotel review link lists
for i in range(0, 360//30+1):
    url = baseurl + str(i*30) + lasturl
    # Send request
    response = requests.get(url, headers=headers)

    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    # Get hotel review link list
    hotels = soup.find_all('a', {'class': 'review_count'})
    print("Got "+str(len(hotels))+' links on page '+str(i))
    for j, hotel in enumerate(hotels):
        if hotel.has_attr('href'):
            links.append(homeurl+hotel['href'])


# Convert link list to set to remove duplicate links
links_set = set(links)
# Convert set back to list
links = list(links_set)
print('Got '+str(len(links))+' links in total')

# Save links to csv file and remove duplicates
with open('links.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    for link in links:
        writer.writerow([link])





# Get reviews

# # Read hotel review link list
# links = []
# with open('links.csv', 'r', encoding='utf-8') as file:
#     reader = csv.reader(file)
#     for row in reader:
#         links.append(row[0])


# Create an empty list to store reviews
reviews = []
# Create an empty list to store review titles
tittles = []
# Create an empty list to store review texts
texts = []
# Create an empty list to store review ratings
rates = []


# Save reviews to csv file

with open('reviews.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Hotel Name', 'Rating', 'Title', 'Text'])

# Loop to get all hotel reviews
for j,link in enumerate(links):
    response = requests.get(link, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    hotelname = soup.find('h1', {'id': 'HEADING'}).text.replace("’", "\'").replace('“', '" ').replace('”', ' "').replace('…','...').replace('°','\°').replace('´','\'').replace('®','\®').replace('¨','\¨')
    # Get total number of English reviews
    count = soup.find('span', text='English').find_next('span', {'class': 'POjZy'})
    if count is None:
        # If there are no English reviews, possibly due to network issues, save the link for inspection and skip.
        with open('links_error.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([link])
        print('No English reviews for hotel '+str(j)+': '+hotelname+', skipping...')
        continue
    else:count = count.text.replace('(',"").replace(')',"")# There may be ',' that need to be removed
    print('Getting '+count+' English reviews for hotel '+str(j)+': '+hotelname+'...')
    for i in range(int(count.replace(',', ''))//10+1):
        reviews.clear()
        rates.clear()
        tittles.clear()
        texts.clear()
        print('Getting page '+str(i+1)+' reviews...')
        url = link.replace('Reviews-', 'Reviews-or'+str(i*10)+'-')
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        # Get rating span tags, extract the last two digits of class="ui_bubble_rating bubble_**", divide by 10 to get rating
        divs = soup.find_all('div', {'class': 'Hlmiy F1'})
        for div in divs:
            span = div.find('span')
            rates.append(int(span['class'][1].split('_')[1]) // 10)
        # Get review titles
        tittleContainers = soup.find_all('a', {'class': 'Qwuub'})
        for tittleContainer in tittleContainers:
            tittles.append(remove_emoji(tittleContainer.find('span').find('span').text.replace("’", "\'").replace('“', '" ').replace('”', ' "').replace('…','...').replace('°','\°').replace('´','\'').replace('®','\®').replace('¨','\¨')))
        # Get review texts
        textContainers = soup.find_all('span', {'class': 'QewHA H4 _a'})
        for textContainer in textContainers:
            texts.append(remove_emoji(textContainer.find('span').text.replace("’", "\'").replace('“', '" ').replace('”', ' "').replace('…','...').replace('°','\°').replace('´','\'').replace('®','\®').replace('¨','\¨')))

        for i in range(len(tittles)):
           reviews.append({'Hotel Name': hotelname, 'Rating': rates[i], 'Title': tittles[i], 'Text': texts[i]})
        # Automatically save reviews to csv file
        with open('reviews.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for review in reviews:
                writer.writerow([review['Hotel Name'], review['Rating'], review['Title'], review['Text']])
        # Clear review lists
        

print('All reviews obtained!')
