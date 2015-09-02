This project builds a csv of over 900000 soccer games throughout history, starting at before 1900 to the current day from the individual round pages at http://www.footballdatabase.eu/ (http://www.footballdatabase.eu/football.competition.premier-league.angleterre.2015-2016..4465.en.html).

To run this you will need to register at footballdatabase.eu and make one code change locally. When you sign up for the site you should get an email with a url which sets your cookie.
The url is of the form #"http://www.footballdatabase.eu/index.php?m=_username_&autolog=_hash_".   Replace the string in ln 19 of fr.py with this url.

Running the commands below may take some time. Over 100,000 webpages will be scraped to collect the data. After the data is scraped and cleaned the elo rating for each team in each game is calculated sequentially.

Instructions to run

	1. Update fr.py with your personal cookie setting url
	2. run scrapeCompetitions.py
		- writes data/competitions.csv which has all the competitions which will be collected (768 unique as of my last run)
	3. run scrapeRounds.py
		- writes a csv with all of the individual rounds to be hit (126281 as of my last run)
	4. run scrapeGames.py
		- This may take a while, use the inputs for this function to run multiple processes at once 
			- ```python scrapeGames.py 0 10000 1``` -> puts the games from the first 10000 urls in data/games1.csv
			- ```python scrapeGames.py 10000 20000 2```
	5. run cleanAndCalcElo.py
		- aggregates the games in games1-99.csv, clean, sort by date, calc ELOs


A compressed csv is already available at data/games.csv.tar.gz
Some analysis of the collected data is done in footyAnalysis.ipynb.