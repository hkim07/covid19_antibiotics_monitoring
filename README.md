# COVID-19 Twitter Misinformation Monitor for Fact Checkers

## Dependency

This system was built on the Python 3.7.3 environment. The following libraries need to be installed before running the system. We installed all libraries via pip. 

- Tweepy
- Dash: https://dash.plotly.com/installation / pip install dash==1.9.1
- Sentence_transformers: https://github.com/UKPLab/sentence-transformers
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

