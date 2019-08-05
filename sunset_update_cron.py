#!/usr/bin/env python

import math
import datetime
import calendar
from datetime import date
from crontab import CronTab

debug = 0
pi = 3.1415926536
RAD = pi/180.0

# 0-normal twilight, 1-civil twilight, 2-nautical twilight, 3-astronomical twilight
Twilight = 1 

if (Twilight == 0): Horizon = -(50.0/60.0)*RAD  # normal twilight
elif (Twilight == 1): Horizon = -6*RAD            # civil twilight
elif (Twilight == 2): Horizon = -12*RAD           # nautical twilight
elif (Twilight == 3): Horizon = -18*RAD           # astronomical twilight

Latitude = 50.459227
Longitude = 9.607250
LatitudeInRad = Latitude*RAD

def setzone(i_year, i_month, i_day): #This is used to find the first and last day of summer time.
  
  d_date = date(i_year, i_month, i_day)
  
  #calculate last sunday in March
  day3  = max(week[-1] for week in calendar.monthcalendar(i_year, 3))
  dayOfSummertimeStart = date(i_year,3,day3)
  #calculate last sunday in October
  day10 = max(week[-1] for week in calendar.monthcalendar(i_year, 10))
  dayOfSummertimeEnd = date(i_year,10,day10)
  
  if d_date >= dayOfSummertimeStart and d_date <= dayOfSummertimeEnd:
    Zone = 2
  else:
    Zone = 1
	
  if (debug == 1):
    print ('day3:%d \n' % (day3))
    print ('dayOfSummertimeStart: ' + str(dayOfSummertimeStart) + '\n')
    print ('day10:%d \n' % (day10))
    print ('dayOfSummertimeEnd: ' + str(dayOfSummertimeEnd) + '\n')	
    print ('Zone:%d \n' % (Zone))

  return (Zone)


def sunDeclination(DOY):
  #declination of the sun
  return (0.409526325277017*math.sin(0.0169060504029192*(DOY-80.0856919827619)));


def timeDifference(Deklination):
  #Time from sunrise to noon
  return (12.0*math.acos((math.sin(Horizon) - math.sin(LatitudeInRad)*math.sin(Deklination)) / (math.cos(LatitudeInRad)*math.cos(Deklination)))/pi);


def timeFormula(DOY):
  #Equation of time
  return (-0.170869921174742*math.sin(0.0336997028793971 * DOY + 0.465419984181394) - 0.129890681040717*math.sin(0.0178674832556871*DOY - 0.167936777524864));

def sunrise(DOY):
  DK = sunDeclination(DOY)
  return (12 - timeDifference(DK) - timeFormula(DOY));

def sunset(DOY):
  DK = sunDeclination(DOY)
  return (12 + timeDifference(DK) - timeFormula(DOY));




#######################
#main here


dateToCheck = datetime.datetime.today();
Zone = setzone(dateToCheck.year, dateToCheck.month, dateToCheck.day);

DOY = float(dateToCheck.strftime('%j'));

Sunrise = sunrise(DOY)
Sunset  = sunset(DOY)

Sunrise    = Sunrise   - Longitude / 15.0 + Zone
Sunset  = Sunset - Longitude / 15.0 + Zone

# print Sunrise
RiseMin,RiseStd = math.modf(Sunrise)
RiseMin = RiseMin * 60
#print ('Sunrise   : ' + '%02d:%02d' % (RiseStd,RiseMin))

# print Sunset
SetMin,SetStd = math.modf(Sunset)
SetMin = SetMin * 60
#print ('Sunset : ' + '%02d:%02d' % (SetStd,SetMin))

#crontab stuff starts here
#Either update the existing job or create a new one
mycron = CronTab(user='heiko')

CronjobExists = 0
for item in mycron:
  if item.comment == 'sunset':
    item.hour.on(int(SetStd))
    item.minute.on(int(SetMin))
    CronjobExists = 1

if (CronjobExists == 0): 
  job = mycron.new(command='python /home/heiko/outsideLight/licht_aussen_an.py', comment='sunset')
  job.hour.on(int(SetStd))
  job.minute.on(int(SetMin))

mycron.write()

#Write to logfile
myFile = open('/home/heiko/outsideLight/outsideLight.log', 'a') 
myFile.write(dateToCheck.strftime('%d.%m.%Y %H:%M '))
myFile.write('DOY:%d ' % (DOY))
myFile.write('Sunset:%d:%d ' % (SetStd, SetMin))
myFile.write('Sunrise:%d:%d ' % (RiseStd, RiseMin))
myFile.write('Twilight:' + str(Twilight))
myFile.write(' Zone:%d' % (Zone))
myFile.write('\n')
myFile.close()
