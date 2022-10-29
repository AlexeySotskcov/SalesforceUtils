import xml.etree.ElementTree as ET

from xml.etree.ElementTree import Element, SubElement
from operator import attrgetter


def getList(dict):
    list = []
    for key in dict.keys():
        list.append(key)

    return list

def getElementsDict(root):
    profileMetaTypes = ['applicationVisibilities', 'categoryGroupVisibilities', 'classAccesses',
        'customMetadataTypeAccesses', 'customPermissions', 'customSettingAccesses', 'externalDataSourceAccesses',
        'fieldPermissions', 'flowAccesses', 'layoutAssignments', 'loginFlows', 'loginHours', 'loginIpRanges',
        'objectPermissions', 'pageAccesses', 'profileActionOverrides', 'recordTypeVisibilities', 'tabVisibilities',
        'userPermissions']

    itemsDict = {}

    for meta in profileMetaTypes:
        matchExp = './' + meta
        itemsDict[meta] = root.findall(matchExp)

    return itemsDict


def sortElementsByTag(itemsDict):
    for parent in itemsDict:
        isReversed = parent == 'loginHours'
        itemsDict[parent][:] = sorted(itemsDict[parent], key=lambda child: child.tag, reverse=isReversed)

def sortElementsByMetaElementValue(itemsDict):
    nameTag = ['customMetadataTypeAccesses', 'customSettingAccesses', 'customPermissions', 'customMetadataTypeAccesses', 'userPermissions']
    tagValue = './'
    for parent in itemsDict:
        if parent in nameTag:
            tagValue = 'name'
        elif parent == 'recordTypeVisibilities':
            tagValue = 'recordType'
        elif parent == 'applicationVisibilities':
            tagValue = 'application'
        elif parent == 'categoryGroupVisibilities':
            tagValue = 'dataCategoryGroup'
        elif parent == 'classAccesses':
            tagValue = 'apexClass'
        elif parent == 'externalDataSourceAccesses':
            tagValue = 'externalDataSource'
        elif parent == 'fieldPermissions':
            tagValue = 'field'
        elif parent == 'flowAccesses':
            tagValue = 'flow'
        elif parent == 'layoutAssignments':
            tagValue = 'layout'
        elif parent == 'loginFlows':
            tagValue = 'friendlyname'
        elif parent == 'loginIpRanges':
            tagValue = 'startAddress'
        elif parent == 'objectPermissions':
            tagValue = 'object'
        elif parent == 'pageAccesses':
            tagValue = 'apexPage'
        elif parent == 'profileActionOverrides':
            tagValue = 'pageOrSobjectType'
        elif parent == 'tabVisibilities':
            tagValue = 'tab'

        if tagValue != './' and len(itemsDict[parent]) > 0:
            itemsDict[parent][:] = sorted(itemsDict[parent], key=lambda child: child.find(tagValue).text)

def normalize(path):

    tree = ET.parse(path)
    root = tree.getroot()
    stripNs(root)

    itemsDict = getElementsDict(root)
    sortElementsByTag(itemsDict)
    sortElementsByMetaElementValue(itemsDict)


    for meta in itemsDict:
        for el in itemsDict[meta]:
            root.remove(el)
            root.insert(-1,el)

    root[:] = sorted(root, key=lambda child: child.tag)

    spaceType = '    '
    ET.indent(tree, space=spaceType, level=0)
    root.attrib["xmlns"] = "http://soap.sforce.com/2006/04/metadata"
    out = open(path, 'wb')
    out.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')

    tree.write(out, encoding = 'UTF-8', xml_declaration = False)
    print('processed')

def main(path, isEditable, isReadable, isRemove, fieldsForUpdate):
    tree = ET.parse(path)
    root = tree.getroot()

    stripNs(root)

    profileData = root.findall("./fieldPermissions")
    profileFields = []
    for fieldName in profileData:
        profileFields.append(fieldName.find('field').text)

    for field in fieldsForUpdate:
        if field in profileFields:

            for fieldPermission in root.findall("./fieldPermissions"):
                if fieldPermission.find('field').text == field:
                    if isRemove:
                        root.remove(fieldPermission)
                    else:
                        for param in fieldPermission:
                            if param.tag == 'editable':
                                param.text = str(isEditable)
                            if param.tag == 'readable':
                                param.text = str(isReadable)
        else:
            if isRemove == False:
                profileFields.append(field)
                child = createChild(field, isEditable, isReadable)
                pos = 0 if len(profileData) == 0 else list(root).index(profileData[-1])+1 ;
                root.insert(pos,child)

    for node in root.findall("*"):
        node[:] = sorted(node, key=attrgetter("tag"))


    spaceType = '    '
    ET.indent(tree, space=spaceType, level=0)
    root.attrib["xmlns"] = "http://soap.sforce.com/2006/04/metadata"
    out = open(path, 'wb')
    out.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')

    print(tree)
    tree.write(out, encoding = 'UTF-8', xml_declaration = False)
    out.close()
    print('File:', path, 'has been processed')


def stripNs(el):
    '''Recursively search this element tree, removing namespaces.'''
    if el.tag.startswith("{"):
        el.tag = el.tag.split('}', 1)[1]
    for k in el.attrib.keys():
        if k.startswith("{"):
            k2 = k.split('}', 1)[1]
            el.attrib[k2] = el.attrib[k]
            del el.attrib[k]
    for child in el:
        stripNs(child)

def createChild(field, isEditable, isReadable):
    child = Element('fieldPermissions')
    editChild = SubElement(child,("editable"))
    editChild.text = str(isEditable)
    nameChild = SubElement(child,("field"))
    nameChild.text = field
    readChild = SubElement(child,("readable"))
    readChild.text = str(isReadable)
    return child
