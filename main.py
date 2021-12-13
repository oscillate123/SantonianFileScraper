import requests
import json
import re
import sys
import logging
import pprint

_disklist_uri = 'https://santonianindustries.com/backend/hdd'
_diskdetails_uri = 'https://santonianindustries.com/backend/hdd_details'
_filelist_uri = 'https://santonianindustries.com/backend/file'
_readfile_uri = 'https://santonianindustries.com/backend/readFile'

_log = ".LOG"
_audio = ".AUD"
_delimiter = f"{'-'*25}"

# 1
def getDiskList(uri):
    return requests.get(uri)

# 2
def getDiskInfo(uri, disk):
    return requests.get(f"{uri}/{disk}")

# 3
def getDiskFileList(uri, file_id):
    return requests.get(f"{uri}/{file_id}")

# 4
def getFileInformation(uri, filename):
    return requests.get(f"{uri}/{filename}")

def dataSerialization(str, remove_list):
    return str.translate({ord(i): None for i in remove_list})

def getDateFromFile(file):
    # (?:Date:(\s*(.*)))
    # (\w+ ([0-9](st|rd)) [0-9]{4})
    # (?=Date:\s*(.*))
    date = re.search(r'/(?=Date:\s*(.*))/g', file)

    if date:
        return date
    else:
        return None

def getArchiveInfo(disk, _debug):
    # get archive info
    disk_info = json.loads(getDiskInfo(_diskdetails_uri, disk).text)
    if _debug:
        print(f"Backend Disk: {disk_info}\n")
    
    return disk_info

def categorizeAllFiles(disk_file_list, _debug):
    _log_list = []
    _audio_list = []

    # list files
    if len(disk_file_list) > 1:
        if _debug:
            print(f"___ FILES ___")
            print(f"INDEX - FILE")

        # add file to its type list
        for file_idx, file in enumerate(disk_file_list):
            if file.endswith(_log):
                _log_list.append(file)
            elif file.endswith(_audio):
                _audio_list.append(file)

        # display logs
        if len(_log_list):
            if _debug:
                print("\nLogs")
            for xidx, log in enumerate(_log_list):
                if _debug:
                    print(f"{xidx} - {log}")

        # display audios
        if len(_audio_list):
            if _debug:
                print("\nAudios")
            for yidx, audio in enumerate(_audio_list):
                if _debug:
                    print(f"{yidx} - {audio}")

    return [_log_list, _audio_list]
 
def getAllDisksAndFiles(disk_list, _debug=True):
    # retrieve all archives
    disk_list = getDiskList(_disklist_uri)

    # store all archives and files in json database
    _files = {}

    # iterate each archive
    for idx, disk in enumerate(disk_list.json()):
        _files[disk] = {}

        if _debug:
            print(f"\n{_delimiter}\n{idx} - {disk}\n")
        
        disk_info = getArchiveInfo(disk, _debug)
        _files[disk]['info'] = disk_info

        # get files from archive
        disk_file_list = getDiskFileList(_filelist_uri, disk_info['message'][0]).json()

        _files[disk]['files'] = disk_file_list

        categorized = categorizeAllFiles(disk_file_list, _debug)        

        _files[disk]['Logs'] = categorized[0]
        _files[disk]['Audios'] = categorized[1]

    writeToDatabase(_files)

def writeToDatabase(dict):
    if type(dict) != "dict":
        with open('db.json', 'w') as db:
            json.dump(dict, db)

def checkIfDatabaseEmpty(file):
    with open(file,'r',encoding='utf-8') as r:
        try:
            j = json.load(r)
        except:
            r.seek(0)
            j = json.loads('['+r.read().replace('}{','},{')+']')[0]

    return j


if __name__ == '__main__':

    # _log = ".LOG"
    # _audio = ".AUD"
    # _delimiter = f"{'-'*25}"

    pp = pprint.PrettyPrinter(indent=4)

    try:

        #_files = getAllDisksAndFiles()
        _files = checkIfDatabaseEmpty('db.json')
        pp.pprint(_files)

    except Exception as E:
        print(E)
