import json #used to decode the JSON files and fetch the data
import urllib.request as urllib #used for Google Knowledge Graph
import ast
import scipy as sp
import scipy.stats as stats
import matplotlib.pyplot as plt
from numpy.random import normal
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import zero_one_loss
from sklearn.metrics import accuracy_score
import spacy
from sklearn.datasets import make_classification
from demjson import decode
import nltk
from sklearn.preprocessing import PolynomialFeatures



a = "{test test test}{test1 test1 test1}{test2 test2 test2}{test3 test3 test3}"


a = a.replace("}{", "}\n{")
print(a)
