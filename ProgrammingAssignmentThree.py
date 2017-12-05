import json #used to decode the JSON files and fetch the data
import urllib.request as urllib #used for Google Knowledge Graph
import ast
from demjson import decode

class ProgrammingAssignmentThree():

    file = None #JSON file to read from
    rawData = [] #JSON raw data
    positiveExamples = [] #Keep in this list just the positive examples
    negativeExamples = [] #Keep in this list just the negative examples
    positiveElementsResolved = [] #No more ids
    negativeElementsResolved = [] #No more ids
    positiveAndNegativeExamples = {} #Keep in this dictionary positive and negative examples, {JSON OBJECT:"yes"}, {JSON OBJECT: "no"}

    """
    Constructor
    1) Reads a JSON file from an indicated file path and takes its' content into :var file
    2) Decodes the JSON file and saves its' content to :var rawData
    """
    def __init__(self, filePath=""):

        self.file = open(filePath, "r", encoding="utf-8")
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

        writePositiveExamples = open("positive_example2.txt", "a", encoding="utf-8")
        #writeNegativeExamples = open("negative_example_place.txt", "a", encoding="utf-8")

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
            writePositiveExamples.write(str(element))
        print(self.positiveExamples)

        # for element in self.positiveExamples:
        #     writePositiveExamples.write(str(element))

        # for element in self.negativeExamples:
        #     subjectId = element['sub']
        #     objectId = element['obj']
        #
        #     #print(subjectId, objectId)
        #     try:
        #         subjectName = self.queryGoogleKnowledgeGraph(subjectId)
        #         objectName = self.queryGoogleKnowledgeGraph(objectId)
        #     except Exception as e:
        #         self.negativeExamples.remove(element)
        #         print("An error occured while resolving ids: " + str(subjectId) + ", "+str(objectId)+". From the following element: "+str(element)+"\n")
        #         print("As a consequence, the element will be remove from the examples list")
        #
        #     if(subjectName != ""):
        #         element['sub'] = subjectName
        #     else:
        #         print("Because the subject wasn't found in the google knowledge graph, the element will be removed from the list")
        #         try:
        #             self.negativeExamples.remove(element)
        #         except:
        #             pass
        #     if(objectName != ""):
        #         element['obj'] = objectName
        #     else:
        #         print("Because the subject wasn't found in the google knowledge graph, the element will be removed from the list")
        #         try:
        #             self.negativeExamples.remove(element)
        #         except:
        #             pass
        #print(self.negativeExamples)

        #for element in self.negativeExamples:
            #writeNegativeExamples.write(str(element))

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
    """
    def reviewTheSet(self, path):

        readFile = open(str(path), "r", encoding="utf-8")
        #writeFile = open("CorrectedSet.json", "a", encoding="utf-8")

        i=0
        for element in readFile:
            if(i<100):
                list = decode(element, encoding="utf-8")
                if((list['sub'] in list['evidences'][0]['snippet']) and (list['obj'] in list['evidences'][0]['snippet'])):
                    #print(list['evidences'][0]['snippet'])
                    new_element = json.dumps(list)
                    print(new_element)
                else:
                    #new_element = json.dumps(list)
                    #print(new_element)
                    pass

                i += 1
            else:
                break




test = ProgrammingAssignmentThree("20130403-institution.json")
#test.queryGoogleKnowledgeGraph("/m/02v_brk")
#test.sortExamples()
#test.idToName()
test.reviewTheSet("positive_example2_nornalized.json")


#For debug purposes
#test.normalizeDocuments("positive_example2.txt")
