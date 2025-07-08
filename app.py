from flask import Flask, request, render_template, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = Flask(__name__)

def duckduckgo_summary(query):
    url = "https://api.duckduckgo.com/"
    params = {"q": query, "format": "json", "no_redirect": 1, "no_html": 1}
    try:
        res = requests.get(url, params=params)
        data = res.json()
        return data.get("AbstractText", "")
    except:
        return "Summary unavailable."

def duckduckgo_links(query):
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {"q": query}
    try:
        res = requests.get("https://html.duckduckgo.com/html/", headers=headers, params=params)
        soup = BeautifulSoup(res.text, "html.parser")
        results = []
        for a in soup.select(".result__url"):
            href = a.get("href")
            title = a.text.strip()
            if href:
                domain = urlparse(href).netloc
                favicon = f"https://www.google.com/s2/favicons?domain={domain}"
                results.append({"title": title, "url": href, "favicon": favicon})
        return results
    except:
        return []

@app.route("/", methods=["GET", "POST"])
def search():
    query = request.form.get("query", "")
    page = int(request.args.get("page", 1))
    per_page = 5
    summary = ""
    links = []
    if query:
        summary = duckduckgo_summary(query)
        all_links = duckduckgo_links(query)
        total = len(all_links)
        start = (page - 1) * per_page
        end = start + per_page
        links = all_links[start:end]
        return render_template("search.html", query=query, summary=summary, links=links, page=page, total=total, per_page=per_page)
    return render_template("search.html", query="", summary="", links=[], page=1, total=0, per_page=per_page)

@app.route("/autocomplete")
def autocomplete():
    q = request.args.get("q", "")
    suffixes = [" news", " stats", " history", " results", " prediction"]
    suggestions = [q + s for s in suffixes if q]
    return jsonify(suggestions)

if __name__ == "__main__":
    app.run(debug=True)
