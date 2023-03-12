# Leetcode Questions Scraper For GitHub Contribution Graph

<p align="center">
  <img src="https://static.vecteezy.com/system/resources/previews/005/161/828/original/cartoon-genie-appear-from-magic-lamp-free-vector.jpg" width=50%   height=50% style="align: center">
</p>

Leetcode Questions Scraper is a simple scrapper built on top of Selenium that fetches all the problems from leetcode and write as md files. It then commits each file with a random date in a range that you provide so that you can push it to GitHub and improve your contribution graph.

## Inspirations
[LeetCode-Questions-Scraper](https://github.com/Bishalsarang/Leetcode-Questions-Scraper)

[Github Activity Generator](https://github.com/Shpota/github-activity-generator)

## How it works

Although leetcode doesn't provide an official API to fetch all the list of problems, we can use the API url  [https://leetcode.com/api/problems/algorithms/](https://leetcode.com/api/problems/algorithms/) used by leetcode internally to fetch problems that returns a json file containing info about problems.

We can build links to each problem as

`"https://leetcode.com/problems/" + question_title_slug`

After getting the problem link we can fetch the content from the page using selenium (as Leetcode is built using react where content is rendered using JS we can't use lightweight library like requests).

## Requirements

I have tested it on Mac OS running with Google Chrome Version 111.0.5563.64 (arm64)
 and chrome driver from homebrew. I haven't tested with Linux and Windows but you can download chrome driver for respective platform and make change to `CHROMEDRIVER_PATH` inside `main.py`

Pip install all the requirements.

    requests==2.22.0
    beautifulsoup4==4.8.0
    selenium==3.141.0
    colorama==0.4.1


## How to use
 - Clone the repo and install all the dependencies including latest Google Chrome and latest Chrome Driver
 - Update Chrome Driver path
 - Run the following commands to download all algorithmic problems from leetcode
 `python main.py`

 This downloads problem contents to *****< leetcode-question-slug>.html*****.

 **NOTE:** Leetcode may temporarily block requests. If the error occurs, wait for sometime and try again or use the proxy. Don't worry, since, the previous state is saved to ***track.conf*** file, the download resumes from where it failed.

