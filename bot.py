# -*- coding: utf-8 -*-
# ^enables you to use non english chars
# -*- coding: iso-8859-15 -*-
# ^enables you to send emojis

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, JobQueue
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.error import TelegramError, Unauthorized, BadRequest,TimedOut, ChatMigrated, NetworkError

from helpers import *

import random
import os.path
import os
import sys
import traceback

import logging

import datetime

import httplib2

from apiclient import discovery

from quickstart_cal import get_credentials, timeForAPI, monthForMonthEvent, unicodeToStr
from quickstart_drv import download_file_from_google_drive


def start(bot, update):
    try:
        iknow = InFile(bot, update)
        name = get_full_name(update)
        print name + " used '/start' @ " + str(datetime.datetime.now())
        logs = open("logs.txt","a")
        if not is_ascii(name):
            logs.write("nonASCII used '/start' @ " + str(datetime.datetime.now()) + "\n")
        else:
            logs.write(name + " used '/start' @ " + str(datetime.datetime.now()) + "\n")
        logs.close()
        if iknow:
            txt = "Hello human No. " + str(update.message.from_user.id) + " named " + name + " I'm JBbot!\nhave I told you that you look stunning today?"
            bot.send_message(chat_id=update.message.chat_id, text=txt)
            bot.send_message(chat_id=update.message.chat_id, text="type '/help' to get all of my functionalities")
        else:
            if update.message.chat.type == "private":
                name_parts = name.split(" ")
                for jb in JB_names:
                    found = False
                    for part in name_parts:
                        if part.lower() in jb.En_Name.lower():
                            found = True
                        else:
                            found = False
                            break
                    if found:
                        print "found a match with " + name + "'s phone @ " + str(datetime.datetime.now())
                        logs = open("logs.txt","a")
                        if not is_ascii(name):
                            logs.write("found a match with nonASCII's phone @ " + str(datetime.datetime.now()) + "\n")
                        else:
                            logs.write("found a match with " + name + "'s phone @ " + str(datetime.datetime.now()) + "\n")
                        logs.close()
                        data = "Exists;" + jb.En_Name
                        keyboard = [[InlineKeyboardButton("Yes", callback_data=data), InlineKeyboardButton("No", callback_data="Exists;False")]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        update.message.reply_text("Is this your phone number?\n" + jb.Phone, reply_markup=reply_markup)
                        break
            else:
                bot.send_message(chat_id=update.message.chat_id, text="I don't know who you are.\n use /add_jber to add yourself to the JB list or contact Oz Sabbag @sexycow69 for help.")
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def new_member(bot, update):
    try:
        if update.message.chat_id == JB_group_id:
            InFile(bot, update)
            if len(update.message.new_chat_members) == 1:
                if update.message.new_chat_members[-1].first_name != "JBbot":
                    logs = open("logs.txt","a")
                    logs.write(update.message.new_chat_members[-1].first_name + " was added to the group\n")
                    logs.close()
                    print update.message.new_chat_members[-1].first_name + " was added to the group"
                    if not bool(update.message.new_chat_members[-1].is_bot):
                        txt = "Hello human No. " + str(update.message.new_chat_members[-1].id) + " named " + update.message.new_chat_members[-1].first_name + " I'm JBbot!\nhave I told you that you look stunning today?"
                    else:
                        txt = "Hello fellow bot named " + update.message.new_chat_members[-1].first_name + ", I'm JBbot!"
                    bot.send_message(chat_id=update.message.chat_id, text=txt)
                    if bool(update.message.new_chat_members[-1].is_bot):
                        txt = "FYI. Anything you can do, I can do better. I can do anything better than you!"
                        bot.send_message(chat_id=update.message.chat_id, text=txt)
                    else:
                        bot.send_message(chat_id=update.message.chat_id, text="why don't you PM me @jbisrael_bot so I can add you to the JB list?")
            else:
                bot.send_message(chat_id=update.message.chat_id, text="Welcome to all!\nPlease PM me @jbisrael_bot so I can add you to the JB list ")
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def leaving(bot, update):
    if update.message.chat_id == JB_group_id:
        left = update.message.left_chat_member
        ID = left.id
        try:
            try:
                name = left.first_name + " " + left.last_name
            except Exception:
                name = left.first_name
            logs = open("logs.txt","a")
            logs.write(name + " has left the group\n")
            logs.close()
            print name + " has left the group"
            
            with open(work_dir + "JBtest.csv","r") as csvfile:
                allJB = csvfile.read()
                csvfile.close()
            os.rename(work_dir + "JB.csv", work_dir + "PrevJB.csv")
            allJB = allJB.split("\n") #getting a string array that represent the JB
            jber = []
            prev_JB = []
            for Jb in allJB:
                if len(jber) == 0:
                    if str(ID) in str(Jb.split(',')[5]):
                        jber.append(Jb) # saving the relevant jber
                    if len(jber) == 0:
                        prev_JB.append(Jb)
                else:
                    jber.append(Jb)
                
            if jber != None:
                jber_edit = jber[0].split(",") # getting an array of the relevant jber attributes
                jber_edit[4] = "_" + jber_edit[4] # changing the birthdate
                jber_edit[3] = "None"

                jb = ""
                for prev in prev_JB:
                    jb += prev + '\n'
                for part in jber_edit:
                    jb += str(part) + ","
                jb = jb[:len(jb) - 1] + "\n" # building back a string that represent the jber
                for i in range(1, len(jber)):
                    jb += jber[i] + "\n"
                jb = jb[:len(jb) - 1] # building the rest of the string
                with open(work_dir + "JB.csv", 'w') as csvfile:
                    csvfile.write(jb) #overwriting the old info with the new one
                    csvfile.close()
                try:
                    Refresh_Command(bot, query)
                    os.remove(work_dir + "PrevJB.csv") 
                except Exception, e:
                    bot.send_message(text="wasn't able to apply the edit.\nError: " + str(e), chat_id=update.message.chat_id)
            else:
                bot.send_message(chat_id=Oz_id, text="I don't know who left, I couldn't find %s id" % name)    
                bot.send_message(chat_id=Oz_id, text="the id is %s" % ID)  
        except Exception, e:    
            bot.send_message(chat_id=Oz_id, text="I had problems with deleting ID:" + ID + " from the file.\nError: " + str(e))


def button_prog(bot, update):
    try:
        global grades_arr, JB_names, newbies, editing
        query = update.callback_query
        query_type = query.data.split(";")[0]
        query_data = query.data.split(";")[1]
        if query_type == "Programme":
            bot.edit_message_text(
                text="hey! you can read more about it at: http://www.cisv.org/cisv-programmes/%s" % query_data,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
        if query_type == "Grade":
            query_data = int(query_data)
            leaders = []
            for jb in JB_names:
                if grades_arr[query_data] in jb.Roles:
                    leaders.append(jb.En_Name)
            if len(leaders) > 0:
                txt = "The leaders of the " + grades_arr[query_data] + " grade are:\n"
                for l in leaders:
                    txt += l + ", "
                txt = txt[:-2]
                txt += "\nIf you need to contact any one of them, use /jb_phone"
            else:
                txt = "There are no leaders for the " + grades_arr[query_data] + " grade\nWhat will we do???"
            bot.edit_message_text(text=txt, chat_id=query.message.chat_id, message_id=query.message.message_id)
        if query_type == "Gather":
            data_high = query_data.encode("utf-8").split("-")[0]
            data_low = query_data.encode("utf-8").split("-")[1]
            if data_high == "True":
                newbies[str(query.message.chat_id)]["stage"] += 1
                Save_Newbies()
                bot.edit_message_text(text="OK, cool!",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id)
                if int(data_low) == 0:
                    bot.send_message(text="And how do you write your full name in Hebrew?", chat_id=query.message.chat_id)
                elif int(data_low) == 1:
                    txt = "What is your phone number?\n(write it like this '0504862275')"
                    bot.send_message(text=txt, chat_id=query.message.chat_id)
                elif int(data_low) == 2:
                    txt = "What is your birthdate?\nwrite it as dd/mm i.e. 13/02 or 01/10"
                    bot.send_message(text=txt, chat_id=query.message.chat_id)
                elif int(data_low) == 3:
                    txt = "English Name: %s\n" % newbies[str(query.message.chat_id)]["JBer"].En_Name
                    txt += "Hebrew name: %s\n" % newbies[str(query.message.chat_id)]["JBer"].He_Name
                    txt += "Phone number: %s\n" % newbies[str(query.message.chat_id)]["JBer"].Phone
                    txt += "Birth date: %s" % newbies[str(query.message.chat_id)]["JBer"].Birthday
                    bot.send_message(text=txt, chat_id=query.message.chat_id)
                    keyboard = [[InlineKeyboardButton("Yes", callback_data="Gather;True-6"), InlineKeyboardButton("No", callback_data="Gather;False-0")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    query.message.reply_text("is that true?", reply_markup=reply_markup)
                elif int(data_low) == 6:
                    bot.send_message(text="Thank you!\nI will now update the data...", chat_id=query.message.chat_id)
                    jb = newbies[str(query.message.chat_id)]["JBer"]
                    add_to_file(jb)
                    Refresh_Command(bot, query)
                    bot.send_message(text="Press /start so we can start things right!", chat_id=query.message.chat_id)
                    del newbies[str(query.message.chat_id)]
                    Save_Newbies()
            else:
                if int(data_low) == 0:
                    del newbies[str(query.message.chat_id)]
                    Save_Newbies()
                    bot.send_message(text="please press here /add_jber", chat_id=query.message.chat_id)
                else:
                    bot.edit_message_text(text="Then please type it again", chat_id=query.message.chat_id, message_id=query.message.message_id)
        if query_type == "Exists":
            if query_data == "False":
                bot.edit_message_text(text="Then press here please!\n/add_jber", chat_id=query.message.chat_id, message_id=query.message.message_id)
            else:
                bot.edit_message_text(text="So I already have your info, thank you!\nPlease wait while I refesh the data...", chat_id=query.message.chat_id, message_id=query.message.message_id)
                with open(workdir + "JB.csv","r") as csvfile:
                    allJB = csvfile.read()
                    csvfile.close()
                os.rename(work_dir + "JB.csv", work_dir + "PrevJB.csv")
                allJB = allJB.split("\n") #getting a string array that represent the JB
                jber = []
                prev_JB = []
                for Jb in allJB:
                    if len(jber) == 0:
                        if query_data in Jb.split(',')[0]:
                            jber.append(Jb) # saving the relevant jber
                        if len(jber) == 0:
                            prev_JB.append(Jb)    
                    else:
                        jber.append(Jb)

                jber_edit = jber[0].split(",") # getting an array of the relevant jber attributes
                jber_edit[5] = query.message.chat_id # attaching the id

                jb = ""
                for prev in prev_JB:
                    jb += prev + '\n'
                for part in jber_edit:
                    jb += str(part) + ","
                jb = jb[:len(jb) - 1] + "\n" # building back a string that represent the jber
                for i in range(1, len(jber)):
                    jb += jber[i] + "\n"
                jb = jb[:len(jb) - 1] # building up the rest of the string
                with open(work_dir + "JB.csv", "w"):
                    csvfile.write(jb) #overwriting the old info with the new one
                    csvfile.close()
                try:
                    Refresh_Command(bot, query)
                    os.remove(work_dir + "PrevJB.csv")
                except Exception, e:
                    bot.send_message(text="wasn't able to apply the edit.\nError: " + str(e), chat_id=query.message.chat_id)
        if query_type == "Edit":
            query_data = int(query_data)
            txt = "Then send me " + editing[str(query.message.chat_id)]["JBer"].En_Name+ "'s new "
            if query_data == 0:
                txt += "English name"
    ##        elif query_data == 1:
    ##            txt += "Hebrew name"
            elif query_data == 2:
                txt += "Phone number as following:\n0512345678"
            elif query_data == 3:
                txt += "Roles as following:\nrole1, role2, role3..."
            elif query_data == 4:
                txt += "Birthdate as following:\ndd-mm\nSend me 'del' to unmark their birthday, or 'mark' to mark it"
            else:
                txt += "ID number"
            editing[str(query.message.chat_id)]["field"] = query_data
            Save_Editors()
            bot.edit_message_text(text=txt, chat_id=query.message.chat_id, message_id=query.message.message_id)
        if query_type == "Conformation":
            query_data_bool = "True" in query_data
            if not query_data_bool:
                bot.edit_message_text(text="Then please send it to me again", chat_id=query.message.chat_id, message_id=query.message.message_id)
            else:
                bot.edit_message_text(text="OK, I'm changing the data...", chat_id=query.message.chat_id, message_id=query.message.message_id)
                NAME = query_data.split('-')[1]
                with open("JB.csv","r") as csvfile:
                    allJB = csvfile.read()
                    csvfile.close()
                os.rename(work_dir + "JB.csv", work_dir + "PrevJB.csv")
                allJB = allJB.split("\n") #getting a string array that represent the JB 
                prev_jb = []
                jber = []
                for Jb in allJB:
                    if len(jber) == 0:
                        if NAME in Jb.split(',')[0]:
                            jber.append(Jb) # saving the relevant jber
                        if len(jber) == 0:
                            prev_jb.append(Jb)   
                    else:
                        jber.append(Jb)

                jber_edit = jber[0].split(",") # getting an array of the relevant jber attributes
                jber_edit[editing[str(query.message.chat_id)]["field"]] = editing[str(query.message.chat_id)]["change"] # applying changes

                jb = ""
                for prev in prev_jb:
                    jb += prev + "\n"
                for part in jber_edit:
                    jb += str(part) + ","
                jb = jb[:len(jb) - 1] + "\n" # building back a string that represent the jber
                for i in range(1, len(jber)):
                    jb += jber[i] + "\n"
                jb = jb[:len(jb) - 1] # building up the rest of the string
                with open("JB.csv","w") as csvfile:
                    csvfile.write(jb) #overwriting the old info with the new one
                    csvfile.close()
                try:
                    Refresh_Command(bot, query)
                    os.remove(work_dir + "PrevJB.csv")
                except Exception, e:
                    bot.send_message(text="wasn't able to apply the edit.\nError: " + str(e), chat_id=query.message.chat_id)
                del editing[str(query.message.chat_id)]
                Save_Editors()
        if query_type == "PreEdit":
            if query_data == "True":
                bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
                name = "nonASCII"
                for jb in JB_names:
                    if jb.ID == int(query.message.chat_id):
                        name = jb.En_Name
                        break
                print name + " started editing " + editing[str(query.message.chat_id)]["JBer"].En_Name + "'s info @ " + str(datetime.datetime.now())
                logs = open("logs.txt","a")
                logs.write(name + " started editing " + editing[str(query.message.chat_id)]["JBer"].En_Name + "'s info @ " + str(datetime.datetime.now()) + "\n")
                logs.close()
                
                keyboard = [[InlineKeyboardButton("English Name", callback_data="Edit;0")],
        ##                                [InlineKeyboardButton("Hebrew Name", callback_data="Edit;1")],
                                        [InlineKeyboardButton("Phone", callback_data="Edit;2")],
                                        [InlineKeyboardButton("Roles", callback_data="Edit;3")],
                                        [InlineKeyboardButton("Birthdate", callback_data="Edit;4")],
                                        [InlineKeyboardButton("User ID", callback_data="Edit;5")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.message.reply_text("What part of " + editing[str(query.message.chat_id)]["JBer"].En_Name + "'s info do you want to edit?", reply_markup=reply_markup)
            else:
                del editing[str(query.message.chat_id)]
                Save_Editors()
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def prog(bot, update):
    try:
        InFile(bot, update)
        name = get_full_name(update)
        print name + " used '/programmes' @ " + str(datetime.datetime.now())
        logs = open("logs.txt","a")
        if not is_ascii(name):
            logs.write("nonASCII used '/programmes' @ " + str(datetime.datetime.now()) + "\n")
        else:
            logs.write(name + " used '/programmes' @ " + str(datetime.datetime.now()) + "\n")
        logs.close()
        global en_programmes
        keyboard = []
        for prog_index in range(0, len(en_programmes)):
            keyboard.append(
                [InlineKeyboardButton(en_programmes[prog_index],
                                      callback_data="Programme;" + en_programmes[prog_index].split(" ")[0])])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('What program do you want to read about?', reply_markup=reply_markup)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def grade(bot, update):
    try:
        InFile(bot, update)
        name = get_full_name(update)
        print name + " used '/grades' @ " + str(datetime.datetime.now())
        logs = open("logs.txt","a")
        if not is_ascii(name):
            logs.write("nonASCII used '/grades' @ " + str(datetime.datetime.now()) + "\n")
        else:
            logs.write(name + " used '/grades' @ " + str(datetime.datetime.now()) + "\n")
        logs.close()
        global grades_arr
        keyboard = []
        for index in range(0, len(grades_arr)):
            keyboard.append([InlineKeyboardButton(grades_arr[index], callback_data="Grade;" + str(index))])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('What grade do you want to know about?', reply_markup=reply_markup)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def energizer(bot, update):
    try:
        InFile(bot, update)
        name = get_full_name(update)
        print name + " used '/energizer' @ " + str(datetime.datetime.now())
        logs = open("logs.txt","a")
        if not is_ascii(name):
            logs.write("nonASCII used '/energizer' @ " + str(datetime.datetime.now()) + "\n")
        else:
            logs.write(name + " used '/energizer' @ " + str(datetime.datetime.now()) + "\n")
        logs.close()
        global energizers
        energy = update.message.text.lower()
        energy = energy.split(" ")
        if len(energy) == 1:
            a = random.randint(1, len(energizers))
            bot.send_message(chat_id=update.message.chat_id, text=energizers[a])
            txt = get_lyrics(energizers[a], "energizers")
            if txt:
                bot.send_message(chat_id=update.message.chat_id, text=txt.decode("hebrew"), parse_mode=ParseMode.MARKDOWN)
        else:
            energi = get_input(energy)
            arr = []
            for e in energizers:
                if energi.lower() in e.lower():
                    arr.append(e)
            if len(arr) == 1:
                bot.send_message(chat_id=update.message.chat_id, text=arr[0])
                txt = get_lyrics(arr[0], "energizers")
                if txt:
                    bot.send_message(chat_id=update.message.chat_id, text=txt.decode("hebrew"), parse_mode=ParseMode.MARKDOWN)
            elif len(arr) > 1:
                for txt in arr:
                    bot.send_message(chat_id=update.message.chat_id, text=txt)
            else:
                txt = "I don't know an energizer named '{}'\nyou can use /add_energizer to add it!".format(energi)
                bot.send_message(chat_id=update.message.chat_id, text=txt)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def Njr(bot, update):
    try:
        global JB_names
        iknow = InFile(bot, update)
        name = get_full_name(update)
        logs = open("logs.txt","a")
        if iknow:
            NJRs = []
            for jb in JB_names:
                if "JB!!!" in jb.Roles:
                    NJRs.append(jb)
            print name + " used '/Njrs' @ " + str(datetime.datetime.now())
            if not is_ascii(name):
                logs.write("nonASCII used '/Njrs' @ " + str(datetime.datetime.now()) + "\n")
            else:
                logs.write(name + " used '/Njrs' @ " + str(datetime.datetime.now()) + "\n")
            txt = "The Njrs are:\n"
            for i in range(0, len(NJRs)):
                txt += NJRs[i].En_Name + " " + NJRs[i].Phone + "\n"
            bot.send_message(chat_id=update.message.chat_id, text=txt)
        else:
            print name + " failed to use '/Njrs' @ " + str(datetime.datetime.now())
            if not is_ascii(name):
                logs.write("nonASCII failed to use '/Njrs' @ " + str(datetime.datetime.now()) + "\n")
            else:
                logs.write(name + " failed to use '/Njrs' @ " + str(datetime.datetime.now()) + "\n")
            txt = "I am sorry, I can't seem to recognize you. As a precaution, you will not be able to view 'sensitive' information.\nPlease contact Oz Sabbag @sexycow69 to fix this inconvenience."
            bot.send_message(chat_id=update.message.chat_id, text=txt)
        logs.close()
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def name_search(bot, update):
    try:
        iknow = InFile(bot, update)
        full_name = get_full_name(update)
        logs = open("logs.txt","a")
        global JB_names
        if iknow:
            print full_name + " used '/jb_phone' @ " + str(datetime.datetime.now())
            if not is_ascii(full_name):
                logs.write("nonASCII used '/jb_phone' @ " + str(datetime.datetime.now()) + "\n")
            else:
                logs.write(full_name + " used '/jb_phone' @ " + str(datetime.datetime.now()) + "\n")
            key = get_keyboard("ABCDEFGHIJKLMNOPQRSTUVWXYZ",5)
            reply_markup = ReplyKeyboardMarkup(key)
            txt = "Please choose the person's first letter"
            bot.send_message(text=txt,chat_id=update.message.chat_id, reply_markup=reply_markup)
            nameies[str(update.message.chat_id)] = None
            Save_Nameies()
        else:
            if not is_ascii(full_name):
                logs.write("nonASCII failed to use '/jb_phone' @ " + str(datetime.datetime.now()) + "\n")
            else:
                logs.write(full_name + "failed to use'/jb_phone' @ " + str(datetime.datetime.now()) + "\n")
            txt = "I am sorry, I can't seem to recognize you. As a precaution, you will not be able to view 'sensitive' information.\nPlease contact Oz Sabbag @sexycow69 to fix this inconvenience."
            bot.send_message(chat_id=update.message.chat_id, text=txt)
        logs.close()
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()

        
"""def board_search(bot, update):
    InFile(bot, update)
    global board_arr
    names = update.message.text
    results = []
    names = names.split(" ")
    logs = open("logs.txt","a")
    if len(names) <= 1:
        if not is_ascii(update.message.from_user.first_name):
            logs.write("Barogel" + " used '/board_phone' without a name @ " + str(datetime.datetime.now()) + "\n")
            print update.message.from_user.first_name + " used '/board_phone' without a name @ " + str(datetime.datetime.now())
        else:
            logs.write(update.message.from_user.first_name + " " + update.message.from_user.last_name + " used '/board_phone' without a name @ " + str(datetime.datetime.now()) + "\n")
            print update.message.from_user.first_name + " " + update.message.from_user.last_name + " used '/board_phone' without a name @ " + str(datetime.datetime.now())
        bot.send_message(chat_id=update.message.chat_id,text="Please add a name after \"/board_phone\", i.e: \"/board_phone Doris\"")
        return
    name = get_input(names)
    names = name
    if not is_ascii(name):
        names = "a hebrew name"
    if not is_ascii(update.message.from_user.first_name):
        logs.write("Barogel" + " used '/board_phone' and looked for " + names + " @ " + str(datetime.datetime.now()) + "\n")
        print update.message.from_user.first_name + " used '/board_phone' and looked for " + names + " @ " + str(datetime.datetime.now())
    else:
        logs.write(update.message.from_user.first_name + " " + update.message.from_user.last_name + " used '/board_phone' and looked for " + names + " @ " + str(datetime.datetime.now()) + "\n")
        print update.message.from_user.first_name + " " + update.message.from_user.last_name + " used '/board_phone' and looked for " + names + " @ " + str(datetime.datetime.now())
    logs.close()
    bot.send_message(chat_id=update.message.chat_id, text="Looking for: '%s'" % name)
    for bord in board_arr:
        if name.lower() in bord.En_Name.lower() or name.lower() == "all" or name.encode("utf8") in bord.He_Name:
            results.append(bord)
    if len(results) >= 1:
        txt = ""
        for bord in results:
            if is_ascii(name):
                txt += bord.En_Name + ": " + bord.Phone + "\n"
            else:
                txt += bord.He_Name + ": " + bord.Phone + "\n"
        if len(results) > 1:
            bot.send_message(chat_id=update.message.chat_id,
                             text="I've found all of these people that matches your search:")
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text="I've found one person that matches your search:")
        bot.send_message(chat_id=update.message.chat_id, text=txt)
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Apparently you don't know how to spell...\nThere were no results found for \"%s\"\nTry sending me a name again" % name)"""


def emberes(bot, update):
    try:
        iknow = InFile(bot, update)
        logs = open("logs.txt","a")
        name = get_full_name(update)
        if iknow:
            print name + " used '/embarrassment' @ " + str(datetime.datetime.now())
            if not is_ascii(name):
                logs.write("nonASCII used '/embarrassment' @ " + str(datetime.datetime.now()) + "\n")
            else:
                logs.write(name + " used '/embarrassment' @ " + str(datetime.datetime.now()) + "\n")
            index = random.randint(1, len(folders[u'embarrassment']))
            name = "emb" + str(index) + ".jpg"
            if not os.path.exists(work_dir + "embarrassment\\" + name):
                if name in folders[u'embarrassment']:
                    download_file_from_google_drive(folders[u'embarrassment'][name]["file_id"], work_dir + "embarrassment\\" + name)
            bot.send_photo(chat_id=update.message.chat_id, photo=open(work_dir + "embarrassment\\" + name, "rb"))
        else:
            print name + " failed to use '/embarrassment' @ " + str(datetime.datetime.now())
            if not is_ascii(name):
                logs.write(name + " failed to use '/embarrassment' @ " + str(datetime.datetime.now()) + "\n")
            else:
                logs.write(name + " failed to use  '/embarrassment' @ " + str(datetime.datetime.now()) + "\n")
            txt = "I am sorry, I can't seem to recognize you. As a precaution, you will not be able to view 'sensitive' information.\nPlease contact Oz Sabbag @sexycow69 to fix this inconvenience."
            bot.send_message(chat_id=update.message.chat_id, text=txt)
        logs.close()
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def bannana(bot, update):
    try:
        global banana_arr
        InFile(bot, update)
        name = get_full_name(update)
        logs = open("logs.txt","a")
        print name + " used '/banana' @ " + str(datetime.datetime.now())
        if not is_ascii(name):
            logs.write("nonASCII used '/banana' @ " + str(datetime.datetime.now()) + "\n")
        else:
            logs.write(name + " used '/banana' @ " + str(datetime.datetime.now()) + "\n")
        logs.close()
        c = random.randint(1, len(folders[u'Bananas']))
        name = "ban" + str(c) + ".png"
        if not os.path.exists(work_dir + "bananas\\" + name):
            if name in folders[u'Bananas']:
                download_file_from_google_drive(folders[u'Bananas'][name]["file_id"], work_dir + "bananas\\" + name)
        bot.send_photo(chat_id=update.message.chat_id, photo=open(work_dir + "bananas\\" + name, "rb"))
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def jbb(bot, update):
    try:
        global JB_names
        InFile(bot, update)
        name = get_full_name(update)
        logs = open("logs.txt","a")
        print name + " used '/jb_board' @ " + str(datetime.datetime.now())
        if not is_ascii(name):
            logs.write("nonASCII used '/jb_board' @ " + str(datetime.datetime.now()) + "\n")
        else:
            logs.write(name + " used '/jb_board' @ " + str(datetime.datetime.now()) + "\n")
        logs.close()
        JBB = {"njrs":"", "projects":"", "treasure":"", "communication":"", "store":"", "criticize":""}
        for jb in JB_names:
            if "JB!!!" in jb.Roles:
                JBB["njrs"] += jb.En_Name + ", "
            elif "projects" in jb.Roles:
                JBB["projects"] = jb.En_Name
            elif "treasure" in jb.Roles:
                JBB["treasure"] = jb.En_Name
            elif "communication" in jb.Roles:
                JBB["communication"] = jb.En_Name
            elif "store" in jb.Roles:
                JBB["store"] = jb.En_Name
            elif "criticize" in jb.Roles:
                JBB["criticize"] = jb.En_Name
        for role in JBB:
            if JBB[role] == "":
                JBB[role] = "Currently without a manager."
        JBB["njrs"] = JBB["njrs"][:-2]
        txt = "The JBB consists of:\nThe NJRs: " + JBB["njrs"] + "\n'project manager': " + JBB["projects"] + "\n'treasurer': " + JBB["treasure"] + "\n'communications manager': " + JBB["communication"] + "\n'store manager': " + JBB["store"] + "\nCriticizer: " + JBB["criticize"]
        bot.send_message(chat_id=update.message.chat_id, text=txt)
        txt = "If you need to contact any one of them, use /jb_phone"
        bot.send_message(chat_id=update.message.chat_id, text=txt)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def addjb(bot, update):
    try:
        global newbies, JB_names
        if update.message.chat.type != "private":
            with open("logs.txt","a") as logs:
                print name + " used '/add_jber' in a group @ " + str(datetime.datetime.now())
                if not is_ascii(name):
                    logs.write("nonASCII used '/add_jber' in a group @ " + str(datetime.datetime.now()) + "\n")
                else:
                    logs.write(name + " used '/add_jber' in a group @ " + str(datetime.datetime.now()) + "\n")
                logs.close()
                txt = "I'm sorry, I can't take your personal information from a group, please PM me @jbisrael_bot"
                bot.send_message(chat_id=update.message.chat_id, text= txt)
        else:
            iknow = InFile(bot, update)
            try:
                newbie = bot.get_chat_member(JB_group_id, update.message.chat_id)
            except Exception:
                newbie = None
            if newbie != None:
                name = get_full_name(update)
                logs = open("logs.txt","a")
                if iknow:
                    bot.send_message(chat_id=update.message.chat_id, text="You are already in my list, I don't need to take your information.")
                elif str(update.message.chat_id) in newbies:
                    txt = "I've already started taking your info, no need to start all over again. please continue to answer my questions."
                    bot.send_message(chat_id=update.message.chat_id, text=txt)
                    txt = Again_Question(bot, newbies[str(update.message.chat_id)]["JBer"], newbies[str(update.message.chat_id)]["stage"])
                    if txt != "":
                        bot.send_message(text=txt, chat_id=update.message.chat_id, parse_mode='Markdown')
                else:
                    print "started taking info from " + name + " @ " + str(datetime.datetime.now())
                    if not is_ascii(name):
                        logs.write("started taking info from nonASCII @ " + str(datetime.datetime.now()) + "\n")
                    else:
                        logs.write("started taking info from " + name + " @ " + str(datetime.datetime.now()) + "\n")
                    try:
                        newJB = JBer(English_Name="",Hebrew_Name="", Phone_Number="", Roles=["None"], Birthdate="", ID=update.message.from_user.id)
                        newbies[str(update.message.chat_id)] = {"JBer":newJB, "stage":0}
                        Save_Newbies()
                        bot.send_message(chat_id=update.message.chat_id, text="First, what is your full name in English?")
                    except Exception, e:
                        print str(e)
                logs.close()
            else:
                bot.send_message(chat_id=update.message.chat_id, text="I am sorry, mother always told me not to talk to strangers.")
                bot.send_message(chat_id=update.message.chat_id, text="If there is a problem, contact Oz Sabbag @sexycow69")
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def Again_Question(bot, jber, num):
    try:
        index = int(num)
        if index == 0:
            return "What is your full name in English?"
        elif index == 1:
            return "how do you write your full name in Hebrew?"
        elif index == 2:
            return "What is your phone number?\n(write it like this '0504862275')"
        elif index == 3:
            return "What is your birthdate?\nwrite it as dd/mm i.e. 13/02 or 01/10"
        else:
            txt = "English Name: %s\n" % jber.En_Name
            txt += "Hebrew name: %s\n" % jber.He_Name
            txt += "Phone number: %s\n" % jber.Phone
            txt += "Birth date: %s" % jber.Birthday
            bot.send_message(chat_id=jber.ID, text=txt)
            keyboard = [[InlineKeyboardButton("Yes", callback_data="Gather;True-6"), InlineKeyboardButton("No", callback_data="Gather;False-0")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(chat_id=jber.ID, text="is that true?", reply_markup=reply_markup)
            return ""
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def addenergy(bot, update):
    try:
        InFile(bot, update)
        name = get_full_name(update)
        print name + " used '/add_energizer' @ " + str(datetime.datetime.now())
        logs = open("logs.txt","a")
        if not is_ascii(name):
            logs.write("nonASCII used '/add_energizer' @ " + str(datetime.datetime.now()) + "\n")
        else:
            logs.write(name + " used '/add_energizer' @ " + str(datetime.datetime.now()) + "\n")
        logs.close()
        bot.send_message(chat_id=update.message.chat_id,
                         text="So? you have an energizer that isn't in our database?\nGo to this link and write it's name and lyrics and we'll add it!")
        bot.send_message(chat_id=update.message.chat_id, text="http://bit.ly/2rZwZYe")
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def help(bot, update):
    try:
        InFile(bot, update)
        name = get_full_name(update)
        print name + " used '/help' @ " + str(datetime.datetime.now())
        logs = open("logs.txt","a")
        if not is_ascii(name):
            logs.write("nonASCII used '/help' @ " + str(datetime.datetime.now()) + "\n")
        else:
            logs.write(name + " used '/help' @ " + str(datetime.datetime.now()) + "\n")
        logs.close()
        txt = "/energizer - gives you an energizer when you feel sleepy! (you can also look for energizers)\n"
        txt += "/lullaby - when you have a guitar and out of ideas (you can search for lullabies)\n"
        txt += "/programmes - gives you information about CISV programmes\n"
        txt += "/grades - wanna know who's which grade's leader?\n"
        txt += "/njrs - tells you who your NJRs are\n"
        txt += "/jb_phone - you can search for a person's phone number\n"
        #txt += "/board_phone <NAME> - you can search for a board member's phone number, try 'all' to get everyone\n"
        txt += "/banana - when you just need a banana in your life\n"
        txt += "/embarrassment - you don't want to, believe me\n"
        txt += "/jb_board - tells you who is part of the JBB\n"
        txt += "/add_jber - for those we forgot\n"
        txt += "/add_energizer - the more the merrier\n"
        txt += "/add_lullaby - what's your camp song?\n"
        txt += "/next_event - shows you the next cisv event\n"
        txt += "/next_activity - shows you when is the next activity\n"
        txt += "/this_month - shows you the schedule for this month\n"
        txt += "/next_month - shows you the schedule for next month\n"
        txt += "/schedule_for <MONTH> - shows the schedule for a specific month\n"
        txt += "/anonymous <TEXT> - sends an anonymous message to the group\n"
        txt += "/get_me - gives the information saved about you\n"
        txt += "/activity - search through the archive"
        bot.send_message(chat_id=update.message.chat_id, text=txt)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def birthday(bot, update):
    global JB_names, brday, wishes
    try:
        if brday != str(datetime.datetime.now().day) + "-" + str(datetime.datetime.now().month):
            brday = str(datetime.datetime.now().day) + "-" + str(datetime.datetime.now().month)
            logs = open("logs.txt", "a")
            print "brday is now %s" % brday
            logs.write("brday is now %s\n" % brday)
            for i in JB_names:
                if brday == i.Birthday:
                    print "it's " + i.En_Name + "'s Birthday!"
                    logs.write("it's " + i.En_Name + "'s Birthday!\n")
                    txt = wishes[random.randint(0,len(wishes) - 1)]
                    txt += "\n מזל טוב {} 🎉🎊🎁❤️❤️".format(i.He_Name)
                    bot.send_message(chat_id=JB_group_id,text=txt)
            logs.close()
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def again_bd(bot, update):
    try:
        global brday
        logs = open("logs.txt", "a")
        logs.write("retrying bday\n")
        print ("retrying bday")
        logs.close()
        brday = "30-2"
        birthday(bot, update)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def lullabies(bot, update):
    try:
        InFile(bot, update)
        name = get_full_name(update)
        print name + " used '/lullaby' @ " + str(datetime.datetime.now())
        logs = open("logs.txt","a")
        if not is_ascii(name):
            logs.write("nonASCII used '/lullaby' @ " + str(datetime.datetime.now()) + "\n")
        else:
            logs.write(name + " used '/lullaby' @ " + str(datetime.datetime.now()) + "\n")
        logs.close()
        global lullaby
        message = update.message.text.lower()
        parts = message.split(" ")
        if len(parts) == 1:
            r = random.randint(1, len(lullaby))
            bot.send_message(chat_id=update.message.chat_id, text=lullaby[r])
            word = get_lyrics(lullaby[r], "lullabies")
            if word:
                bot.send_message(chat_id=update.message.chat_id, text=word, parse_mode=ParseMode.MARKDOWN)
        else:
            lul = get_input(parts)
            arr = []
            for l in lullaby:
                if lul in l.lower():
                    arr.append(l)
            if len(arr) == 1:
                bot.send_message(chat_id=update.message.chat_id, text=arr[0])
                word = get_lyrics(arr[0], "lullabies")
                if word:
                    bot.send_message(chat_id=update.message.chat_id, text=word, parse_mode=ParseMode.MARKDOWN)
            elif len(arr) > 1:
                for txt in arr:
                    bot.send_message(chat_id=update.message.chat_id, text=txt)
            else:
                txt = "I don't know the song '{}'\nyou can use /add_lullaby to add it!".format(lul)
                bot.send_message(chat_id=update.message.chat_id, text=txt)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def addsong(bot, update):
    try:
        InFile(bot, update)
        name = get_full_name(update)
        print name + " used '/add_lullaby' @ " + str(datetime.datetime.now())
        logs = open("logs.txt","a")
        if not is_ascii(name):
            logs.write("nonASCII used '/add_lullaby' @ " + str(datetime.datetime.now()) + "\n")
        else:
            logs.write(name + " used '/add_lullaby' @ " + str(datetime.datetime.now()) + "\n")
        logs.close()
        bot.send_message(chat_id=update.message.chat_id,text="A special song from camp?\none that you hear every night before bed?\nyou can trust us to add it!")
        bot.send_message(chat_id=update.message.chat_id, text="http://bit.ly/2rZwZYe")
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def info(bot, update):
    try:
        global JB_names
        if InFile(bot, update) and IsDev(update.message.chat_id):
            names = update.message.text
            results = []
            names = names.split(" ")
            full_name = get_full_name(update)
            if len(names) <= 1:
                print full_name + " found out about '/info' @ " + str(datetime.datetime.now())
                bot.send_message(chat_id=update.message.chat_id,
                                 text="Please add a name after \"/info\", i.e: \"/info Doris\"")
                return
            name = get_input(names)
            print full_name + " used '/info' and looked for " + name + " @ " + str(datetime.datetime.now())
            for jb in JB_names:
                if name.lower() in jb.En_Name.lower() or "all" in name.lower() or name.encode("utf8") in jb.He_Name or name.encode("utf8") == "כולם":
                    results.append(jb)
            if len(results) > 0:
                txt = ""
                for jb in results:
                    role = ""
                    for r in jb.Roles:
                        role += r + ", "
                    role = role[:len(role) - 2] 
                    txt += "En_Name: {}\nHe_Name: {}\nPhone: {}\nRoles: {}\nBday: {}\nuser_id: {}".format(jb.En_Name,jb.He_Name,jb.Phone,role,jb.Birthday,str(jb.ID))
                    bot.send_message(chat_id=update.message.chat_id, text=txt)
                    txt = ""
            else:
                txt = 'I have no information for "' + name + '"'
                bot.send_message(chat_id=update.message.chat_id, text=txt)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def nextEvent(bot, update):
    try:
        InFile(bot, update)
        name = get_full_name(update)
        print name + " used '/next_event' @ " + str(datetime.datetime.now())
        logs = open("logs.txt","a")
        if not is_ascii(name):
            logs.write("nonASCII used '/next_event' @ " + str(datetime.datetime.now()) + "\n")
        else:
            logs.write(name + " used '/next_event' @ " + str(datetime.datetime.now()) + "\n")
        logs.close()
        
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        now = timeForAPI
        activity = "פעולת"
        eventsResult = service.events().list(
            calendarId='6ka78oi2sa0ou16epr15d3kqn8@group.calendar.google.com', timeMin=timeForAPI(), maxResults=50,
            singleEvents=True,
            orderBy='startTime').execute()

        events = eventsResult.get('items', [])

        oneEvent = ""

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start = start + ">" + event['end'].get('dateTime', event['end'].get('date'))
            start = start + " " + event['summary']

            eventName, eventDate, eventTime = format_event(start)

            eventNameStr = eventName.encode('utf8', 'replace')

            if (activity != compare(activity, eventNameStr)):
                if eventTime != "":
                    oneEvent = oneEvent + "%s from %s - %s" % (eventDate, eventTime, eventName)
                else:
                    oneEvent = oneEvent + "%s - %s" % (eventDate, eventName)                
                break
            else:
                continue

        if oneEvent != "":
            oneEvent = "The next event is:\n"+oneEvent
        else:
            oneEvent = "there are no more events for now"
        bot.send_message(chat_id=update.message.chat_id, text=oneEvent)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def eventThisMonth(bot, update):
    try:
        InFile(bot, update)
        name = get_full_name(update)
        print name + " used '/this_month' @ " + str(datetime.datetime.now())
        logs = open("logs.txt","a")
        if not is_ascii(name):
            logs.write("nonASCII used '/this_month' @ " + str(datetime.datetime.now()) + "\n")
        else:
            logs.write(name + " used '/this_month' @ " + str(datetime.datetime.now()) + "\n")
        logs.close()

        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        now = timeForAPI

        eventsResult = service.events().list(
            calendarId='6ka78oi2sa0ou16epr15d3kqn8@group.calendar.google.com', timeMin=timeForAPI(), maxResults=50,
            singleEvents=True,
            orderBy='startTime').execute()

        events = eventsResult.get('items', [])

        oneEvent = ""

        nowMonth = monthForMonthEvent()

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start = start + ">" + event['end'].get('dateTime', event['end'].get('date'))
            start = start + " " + event['summary']
            
            eventName, eventDate, eventTime = format_event(start)

            if (nowMonth != int(eventDate.split("/")[1])):
                break
            if eventTime != "":
                oneEvent = oneEvent + "%s from %s - %s" % (eventDate, eventTime, eventName) + "\n"
            else: 
                oneEvent = oneEvent + "%s - %s" % (eventDate, eventName) + "\n"
        
        if oneEvent == "":
            Eventim = "{} does not contain any events or activities".format(month_arr[nowMonth - 1])
        else:
            Eventim = "The schedule for the rest of {} is:\n".format(month_arr[nowMonth - 1])+oneEvent
        bot.send_message(chat_id=update.message.chat_id, text=Eventim)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def eventNextMonth(bot, update):
    try:
        InFile(bot, update)
        name = get_full_name(update)
        print name + " used '/next_month' @ " + str(datetime.datetime.now())
        logs = open("logs.txt","a")
        if not is_ascii(name):
            logs.write("nonASCII used '/next_month' @ " + str(datetime.datetime.now()) + "\n")
        else:
            logs.write(name + " used '/next_month' @ " + str(datetime.datetime.now()) + "\n")
        logs.close()

        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        now = timeForAPI

        eventsResult = service.events().list(
            calendarId='6ka78oi2sa0ou16epr15d3kqn8@group.calendar.google.com', timeMin=timeForAPI(), maxResults=50,
            singleEvents=True,
            orderBy='startTime').execute()

        events = eventsResult.get('items', [])

        oneEvent = ""

        nowMonth = monthForMonthEvent()
        if nowMonth == 12:
            nextMonth = 1
        else:
            nextMonth = nowMonth + 1
            
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start = start + ">" + event['end'].get('dateTime', event['end'].get('date'))
            start = start + " " + event['summary']

            eventName, eventDate, eventTime = format_event(start)

            if (nextMonth > int(eventDate.split("/")[1])):
                continue
            elif nextMonth != int(eventDate.split("/")[1]):
                break

            if eventTime != "":
                oneEvent = oneEvent + "%s from %s - %s" % (eventDate, eventTime, eventName) + "\n"
            else:
                oneEvent = oneEvent + "%s - %s" % (eventDate, eventName) + "\n"

        if oneEvent != "":
            oneEvent = "The schedule for {} is:\n".format(month_arr[nextMonth - 1])+oneEvent
        else:
            oneEvent = "{} does not contain any events or activities".format(month_arr[nextMonth - 1])
        bot.send_message(chat_id=update.message.chat_id, text=oneEvent)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def nextActivity(bot, update):
    try:
        InFile(bot, update)
        name = get_full_name(update)
        print name + " used '/next_activity' @ " + str(datetime.datetime.now())
        logs = open("logs.txt","a")
        if not is_ascii(name):
            logs.write("nonASCII used '/next_activity' @ " + str(datetime.datetime.now()) + "\n")
        else:
            logs.write(name + " used '/next_activity' @ " + str(datetime.datetime.now()) + "\n")
        logs.close()

        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        now = timeForAPI
        activity = "פעולת"
        eventsResult = service.events().list(
            calendarId='6ka78oi2sa0ou16epr15d3kqn8@group.calendar.google.com', timeMin=timeForAPI(), maxResults=50,
            singleEvents=True,
            orderBy='startTime').execute()

        events = eventsResult.get('items', [])

        oneEvent = ""

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start = start + ">" + event['end'].get('dateTime', event['end'].get('date'))
            start = start + " " + event['summary']

            eventName, eventDate, eventTime = format_event(start)

            eventNameStr = eventName.encode('utf8', 'replace')

            if (activity == compare(activity, eventNameStr)):
                if eventTime != "":
                    oneEvent = oneEvent + "%s from %s - %s" % (eventDate, eventTime, eventName)
                else:
                    oneEvent = oneEvent + "%s - %s" % (eventDate, eventName)
                break
            else:
                continue
            
        if oneEvent != "":
            oneEvent = "The next activity is:\n"+oneEvent
        else:
            oneEvent = "There are no more activities this year :("
        bot.send_message(chat_id=update.message.chat_id, text=oneEvent)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def eventChooseMonth(bot, update):
    try:
        InFile(bot, update)
        name = get_full_name(update)
        print name + " used '/schedule_for' @ " + str(datetime.datetime.now())
        logs = open("logs.txt","a")
        if not is_ascii(name):
            logs.write("nonASCII used '/schedule_for' @ " + str(datetime.datetime.now()) + "\n")
        else:
            logs.write(name + " used '/schedule_for' @ " + str(datetime.datetime.now()) + "\n")
        logs.close()

        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        now = timeForAPI

        userInput = update.message.text
        userInput = unicodeToStr(userInput)
        userInput = userInput.split(" ")

        if len(userInput) == 1:
            txt = "Please add a month's name after \"/schedule_for\", i.e: \"/schedule_for march\"\You can use the month's full name, the short name (such as Nov or Jan) or the number of the month"
            bot.send_message(chat_id=update.message.chat_id, text=txt)
            return
        monInput = userInput[1].lower()

        if monInput == "jan" or monInput == "january" or monInput == "1":
            monInput = 1
        elif monInput == "feb" or monInput == "february" or monInput == "2":
            monInput = 2
        elif monInput == "mar" or monInput == "march" or monInput == "3":
            monInput = 3
        elif monInput == "apr" or monInput == "april" or monInput == "4":
            monInput = 4
        elif monInput == "may" or monInput == "5":
            monInput = 5
        elif monInput == "jun" or monInput == "june" or monInput == "6":
            monInput = 6
        elif monInput == "jul" or monInput == "july" or monInput == "7":
            monInput = 7
        elif monInput == "aug" or monInput == "august" or monInput == "8":
            monInput = 8
        elif monInput == "sep" or monInput == "september" or monInput == "9":
            monInput = 9
        elif monInput == "oct" or monInput == "october" or monInput == "10":
            monInput = 10
        elif monInput == "nov" or monInput == "november" or monInput == "11":
            monInput = 11
        elif monInput == "dec" or monInput == "december" or monInput == "12":
            monInput = 12
        else:
            txt = "Apparently you don't know how to spell...\nThere is no month named \""+monInput+"\"\nTry sending me a month again"
            bot.send_message(chat_id=update.message.chat_id, text=txt)

        eventsResult = service.events().list(
            calendarId='6ka78oi2sa0ou16epr15d3kqn8@group.calendar.google.com', timeMin=timeForAPI(), maxResults=100,
            singleEvents=True,
            orderBy='startTime').execute()

        events = eventsResult.get('items', [])

        oneEvent = ""

        nowMonth = monthForMonthEvent()
        nextMonth = nowMonth + 1

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start = start + ">" + event['end'].get('dateTime', event['end'].get('date'))
            start = start + " " + event['summary']

            eventName, eventDate, eventTime = format_event(start)
            eventMonth = eventDate.split("/")[1]

            eventDateInt = int(eventMonth)

            if monInput == eventDateInt:
                if eventTime != "":
                    oneEvent = oneEvent + "%s from %s - %s" % (eventDate, eventTime, eventName) + "\n"
                else:
                    oneEvent = oneEvent + "%s - %s" % (eventDate, eventName) + "\n"
            elif monInput != eventDateInt:
                continue
        if oneEvent != "":
            oneEvent = "The schedule for {} is:\n".format(month_arr[monInput-1])+oneEvent
        else:
            oneEvent = "{} does not contain any events or activities".format(month_arr[monInput-1])
        bot.send_message(chat_id=update.message.chat_id, text=oneEvent)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def newMonth(bot, update):
    try:
        if int(datetime.datetime.now().day) == 1:
            credentials = get_credentials()
            http = credentials.authorize(httplib2.Http())
            service = discovery.build('calendar', 'v3', http=http)

            now = timeForAPI

            eventsResult = service.events().list(
                calendarId='6ka78oi2sa0ou16epr15d3kqn8@group.calendar.google.com', timeMin=timeForAPI(), maxResults=50,
                singleEvents=True,
                orderBy='startTime').execute()

            events = eventsResult.get('items', [])

            oneEvent = ""

            nowMonth = monthForMonthEvent()

            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                start = start + ">" + event['end'].get('dateTime', event['end'].get('date'))
                start = start + " " + event['summary']
                
                eventName, eventDate, eventTime = format_event(start)

                if (nowMonth != int(eventDate.split("/")[1])):
                    break
                if eventTime != "":
                    oneEvent = oneEvent + "%s from %s - %s" % (eventDate, eventTime, eventName) + "\n"
                else: 
                    oneEvent = oneEvent + "%s - %s" % (eventDate, eventName) + "\n"
            
            if oneEvent == "":
                Eventim = "Apparently {} does not contain any events or activities".format(month_arr[nowMonth - 1])
            else:
                Eventim = "The schedule for {} is:\n".format(month_arr[nowMonth - 1])+oneEvent
            bot.send_message(chat_id=JB_group_id, text="let's see what interesting things are happening this month!")
            bot.send_message(chat_id=JB_group_id, text=Eventim)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def logs(bot, update):
    try:
        if InFile(bot, update) and IsDev(update.message.chat_id):
            name = get_full_name(update)
            if not is_ascii(update.message.from_user.first_name):
                user = "nonASCII used '/log' @ " + str(datetime.datetime.now())
            else:
                user = name + " used '/log' @ " + str(datetime.datetime.now())
            logf = open("logs.txt", 'r')
            rawdata = logf.read()
            with open(work_dir + "permanent_log.txt", "a") as per_log:
                per_log.write(rawdata)
                per_log.close()
            splitted = rawdata.split(chr(10))
            logf.close()
            logf = open("logs.txt", "w")
            logf.write(user + "\n")
            logf.close()
            data = ""
            for d in range(0, len(splitted)):
                data += splitted[d] + chr(10)
                if d != 0 and d % 50 == 0:
                    bot.send_message(chat_id=update.message.chat_id, text=data)
                    data = ""
            bot.send_message(chat_id=update.message.chat_id, text=data)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()

        
def Per_log(bot, update):
    try:
        if InFile(bot, update) and IsDev(update.message.chat_id):
            name = get_full_name(update)
            if not is_ascii(update.message.from_user.first_name):
                user = "nonASCII requested permanent_log.txt @ " + str(datetime.datetime.now())
            else:
                user = name + " requested permanent_log.txt @ " + str(datetime.datetime.now())
            logf = open("logs.txt", 'r')
            rawdata = logf.read()
            logf.close()
            logf = open("logs.txt", 'w')
            logf.close()
            with open(work_dir + "permanent_log.txt", "a") as per_log:
                per_log.write(rawdata)
                per_log.close()
            logf = open("logs.txt", 'a')
            logf.write(user + '\n')
            logf.close()
            bot.send_message(chat_id=update.message.chat_id, text="file for " + str(datetime.datetime.now()))
            bot.send_document(chat_id=update.message.chat_id, document=open(work_dir + "permanent_log.txt", 'rb'))
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()
    

def Refresh_Command(bot, update):
    try:
        global JB_names, newbies, editing, activitors, folders, energizers, lullaby, grades
        JB_names, newbies, editing, activitors, folders, energizers, lullaby, grades = refresh()
                    
        print "The data was refreshed @ " + str(datetime.datetime.now())
        logs = open("logs.txt","a")
        logs.write("The data was refreshed @ " + str(datetime.datetime.now()) + "\n")
        logs.close()
        
        bot.send_message(chat_id=update.message.chat_id, text="I refreshed the data")
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def info_gather(bot, update):
    try:
        global newbies, month_arr, editing, activitors, tags, grades
        if str(update.message.chat_id) in nameies:
            if nameies[str(update.message.chat_id)]: #choosing a person
                if update.message.text == "change letter":
                    nameies[str(update.message.chat_id)] = None
                    name_search(bot, update)
                elif update.message.text == "finished":
                    reply = ReplyKeyboardRemove(remove_keyboard="True")
                    bot.send_message(text="Thank you😘", chat_id=update.message.chat_id, reply_markup=reply)
                    del nameies[str(update.message.chat_id)]
                else:
                    for jb in JB_names:
                        if jb.En_Name == update.message.text:
                            bot.send_message(text=jb.En_Name+"'s phone is:\n"+jb.Phone, chat_id=update.message.chat_id)
                            break
            else: #choosing a name
                nameies[str(update.message.chat_id)] = update.message.text
                
                names = []
                for j in JB_names:
                    if j.En_Name[0] == update.message.text:
                        names.append(j.En_Name)
                        
                keyboard = get_keyboard(names, 3)
                keyboard.append([KeyboardButton("change letter")])
                keyboard.append([KeyboardButton("finished")])
                reply_markup = ReplyKeyboardMarkup(keyboard)
                txt = "Which person's phone would you like to view?"
                bot.send_message(text=txt, chat_id=update.message.chat_id, reply_markup=reply_markup)
            Save_Nameies()
        if str(update.message.chat_id) in newbies:
            txt = ""
            if int(newbies[str(update.message.chat_id)]["stage"]) == 0: #getting the En_Name
                EN_name = update.message.text.encode("utf-8").split(" ")
                En_Name = ""
                for part in EN_name:
                    En_Name += part[0].upper() + part[1:len(part)].lower() + " "
                En_Name = En_Name[:len(En_Name) - 1]
                newbies[str(update.message.chat_id)]["JBer"].set_English_Name(En_Name)
                txt = "is your full name in English: %s?" % En_Name
                keyboard = [[InlineKeyboardButton("Yes", callback_data="Gather;True-0"), InlineKeyboardButton("No", callback_data="Gather;False-9")]]
            elif int(newbies[str(update.message.chat_id)]["stage"]) == 1: #getting the He_Name
                HE_name = update.message.text.split(" ")
                He_Name = ""
                for part in HE_name:
                    He_Name += part[0].upper() + part[1:len(part)].lower() + " "
                He_Name = He_Name[:len(He_Name) - 1]
                newbies[str(update.message.chat_id)]["JBer"].set_Hebrew_Name(He_Name)
                txt = "is your full name in Hebrew: %s?" % He_Name
                keyboard = [[InlineKeyboardButton("Yes", callback_data="Gather;True-1"), InlineKeyboardButton("No", callback_data="Gather;False-9")]]
            elif int(newbies[str(update.message.chat_id)]["stage"]) == 2: #getting the phone number
                phone = update.message.text.encode("utf-8")
                if len(phone) == 10:
                    phone_num = "+972-{}-{}-{}".format(phone[1:3], phone[3:6], phone[6:10])
                    newbies[str(update.message.chat_id)]["JBer"].set_Phone_Number(phone_num)
                    txt = "is your phone number: %s?" % phone_num
                    keyboard = [[InlineKeyboardButton("Yes", callback_data="Gather;True-2"), InlineKeyboardButton("No", callback_data="Gather;False-9")]]
                else:
                    bot.send_message(text="a phone number is 10 digits long, please type yours again", chat_id=update.message.chat_id)
                    return
            elif int(newbies[str(update.message.chat_id)]["stage"]) == 3: #getting the bday
                raw_date = update.message.text.encode("utf-8")
                raw_date = raw_date.replace(" ","")
                date_arr = raw_date.split('/')
                if len(date_arr) > 1:
                    try:
                        month = int(date_arr[1])
                        day = int(date_arr[0])
                        if month <= 12 and month > 0 and day <= 31 and day > 0:
                            newbies[str(update.message.chat_id)]["JBer"].set_Birthdate(str(day) + '-' + str(month))
                            txt = "were you born on " + str(day) + " of " + month_arr[month - 1] + "?"
                            keyboard = [[InlineKeyboardButton("Yes", callback_data="Gather;True-3"), InlineKeyboardButton("No", callback_data="Gather;False-9")]]
                        else:
                            raise Exception("birthdate not in the correct format")
                    except Exception:
                        txt = "the date you've sent is invalid, please send it as dd/mm with 2 numbers representing the day and 2 representing the month"
                        bot.send_message(text=txt, chat_id=update.message.chat_id,parse_mode='Markdown')
                else:
                    txt = "please send me the date as *dd/mm*\nBe sure to use */* and not *\\*"
                    bot.send_message(text=txt, chat_id=update.message.chat_id,parse_mode='Markdown')
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(txt, reply_markup=reply_markup)
        elif str(update.message.chat_id) in editing:
            received = update.message.text
            txt = "Would you like to change " + editing[str(update.message.chat_id)]["JBer"].En_Name + "'s "
            if editing[str(update.message.chat_id)]["field"] == 0: #En_Name
                received = received.lower()
                parts = received.split(" ")
                capped = ""
                for p in parts:
                    capped += p[0].upper() + p[1:] + " "
                capped = capped[:-1]
                txt += "English Name from '" + editing[str(update.message.chat_id)]["JBer"].En_Name + "' to '" + capped + "'?"
                change = capped
    ##        elif editing[str(update.message.chat_id)]["field"] == 1: #He_Name
    ##            try:
    ##                print type("Hebrew Name from '" + editing[str(update.message.chat_id)]["JBer"].He_Name + "' to '")
    ##                print type("Hebrew Name from '" + "' to '" + received + "'?")
    ##                txt += "Hebrew Name from '" + editing[str(update.message.chat_id)]["JBer"].He_Name + "' to '" + received + "'?"
    ##                print txt
    ##                change = received.encode("utf8")
    ##            except Exception, c:
    ##                print str(c)
            elif editing[str(update.message.chat_id)]["field"] == 2: #Phone
                if len(received) == 10:
                    phone = "972-" + received[1:3] + "-" + received[3:6] + "-" + received[6:]
                    txt += "Phone number from '" + editing[str(update.message.chat_id)]["JBer"].Phone + "' to '+" + phone + "'?"
                    change = phone
                else:
                    bot.send_message(text="Phone numbers must be 10 digits long.\nPlease send it to me again", chat_id=update.message.chat_id)
            elif editing[str(update.message.chat_id)]["field"] == 3: #Roles
                role = ""
                for r in editing[str(update.message.chat_id)]["JBer"].Roles:
                    role += r + ", "
                role = role[0:len(role) - 2] 
                txt += "Roles from '" + role + "' to '" + received + "'?"
                change = received.replace(", ", "$")
            elif editing[str(update.message.chat_id)]["field"] == 4: #Bday
                if received.lower() == "del":
                    txt += "Birthday and add '-' infront?"
                    change = "_" + str(editing[str(update.message.chat_id)]["JBer"].Birthday.replace("-","_"))
                elif received.lower() == "mark":
                    txt += "Birthday and remove the first '-'?"
                    change = str(editing[str(update.message.chat_id)]["JBer"].Birthday)[1:len(str(editing[str(update.message.chat_id)]["JBer"].Birthday))].replace('-','_')
                else:
                    date_arr = received.split('-')
                    if len(date_arr) > 1:
                        try:
                            month = int(date_arr[1])
                            day = int(date_arr[0])
                            if month <= 12 and month > 0 and day <= 31 and day > 0:
                                txt += "Birthday from " + str(editing[str(update.message.chat_id)]["JBer"].Birthday.split('-')[0]) + " of " + month_arr[int(editing[str(update.message.chat_id)]["JBer"].Birthday.split('-')[1]) - 1] + " to " + str(day) + " of " + month_arr[month - 1] + "?"
                                change = str(day) + "_" + str(month)
                            else:
                                raise Exception("birthdate not in the correct format")
                        except Exception:
                            txt = "the date you've sent is invalid, please send it as dd/mm with 2 numbers representing the day and 2 representing the month"
                            bot.send_message(text=txt, chat_id=update.message.chat_id,parse_mode='Markdown')
                    else:
                        send = "please send me the date as *dd-mm*\nBe sure to use *-* in between"
                        bot.send_message(text=send, chat_id=update.message.chat_id,parse_mode='Markdown')
            else: #id
                txt += "ID number from '" + str(editing[str(update.message.chat_id)]["JBer"].ID) + "' to '" + received + "'?"
                change = received
            editing[str(update.message.chat_id)]["change"] = change
            Save_Editors()
            keyboard = [[InlineKeyboardButton("Yes", callback_data="Conformation;True-"+editing[str(update.message.chat_id)]["JBer"].En_Name), InlineKeyboardButton("No", callback_data="Conformation;False")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(txt, reply_markup=reply_markup)
        elif str(update.message.chat_id) in activitors:
            if activitors[str(update.message.chat_id)]["grade"] == "": #getting grades
                if update.message.text in grades:
                    activitors[str(update.message.chat_id)]["grade"] = update.message.text
                    Save_Activitors()
                    txt = "The grade you chose: " + update.message.text
                    bot.edit_message_text(text=txt,chat_id=update.message.chat_id, message_id=int(activitors[str(update.message.chat_id)]["messageID"]))
                    keyboard = get_keyboard(tags[:4],2)
                    rest = get_keyboard(tags[4:], 3)
                    for r in rest:
                        keyboard.append(r)
                    keyboard.append([KeyboardButton("Choose a different grade")])
                    keyboard.append([KeyboardButton("End")])
                    reply_markup = ReplyKeyboardMarkup(keyboard)
                    txt = "Please send me which tags would you like to view.\nWhen you're finished, just hit 'End'\nTo delete one, send it again"
                    bot.send_message(text=txt,chat_id=update.message.chat_id, reply_markup=reply_markup)
                    txt = "The tags you chose: "
                    if len(activitors[str(update.message.chat_id)]["tags"]) == 0:
                        txt += "None"
                    else:
                        for tag in activitors[str(update.message.chat_id)]["tags"]:
                            txt += tag + ', '
                        txt = txt[:-2]
                    sent = bot.send_message(text=txt,chat_id=update.message.chat_id)
                    activitors[str(update.message.chat_id)]["messageID"] = sent.message_id
            elif not 'End' in activitors[str(update.message.chat_id)]["tags"]: #getting tags
                if not update.message.text in grades:
                    if update.message.text == "Choose a different grade":
                        activitors[str(update.message.chat_id)]["grade"] = ""
                        keyboard = get_keyboard(grades, 3)
                        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
                        txt = "Please send me which grade's activities would you like to view."
                        bot.send_message(text=txt,chat_id=update.message.chat_id, reply_markup=reply_markup, parse_mode='Markdown')
                        sent = bot.send_message(text="The grade you chose: None",chat_id=update.message.chat_id)
                        activitors[str(update.message.chat_id)]["messageID"] = sent.message_id
                        Save_Activitors()
                    elif update.message.text == "End": #getting the activities
                        acts = acts_by_tags(activitors[str(update.message.chat_id)]["grade"], activitors[str(update.message.chat_id)]["tags"])
                        activitors[str(update.message.chat_id)]["files"] = acts
                        Save_Activitors()
                        if len(acts) == 0:
                            txt = "I found no activities that are for the " + activitors[str(update.message.chat_id)]["grade"] + ' grade\n'
                            if activitors[str(update.message.chat_id)]["tags"][0] != "End":
                                txt += "And contains the tags: "
                                for tag in activitors[str(update.message.chat_id)]["tags"]:
                                    if tag != "End":
                                        txt += tag + ', and '
                                txt = txt[:-6]
                            reply = ReplyKeyboardRemove(remove_keyboard="True")
                            bot.send_message(text=txt,chat_id=update.message.chat_id, reply_markup=reply)
                            update.message.reply_text("You can plan this activity, so that next time someone search for this kind of activity, I'll have it on hand", reply_markup=reply)
                            del activitors[str(update.message.chat_id)]
                        elif len(acts) == 1:
                            file_name = str(acts.keys()[0])
                            if not os.path.exists(work_dir + "activities\\" + file_name):
                                download_file_from_google_drive(acts[file_name], work_dir + "activities\\" + file_name)
                            bot.send_document(chat_id=update.message.chat_id, document=open(work_dir + "activities\\" + file_name, 'rb'))
                            reply = ReplyKeyboardRemove(remove_keyboard="True")
                            update.message.reply_text("Thank you!\nKeep planning activities so I can always have some to suggest!", reply_markup=reply)
                            del activitors[str(update.message.chat_id)]
                        elif len(acts) < 20:
                            keyboard = get_keyboard(acts.keys())
                            keyboard.append([KeyboardButton("Choose different tags")])
                            keyboard.append([KeyboardButton("END")])
                            reply_markup = ReplyKeyboardMarkup(keyboard)
                            txt = "I found multiple activities that fit your search, which one would you like me to send you?\nYou can choose as many as you like, just hit 'END' when you're finished"
                            bot.send_message(text=txt,chat_id=update.message.chat_id, reply_markup=reply_markup)
                        else:
                            activitors[str(update.message.chat_id)]["tags"].remove("End")
                            
                            keyboard = get_keyboard(tags[:4],2)
                            rest = get_keyboard(tags[4:], 3)
                            for r in rest:
                                keyboard.append(r)
                            keyboard.append([KeyboardButton("End")])
                            reply_markup = ReplyKeyboardMarkup(keyboard)
                            txt = "I found over 20 activities that fit your search, I suggest to narrow your search and add more tags"
                            bot.send_message(text=txt, chat_id=update.message.chat_id, reply_markup=reply_markup)
                            
                            txt = "The tags you chose: "
                            if len(activitors[str(update.message.chat_id)]["tags"]) == 0:
                                txt += "None"
                            else:
                                for tag in activitors[str(update.message.chat_id)]["tags"]:
                                    txt += tag + ', '
                                txt = txt[:-2]
                                
                            msg = bot.send_message(text=txt,chat_id=update.message.chat_id)
                            activitors[str(update.message.chat_id)]["messageID"] = msg.message_id
                        Save_Activitors()
                    else:
                        if update.message.text in tags:
                            if not update.message.text in activitors[str(update.message.chat_id)]["tags"]:
                                activitors[str(update.message.chat_id)]["tags"].append(update.message.text)
                            else:
                                activitors[str(update.message.chat_id)]["tags"].remove(update.message.text)
                            Save_Activitors()
                            txt = "The tags you chose: "
                            if len(activitors[str(update.message.chat_id)]["tags"]) == 0:
                                txt += "None"
                            else:
                                for tag in activitors[str(update.message.chat_id)]["tags"]:
                                    txt += tag + ', '
                                txt = txt[:-2]
                            bot.edit_message_text(text=txt,chat_id=update.message.chat_id, message_id=activitors[str(update.message.chat_id)]["messageID"])
            else:
                if update.message.text != "END":
                    if update.message.text == "Choose different tags":
                        activitors[str(update.message.chat_id)]["tags"].remove("End")
                        keyboard = get_keyboard(tags[:4],2)
                        rest = get_keyboard(tags[4:], 3)
                        for r in rest:
                            keyboard.append(r)
                        keyboard.append([KeyboardButton("Choose a different grade")])
                        keyboard.append([KeyboardButton("End")])
                        reply_markup = ReplyKeyboardMarkup(keyboard)
                        txt = "Please send me which tags would you like to view.\nWhen you're finished, just hit 'End'\nTo delete one, send it again"
                        bot.send_message(text=txt,chat_id=update.message.chat_id, reply_markup=reply_markup)
                        txt = "The tags you chose: "
                        if len(activitors[str(update.message.chat_id)]["tags"]) == 0:
                            txt += "None"
                        else:
                            for tag in activitors[str(update.message.chat_id)]["tags"]:
                                txt += tag + ', '
                            txt = txt[:-2]
                        sent = bot.send_message(text=txt,chat_id=update.message.chat_id)
                        activitors[str(update.message.chat_id)]["messageID"] = sent.message_id
                        Save_Activitors()
                    else:
                        if update.message.text in activitors[str(update.message.chat_id)]["files"].keys():
                            file_name = str(update.message.text)
                            if not os.path.exists(work_dir + "activities\\" + file_name):
                                download_file_from_google_drive(activitors[str(update.message.chat_id)]["files"][file_name], work_dir + "activities\\" + file_name)
                            bot.send_document(chat_id=update.message.chat_id, document=open(work_dir + "activities\\" + file_name, 'rb'))
                else:
                    del activitors[str(update.message.chat_id)]
                    Save_Activitors()
                    reply = ReplyKeyboardRemove(remove_keyboard="True")
                    update.message.reply_text("Thank you!\nKeep planning activities so I can always have some to suggest!", reply_markup=reply)
        else:
            InFile(bot, update)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def View_Newbies(bot, update):
    try:
        global newbies
        if InFile(bot, update) and IsDev(update.message.chat_id):
            txt = ""
            for k in newbies:
                txt += k + " - "
                if newbies[k]["JBer"].En_Name == "":
                    txt += "N/A\n"
                else:
                    txt += "English Name: %s\n" % newbies[k]["JBer"].En_Name
                    txt += "Hebrew name: %s\n" % newbies[k]["JBer"].He_Name
                    txt += "Phone number: %s\n" % newbies[k]["JBer"].Phone
                    txt += "Birth date: %s" % newbies[k]["JBer"].Birthday
            if txt == "":
                txt = "None"
            bot.send_message(chat_id=update.message.chat_id, text=txt)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def Remove_Newbie(bot, update):
    try:
        if InFile(bot, update) and IsDev(update.message.chat_id):
            id_num = str(update.message.text.split(" ")[1])
            del newbies[id_num]
            Save_Newbies()
            bot.send_message(chat_id=update.message.chat_id, text="removed " + id_num)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        bot.send_message(chat_id=Oz_id, text=Unauthorized)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        bot.send_message(chat_id=Oz_id, text=BadRequest)
        # handle malformed requests - read more below!
    except TimedOut:
        pass
        # handle slow connection problems
    except NetworkError:
        bot.send_message(chat_id=Oz_id, text=NetworkError)
        # handle other connection problems
    except ChatMigrated as e:
        bot.send_message(chat_id=Oz_id, text=e)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        bot.send_message(chat_id=Oz_id, text=TelegramError)
        # handle all other telegram related errors


def Admin(bot, update):
    try:
        if InFile(bot, update) and IsDev(update.message.chat_id):
            txt = "you have the following commands to use:\n"
            txt += "/info <NAME> - to view the contact information of a person\n"
            txt += "/refresh - to commit changes made to the folders or contact file\n"
            txt += "/log - to view the activity logs\n"
            txt += "/per_log - get the permanent log file\n"
            txt += "/newbie - to view the newbies list\n"
            txt += "/remove <ID> - to remove a person from the newbies list\n"
            txt += "/message <TEXT> - send this to the JB group as the bot\n"
            txt += "/edit - to edit the information of a person\n"
            txt += "/birthday - retry birthday\n"
            txt += "exit - to stop the bot"
            bot.send_message(text=txt, chat_id=update.message.chat_id)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def Anonymous(bot, update):
    try:
        if InFile(bot, update):
            if update.message.chat.type == "private":
                message = get_input(update.message.text.lower().split(" "))
                if message != "":
                    with open("logs.txt", 'a') as logf:
                        encrypted = int(update.message.from_user.id) * int(update.message.from_user.id)
                        print "the person with ID sqrt("+ str(encrypted) + ") sent an anonymous message @ " + str(datetime.datetime.now()) + "\n"
                        logf.write("sqrt("+ str(encrypted) + ") sent an anonymous message @ " + str(datetime.datetime.now()) + "\n")
                        logf.close()
                    txt = "*New Anonymous Message:*\n" + message
                    send = Check_Format(txt)
                    bot.send_message(text=send, chat_id=JB_group_id, parse_mode='Markdown')
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def Edit(bot, update):
    try:
        global editing, JB_names
        if InFile(bot, update) and IsDev(update.message.chat_id):
            if update.message.chat.type == "private":
                if update.message.reply_to_message != None:
                    org_msg = update.message.reply_to_message.text
                    if "En_Name" in org_msg and "Bday" in org_msg:
                        jb = org_msg.split('\n')
                        jb_name = get_input(jb[0].split(" "))
                        for jber in JB_names:
                            if jb_name == jber.En_Name:
                                editing[str(update.message.chat_id)] = {"JBer":jber, "field":None, "change":None}
                                break
                        Save_Editors()

                        keyboard = [[InlineKeyboardButton("Yes", callback_data="PreEdit;True"), InlineKeyboardButton("No", callback_data="PreEdit;Flase")]]
                        
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        update.message.reply_text("Are you sure you want to edit " + editing[str(update.message.chat_id)]["JBer"].En_Name + "'s info?", reply_markup=reply_markup)
                    else:
                        txt = "use /info <NAME> to search for the person you want to edit.\nThen, replay to that message with the command /edit"
                        bot.send_message(text=txt, chat_id=update.message.chat_id)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()
                    

def Get_Self(bot, update):
    try:
        if InFile(bot, update):
            jber = None
            if update.message.chat.type == "private":
                name = get_full_name(update)
                print name + " used '/get_me' @ " + str(datetime.datetime.now())
                logs = open("logs.txt","a")
                if not is_ascii(name):
                    logs.write("nonASCII used '/get_me' @ " + str(datetime.datetime.now()) + "\n")
                else:
                    logs.write(name + " used '/get_me' @ " + str(datetime.datetime.now()) + "\n")
                logs.close()
                
                for jb in JB_names:
                    if jb.ID == update.message.chat_id:
                        jber = jb
                        break
                if jber != None:
                    txt = "English Name: " + jber.En_Name + "\n"
                    txt += "Hebrew Name: " + jber.He_Name + "\n"
                    txt += "Phone Number: " + jber.Phone + "\n"
                    txt += "Birthdate: " + jber.Birthday.split("-")[0] + " of " + month_arr[int(jber.Birthday.split("-")[1]) - 1] + "\n"
                    is_JA = True
                    for role in jber.Roles:
                        if role in grades_arr and role != "JB!!!":
                            is_JA = False
                            break
                    for role in jber.Roles:
                        if role in grades_arr:
                            if role == "JB!!!":
                                txt += "You are an NJR, "
                            else:
                                txt += "You are the leader of " + role + " grade, "
                        if "projects" == role or "communication" == role or "store" == role:
                            txt += "You are in charge of the " + role + " in the JBB, "
                        if "treasure" == role or "criticize" == role:
                            txt += "You are the " + role + "r of the JBB, "
                        if role == "dev":
                            txt += "You are part of the Tech Team, "
                        if is_JA:
                            is_JA = False
                            txt += "You are a member of the JA, "
                    txt = txt[:-2]
                    bot.send_message(text=txt, chat_id=update.message.chat_id)
                else:
                    bot.send_message(text="I don't have any info on you.\nYou can start a new conversation with me by pressing /start and I'll check again", chat_id=update.message.chat_id)
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def Activities(bot, update):
    try:
        global activitors, grades, tags

        if InFile(bot, update):
            if update.message.chat.type == "private":
                name = get_full_name(update)
                print name + " used '/activity' @ " + str(datetime.datetime.now())
                logs = open("logs.txt","a")
                if not is_ascii(name):
                    logs.write("nonASCII used '/activity' @ " + str(datetime.datetime.now()) + "\n")
                else:
                    logs.write(name + " used '/activity' @ " + str(datetime.datetime.now()) + "\n")
                logs.close()
                if str(update.message.chat_id) in activitors:
                    if activitors[str(update.message.chat_id)]["grade"] == "":
                        keyboard = get_keyboard(grades, 3)
                        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
                        txt = "Please send me which grade's activities would you like to view."
                        bot.send_message(text=txt,chat_id=update.message.chat_id, parse_mode='Markdown', reply_markup=reply_markup)
                        msg = bot.send_message(text="The grade you chose: None",chat_id=update.message.chat_id)
                        activitors[str(update.message.chat_id)]["messageID"] = msg.message_id
                    elif not "End" in activitors[str(update.message.chat_id)]["tags"]:
                        keyboard = get_keyboard(tags[:4],2)
                        rest = get_keyboard(tags[4:], 3)
                        for r in rest:
                            keyboard.append(r)
                        keyboard.append([KeyboardButton("Choose a different grade")])
                        keyboard.append([KeyboardButton("End")])
                        reply_markup = ReplyKeyboardMarkup(keyboard)
                        bot.send_message(text="Please send me which tags would you like to view.\nWhen you're finished, just hit 'End'\nTo delete one, send it again",chat_id=update.message.chat_id, reply_markup=reply_markup)
                        txt = "The tags you chose: "
                        if len(activitors[str(update.message.chat_id)]["tags"]) == 0:
                            txt += "None"
                        else:
                            for tag in activitors[str(update.message.chat_id)]["tags"]:
                                txt += tag + ', '
                            txt = txt[:-2]
                        msg = bot.send_message(text=txt, chat_id=update.message.chat_id)
                        activitors[str(update.message.chat_id)]["messageID"] = msg.message_id
                    else:
                        keyboard = get_keyboard(activitors[str(update.message.chat_id)]["files"].keys())    
                        keyboard.append([KeyboardButton("END")])
                        keyboard.append([KeyboardButton("Choose different tags")])
                        reply_markup = ReplyKeyboardMarkup(keyboard)
                        txt = "I found multiple activities that fit your search, which one would you like me to send you?\nYou can choose as many as you like, just hit 'END' when you're finished"
                        msg = bot.send_message(text=txt, chat_id=update.message.chat_id, reply_markup=reply_markup)
                        activitors[str(update.message.chat_id)]["messageID"] = msg.message_id
                    Save_Activitors()
                else:
                    keyboard = get_keyboard(grades, 3)
                    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
                    txt = "Please send me which grade's activities would you like to view."
                    bot.send_message(text=txt,chat_id=update.message.chat_id, reply_markup=reply_markup, parse_mode='Markdown')
                    sent = bot.send_message(text="The grade you chose: None",chat_id=update.message.chat_id)
                    activitors[str(update.message.chat_id)] = {"grade":"", "tags":[], "messageID":sent.message_id, "files":{}}
                    Save_Activitors()
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()
    

def DevMessage(bot, update):
    try:
        if InFile(bot, update) and IsDev(update.message.from_user.id):
            txt = get_input(update.message.text.split(" "))
            send = Check_Format(txt)
            bot.send_message(text=send, chat_id=JB_group_id, parse_mode='Markdown')
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()


def stop(bot, update):
    try:
        if InFile(bot, update) and IsDev(update.message.chat_id):
            with open("logs.txt", "a") as logf:
                logf.write("terminating bot @ " + str(datetime.datetime.now()) + "\n")
                logf.close()
            bot.send_message(text="termanating bot", chat_id=update.message.chat_id)
            updater.stop()
            sys.exit()
    except:
        print(traceback.format_exc())
        logs = open("logs.txt","a")
        logs.write(str(traceback.format_exc()) + "\n")
        logs.close()
        

print "REMEMBER TO /EXIT BEFORE CLOSING!!!"
if not os.path.exists("logs.txt"):
    logf = open("logs.txt", 'w')
    logf.close()
with open("logs.txt", "a") as logf:
    logf.write("started the bot @ " + str(datetime.datetime.now()) + "\n")
    logf.close()
bot_token = ""
with open("bot_id.txt", "r") as botID:
    bot_token = botID.read()
    botID.close()
if bot_token != "":
    updater = Updater(token=bot_token)
    queue = updater.job_queue
    queue.run_daily(callback=birthday,time=datetime.time(0,5,0,0),name="auto bday")
    queue.run_daily(callback=newMonth,time=datetime.time(0,5,0,0),name="monthly schedule")
    queue.start()
    dispatcher = updater.dispatcher
    #logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('programmes', prog))
    updater.dispatcher.add_handler(CallbackQueryHandler(button_prog))
    dispatcher.add_handler(CommandHandler('energizer', energizer))
    dispatcher.add_handler(CommandHandler('lullaby', lullabies))
    dispatcher.add_handler(CommandHandler('grades', grade))
    dispatcher.add_handler(CommandHandler('njrs', Njr))
    dispatcher.add_handler(CommandHandler('jb_phone', name_search))
    # dispatcher.add_handler(CommandHandler('Board_phone', board_search))
    dispatcher.add_handler(CommandHandler('banana', bannana))
    dispatcher.add_handler(CommandHandler('embarrassment', emberes))
    dispatcher.add_handler(CommandHandler('jb_board', jbb))
    dispatcher.add_handler(CommandHandler('add_jber', addjb))
    dispatcher.add_handler(CommandHandler('add_energizer', addenergy))
    dispatcher.add_handler(CommandHandler('add_lullaby', addsong))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('next_event', nextEvent))
    dispatcher.add_handler(CommandHandler('next_activity', nextActivity))
    dispatcher.add_handler(CommandHandler('next_month', eventNextMonth))
    dispatcher.add_handler(CommandHandler('this_month', eventThisMonth))
    dispatcher.add_handler(CommandHandler('schedule_for', eventChooseMonth))
    dispatcher.add_handler(CommandHandler('anonymous', Anonymous))
    dispatcher.add_handler(CommandHandler('get_me', Get_Self))
    dispatcher.add_handler(CommandHandler('activity', Activities))

    dispatcher.add_handler(CommandHandler('info', info))
    dispatcher.add_handler(CommandHandler('refresh', Refresh_Command))
    dispatcher.add_handler(CommandHandler('log', logs))
    dispatcher.add_handler(CommandHandler('per_log', Per_log))
    dispatcher.add_handler(CommandHandler('newbie', View_Newbies))
    dispatcher.add_handler(CommandHandler('remove', Remove_Newbie))
    dispatcher.add_handler(CommandHandler('edit', Edit))
    dispatcher.add_handler(CommandHandler('exit', stop))
    dispatcher.add_handler(CommandHandler('message', DevMessage))
    dispatcher.add_handler(CommandHandler('dev', Admin))
    dispatcher.add_handler(CommandHandler('birthday', again_bd))

    dispatcher.add_handler(MessageHandler(Filters.text, info_gather))
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))
    dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member, leaving))
    #updater.dispatcher.add_error_handler(error_callback)

    """use ConversationHandler to maintain a number of conversations"""  # ***************************************************************************************************************************

    updater.start_polling()
    updater.idle()
