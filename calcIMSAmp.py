import glob
import os
from subprocess import Popen, PIPE
from obspy.core import read, UTCDateTime
from obspy.mseed.util import getRecordInformation
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
            #if True:

                if '_BC0' in cal:
                    calOut =cal.replace('_BC0','00_BHZ')
                    print(calOut)
                elif '_BC1' in cal:
                    calOut = cal.replace('_BC1','10_BHZ')
                stdout = Popen('dumpCAL  ' + calOut, shell=True, 
                   stdout=PIPE).stdout
                results = stdout.read()
                ri= getRecordInformation(calOut)
                print(ri)
# what is wrong with the string
# is there a way to reproduce this in obspy?
                result = stdout.read()
                print(results)

                #results = results.split('\\n')
                print('here')
                #for result in results:
                #    print('result'+result)
                #    result = ' '.join(result.split())
                if 'Type: 310' in result:
# 310 is the sine blockette flag.
                   time = result.split(' ')[9]
                   time = time.split(',')
                   time = UTCDateTime(time[0] + '-' + time[1] + 'T' + 
                          time[2])
                   print(time)
                   dur = float(result.split(' ')[13])/10000.
                   per = float(result.split(' ')[15])
                   stIn = read(cal, starttime=time, endtime=time+dur)
                   stOut = read(calOut, starttime=time, endtime=time+dur)
                   rat = stIn[0].std() / stOut[0].std()
                   f.write('Cal ' + stOut[0].stats.station + ' ' + 
                      stOut[0].stats.location + ' ' + ' ' + 
                      time.format_seed() + ' ' + str(per) + 
                      ' ' + str(rat) + '\n')
            except:
                print('Problem with' + cal)
                pass
    f.close()
