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
i_twilight = 1 

# 1-Standard time, 2-Summertime (+1h)
# For Germany 1 hour must be added to CT to get CET (i_addToCT=1), 2 hours must be added during summer time (i_addToCT=2).  
i_addToCT = 0

if (i_twilight == 0): Horizon = -(50.0/60.0)*RAD  # normal twilight
elif (i_twilight == 1): Horizon = -6*RAD            # civil twilight
elif (i_twilight == 2): Horizon = -12*RAD           # nautical twilight
elif (i_twilight == 3): Horizon = -18*RAD           # astronomical twilight

Latitude = 50.459227
Longitude = 9.607250
LatitudeInRad = Latitude*RAD

def addToCentralTime(i_year, i_month, i_day): 
  # This is used to calculate the hours that need to be added to CT to get the local time.
  # Returns 1 for normal time and 2 during summer time.
  
  d_date = date(i_year, i_month, i_day)
  
  #calculate last sunday in March
  lastSundayInMarch  = max(week[-1] for week in calendar.monthcalendar(i_year, 3))
  dayOfSummertimeStart = date(i_year,3,lastSundayInMarch)
  #calculate last sunday in October
  lastSundayInOctober = max(week[-1] for week in calendar.monthcalendar(i_year, 10))
  dayOfSummertimeEnd = date(i_year,10,lastSundayInOctober)
  
  if d_date >= dayOfSummertimeStart and d_date <= dayOfSummertimeEnd:
    i_addToCT = 2
  else:
    i_addToCT = 1
	
  if (debug == 1):
    print ('lastSundayInMarch:%d \n' % (lastSundayInMarch))
    print ('dayOfSummertimeStart: ' + str(dayOfSummertimeStart) + '\n')
    print ('lastSundayInOctober:%d \n' % (lastSundayInOctober))
    print ('dayOfSummertimeEnd: ' + str(dayOfSummertimeEnd) + '\n')	
    print ('i_addToCT:%d \n' % (i_addToCT))

  return (i_addToCT)


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
i_addToCT = addToCentralTime(dateToCheck.year, dateToCheck.month, dateToCheck.day);

DOY = float(dateToCheck.strftime('%j'));
i_DOY = int(DOY);

Sunrise = sunrise(DOY)
Sunset  = sunset(DOY)

Sunrise    = Sunrise   - Longitude / 15.0 + i_addToCT
Sunset  = Sunset - Longitude / 15.0 + i_addToCT

# Sunrise
RiseMin,RiseStd = math.modf(Sunrise)
i_RiseMin = int(RiseMin * 60)
i_RiseStd = int(RiseStd)
if (debug == 1):
   print ('Sunrise:{:02d}:{:02d} '.format(i_RiseStd,i_RiseMin))

# Sunset
SetMin,SetStd = math.modf(Sunset)
i_SetMin = int(SetMin * 60)
i_SetStd = int(SetStd)
if (debug == 1):
   print ('Sunset:{:02d}:{:02d} '.format(i_SetStd,i_SetMin))


#crontab stuff starts here
#Either update the existing job or create a new one
mycron = CronTab(user='heiko')

CronjobExists = 0
for item in mycron:
  if item.comment == 'sunset':
    item.hour.on(i_SetStd)
    item.minute.on(i_SetMin)
    CronjobExists = 1

if (CronjobExists == 0): 
  job = mycron.new(command='python /home/heiko/outsideLight/licht_aussen_an.py', comment='sunset')
  job.hour.on(i_SetStd)
  job.minute.on(i_SetMin)

mycron.write()

#Write to logfile
myFile = open('/home/heiko/outsideLight/outsideLight.log', 'a') 
myFile.write(dateToCheck.strftime('%d.%m.%Y %H:%M '))
myFile.write('DOY:{:03d} '.format(i_DOY))
myFile.write('Sunset:{:02d}:{:02d} '.format(i_SetStd,i_SetMin))
myFile.write('Sunrise:{:02d}:{:02d} '.format(i_RiseStd,i_RiseMin))
myFile.write('Twilight:{:d} '.format(i_twilight))
myFile.write('Zone:{:d}'.format(i_addToCT))
myFile.write('\n')
myFile.close()
