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
    language_list = {}
    sorted_language_list = {}
    language_codes = []
    language_values = []
    colors = ["#76D9B9", "#15AB89", "#09736A", "#0E5159", "#52959d"]
    try:
      response = requests.get(f'https://api.github.com/users/{github_username}', headers=HEADERS).json()
      user_data = {
        "username": response["login"],
        "fullname": response["name"],
        "url": response["html_url"],
        "avatar": response["avatar_url"],
        "company": response["company"],
        "repo_number": response["public_repos"],
      }

      repos_response = requests.get(f'https://api.github.com/users/{github_username}/repos?per_page=100', headers=HEADERS).json()
      for repo in repos_response:
        if repo["language"] not in language_list:
          language_list.update({
              repo["language"]: 1
            })
        else:
          language_list[repo["language"]] += 1

      sortedValuesList = sorted(language_list.values(), reverse = True)
  
      for sorted_value in sortedValuesList:
        for key, value in language_list.items():
          if value == sorted_value:
            sorted_language_list.update({
              key: sorted_value
            })

      for language in sorted_language_list:
        language_codes.append(language)
      
      for count in sorted_language_list.values():
        language_values.append(count)

    except:
      user_data = {
        "message": "Cannot find Github user"
      }
    finally:
      print(sorted_language_list)

    return render_template("result.html", value=user_data, language_codes=language_codes, language_values=language_values, colors=colors)

if __name__ == "__main__":
  app.run()