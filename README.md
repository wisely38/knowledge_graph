# knowledge_graph

github:  https://github.com/wisely38/knowledge_graph.git


The project includes:

- a spider to download asset management pages from HSBC UK
- a sentences cleanser
- a entities-relations generator


Instruction 

1. python -m spacy download en_core_web_lg

2. pip install -r requirements.txt

3. go to folder "knowledge_graph/crawler" and run "scrapy crawl fundspider"

4. now you should see scrapped sentences in folder "knowledge_graph/staging/11-08-2019"

5. run "python -m spacy download en_core_web_lg" to download model

6. go to folder "knowledge_graph" and run "python pipeline_sentence_filer.py", we will filter out sentences which contains subject + verb + object with the dependency tags:
"nsubj","nsubjpass", "ROOT", "dobj", "pobj", "dobj" 

7. go to folder "knowledge_graph" and run "python pipeline_training_generator.py", in here we:

i. 	generate NER-based entities based on NLP tags that indicates nouns and object related tokens with function to possible guess annotated labels like RISK/ASSET/PRODUCT
ii.	generate entity-relation pairs based on subject, object, main verb which determined by NLP Universal Dependencies tags
ii.	also generate annotated training data for further machine modeling if time is allowed to do so with the possible guess annotated labels found in i above


outputs: 
i.  The training out file will be "preparation-training_data.json"  
ii. The recognized entities could be found in "preparation-relations_token_data.json" and "preparation-relations_compound_data.json" for standard single token and noun chunked token, respectively.


9. copy file "knowledge_graph/staging/11-08-2019/preparation-relations_token_data.json" to folder "knowledge_graph/", then open jupyter notebook "Visualize Graph.ipynb" and run for graph visualization
Here we import the "preparation-relations_token_data.json" to jupyter and convert to pandas frame for further visualization in graph relations