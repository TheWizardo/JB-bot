# -*- coding: utf-8 -*-
# Helpers

from telegram import KeyboardButton

import datetime
import pickle
import httplib2
from apiclient import discovery
from quickstart_cal import unicodeToStr, unicodeToInt
from quickstart_drv import download_file_from_google_drive, get_creds, getFolders
import difflib
from bot_init import *


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def Save_Newbies():
    global newbies
    newbi = open("newbies.txt", 'w')
    newbi.close()
    pickle.dump(newbies, open("newbies.txt", 'w'))


def Save_Nameies():
    global nameies
    namei = open("nameies.txt", 'w')
    namei.close()
    pickle.dump(nameies, open("nameies.txt", 'w'))


def Save_Editors():
    global editing
    edits = open("editors.txt", 'w')
    edits.close()
    pickle.dump(editing, open("editors.txt", 'w'))


def Save_Activitors():
    global activitors
    acts = open("activitors.txt", 'w')
    acts.close()
    pickle.dump(activitors, open("activitors.txt", 'w'))


def get_full_name(update):
    try:
        name = update.message.from_user.first_name + " " + update.message.from_user.last_name
        return name
    except Exception:
        name = update.message.from_user.first_name
        return name


def IsDev(idnum):
    global JB_names
    for jb in JB_names:
        if jb.ID == idnum:
            if "dev" in jb.Roles or "communication" in jb.Roles:
                return True
    return False


def InFile(bot, update):
    found = False
    for Jber in JB_names:
        usr_id = 0
        if Jber.ID != 0:
            try:
                if Jber.ID == int(update.message.from_user.id):
                    found = True
                    break
            except Exception:
                if Jber.ID == int(update.message.chat_id):
                    found = True
                    break
    if not found:
        try:
            txt = "I got a message from an unknown user.\n{}'s id is {} and the message was sent in a {} chat.\nthe message is: '{}'".format(get_full_name(update), update.message.from_user.id, str(update.message.chat.type), update.message.text)
        except Exception:
            txt = "I don’t know how to interpert this update:\n{}".format(str(update))
        bot.send_message(chat_id=Oz_id,text=txt)
        return False
    return True


def compare(str1, str2):
    difference = difflib.SequenceMatcher()

    difference.set_seqs(str1, str2)

    for match in difference.get_matching_blocks():
        return str1[match[0]:match[0] + match[2]]


def format_event(raw_event): #(startDate)T(startTime)+(UTC)>(endDate)T(endTime)+(UTC) (name)
    event = raw_event.split(" ")
    eventDateTime = event[0]
    eventName = ""
    
    for i in range(1, len(event)):
        eventName += event[i] + " "
    if len(eventName) > 0:
        eventName = eventName[:-1]
        
    datetime_arr = eventDateTime.split(">")
    startTime = datetime_arr[0].split("T")
    endTime = datetime_arr[1].split("T")
    raw_sDate = startTime[0]
    if len(startTime) == 1:
        raw_sTime = ""
    else:
        raw_sTime = startTime[1]

    raw_eDate = endTime[0]    
    if len(endTime) == 1:
        raw_eTime = ""
    else:
        raw_eTime = endTime[1]
        
    strSDate = unicodeToStr(raw_sDate)
    strEDate = unicodeToStr(raw_eDate)
    sDate = strSDate.split("-")
    eventSDate = ("{}/{}/{}").format(sDate[2], sDate[1], sDate[0])
    eDate = strEDate.split("-")
    if raw_eTime != "":
        eventEDate = ("{}/{}/{}").format(eDate[2], eDate[1], eDate[0])
    else:
        real_date = datetime.datetime(int(eDate[0]), int(eDate[1]), int(eDate[2])) + datetime.timedelta(days=-1)
        eventEDate = ("{}/{}/{}").format(real_date.day, real_date.month, real_date.year)

    eventDate = eventSDate
    if eventSDate == eventEDate:
        if raw_sTime == "":
            finalTime = ""
        else:
            sTime = raw_sTime.split("+")[0]
            eTime = raw_eTime.split("+")[0]
            sTime = sTime[:5]
            eTime = eTime[:5]
            finalTime = sTime + " until " + eTime
        eventTime = unicodeToStr(finalTime)
    else:
        if raw_sTime == "":
            eventDate = eventSDate + " until " + eventEDate
            finalTime = ""
        else:
            sTime = raw_sTime.split("+")[0]
            eTime = raw_eTime.split("+")[0]
            sTime = sTime[:5]
            eTime = eTime[:5]
            finalTime = sTime + " until " + eventEDate + " at " + eTime
        eventTime = unicodeToStr(finalTime)
    return eventName, eventDate, eventTime


def get_lyrics(File, folder):
    global folders
    File += ".txt"
    to_send = True
    if not os.path.exists(work_dir + folder + "\\" + File):
        if File in folders[folder]:
            download_file_from_google_drive(folders[folder][File]["file_id"], work_dir + folder + "\\" + File)
        else:
            to_send = False
    if to_send:
        ffile = open(work_dir + folder + "\\" + File, "r")
        lyrics = ffile.read()
        ffile.close()
        return lyrics


def get_pic(bot, chat, jbname):
    credentials = get_creds()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    results = service.files().list(fields="nextPageToken, files(id, name)")

    items = results.get('files', [])
    jbname += ".jpg"
    if items:
        for item in items:
            if str(item['name']) == jbname:
                bot.send_photo(chat_id=chat, photo='https://drive.google.com/file/d/{}/view?usp=sharing'.format(item['id']))
                return


def get_input(message):
    msg = message[1]
    for index in range(2, len(message)):
        if index < len(message):
            msg += " " + message[index]
    return msg


def acts_by_tags(grd, tags_arr):
    global folders

    if "End" in tags_arr:
        tags_arr.remove("End")
    acts = {}
    for key in folders[u'activities']:
        if grd in folders[u'activities'][key]["tags"] or grd == "All": #check if the grade is what the user wants
            to_add = True
            for t in tags_arr: #check if all the tags the user chose, exists as tags of the file
                if not (t in folders[u'activities'][key]["tags"]):
                    to_add = False
                    break
            if to_add:
                acts[key] = folders[u'activities'][key]["file_id"]
    tags_arr.append("End")
    return acts


def add_to_file(jb):
    if os.path.exists("JB.csv"):
        EN_name = str(jb.En_Name)
        HE_name = str(jb.He_Name.encode('utf-8'))
        phone = str(jb.Phone[1:len(jb.Phone)])
        role = ""
        for r in jb.Roles:
            role += r + ", "
        role = role[0:len(role) - 2]
        bday = str(jb.Birthday.replace("-", "_"))
        text = chr(10)+"{},{},{},{},{},{}".format(EN_name, HE_name, phone, role, bday, str(jb.ID))
        with open("JB.csv", "a") as csvf:
            csvf.write(text)
            csvf.close()
        return
    elif os.path.exists("JB.txt"):
        role = ""
        for r in jb.Roles:
            role += r + ", "
        role = role[0:len(role) - 2]
        text = chr(10)+"{}/{}/{}/{}/{}/{}".format(jb.En_name, jb.He_Name.encode("utf-8"), jb.Phone, role, jb.Birthday, str(jb.ID))
        with open("JB.txt", "a") as txtf:
            txtf.write(text)
            txtf.close()
        return


def Check_Format(text):
    special = "*_"
    new_text = text
    for char in special:
        No = 0
        start = new_text.find(char)
        last = -1
        while start >= 0:
            No += 1
            last = start
            start = new_text.find(char, last + 1)
        if No % 2 == 1 and last != -1: 
            new_text = new_text[:last] + "\\" + new_text[last:]
    No = 0
    start = new_text.find("```")
    last = -1
    while start >= 0:
        No += 1
        last = start
        start = new_text.find("```", last + 1)
    if No % 2 == 1 and last != -1: 
        new_text = new_text[:last] + "\\" + new_text[last:last + 1]  + "\\" + new_text[last + 1:last + 2] + "\\" + new_text[last + 2:last + 3]
    return new_text


def get_keyboard(arr, col=1):
    index = 0
    keyboard = []
    for i in range(int(len(arr)/col)):
        row = []
        for c in range(col):
            row.append(KeyboardButton(arr[i*col + c]))
        keyboard.append(row)
        index += col
        
    row = []
    for j in range(len(arr) - index):
        row.append(KeyboardButton(arr[index + j]))
    if len(row) > 0:
        keyboard.append(row)
    return keyboard


def Get_JB_by_id(num):
    for Jber in JB_names:
        if Jber.ID != 0:
            if Jber.ID == num:
                return Jber
