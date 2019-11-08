# knowledge_graph


1. python -m spacy download en_core_web_lg

2. pip install -r requirements.txt

3. go to folder "knowledge_graph/crawler" and run "scrapy crawl fundspider"

4. now you should see scrapped sentences in folder "knowledge_graph/staging/11-08-2019"

5. run "python -m spacy download en_core_web_lg" to download model

6. go to folder "knowledge_graph" and run "python pipeline_sentence_filer.py" 

7. go to folder "knowledge_graph" and run "python pipeline_training_generator.py" 

9. copy file "knowledge_graph/staging/11-08-2019/preparation-relations_token_data.json" to "knowledge_graph", then open jupyter notebook "Visualize Graph.ipynb" and run for graph visualization