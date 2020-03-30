# COVID-19 Twitter Misinformation Monitor for Fact Checkers

## Dependency

This system was built on the Python 3.7.3 environment. The following libraries need to be installed before running the system. We installed all libraries via pip. 

- Tweepy
- Dash: https://dash.plotly.com/installation / pip install dash==1.9.1
- Sentence_transformers: https://github.com/UKPLab/sentence-transformers
- and other useful libraries: pandas, sklearn, unidecode, and tweet preprocessor (https://github.com/s/preprocessor)

## Python files

### stream.py
It collects tweet replies from the Twitter stream. For simplicity, we used three keywords to filter the stream: "corona", "virus", and "covid". 
```python
twitterStream.filter(track=['corona', 'virus', 'covid'])
```

It initiates a sqlite database having seven fields (parent_id, parent_created, parent_text, 
