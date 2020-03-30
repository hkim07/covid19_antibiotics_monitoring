# COVID-19 Twitter Misinformation Monitor for Fact Checkers

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/YOUTUBE_VIDEO_ID_HERE/0.jpg)](https://www.youtube.com/watch?v=7BPBhW6SLpw)


## Dependency

This system was built on the Python 3.7.3 environment. The following libraries need to be installed before running the system. We installed all libraries via pip. 

- Tweepy 3.8.0
- Dash 1.9.1: https://dash.plotly.com/installation / pip install dash==1.9.1
- Sentence_transformers: https://github.com/UKPLab/sentence-transformers ('bert-base-nli-mean-tokens' ~ 400MB)
- and other useful libraries: pandas, sklearn, unidecode, and tweet preprocessor (https://github.com/s/preprocessor)

## Python files

### stream.py
It collects tweet replies from the Twitter stream. For simplicity, we filtered the stream with the keywords "corona", "virus", and "covid". 
```python
twitterStream.filter(track=['corona', 'virus', 'covid'])
```
Next, we should set an official advice which is a reference to calculate reply's similarity. You should change this advice depending on your interests. 
```python
who_official = 'No, antibiotics do not work against viruses, only bacteria. The new coronavirus (2019-nCoV) is a virus and, therefore, antibiotics should not be used as a means of prevention or treatment. However, if you are hospitalized for the 2019-nCoV, you may receive antibiotics because bacterial co-infection is possible.'
who_embs = sbert.encode([who_official], show_progress_bar=False) # return a sentence embedding vector
```
In addition to the advice, you should check whether replies have context-specific words. We limit our analysis to tweet replies having the keywords "antibiotic" or "antibiotics"
```python
if len(re.findall("antibiotic|antibiotics", text))!=0:
```
Run this file with `> python stream.py`. It initiates a sqlite database having seven fields (parent_id, parent_created, parent_text, reply_id, reply_created, reply_text, similarity_with_WHO_advice).

### config.py
You should create `config.py` in the same folder with `stream.py`. `config.py` have to contain credential keys provided by the official Twitter api. 

### app.py
Run this file with `>python app.py`. A local development server will be opened. 
- The upper panel shows recent tweet replies and their parents about COVID-19 and antibiotics. It automatically refreshes every 10 seconds. 
- The bottom left panel is the category distribution of misinformation. We classified COVID-19 misinformation about antibiotics into four categories, (1) antibiotics work against COVID-19, (2) antibiotics are able to treat viral pneumonia caused by COVID-19, (3) people can be resistant to antibiotics being used to treat bacterial co-infection, and (4) other wrong claims including conspiracy theories. 
- The bottom right panel shows top 5 parent tweets in order of their replies' similarity. As their replies have similar contexts with the official advice we set, the parent posts are likely to be contain COVID-19 misinformation about antibiotics. Once you identify misinformation in the list, put its ID and category in text boxes and submit them. This information is stored in another sqlite file named "misinformation." Saved results are retrieved to draw the bottom left panel. 

