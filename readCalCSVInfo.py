from obspy import UTCDateTime
import csv

net=[]; sta=[]; cha=[]; HFstart=[];LFstart=[]

with open('CalTracker2018.txt','r') as calInfo:
   calDat = csv.reader(calInfo)
   next(calDat,None) 
   for row in calDat:
      net.append(row[0])
      sta.append(row[1])
      cha.append(row[2])
      try:
         HFstart.append(UTCDateTime(row[3]))
      except:
         print('Check HF Cal for '+net[-1]+'_'+sta[-1]+'.')
      try:
         LFstart.append(UTCDateTime(row[4]))
      except:
         print('Check LF Cal for '+net[-1]+'_'+sta[-1]+'.')


