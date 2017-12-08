import json #used to decode the JSON files and fetch the data
import urllib.request as urllib #used for Google Knowledge Graph
import ast
import scipy as sp
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from numpy.random import normal
from sklearn.metrics import zero_one_loss
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
import spacy
from subject_object_extraction import findSVOs
from demjson import decode
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

class ProgrammingAssignmentThree():

    file = None #JSON file to read from
    rawData = [] #JSON raw data
    positiveExamples = [] #Keep in this list just the positive examples
    negativeExamples = [] #Keep in this list just the negative examples
    positiveElementsResolved = [] #No more ids
    negativeElementsResolved = [] #No more ids
    positiveAndNegativeExamples = {} #Keep in this dictionary positive and negative examples, {JSON OBJECT:"yes"}, {JSON OBJECT: "no"}
    parser = spacy.en.English()

    """
    Constructor
    1) Reads a JSON file from an indicated file path and takes its' content into :var file
    2) Decodes the JSON file and saves its' content to :var rawData
    """
    def __init__(self, filePath=""):


        self.file = open("relevant_resources\\"+filePath, "r", encoding="utf-8")
        #For debug purposes
        #print(str(self.file.read()))

        for line in self.file:
            self.rawData.append(json.loads(line.replace('\\', ''), encoding="utf-8")) #I had to replace all "\" with "" because of character escaping errors
        # For debug purposes
        #print(self.rawData[1]['evidences'][0]['snippet'])
        #print(self.rawData[1]['judgments'])

    """
    This method resolves the id/ name problem using the Google Knowledge Graph API
    """
    def queryGoogleKnowledgeGraph(self, entity):
        #Code taken and adapted from Google's reference
        """Python client calling Knowledge Graph Search API."""


        api_key = "AIzaSyDumYWiT0CbjcJ3i2lkMwZa29ULPhyyGDo"
        service_url = 'https://kgsearch.googleapis.com/v1/entities:search?ids=' + str(entity) + "&indent=True" + "&key=" + api_key
        url = service_url
        response = json.loads(urllib.urlopen(url).read())
        name = ""
        for element in response['itemListElement']:
            try:
                name = element['result']['name']# + ' (' + str(element['resultScore']) + ')')
                #print(name)
            except Exception as e:
                print("There was a problem finding the entity "+ str(entity)+ " in the google knowledge graph")
                print(e)
        return name
    """
    Sort examples by positive and negative
    If there are examples where the raters do not agree, I clasify the dominant answer
    """
    def sortExamples(self):

        for element in self.rawData:
            negativeCount = 0
            positiveCount = 0

            for judgement in element['judgments']:
                if(judgement['judgment'] == 'yes'):
                    positiveCount += 1
                else:
                    negativeCount += 1
            # For debug purposes
            #print(element, positiveCount, negativeCount)

            if(positiveCount > negativeCount):
                self.positiveExamples.append(element)
                #self.positiveAndNegativeExamples[element] = 'yes'
            else:
                self.negativeExamples.append(element)
                #self.positiveAndNegativeExamples[element] = 'no'
        # For debug purposes
        #print(self.positiveExamples)

    """
    Searching and changeing the subject id and object id to proper name entities
    """
    def idToName(self):

        writePositiveExamples = open("positive_examples_place_of_birth.txt", "a", encoding="utf-8")
        writeNegativeExamples = open("negative_examples_place.txt", "a", encoding="utf-8")

        # ----- POSITIVE -----
        for element in self.positiveExamples:
            subjectId = element['sub']
            objectId = element['obj']

            #print(subjectId, objectId)
            try:
                subjectName = self.queryGoogleKnowledgeGraph(subjectId)
                objectName = self.queryGoogleKnowledgeGraph(objectId)
            except Exception as e:
                self.positiveExamples.remove(element)
                print("An error occured while resolving ids: " + str(subjectId) + ", "+str(objectId)+". From the following element: "+str(element)+"\n")
                print("As a consequence, the element will be remove from the examples list")

            if(subjectName != ""):
                element['sub'] = subjectName
            else:
                print("Because the subject wasn't found in the google knowledge graph, the element will be removed from the list")
                try:
                    self.positiveExamples.remove(element)
                except:
                    pass
            if(objectName != ""):
                element['obj'] = objectName
            else:
                print("Because the subject wasn't found in the google knowledge graph, the element will be removed from the list")
            # try:
            #     self.positiveExamples.remove(element)
            # except:
            #     pass
            writePositiveExamples.write(str(element)+"\n")
        #For debug purposes
        #print(self.positiveExamples)

        #----- NEGATIVE -----
        for element in self.negativeExamples:
            subjectId = element['sub']
            objectId = element['obj']

            #print(subjectId, objectId)
            try:
                subjectName = self.queryGoogleKnowledgeGraph(subjectId)
                objectName = self.queryGoogleKnowledgeGraph(objectId)
            except Exception as e:
                self.negativeExamples.remove(element)
                print("An error occured while resolving ids: " + str(subjectId) + ", "+str(objectId)+". From the following element: "+str(element)+"\n")
                print("As a consequence, the element will be remove from the examples list")

            if(subjectName != ""):
                element['sub'] = subjectName
            else:
                print("Because the subject wasn't found in the google knowledge graph, the element will be removed from the list")
                try:
                    self.negativeExamples.remove(element)
                except:
                    pass
            if(objectName != ""):
                element['obj'] = objectName
            else:
                print("Because the subject wasn't found in the google knowledge graph, the element will be removed from the list")
            # try:
            #     self.negativeExamples.remove(element)
            # except:
            #     pass
            writeNegativeExamples.write(str(element)+"\n")
        #For debug purposes
        #print(self.positiveExamples)

    """
    Observed a bug in files, and I had to split the elements with a new line
    This method was created for debug purposes
    """
    def normalizeDocuments(self, path):

        readFile = open(str(path), "r", encoding="utf-8")

        elements = readFile.read()
        elements = elements.replace("}{", "}\n{")
        #elements = elements.replace("'", "\"")

        writeFile = open(str(path)+"Nornalized.json", "a", encoding="utf-8")
        writeFile.write(str(elements))

    """
    Remove the entities in which the subject or the object cannot be found in the text snippet
    ---Once you resolve the IDs, identify the strings in the text snippet.
    """
    def reviewTheSet(self, path):

        readFile = open(str(path), "r", encoding="utf-8")
        writeFile = open("negative_example_place_CorrectedSet.json", "a", encoding="utf-8")

        for element in readFile:
            list = decode(element, encoding="utf-8")
            if((list['sub'] in list['evidences'][0]['snippet']) and (list['obj'] in list['evidences'][0]['snippet'])):
                #print(list['evidences'][0]['snippet'])
                new_element = json.dumps(list)
                writeFile.write(new_element+"\n")
            else:
                print("---")
                print("The exact string was not found in the text snippet")
                print(element)
                print("---")


    """
    Tokenization, Lemmatization, shape, prefix, suffix, probability, cluster
    """
    def nlp(self, sentence):

        parsedData = self.parser(sentence)
        dict = {}
        for token in parsedData:
            dict[token] = [token, token.lemma_, token.shape_, token.prefix_, token.suffix_, token.prob, token.cluster]
        return dict

    """
    Get the entities of a sentence
    """
    def getEntities(self, sentence):
        entities = []
        parsedEx = self.parser(sentence)
        ents = list(parsedEx.ents)
        for entity in ents:
            entities.append([entity.label, entity.label_, ' '.join(t.orth_ for t in entity)])

        return entities

    """
    Part of speech tagging of a given text snippet
    """
    def partOfSpeechTagging(self, text):
        return nltk.pos_tag(nltk.word_tokenize(str(text)))

    """
    Split sentences of a text and return a list of sentences
    """
    def sentenceTokenizer(self, text):
        return nltk.sent_tokenize(text, language='english')

    def subjectObjectExtraction(self, sentence):
        parse = self.parser(sentence)
        return findSVOs(parse)


    #TO DO base-phrase chunking

    """
    Dependency parsing with SPACY
    """
    def dependencyParsing(self, sentence):
        dependencyParsingList = []

        doc = self.parser(sentence)
        for chunk in doc.noun_chunks:
            dependencyParsingList.append([chunk.text, chunk.root.text, chunk.root.dep_,chunk.root.head.text])
        return dependencyParsingList

    #TO DO  full constituent parsing


    #Machine Learning Part

    #Logistic Regression
    def sigm(self, x):
        return 1 / (1 + sp.exp(-x))

    def doLogisticRegression(self, X, y):
        h = LogisticRegression()
        h.fit(X,y)
        plt.plot(X, y, h.predict())

    #Empirical Error
    def misclassification_error(self, h, X, y):
        error = 0
        for xi, yi in zip(X, y):
            if h(xi) != yi: error += 1
        return float(error) / len(X)

    #Perceptron
    def sigmoid(self, a, x):
        return 1 / (1 + np.exp(-a * x))

    def unit_step(x):
        return 1.0 * (x >= 0)


test = ProgrammingAssignmentThree("20130403-place_of_birth.json")
#test.queryGoogleKnowledgeGraph("/m/02v_brk")
#test.sortExamples()
#test.idToName()
#test.reviewTheSet("negative_examples_place_nornalized.json")
print(test.partOfSpeechTagging("Charles Creswell (born 10 March 1813 at Radford, Nottinghamshire; died 22 November 1882 at Heaton Norris, Cheshire) was an English cricketer who played first-class cricket from 1836 to 1843. Mainly associated with Nottinghamshire, he made 12 known appearances in first-class matches. He represented the North in the North v. South series."))
print(test.dependencyParsing("Charles Creswell (born 10 March 1813 at Radford, Nottinghamshire; died 22 November 1882 at Heaton Norris, Cheshire) was an English cricketer who played first-class cricket from 1836 to 1843."))
print(test.nlp("Charles Creswell (born 10 March 1813 at Radford, Nottinghamshire; died 22 November 1882 at Heaton Norris, Cheshire) was an English cricketer who played first-class cricket from 1836 to 1843."))
print(test.getEntities("Charles Creswell (born 10 March 1813 at Radford, Nottinghamshire; died 22 November 1882 at Heaton Norris, Cheshire) was an English cricketer who played first-class cricket from 1836 to 1843."))
print(test.subjectObjectExtraction("Charles Creswell (born 10 March 1813 at Radford, Nottinghamshire; died 22 November 1882 at Heaton Norris, Cheshire) was an English cricketer who played first-class cricket from 1836 to 1843."))



#For debug purposes
#test.normalizeDocuments("positive_examples_institution.txt")
