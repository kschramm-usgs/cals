#!/bin/python/env
''' script to recalculate the sensitivity from Adam Ringler's python'''

from obspy import UTCDateTime
import obspy as ob
import numpy as np

# read in info from Adam's output
linex=[]
date=[]
period=[]
sens=[]
calAmp=[]
calAmpARP=[]
i=0

outfile=open("myResults_ANMO_sineCal.txt",'w')
# create a header
outfile.write('stat, chan, date, per, sens, calAmp, percDiff\n')
# this needs to be not hard coded, but for now it will suffice
RespSens=86299.5*2029.0

with open('Results_ANMO_sineCal.txt','r') as calInfo:
   mydat = calInfo.read()
   lines = mydat.split('\n')
   for line in lines[:-1]:
      print(line)
      linex = line.split(' ')
      station = linex[1]
      channel = linex[2]
      print('~~~~~~~~~~~~~~~~~~~~~~~~')
      print(linex[2])
      print(linex[3])
      print(linex[4])
      date.append(UTCDateTime(linex[4]))
      period.append(float(linex[5]))
      sens.append(float(linex[6]))
      if(channel=='00'):
        calInF='/msd/IU_'+station+'/'+str(date[i].year)+'/'+str(date[i].julday).zfill(3)+'/_BC0.512.seed'
        calOutF='/msd/IU_'+station+'/'+str(date[i].year)+'/'+str(date[i].julday).zfill(3)+'/00_BHZ.512.seed'
      elif(channel=='10'):
        calInF='/msd/IU_'+station+'/'+str(date[i].year)+'/'+str(date[i].julday).zfill(3)+'/_BC1.512.seed'
        calOutF='/msd/IU_'+station+'/'+str(date[i].year)+'/'+str(date[i].julday).zfill(3)+'/10_BHZ.512.seed'

      calIn=ob.read(calInF,starttime=date[i]+10,endtime=date[i]+550)
      calOut=ob.read(calOutF,starttime=date[i]+10,endtime=date[i]+550)

      # measure the amplitude:
      # the std()*np.sqrt(2) = the amplitude.  as we are dividing the Out/In, then we 
      # can leave off the np.sqrt(2)
      calInAmp=calIn[0].std()
      calOutAmp=calOut[0].std()
      # according to ringler et al 2014, this is how you do it.     
      calAmp.append(calOutAmp/(calInAmp*2.0*np.pi))

      # now the python code that Adam sent does it differently
      calAmpARP.append(calInAmp/calOutAmp)
      
      #he leaves off the 2*pi, which if you are looking at the calAmp in comparison to 
      # a previous year, shouldn't matter. ie Sens2 = (F(t1)/F(t2))*Sens1

      # now to get to the CTBTO number, we need to add in the digitizer and convert
      # to the proper units.
      
      #calculate some stats
      percDiff=100*((sens[i]-calAmpARP[i])/sens[i])
      
      # now to calculate the CALIB for the IMS at 1.0s
      calib=0.0
      if (period[i]==1.0) and (i > 0):
      # to get into the units we need to use a known (?) sensitivity:
      #   sensorVMS is 
         sensorVMS=(calAmpARP[i-1]/calAmpARP[i])*RespSens
         calib = period[i]/(sensorVMS*1.677720e+06*1e-09*2.0*np.pi)

      outfile.write(station+',  '+channel+',  '+str(date[i])+',  '+str(period[i])+',  '
                   +str(sens[i])+',  '+str(calAmpARP[i])+',  '+str(percDiff)+',  '
                   +str(calib)+'\n')

      i=i+1

print(sens,calAmp,calAmpARP)
print(np.isclose(sens,calAmpARP,rtol=1e-03))

