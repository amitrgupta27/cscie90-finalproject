import numpy as np
import pandas as pd
import re
from nltk.tokenize import sent_tokenize
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import gc
import string
import nltk
import sys

nltk.download('punkt')

review = sys.argv[1:]
cmdline = 0
if ((len(sys.argv) == 2)):
    cmdline = 1
    event_col = ["Text"]
    dictionary = dict(zip(event_col, review))
    df=pd.DataFrame([dictionary])
else:
    df = pd.read_csv('Reviews.csv', encoding='utf-8')
    print(df.head(3))

def split_sentences(emails):
    """
    Splits the reviews into individual sentences
    """
    n_emails = len(emails)
    for i in range(n_emails):
        email = emails[i]
        sentences = sent_tokenize(email)
        for j in reversed(range(len(sentences))):
            sent = sentences[j]
            sentences[j] = sent.strip()
            if sent == '':
                sentences.pop(j)
        emails[i] = sentences

rev_list = list(df['Text'])
split_sentences(rev_list)
#Adding split reviews in the data frame
df['sent_tokens'] = rev_list
#Calculating lenght of sentences in each review
df['length_of_rv'] = df['sent_tokens'].map(lambda x: len(x))

choice_length = 4
df = df[df['length_of_rv']>choice_length]


#Making vocabulary with reviews with max vocabs=5000.
list_sentences_train = df['Text']
max_features = 5000
tokenizer = Tokenizer(num_words=max_features)
tokenizer.fit_on_texts(list(list_sentences_train))
list_tokenized_train = tokenizer.texts_to_sequences(list_sentences_train)
maxlen = 200
X_t = pad_sequences(list_tokenized_train, maxlen=maxlen)


def loadEmbeddingMatrix(typeToLoad):
    # load different embedding file from Kaggle depending on which embedding
    # matrix we are going to experiment with
    if (typeToLoad == "glove"):
        EMBEDDING_FILE = 'glove.twitter.27B.25d.txt'
        embed_size = 25

    elif (typeToLoad == "fasttext"):
        EMBEDDING_FILE = 'wiki.simple.vec/wiki.simple.vec'
        embed_size = 300

    if (typeToLoad == "glove" or typeToLoad == "fasttext"):
        embeddings_index = dict()
        # Transfer the embedding weights into a dictionary by iterating through every line of the file.
        f = open(EMBEDDING_FILE, encoding='utf-8')
        for line in f:
            # split up line into an indexed array
            values = line.split()
            # first index is word
            word = values[0]
            # store the rest of the values in the array as a new array
            coefs = np.asarray(values[1:], dtype='float32')
            embeddings_index[word] = coefs  # 50 dimensions
        f.close()



    gc.collect()
    return embeddings_index  # , embedding_matrix

## Loading 'glove' words
emb_index= loadEmbeddingMatrix('glove')

def calculate_sentence_embedding(wordList):
    
    #This function calculates the embedding for entire sentence by taking the mean of embedding of
    #each word in the sentence. To be improved.
    emb_li =[]
    for k in wordList:
        embedding_vector = emb_index.get(k)
        if embedding_vector is not None:
            if(len(embedding_vector) == 25):
                emb_li.append(list(embedding_vector))
    mean_arr = np.array(emb_li)
    return np.mean(mean_arr, axis=0)


def get_sent_embedding(mylist):
    
    #This function calculates the embedding of each sentence in the review. Checks if the sentence being passed is a valid one,
    #removing the punctuation and emojis etc.
    
    sent_emb = []
    n_sentences = len(mylist)
    for i in mylist:
        i = i.lower()
        wL = re.sub("[^\w]", " ",  i).split()
        if(len(wL)>0):
            for k in wL:
                if(k in string.punctuation):
                    wL.remove(k)
            if(len(wL) <= 2):
                continue
        else:
            continue
        res = list(calculate_sentence_embedding(wL))
        sent_emb.append(res)
    return np.array(sent_emb)

from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
## Calculating summaries for first 5000 reviews.
if (cmdline):
    how_many_summaries = 1
else:
    how_many_summaries = 500
summary = [None]*how_many_summaries

for rv in range(how_many_summaries):
        review = df['sent_tokens'].iloc[rv]
        enc_email = get_sent_embedding(review)
        if(len(enc_email) > 0):
            n_clusters = int(np.ceil(len(enc_email)**0.5))
            kmeans = KMeans(n_clusters=n_clusters, random_state=0)
            kmeans = kmeans.fit(enc_email)
            avg = []
            closest = []
            for j in range(n_clusters):
                idx = np.where(kmeans.labels_ == j)[0]
                avg.append(np.mean(idx))
            closest, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_,\
                                                       enc_email)
            ordering = sorted(range(n_clusters), key=lambda k: avg[k])
            summary[rv] = ' '.join([review[closest[idx]] for idx in ordering])
        else:
            print("This is not a valid review")



if (cmdline):
    print(f'{summary}')
else:
    df_500 = df.iloc[:how_many_summaries]
    print(df_500.head())
    df_500['PredictedSummary'] = summary
    df_500[['Text', 'PredictedSummary']].to_csv('top_500_summary.csv')
