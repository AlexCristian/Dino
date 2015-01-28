#!/usr/bin/env python
import pygame
from pygame.locals import *
import update_info
from update_info import *
from pygame.locals import *
import threading
import time
import datetime
import pytz
import commands
import socket
from sys import platform as _platform

ENABLE_ANIMATIONS = False
MAX_FPS = 30
START_Y = 200
LINE_INCREMENT_Y = 80
SHADOW_SIZE = 10
MARGIN_SIZE = 15
TITLE_X = 20
TITLE_Y = 70
CLOCK_MX = 300
CLOCK_Y = 90
DEBUG = False
ANIM_Y_OFFSET = 0
ANIM_X_OFFSET = 0
SLIDE_INTERVAL = 3.0
ANIMATION_LENGTH = 1
ASSETS_PATH = os.path.dirname(os.path.abspath(__file__)) + os.sep + "weather" + os.sep

projects = []

def get_wlan_IP():
    if _platform == "win32":
        intf_ip = socket.gethostbyname(socket.gethostname())
    else:
        intf = 'wlan0'
        intf_ip = commands.getoutput("ip address show dev " + intf).split()
        intf_ip = intf_ip[intf_ip.index('inet') + 1].split('/')[0]
    return intf_ip

def repaint_screen():
    global change_time, ANIM_Y_OFFSET, ANIM_X_OFFSET, BGN_INDEX, END_INDEX, initialized_indexes, running_x_anim, FPS, WEATHER_IMAGE
    #Render the background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((48,48,48))

    #Render title bar
    tbar = pygame.Rect(0, 0, dinfo.current_w, 30)
    color = pygame.Color(3, 101, 100)
    background.fill(color, tbar)
    
    #Render title bar text
    font = pygame.font.Font(None, 25)
    computer_ip = "Unavailable"
    try:
      computer_ip = get_wlan_IP()
    except ValueError:
      computer_ip = "Unavailable"
    text = font.render("Dino 2.0 on IP:" + computer_ip +  " - Services build status", 1, (255, 255, 255))
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.y = 5 
    background.blit(text, textpos)
 
    current_y=START_Y
    active_services=0
    
    #Enable animations for long lists
    now = time.time()
    if len(projects) > NR_TILES:
        if initialized_indexes == False:
            BGN_INDEX = 0
            END_INDEX = NR_TILES
            initialized_indexes = True
        if now - change_time >= SLIDE_INTERVAL and running_x_anim == False:
            if ENABLE_ANIMATIONS == True:
                ANIM_Y_OFFSET+= float(LINE_INCREMENT_Y / float(FPS * ANIMATION_LENGTH))
                if ANIM_Y_OFFSET > LINE_INCREMENT_Y:
                    running_x_anim = True
                    ANIM_Y_OFFSET = 0
                    ANIM_X_OFFSET = dinfo.current_w
                    BGN_INDEX -= 1
                    END_INDEX -= 1
                    if BGN_INDEX < 0:
                        BGN_INDEX = len(projects)-1
                    if END_INDEX < 0:
                        END_INDEX = len(projects) - 1
            else:
                change_time = now
                BGN_INDEX -= 1
                END_INDEX -= 1
                if BGN_INDEX < 0:
                    BGN_INDEX = len(projects)-1
                if END_INDEX < 0:
                    END_INDEX = len(projects) - 1
        elif now - change_time >= SLIDE_INTERVAL and running_x_anim == True:
            ANIM_X_OFFSET -= float(dinfo.current_w / float(FPS * ANIMATION_LENGTH))
            if ANIM_X_OFFSET < 0:
                change_time = now
                ANIM_X_OFFSET = 0
                running_x_anim = False
    else:
        BGN_INDEX = 0
        END_INDEX = len(projects) -1
        initialized_indexes = False
    
    #Render projects
    current_y += ANIM_Y_OFFSET
    i = BGN_INDEX - 1
    while END_INDEX != -1 and i != END_INDEX:
        i += 1
        if i > len(projects) - 1:
            i -= len(projects)
        project = projects[i]
        X_OFFSET = 0
        if running_x_anim == True and i == BGN_INDEX:
            X_OFFSET = ANIM_X_OFFSET
        if project.status == "OK":
            active_services+= 1
        font = pygame.font.Font(None, 36)
        text = font.render(project.name, 1, (255, 255, 255))
        textpos = text.get_rect()
        textpos.x = 100+MARGIN_SIZE+X_OFFSET
        textpos.y = current_y
        
        cprtfont = pygame.font.Font(None, 25)
        culprits = "";
        for culprit in project.culprits:
            culprits += culprit + ", "
        culprits = culprits[:-2]
        culprits = (culprits[:50] + '...') if len(culprits) > 50 else culprits
        cprttext = cprtfont.render(culprits, 1, (255, 255, 255))
        cprttextpos = text.get_rect()
        cprttextpos.x = ERROR_DISPLAY + MARGIN_SIZE + X_OFFSET
        cprttextpos.y = current_y-10
        
        msgfont = pygame.font.Font(None, 36)
        msgtext = msgfont.render(project.comment, 1, (180, 180, 180))
        msgtextpos = msgtext.get_rect()
        msgtextpos.x = ERROR_DISPLAY + MARGIN_SIZE + X_OFFSET
        msgtextpos.y = current_y+10
        
        if project.buildtime != None:
            timefont = pygame.font.Font(None, 36)
	    elapsed = (pytz.utc.localize(datetime.datetime.utcnow()) - project.buildtime).total_seconds()
            m, s = divmod(elapsed, 60)
            h, m = divmod(m, 60)
            d, h = divmod(h, 24)
            elapsedstr = ""
            if d != 0:
                elapsedstr += ("%d days, " % d) if d>1 else ("%d day, " % d)
            if h != 0:
                elapsedstr += ("%d hours, " % h) if h>1 else ("%d hour, " % h)
            if m != 0:
                elapsedstr += ("%02d minutes, " % m) if m>1 else ("%02d minute, " % m)
            elapsedstr = elapsedstr[:-2]
            timetext = timefont.render(elapsedstr, 1, (255, 255, 255))
            timetextpos = timetext.get_rect()
            timetextpos.x = dinfo.current_w-MARGIN_SIZE-20-timetextpos.width+X_OFFSET
            timetextpos.y = current_y
        
        prect = pygame.Rect(MARGIN_SIZE+X_OFFSET, textpos.top-(LINE_INCREMENT_Y/2-8)+MARGIN_SIZE, dinfo.current_w-MARGIN_SIZE*2, LINE_INCREMENT_Y-MARGIN_SIZE)        
        prect_color = project.color
        pshadow = pygame.Rect(prect.x, prect.bottom-SHADOW_SIZE, prect.width, SHADOW_SIZE)        
        pshadow_color = project.color_shadow

        phealth = WEATHER_IMAGE[project.health]
        health_sqrdim = LINE_INCREMENT_Y-MARGIN_SIZE-10
        phrect = pygame.Rect(MARGIN_SIZE+20+X_OFFSET, current_y-15, health_sqrdim, health_sqrdim)
        
        background.fill(prect_color, prect)
        background.fill(pshadow_color, pshadow)
        background.blit(text, textpos) 
        if project.buildtime != None:
            background.blit(timetext, timetextpos) 
        if project.status != "OK":
            background.blit(msgtext, msgtextpos) 
            background.blit(cprttext, cprttextpos)
        background.blit(phealth, phrect)
        
        current_y += LINE_INCREMENT_Y

    #Paint overall status
    font = pygame.font.Font(None, 70)
    if FETCH_FAIL == True:
        stat_string = "Network connection severed"
        status = "ERROR"
    elif loading == True:
        stat_string = "Please wait, polling services"
        status = "WARNING"
    elif active_services == len(projects):
        stat_string = "All services online"
        status = "OK"
    elif active_services < len(projects) and active_services > 0:
        stat_string = "Some services are down"
        status = "WARNING"
    else:
        stat_string = "All services are offline"
        status = "ERROR"

    title_text = font.render(stat_string, 1, (255, 255, 255))
    title_pos = title_text.get_rect()
    title_pos.x = TITLE_X
    title_pos.y = TITLE_Y
    
    ptrect = pygame.Rect(0, title_pos.y-5, title_pos.width+TITLE_X+20, title_pos.height+20)        
    ptrect_color = BOX_COLOR[status]
    ptshadow = pygame.Rect(ptrect.x, ptrect.bottom-SHADOW_SIZE, ptrect.width, SHADOW_SIZE)        
    ptshadow_color = BOX_COLOR_SHADOW[status]
    
    clockfont = pygame.font.Font(None, 90)
    ctime = datetime.datetime.now().strftime("%H:%M:%S")
    clock_text = clockfont.render(ctime, 1, (255, 255, 255))
    clock_pos = clock_text.get_rect()
    clock_pos.x = dinfo.current_w - CLOCK_MX
    clock_pos.y = CLOCK_Y
    
    datefont = pygame.font.Font(None, 30)
    date = datetime.datetime.now().strftime("%A, %B %d, %Y")
    date_text = datefont.render(date, 1, (255, 255, 255))
    date_pos = date_text.get_rect()
    date_pos.x = dinfo.current_w - CLOCK_MX
    date_pos.y = CLOCK_Y - 20
    
    
    background.fill(ptrect_color, ptrect)
    background.fill(ptshadow_color, ptshadow)
    background.blit(title_text, title_pos)
    background.blit(clock_text, clock_pos)
    background.blit(date_text, date_pos)
    if DEBUG == True:
        print "Done compositing frame"

    #Paint frame
    screen.blit(background, (0, 0))
    pygame.display.flip() 
    if DEBUG == True:
        print "Done writing frame"

def main():
    global screen, dinfo, projects, loading, ERROR_DISPLAY, NR_TILES, FETCH_FAIL, change_time, BGN_INDEX, END_INDEX, initialized_indexes, running_x_anim, FPS, WEATHER_IMAGE
    FETCH_FAIL = False
    running_x_anim = False
    loading = True
    initialized_indexes = False
    Clock = pygame.time.Clock()
    change_time = time.time()
    pygame.init()
    
    health_sqrdim = LINE_INCREMENT_Y-MARGIN_SIZE-10
    zoomfactor = float(health_sqrdim) / 512
    WEATHER_IMAGE[5] = pygame.transform.rotozoom(pygame.image.load(ASSETS_PATH + 'sunny.png'), 0, zoomfactor)
    WEATHER_IMAGE[4] = pygame.transform.rotozoom(pygame.image.load(ASSETS_PATH + 'sunnycloud.png'), 0, zoomfactor)
    WEATHER_IMAGE[3] = pygame.transform.rotozoom(pygame.image.load(ASSETS_PATH + 'cloudy.png'), 0, zoomfactor)
    WEATHER_IMAGE[2] = pygame.transform.rotozoom(pygame.image.load(ASSETS_PATH + 'rain.png'), 0, zoomfactor)
    WEATHER_IMAGE[1] = pygame.transform.rotozoom(pygame.image.load(ASSETS_PATH + 'thunderstorm.png'), 0, zoomfactor)
    WEATHER_IMAGE[0] = pygame.transform.rotozoom(pygame.image.load(ASSETS_PATH + 'bigthunderstorm.png'), 0, zoomfactor)
    WEATHER_IMAGE[-1] = pygame.transform.rotozoom(pygame.image.load(ASSETS_PATH + 'none.png'), 0, zoomfactor)
    
    FPS = MAX_FPS
    if DEBUG == True:
        print "Starting up..."
        CHECK_FREQ = 1
    else:
        CHECK_FREQ = MAX_FPS
    pygame.mouse.set_visible(False)
    dinfo = pygame.display.Info()
    ERROR_DISPLAY = dinfo.current_w *6/20
    screen = pygame.display.set_mode((dinfo.current_w, dinfo.current_h))
    NR_TILES = dinfo.current_h / (LINE_INCREMENT_Y + 2 * MARGIN_SIZE)
    BGN_INDEX = 0
    if NR_TILES < len(projects):
        END_INDEX = NR_TILES-1
    else:
        END_INDEX = len(projects) - 1
    
    if DEBUG == True:
        print "This screen can fit %d tiles" % NR_TILES
    pygame.display.set_caption("Dino 2.0 - Services build status")
    #Initiate fetcher
    updater = update_info.Info_Updater()
    if DEBUG == True:
        print "Class instantiated!"
    updater.daemon = True
    updater.start()
    if DEBUG == True:
        print "Thread started."
    while 1:
        FETCH_FAIL = False
        #Check for user input
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYDOWN and event.key == 27:
                if DEBUG == True:
                    print "Quitting..."
                updater.exit_signal()
                pygame.display.quit()
                pygame.quit()
                return
        if DEBUG == True:
            print "Fetching"
        try:
            #Fetch current projects
            projects = updater.get_projects()
            loading = updater.is_loading()
            FETCH_FAIL = updater.encountered_connection_failure()
            if DEBUG == True:
                print loading
                print projects
        except Exception, e:
            if DEBUG == True:
                print e
        #Draw frame
        if DEBUG == True:
            print "Painting"
        repaint_screen()
        if DEBUG == True:
            print "Done painting, listening"
        #Sleep now
        if DEBUG == True:
            print "Sleepy time"
        Clock.tick(MAX_FPS)
        cFPS = Clock.get_fps()
        if cFPS != 0:
            FPS = cFPS
if __name__ == "__main__":
    main() 
