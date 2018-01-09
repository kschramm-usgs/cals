import glob
import os
from obspy.core import read, UTCDateTime
import sys

debug = True
stas = glob.glob('/msd/IU_ANMO')

for sta in stas:
    print('On station: ' + sta)
    f = open('Results_' + sta.split('/')[2],'w')
    for year in range(2013,2017):
        if debug:
            print(year)
        cals = glob.glob(sta + '/' + str(year) + '/*/_BC*')
        
        for cal in cals:
            print(cal)
            try:
               if('_BC0' in cal):
                  calOutFile=cal.replace('_BC0','00_BHZ')
               elif('_BC1' in cal):
                  calOutFile=cal.replace('_BC1','10_BHZ')
               elif('_BC6' in cal):
                  calOutFile=cal.replace('_BC6','60_BHZ')
               print(calOutFile)
# use the details=True option when reading in the stream.            
               calOut=read(calOutFile,details=True)
               for i in range(0,len(calOut)-1):
                  if(calOut[i].stats.mseed['calibration_type']):
                     print(calOut[i].stats.mseed['calibration_type'])
               # now that we have the file being read in we need to figure out which 
               # sine wave to process
               # looks like it takes ca. 300s to get to the flat part.

               #dur = float(result.split(' ')[13])/10000.
               #per = float(result.split(' ')[15])
               #stIn = read(cal, starttime=time, endtime=time+dur)
               #stOut = read(calOut, starttime=time, endtime=time+dur)
               #rat = stIn[0].std() / stOut[0].std()
               #f.write('Cal ' + stOut[0].stats.station + ' ' + 
               #   stOut[0].stats.location + ' ' + ' ' + 
               #   time.format_seed() + ' ' + str(per) + 
               #   ' ' + str(rat) + '\n')
            except:
                print('Problem with' + cal)
                pass
    f.close()
