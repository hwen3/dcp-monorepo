import sys
import csv
import json
import os
import re
from datetime import datetime
import getpass

configFileVersion = ''
FldArg = ''

try:
    if len(sys.argv) > 3:
        raise Exception('Too many parameters')    
    if len(sys.argv) > 1:
        DevProdArg = sys.argv[1].upper()
    else:
        DevProdArg = ''

    if len(sys.argv) > 2:  
        try:
            t = int(sys.argv[2] )    
            configFileVersion = sys.argv[2]
        except:
            FldArg = sys.argv[2]   

    if len(DevProdArg) > 1:
        raise Exception('use either P or D')
except Exception as inst:
    print( inst)
    print( "Usage: python csv2json.py <[P,D]> <output path>")
    sys.exit(1)


ProductionData = False     # <<<======== IMPORTANT - Default ===============
if (DevProdArg != ''):
    ProductionData = DevProdArg == 'P'

outputDirData = []
outputDirFields = ['..\\..\\..\\..\\..\\ReactJS\\list\\build\\','..\\..\\..\\..\\..\\ReactJS\\list\public\\'                         ]
outputDirConfig = ['..\\src\pages\\details\\']
configFileVerDir = '..\\..\\..\\..\\'

if ProductionData:
    CSV_fileNames = ['CommonCapabilities']
    outputDirData = ['..\\src\\content\\','.\\']

else:
    CSV_fileNames = ['CommonCapabilities','CommonCapabilitiesSamples']
    outputDirData = ['..\\..\\..\\..\\..\\ReactJS\\list\\build\\',
                         '..\\..\\..\\..\\..\\ReactJS\\list\public\\',
                         '.\\','..\\src\\content\\']          

CSV_fileDir = '.\\'
fldArray = 'data','common-capabilities','apps', ''   # need the '' for for loop
tmp = ''
foundPath = ''

fieldsFile = '\CommonCapabilitiesFields'
for addThis in fldArray:
    if configFileVersion != '':
        fieldsFile = fieldsFile + '@' + configFileVersion
    if os.path.exists('.'+ tmp + fieldsFile + '.csv' ):        
        foundPath = '.'+ tmp + '\\'
        break
    tmp = '\\' + addThis + tmp

if foundPath == '':
    print('\n-----------------\nCould not find files\n----------------\n')
    sys.exit()

fieldsFile = fieldsFile + '.csv'
print(fieldsFile)

outputDirData = [foundPath + string for string in outputDirData]
CSV_fileDir = foundPath

if (FldArg != ''):
    if FldArg[-1] != '\\':
        FldArg += '\\'    
    outputDirData = [FldArg]

haveOutput = False
for folderName in outputDirData:
    if os.path.exists(folderName):
        haveOutput = True
        break
if not haveOutput:
    print('\n-----------------\nCould not find output folder:', outputDirData )
    sys.exit()


# Finished checks, I've got everything I need to continue...

#=================================================
from functions import replace_special_characters,replace_Bool,linkList,asArray,asLineArray,createContact,createSecurityList,create_roadmap
#=================================================


fieldMetadata = []
# LookUpData = []
with open(CSV_fileDir + fieldsFile, 'r', encoding='utf-8-sig') as csvfile:
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:        
        row = {key: replace_special_characters(value) for key, value in row.items()}
        row = {key: replace_Bool(value) for key, value in row.items()}       
        if row["fieldName"] != "":
            del row["extra"]
            if row["type"] == "Field":                               
                del row["type"]                

                fieldMetadata.append(row)
data = []
id_counter = 0
if not ProductionData: devMode = 'DEVELOPMENT'
else: devMode = 'Production'  
print('\n------[ Create JSON files for: ' + devMode + ' ]---------\n Working directory: '
      + CSV_fileDir +'\nInput: ' + fieldsFile)


SecurityFields = [item for item in fieldMetadata if item['group'][:8] == 'Security']

for fileName in CSV_fileNames:    
    if os.path.exists(CSV_fileDir + fileName + '.csv'):
        print('Input: '+ fileName + '.csv')   
        with open(CSV_fileDir + fileName + '.csv', 'r', encoding='utf-8-sig') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                csv_row = {key: replace_special_characters(value) for key, value in row.items()}

                if csv_row["serviceName"] != "" and csv_row["provider"] != "" :
                    QA_Contact = 30 if csv_row["altContactLink"] == '' and csv_row["email"] == "" else 0
                    QA_Doc = 20 if csv_row["documentation"] == "" and (csv_row["status"] != "Alpha" or QA_Contact > 0) else 0
                    QA_FGroup = 1 if csv_row["functionalGroup"] == "Other Function" else 0
                    QA_Status = 2 if csv_row["status"] == "" else 0
                    QA_Lang   = 2 if csv_row["language"] == "" else 0
                    QA_Env    = 2 if csv_row["environment"] == "" else 0    
                    QA_Misc   = 12 if csv_row["dataIssues"] != "" else 0    
                    # csv_row["QA"] = QA_Contact + QA_Doc + QA_FGroup + QA_Status + QA_Lang + QA_Env + QA_Misc

                    filterText = ''
                    securityBadge = ''

                    for row2 in [item for item in fieldMetadata if item["filter"] != '' 
                                 and item["filter"] != 'No' 
                                 and item["dataType"] != "int" 
                                 and csv_row[item["fieldName"]] != '']:
                        filterText += ',' + csv_row[row2["fieldName"]].strip()
                    csv_row["filterText"] = filterText[1:].lower().strip()

                    for row2 in [item for item in fieldMetadata if item["default"] != '' and csv_row[item["fieldName"]] == '']:                        
                        csv_row[row2["fieldName"]] = row2["default"]

                    for row2 in fieldMetadata:
                        if row2["filter"] != '':
                            fn = row2["fieldName"]   # int, text, textArray, urlArray, contactList

                            if   row2["dataType"] == "urlArray":
                                csv_row[fn] = linkList(csv_row[fn])

                            elif row2["dataType"] == "lineArray":
                                csv_row[fn] = asLineArray(csv_row[fn])

                            elif row2["dataType"] == "textArray":
                                csv_row[fn] = asArray(csv_row[fn])

                            elif row2["dataType"][:9] == "Contacts(":
                                csv_row["contact"] = createContact(csv_row)
                            
                            elif row2["dataType"][:9] == "Security(":
                                csv_row["security"] = createSecurityList(csv_row,row2["dataType"][9:-1],SecurityFields)

                            elif row2["dataType"] == "int":                            
                                csv_row[fn] = int(csv_row[fn])               
                    
                    if len(csv_row["summary"]) > 200:
                        print('Summay too long: ' + csv_row["ServiceName"] + ' = ' + str(len(csv_row["Summary"])) )
                  
                    if csv_row["altServiceName"] != "":
                        csv_row["serviceName"] = csv_row["altServiceName"]

                    if csv_row["description"] == "":
                        csv_row["description"] = csv_row["summary"]
                    
                    csv_row["roadmap"] = create_roadmap(csv_row["timeline"] ,csv_row["timelineEvent"])
                    csv_row["recommended"] = int(csv_row["internalWeightage"]) >= 50
                    csv_row["editorName"] = ""
                    csv_row["editorEmail"] = ""                                     

                    if int(csv_row["internalWeightage"]) >= 0 or not ProductionData:
                        for delKey in ["dateAdded","lastUpdated","timeline","timelineEvent","email","phone","contactDetails","altContactMethod","altContactLink","nominate","altServiceName"]:
                            if delKey in csv_row:
                                del csv_row[delKey]

                        if ProductionData: 
                            for delKey in ["internalWeightage","dataIssues","reviewed","reviewedBy"]:
                                if delKey in csv_row:
                                    del csv_row[delKey]
                                                        
                        # for delKey in [item['fieldName'] for item in SecurityFields if item['subGroup'] != '']:
                        #     if delKey in csv_row:
                        #         del csv_row[delKey]  

                        id_counter += 1
                        csv_row["appId"] = id_counter
                       
                        data.append(csv_row)


# # ***************** Vote on filter text *********************                     
modifiedRecords = []
# #spellingVote(data,fieldMetadata)
# wordCounts = {}
# needEdit = {}
# def shorten(text): return re.sub('[._ -\\/]', '', text).lower().strip()
# def wordVote(val):
#     if val in wordCounts:        wordCounts[val] += 1
#     else:        wordCounts[val] = 1

# def needsEdit(val):
#     short = shorten(val)
#     if short != '' and short in needEdit and needEdit[short] != val:
#         return needEdit[short]
#     else:
#         return {}
# # ******    
# for row2 in fieldMetadata:
#     fn = row2["fieldName"]
#     if row2["filter"] != 'No' and row2["dataType"] != 'List' and row2["filter"] != '':
#         for dataRow in data:
#             if row2["dataType"] == 'text':
#                 if dataRow[fn] != '':                   
#                     wordVote(dataRow[fn])
#             elif row2["dataType"] == 'textArray':                    
#                     for val in dataRow[fn]:
#                         wordVote(val)
# string_counts_with_group = [{'string': key, 'count': value, 'group': shorten(key)} for key, value in wordCounts.items()]
# groups = set(item['group'] for item in string_counts_with_group)
# # def items_by_group(group): return [item for item in string_counts_with_group if item['group'] == group]

# for grp in groups:    
#     itemGroup = [item for item in string_counts_with_group if item['group'] == grp] # items_group_A = items_by_group(grp)
#     if len(itemGroup) > 1:        
#         gstr = ''
#         cnt = 0
#         grp = itemGroup[0]['group']
#         for item in itemGroup:
#             if item['count'] > cnt:
#                 cnt = item['count']
#                 gstr = item['string']
#         needEdit[grp] = gstr
        
# for row2 in fieldMetadata:
#     fn = row2["fieldName"]
#     if row2["filter"] != 'No' and row2["filter"] != '':
#         for dataRow in data:
#             if row2["dataType"] == 'text':
#                 updated = needsEdit(dataRow[fn])
#                 if updated:
#                     modifiedRecords.append([dataRow['ServiceName'],fn,dataRow[fn],updated])
#                     dataRow[fn] = updated

#             elif row2["dataType"] == 'textArray':
#                     for val in dataRow[fn]:
#                         updated = needsEdit(val)
#                         if updated:
#                             i = dataRow[fn].index(val)
#                             modifiedRecords.append([dataRow['ServiceName'],fn,dataRow[fn][i],updated])                            
#                             dataRow[fn][i] = updated
# # ***************** END - Vote on filter text *********************

######################################
updated_data = [row for row in fieldMetadata if row.get("Group") != "functionalGroup"] 
for row in updated_data:
    for delKey in ["filter","default"]:  # "showBadge"
        del row[delKey]

for item in updated_data:
    item["property"] = item["fieldName"]
    item["title"] = item["display"]
    del item["fieldName"]
    del item["display"]

securityFields = [item for item in updated_data if item['group'] == 'Security']

######################################

folderName = outputDirConfig[0]
exportList = ''
with open(folderName + 'config.ts', 'w') as configfile:
    print('Output: ' + folderName + 'config.ts')
    securityGroupList = []
    for item in [item for item in securityFields if item['subGroup'] == '']:
        itemList = []
        for item in [item2 for item2 in securityFields if item2['subGroup'] == item['property'][8:] ]:
            itemList.append(item['property'])

        th = []
        text = ' '+ item['title']
        for match in re.findall(r'([^()]+)\((.*?)\)', text):
            text_before, inside_parentheses = match        
            text = text_before.strip()
            th = [part.strip() for part in inside_parentheses.split(',')]        
        securityGroupList.append({ "name": item['property']
                                  , "dataSecurityType": item['property'][8:]
                                  , "title": text
                                  , 'items': itemList 
                                  , "tableTh": th
                                  , 'note': item['note']
                                #   , 'fieldList': item['property'][:1].lower() + item['property'][1:]
                                #   , 'id': item['property'].lower()
                                  })
    configfile.write('export const securityGroups = ')      
    configfile.write(json.dumps(securityGroupList, indent=4))    
    exportList += ', securityGroups'

    #################
    securityData = {}
    # for item in [item for item in securityFields if item['subGroup'] != '']:        
    for item in [item for item in securityFields]:
        securityData[item['property']] = {"title": item['title'] }  # , 'id': item['property'].lower()

    configfile.write('\n\n\nexport const securityData = ')      
    configfile.write(json.dumps(securityData, indent=4))    
    exportList += ', securityData'

    items = {}
    for item in [item for item in updated_data if item['group'] == 'Spec']:
        items[item['property']] = {"title": item['title'], 'type': item['dataType'] }  # ,  'id': 'body-'+item['property'].lower()                
    configfile.write('\n\nexport const specifications = ')      
    configfile.write(json.dumps(items, indent=4))             
    exportList += ', specifications'

    items = {}
    for item in [item for item in updated_data if item['group'] == 'Body']:
        items[item['property']] = {"title": item['title'], 'dataIn': item['dataIn'] }  # , 'type': item['dataType'],  'id': 'body-'+item['property'].lower()        
    configfile.write('\n\nexport const bodyItems = ')      
    configfile.write(json.dumps(items, indent=4))             
    exportList += ', bodyItems'

    configfile.write('\n\n\n // import {' + exportList[2:] + '} from \'./config\' ')
  
    ##################################################################################################


# currently not using Security in final data. Maybe in the future. However it was used to build the config file
for row in data:
    for delKey in ["security"]:
        del row[delKey]

# ************** Output data *************************

now = datetime.now() 
current_date = now.strftime("%m/%d/%Y, %H:%M")

data2 = {"lastUpdated": current_date
         ,"isProductionData": ProductionData         
         ,"dateFormat": "mm/dd/yyyy"
         ,"services": data
        }

# Now output to: outputDirData , outputDirFields, outputDirConfig

for folderName in outputDirData:
    if os.path.exists(folderName):
        print('Output: ' + folderName +  'datastore.json')
        with open(folderName +  'datastore.json', 'w') as jsonfile:
            jsonfile.write(json.dumps(data2, indent=4))

for folderName in outputDirFields:
    if os.path.exists(folderName):       
        print('Output: ' + folderName +  'datafields.json')
        with open(folderName + 'datafields.json', 'w') as jsonfile:
           jsonfile.write(json.dumps(fieldMetadata, indent=4))

# ****************** finished with data ***************


if len(modifiedRecords) > 0:
    modifiedRecords.sort()
    with open(CSV_fileDir + 'modifiedRecords.txt', 'w') as file:
        for item in modifiedRecords:
            file.write("%s\n" % item)
    print('AutoFix: '+CSV_fileDir+'modifiedRecords.txt contains '+str(len(modifiedRecords))+' modified records')

if not ProductionData:
    print('DEVELOPMENT mode = Hidden records have been included in the dataset' )

print('------- '+ str(id_counter) + ' total records -------------\n')