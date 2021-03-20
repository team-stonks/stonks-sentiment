import re
import json
from datetime import date, timedelta

import requests
import urllib.parse
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup

import nltk
from transformers import pipeline

nltk.download('punkt')


def remove_markdown(str_with_markdown):
    clean_re = re.compile('<.*?>')
    clean_text = clean_re.sub('', str_with_markdown)
    return ' '.join(clean_text.strip().split())


def extract_text_from_page(url):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")

    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text


def get_news_for_company(name, for_days=1):
    with open("config.json", "r") as c:
        api_key = json.load(c)['apiKey']
    name_encoded = urllib.parse.quote(name)
    date_from = (date.today() - timedelta(days=for_days)).strftime('%Y-%m-%d')
    url = f'https://newsapi.org/v2/everything?q={name_encoded}&from={date_from}&sortBy=relevancy&apiKey={api_key}'
    response = requests.get(url)
    articles = [{'title': remove_markdown(article['title']),
                 'description': remove_markdown(article['description']),
                 'url': article['url'],
                 'content': article['content']} for article in response.json()['articles']]

    texts_to_analyze = []
    i = 0
    for article in articles:
        title, description, url, content = article.values()
        texts_to_analyze.append(title)
        if description.endswith('…'):
            description = description[:-2]
        texts_to_analyze.append(description)
        '''
        try:
            if i < 5 or not content:
                texts_to_analyze.append(extract_text_from_page(url))
                i += 1
            else:
                texts_to_analyze.append(content.split('…')[0])
        except HTTPError:
            texts_to_analyze.append(content.split('…')[0])
        '''
    out_text = ' '.join(' '.join(texts_to_analyze).split())
    return out_text


def analyze_sentiment(large_text):
    sentiment_analysis = pipeline("sentiment-analysis")
    avg_score = 0
    # Bert can't analyze all sentences at once, so we split into pairs and aggregate score
    sentences = nltk.tokenize.sent_tokenize(large_text)

    for i in range(0, len(sentences), 2):
        sentence = ' '.join(sentences[i:i + 2])
        label, score = sentiment_analysis(sentence)[0].values()
        if label == 'POSITIVE':
            avg_score += score
        else:
            avg_score -= score
    avg_score /= len(sentences)

    return avg_score


def company_sentiment(company_name):
    return analyze_sentiment(get_news_for_company(company_name))


def main():
    print(company_sentiment('Tesla'))


if __name__ == '__main__':
    main()
