from flask import Flask, request, render_template, redirect, url_for, session
import os
from dotenv import load_dotenv
import requests

app = Flask(__name__)
load_dotenv()
GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
APP_SECRET = os.getenv('APP_SECRET')
app.secret_key = APP_SECRET
HEADERS = {'Authorization': 'Bearer ' + GITHUB_ACCESS_TOKEN}

@app.route("/", methods=["GET", "POST"])
def home():
  if request.method == "POST":
    session["github_username"] = request.form["username"]
    return redirect(url_for("result"))
  else:
    return render_template("home.html")

@app.route("/result")
def result():
  if "github_username" in session:
    github_username = session["github_username"]
    user_data = {}
    repos_commits = {}
    language_list = {}
    sorted_language_list = {}
    language_codes = []
    language_values = []
    commit_weeks = []
    commit_values = []
    repo_links = []
    colors = ["#76D9B9", "#15AB89", "#09736A", "#0E5159", "#52959d"]

    for number in range(1, 53):
      repos_commits['Week %s' % number] = 0

    try:
      response = requests.get(f'https://api.github.com/users/{github_username}', headers=HEADERS).json()
      user_data = {
        "username": response["login"],
        "fullname": response["name"],
        "url": response["html_url"],
        "avatar": response["avatar_url"],
        "company": response["company"],
        "repos": repo_links
      }
      
      page_range = response["public_repos"] // 30 + 1
      have_extra_page = (response["public_repos"] % 30 > 0)
      if have_extra_page:
        page_range = response["public_repos"] // 30 + 2
      
      for page_number in range(1, page_range):
        repos_response = requests.get(f'https://api.github.com/users/{github_username}/repos?page={page_number}', headers=HEADERS).json()
        for repo in repos_response:
          repo_links.append({
            "repo_name": repo["name"],
            "repo_link": repo["html_url"],
            "repo_language": repo["language"]
          })
          if repo["language"] not in language_list:
            language_list.update({
                repo["language"]: 1
              })
          else:
            language_list[repo["language"]] += 1
          
          # Combine commit counts across repos
          repo_api_link = repo["url"]
          repo_commits = requests.get(f'{repo_api_link}/stats/participation', headers=HEADERS).json()
          commits = repo_commits["owner"]
          for i in range(52):
            repos_commits['Week %s' % (i + 1)] += commits[i]
          
      sortedLanguageValuesList = sorted(language_list.values(), reverse = True)

      for sorted_value in sortedLanguageValuesList:
        for key, value in language_list.items():
          if value == sorted_value:
            sorted_language_list.update({
              key: sorted_value
            })

      for language in sorted_language_list:
        language_codes.append(language)
      
      for count in sorted_language_list.values():
        language_values.append(count)

      for k, v in repos_commits.items():
        commit_weeks.append(k)
        commit_values.append(v)

    except:
      user_data = {
        "message": "Cannot find Github user"
      }

    return render_template(
      "result.html", 
      value=user_data, 
      language_codes=language_codes, 
      language_values=language_values, 
      colors=colors,
      commit_weeks=commit_weeks,
      commit_values=commit_values
    )

if __name__ == "__main__":
  app.run()