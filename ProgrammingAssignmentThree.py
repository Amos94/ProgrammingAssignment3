import json #used to decode the JSON files and fetch the data

class ProgrammingAssignmentThree():

    file = None #JSON file to read from
    rawData = [] #JSON raw data

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




test = ProgrammingAssignmentThree("20130403-institution.json")
