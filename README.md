# information retrieval
These codes are my "modern information retrieval" course project, which included three phases:
## Phase1
In this phase first, we preprocessed some Persian text and then indexed given data. Finally, this indexed data was queried and we evaluated the system by calculating MAP, F-Measure, R-Precision, and NDCG.
## Phase2
In the second phase, we classified data from news into four categories. For classification, we used kNN, Naive Bayes, Random Forest, and SVM. We also used K-means to cluster the data. in the end, we analyzed results using t-SNE.
The evaluation metrics used were: Recall, Precision, Accuracy, Confusion matrix, and Macro averaged F1.
Finally, we used word2vec to reduce the dimension of data and then applied our K-means algorithm on the derived data.
## Phase3
In the third phase, first, we crawled the researchgate.net website and extracted some papers' data and then indexed them in ElasticSearch. After indexing we calculated page rank of each paper and found top authors using HITS algorithm.
Findally, we used learning to rank algorithm  MQ2008 dataset using Ranking SVM and evaluated the result using NDCG.
