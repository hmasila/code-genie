# Author: Hannah Masila
import os
import re
import sys
import json
import time
import random
import argparse
from subprocess import Popen

import bs4
import colorama
import requests
from colorama import Back, Fore

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Initialize Colorama
colorama.init(autoreset=True)

# Setup Selenium Webdriver
CHROMEDRIVER_PATH = r"/opt/homebrew/bin/chromedriver"
options = Options()
options.headless = True
# Disable Warning, Error and Info logs
# Show only fatal errors
options.add_argument("--log-level=3")
driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)


def download(problem_num, url, title, solution_slug, title_slug, commit_date):
    print(Fore.BLACK + Back.CYAN + f"Fetching problem num " + Back.YELLOW + f" {problem_num} " + Back.CYAN + " with url " + Back.YELLOW + f" {url} ")

    try:

        driver.get(url)
        # Wait 30 secs or until div with class '_1l1MA' appears
        element = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "_1l1MA"))
        )
        # Get current tab page source
        html = driver.page_source
        soup = bs4.BeautifulSoup(html, "html.parser")

        # Construct HTML
        problem_html = str(soup.find("div", {"class": "_1l1MA"}))

        # Construct Markdown
        title = f'# {title}\n\n'
        markdown = title + html_to_markdown(problem_html)

        # Append Contents to a md file
        directory = "challenges"
        file_path = os.path.join(directory, f'{title_slug}.md')

        if not os.path.isdir(directory):
            os.mkdir(directory)

        with open(file_path, "wb") as f:
            f.write(markdown.encode(encoding="utf-8"))

        # commit changes
        run(['git', 'add', file_path])
        run(['git', 'commit', '-m', title,
        '--date', commit_date])

        # Update upto which the problem is downloaded
        update_tracker('track.conf', problem_num)
        print(Fore.BLACK + Back.GREEN + f"Writing problem num " + Back.YELLOW + f" {problem_num} " + Back.GREEN + " with url " + Back.YELLOW + f" {url} " )
        print(Fore.BLACK + Back.GREEN + " successfull ")
        # print(f"Writing problem num {problem_num} with url {url} successfull")

    except Exception as e:
        print(Back.RED + f" Failed Writing!!  {e} ")
        driver.quit()


def commit(file_path, title, commit_date):
    run(['git', 'add', file_path])
    run(['git', 'commit', '-m', title,
    '--date', commit_date])

def str_time_prop(start, end):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """
    time_format = "%Y-%m-%d %H:%M:%S"

    ptime = start + random.random() * (end - start)

    return time.strftime(time_format, time.localtime(ptime))

def run(commands):
    p = Popen(commands)
    p.wait()
    output, error = p.communicate()

    if p.returncode != 0:
        print("jishin failed %d %s %s" % (p.returncode, output, error))

def update_tracker(file_name, problem_num):
     """
    Update the tracker number
     """
     with open(file_name, "w") as f:
         f.write(str(problem_num))


def read_tracker(file_name):
    """
    Read the tracker number
    """
    with open(file_name, "r") as f:
        return int(f.readline())

def html_to_markdown(html):
    # Replace opening/closing <div> tags with empty string
    html = re.sub(r'<div.*?>|</div>', '', html)

    html = re.sub(r'<strong>Input:</strong>', '\nInput:', html)
    html = re.sub(r'<strong>Output:</strong>',  'Output:', html)
    html = re.sub(r'<strong>Explanation:</strong>', 'Explanation:', html)
    # Replace <strong> and <code> tags with their markdown equivalents
    html = re.sub(r'<strong>(.*?)</strong>', r'**\1**', html)
    html = re.sub(r'<strong class="example">(.*?)</strong>', r'**\1**', html)
    html = re.sub(r'<code>(.*?)</code>', r'`\1`', html)

    # Replace <ul> and <li> tags with their markdown equivalents
    html = re.sub(r'<ul.*?>|</ul>', '', html)
    html = re.sub(r'<li.*?>(.*?)</li>', r'* \1\n', html)

    # Replace <pre> tags with their markdown equivalents
    html = re.sub(r'<pre>|</pre>', r'```', html)

    # Replace &lt with <
    html = re.sub(r'&lt', '<', html)

    # Replace &gt with >
    html = re.sub(r'&gt', '>', html)

    # Replace remaining <p> tags with line break
    html = re.sub(r'<p.*?>|</p>', '<br />', html)

    return html.strip()


def main(def_args=sys.argv[1:]):
    args = arguments(def_args)
    repository = args.repository
    user_name = args.user_name
    user_email = args.user_email

    if user_name is not None:
        run(['git', 'config', 'user.name', user_name])

    if user_email is not None:
        run(['git', 'config', 'user.email', user_email])

    if repository is not None:
        run(['git', 'clone', repository])

    try:
        start_date = time.mktime(time.strptime(args.start_date, "%Y-%m-%d"))
        end_date = time.mktime(time.strptime(args.end_date, "%Y-%m-%d"))

        commit_date = str_time_prop(start_date, end_date)
    except ValueError:
        sys.exit('Date format is not correct. Please use YYY-MM-DD format.')

    # Leetcode API URL to get json of problems on algorithms categories
    ALGORITHMS_ENDPOINT_URL = "https://leetcode.com/api/problems/algorithms/"

    # Problem URL is of format ALGORITHMS_BASE_URL + question__title_slug
    # If question__title_slug = "two-sum" then URL is https://leetcode.com/problems/two-sum
    ALGORITHMS_BASE_URL = "https://leetcode.com/problems/"

    # Load JSON from API
    algorithms_problems_json = requests.get(ALGORITHMS_ENDPOINT_URL).content
    algorithms_problems_json = json.loads(algorithms_problems_json)

    # List to store question_title_slug
    links = []
    for child in algorithms_problems_json["stat_status_pairs"]:
            # Only process free problems
            if not child["paid_only"]:
                question__title_slug = child["stat"]["question__title_slug"]
                question__article__slug = child["stat"]["question__article__slug"]
                question__title = child["stat"]["question__title"]
                frontend_question_id = child["stat"]["frontend_question_id"]
                difficulty = child["difficulty"]["level"]
                links.append((question__title_slug, difficulty, frontend_question_id, question__title, question__article__slug))

    # Sort by difficulty follwed by problem id in ascending order
    links = sorted(links, key=lambda x: (x[1], x[2]))

    # Get upto which problem it is already scraped from track.conf file
    completed_upto = read_tracker("track.conf")

    try:
        for i in range(completed_upto + 1, len(links)):
             question__title_slug, _ , frontend_question_id, question__title, question__article__slug = links[i]
             url = ALGORITHMS_BASE_URL + question__title_slug
             title = f"{frontend_question_id}. {question__title}"

             # Download each file as html and write chapter to chapters.pickle
             download(i, url , title, question__article__slug, question__title_slug, commit_date)

             # Sleep for 20 secs for each problem and 2 minns after every 30 problems
             if i % 30 == 0:
                 print(f"Sleeping 120 secs\n")
                 time.sleep(120)
             else:
                 print(f"Sleeping 20 secs\n")
                 time.sleep(5)

    finally:
        # Close the browser after download
        driver.quit()
        print(Back.GREEN + "All operations successful")


def arguments(argsval):
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repository', type=str, required=False,
                        help="""A link on an empty non-initialized remote git
                        repository. If specified, the script pushes the changes
                        to the repository. The link is accepted in SSH or HTTPS
                        format. For example: git@github.com:user/repo.git or
                        https://github.com/user/repo.git""")
    parser.add_argument('-un', '--user_name', type=str, required=False,
                        help="""Overrides user.name git config.
                        If not specified, the global config is used.""")
    parser.add_argument('-ue', '--user_email', type=str, required=False,
                        help="""Overrides user.email git config.
                        If not specified, the global config is used.""")
    parser.add_argument('-st', '--start_date', type=str, default='2019-02-14',
                        required=False, help="""Specifies the date to start adding
                        commits. The format should be YYYY-MM-DD.
                        For example: if it's set to 2019-02-14,
                        there will be no commits generated before that date""")
    parser.add_argument('-ed', '--end_date', type=str, default='2023-02-14',
                        required=False, help="""Specifies the date to stop adding
                        commits. The format should be YYYY-MM-DD.
                        For example: if it's set to 2023-02-14,
                        there will be no commits generated after that date.""")
    return parser.parse_args(argsval)

if __name__ == "__main__":
    main()
