# -*- coding: utf-8 -*-
# Bot

from JBer import *
from quickstart_drv import getFolders, download_file_from_google_drive
import datetime
import csv
import os.path
import os
import pickle

work_dir = os.getcwd() + "\\"
grades_arr = ["fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "JA", "JB!!!"]

JB_names = []
folders = {}
energizers = []
lullaby = []
tags = []
grades = []
activitors = {}
editing = {}
newbies = {}
nameies = {}

def Get_Newbies(): #{_id_:{"JBer":JB(_enName_,_heName_,_phone_,_role_,_bday_,_id_), "stage":_stage_}}
    newbies = {}
    if os.path.exists("newbies.txt"):
        with open("newbies.txt", 'r') as newb:
            text = newb.read().decode('utf8')
            newb.close()
        if len(text) > 2:
            newbies = pickle.load(open("newbies.txt", 'r'))
    return newbies


def Get_Nameies(): #{_id_:_letter_}
    nameies = {}
    if os.path.exists("nameies.txt"):
        with open("nameies.txt", 'r') as nam:
            text = nam.read().decode('utf8')
            nam.close()
        if len(text) > 2:
            nameies = pickle.load(open("nameies.txt", 'r'))
    return nameies


def Get_Editors(): #{_id_:{"JBer":JB(_enName_,_heName_,_phone_,_role_,_bday_,_id_), "field":_parameter_, "change":_change_}}
    edits = {}
    if os.path.exists("editors.txt"):
        with open("editors.txt", 'r') as edit:
            text = edit.read()
            edit.close()
        if len(text) > 2:
            edits = pickle.load(open("editors.txt", 'r'))
    return edits


def Get_Activitors(): #{_id_:{"grade":_grade_, "tags":[_tags_], "messageID":_messageId_, "files":{_fileName_:_fileID_}}}
    acts = {}
    if os.path.exists("activitors.txt"):
        with open("activitors.txt", 'r') as act:
            text = act.read()
            act.close()
        if len(text) > 2:
            acts = pickle.load(open("activitors.txt", 'r'))
    return acts


def Get_Contacts():
    jb_arr = []
    if os.path.exists(work_dir + "\\JB.csv"):
        print "Reading CSV"
        with open("JB.csv","rb") as csvf:
            dialect = csv.Sniffer().sniff(csvf.read())
            csvf.seek(0)
            reader = csv.reader(csvf, dialect)
            for jber in reader:
                if jber != []:
                    jber_roles = []
                    for r in jber[3].split("$"):
                        jber_roles.append(r)
                    uid = 0
                    try:
                        uid = int(jber[5])
                    except Exception, e:
                        pass
                    try:
                        jb_arr.append(JBer(English_Name=jber[0],Hebrew_Name=jber[1].decode("hebrew").encode("utf8"),Phone_Number="+"+jber[2],Roles=jber_roles,Birthdate=jber[4].replace("_","-"),ID=uid))
                    except Exception:
                        jb_arr.append(JBer(English_Name=jber[0],Hebrew_Name=jber[1],Phone_Number="+"+jber[2],Roles=jber_roles,Birthdate=jber[4].replace("_","-"),ID=uid))
        return jb_arr
    elif os.path.exists(work_dir + "\\JB.txt"):
        print "Reading TXT"
        with open("JB.txt", "r") as fil:
            JBlist = fil.read().split(chr(10))
            fil.close()
        for jb in JBlist:
            jber = jb.split("/")
            hebname = jber[1]
            hebname = hebname.decode("hebrew").encode("utf8")
            jber_roles = []
            for r in jber[3].split("$"):
                jber_roles.append(r)
            uid = 0
            try:
                uid = int(jber-5)
            except Exception:
                pass
            jb_arr.append(JBer(English_Name=jber[0],Hebrew_Name=hebname,Phone_Number=jber[2],Roles=jber_roles,Birthdate=jber[4],ID=uid))
        with open("logs.txt", "a") as logf:
            logf.write("started the bot\n")
            logf.close()
        return jb_arr
    else:
        print "there is no file from which I can get the contacts."
        print "check to see if the file is under the same folder as this file"
        os.exit()


def refresh():
    global JB_names, grades_arr, folders, energizers, lullaby, tags, grades, activitors, editing, newbies
    
    JB_names = Get_Contacts()
    newbies = Get_Newbies()
    editing = Get_Editors()
    activitors = Get_Activitors()
    
    folders = getFolders()
    for key in folders:
        if not os.path.exists(work_dir + key):
            os.makedirs(work_dir + key)
            
    energizers = []
    for key in folders[u'energizers']:
        energizers.append(key.replace(".txt",""))
    lullaby = []
    for key in folders[u'lullabies']:
        lullaby.append(key.replace(".txt",""))
    tags = [u"Human Rights", u"Sustainable Development♻", u"Conflict and Resolution🤝", u"Diversity"]
    for name in folders[u'activities']:
        if name != "emojis.txt":
            for tag in folders[u'activities'][name]["tags"]:
                if (not (unicode(tag) in tags)) and (not (tag in grades_arr)) and (tag != "JB"):
                    tags.append(tag)
    grades = []
    for g in grades_arr:
        if g.islower():
            grades.append(g)
    grades.append("JB")
    grades.append("All")
        
    for folder in folders:
        for File in folders[folder]:
            if not os.path.exists(work_dir + folder + "\\" + File):
                download_file_from_google_drive(folders[folder][File]["file_id"], work_dir + folder + "\\" + File)

    return JB_names, newbies, editing, activitors, folders, energizers, lullaby, grades

refresh()
TT_group_id = -1001137610324
JB_group_id = -1001347723461
Oz_id = 118435275
month_arr = ["January","February","March","April","May","June","July","August","September","October","November","December"]
brday = str(datetime.datetime.now().day) + "-" + str(datetime.datetime.now().month)
en_programmes = ["Village (11)", "Interchange (12-15)", "Step-Up (14-15)", "Seminar-Camp (17-18)", "Youth-Meeting (12-19+)", "Mosaic (All ages)", "International-Peoples-Project (19+)"]
wishes = ["ימי הולדת הם הדרך של הטבע להגיד לנו לאכול עוד עוגות,","אומרים שכשאתה מתבגר אתה מאבד שלושה דברים, הראשון הוא הזיכרון ושכחתי את השניים האחרים,","מחקרים מראים שככל שיש יותר ימי הולדת, חיים יותר שנים,"]
