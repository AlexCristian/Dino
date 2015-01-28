#!/usr/bin/env python
import urllib2
import json
import xml.etree.ElementTree as ET
import jenkinsapi
from jenkinsapi.jenkins import Jenkins
import datetime
import socket
from project import *
import threading
import pytz
import time
import os
import pygame
from dateutil import parser

class Struct:
    def __init__(self, **entries): 
        self.__dict__.update(entries)
class Info_Updater(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        #inits
        self.J = None
        self.DEBUG = 0
        self.CHECK_FREQ = 10
        self.RUNNING=True
        self.FETCH_FAILURE=False
        self.LOADING = True
        self.FILE_ROOT = os.path.dirname(os.path.abspath(__file__)) + os.sep
        self.CONFIG_FILE = self.FILE_ROOT + "dino.config"
        self.TEAMCITY_URL = "url:port";
        self.JENKINS_URL = "url:port";

        self.team_projectid_lst = []
        self.jenk_projectid_lst = []
        self.prjs = []
        self.build_status = {}
        return
    def get_status(self):
        for value in self.build_status:
            if value == "FAILURE":
                return "bad"
        return "great"

    def read_projects(self, path):
        self.team_projectid_lst = []
        self.jenk_projectid_lst = []
        file = open(path, "r")
        file_xml = file.read()
        tree = ET.fromstring(file_xml)
        for element in tree:
            if element.attrib['type'] == 'teamcity':
                self.team_projectid_lst.append(element.attrib['id'])
            elif element.attrib['type'] == 'jenkins':
                self.jenk_projectid_lst.append(element.attrib['id'])
        file.close()
    def teamcity_watchdog(self, i):
        status = "ERROR"
        website = urllib2.urlopen("http://" + self.TEAMCITY_URL + "/httpAuth/app/rest/builds/buildType:%28id:" + self.team_projectid_lst[i] + "%29?guest=1")
        website_xml = website.read()
        tree = ET.fromstring(website_xml)
        buildstatus = tree.attrib['status']
        name = tree[1].attrib['projectName']
        date = tree[3].text
        self.build_status[i] = buildstatus
        
        if buildstatus == "SUCCESS":
           status = "OK"

        elif buildstatus == "FAILURE":
            status = "ERROR"
        
        website = urllib2.urlopen("http://" + self.TEAMCITY_URL + "/httpAuth/app/rest/builds/?locator=buildType:(id:" + self.team_projectid_lst[i] + ")&count=5&guest=1")
        website_xml = website.read()
        tree = ET.fromstring(website_xml)
        health  = 0
        buildID = tree[0].attrib['id']
        for element in tree:
            if element.attrib['status'] == 'SUCCESS':
                health += 1
                
        result = Project(name, status, health)
        
        website = urllib2.urlopen("http://" + self.TEAMCITY_URL + "/httpAuth/app/rest/changes?build=id:" + buildID + "&guest=1")
        website_xml = website.read()
        tree = ET.fromstring(website_xml)

        #todo should handle rebuilds ordered manually (perhaps ignore the change)
        if tree.attrib['count'] != '0':
                changeID = tree[0].attrib['id']

            
                website = urllib2.urlopen("http://" + self.TEAMCITY_URL + "/httpAuth/app/rest/changes/id:" + changeID  + "?guest=1")
                website_xml = website.read()
                tree = ET.fromstring(website_xml)
                result.add_build_comment(tree._children[0].text)
                result.add_culprit(tree._children[2].attrib['name'])
            #result.add_avatar(tree._children[2].attrib['username'])
            
        result.set_buildtime(parser.parse(date))
        return result

    def jenkins_watchdog(self, n):
        led_offset = 1
        status = "ERROR"
        job = self.J[self.jenk_projectid_lst[n]]
        try:
            lgb = job.get_last_good_build()
        except Exception, e:
            lgb = None
        lb = job.get_last_build()
        health = 0
        for i in range(0, 5):
            try:
                if job.get_build(lb.get_number()-i).get_status() == "SUCCESS":
                    health+=1
            except Exception, e:
                health+=1
        isrunning =  self.J[self.jenk_projectid_lst[n]].is_running()
        if isrunning == False:
            if lgb != None and lgb == lb:
                self.build_status[n + len(self.team_projectid_lst)] = "SUCCESS";
                if self.DEBUG:
                    print ("Valid build ", self.jenk_projectid_lst[n])
                status = "OK"
            else:
                self.build_status[n + len(self.team_projectid_lst)] = "FAILURE"
                if self.DEBUG:
                    print ("Broken build ", self.jenk_projectid_lst[n])
                status = "ERROR"
        result = Project(self.jenk_projectid_lst[n], status, health)
        result.set_buildtime(lb.get_timestamp())
        s =  Struct(**getattr(lb, "_data"))
        for item in s.culprits:
            culprit = Struct(**item)
            result.add_culprit(culprit.fullName)
        try:
            for item in s.changeSet.items():
                result.add_build_comment(item[1][0]["comment"])
        except Exception, e:
            pass
        return result

    def get_projects(self):
        return self.prjs


    def exit_signal(self):
        self.RUNNING = False

    def is_loading(self):
        return self.LOADING
    def encountered_connection_failure(self):
        return self.FETCH_FAILURE
    def run(self):
        self.read_projects(self.CONFIG_FILE)
        while self.RUNNING:
            self.FETCH_FAILURE = False
            try:
                #Jenkins stuff
                if self.J == None:
                    self.J = Jenkins('http://' + self.JENKINS_URL)
            except Exception, e:
                self.FETCH_FAILURE = True
            try:
                result = []
                for i in range(len(self.team_projectid_lst)):
                    try:
                        result.append(self.teamcity_watchdog(i))
                    except Exception, e:
                        result.append(Project(self.team_projectid_lst[i], "ERROR", -1))
                        self.FETCH_FAILURE = True
                for i in range(len(self.jenk_projectid_lst)):
                    try:
                        result.append(self.jenkins_watchdog(i)) 
                    except Exception, e:
                        result.append(Project(self.jenk_projectid_lst[i], "ERROR", -1))
                        self.FETCH_FAILURE = True
                self.prjs = result
                self.LOADING = False
                time.sleep(self.CHECK_FREQ)
            except Exception, e:
                print "Unhandled error! "
                print e
