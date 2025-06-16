from flask import Flask, request
import requests, validators
from bs4 import BeautifulSoup

app = Flask(__name__)

def is_valid_url(url):
    return validators.url(url)

def trace_redirects(url):
    session = requests.Session()
    try:
        response = session.get(url, allow_redirects=True, timeout=10)
        return response.url, response.text
    except:
        return None, None

def extract_links(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return [a['href'] for a in soup.find_all('a', href=True)]

def is_tracking_url(url):
    keywords = ['track', 'spy', 'log', 'ads', 'click', 'redirect']
    return any(word in url.lower() for word in keywords)

@app.route('/')
def home():
    return '''
        <form action="/scan" method="post">
            <input name="url" placeholder="Enter URL to scan" style="width:300px"/>
            <button type="submit">Scan</button>
        </form>
    '''

@app.route('/scan', methods=['POST'])
def scan():
    url = request.form['url']
    if not is_valid_url(url):
        return "Invalid URL"
    final_url, html = trace_redirects(url)
    if final_url is None:
        return "Failed to trace URL"
    result = f"<h3>Final URL:</h3><p>{final_url}</p>"
    links = extract_links(html)
    result += "<h3>Extracted Links:</h3><ul>"
    for link in links:
        style = "color:red;" if is_tracking_url(link) else "color:green;"
        result += f"<li style='{style}'>{link}</li>"
    result += "</ul>"
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
