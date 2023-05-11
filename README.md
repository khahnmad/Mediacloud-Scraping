# Mediacloud-Scraping
*Note: Updated 5/11 - while the Media Cloud API is under construction*

This repository contains code to execute two tasks: 1) querying media cloud, and 2) scraping urls of newspaper articles. It was developed and used in two projects
of mine, my [Master's Thesis](https://github.com/khahnmad/MA-Thesis_Fringe-to-Familiar) on computationally tracking narratives in newspaper text and a [project](https://github.com/khahnmad/Lest-They-Forget)
analyzing the news coverage of mass shootings. 


### 1) Querying MediaCloud
The code for querying MediaCloud is housed in the query_mediacloud folder. It functions by taking a query phrase, start and end date, and media cloud collection id 
and querying the MediaCloud API and Wayback Machine for stories (urls of articles) that match those parameters. It then exports the retrieved stories as .json files. 

### 2) Scraping Newspaper Urls
The code for scraping newspaper urls uses requests and BeautifulSoup and returns article text or a speciifc error message. The code contains the following features:

- includes a parameter for collecting only English text
- pauses in between scraping urls if they come from the same domain
- contains hard-coded tailored scraping and error handling for over 160 newspapers 
- can handle over 78 unqiue error messages given my websites when scraping failed 
