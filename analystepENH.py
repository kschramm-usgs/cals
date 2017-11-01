#!/usr/bin/env python

# code from Adam Ringler.


from obspy.core import read, Stream, UTCDateTime
import commands
import glob
import sys
import math
import matplotlib.pyplot as plt
from obspy.signal import cornFreq2Paz
import sys
from scipy.optimize import fsolve, fmin
import numpy

net = 'IC'
debug = True

fin = open('ENHCals','r')


def pzvals(sensor):
    if sensor == 'STS2':
        pz ={'zeros': [0.], 'poles': [-0.035647 - 0.036879j, \
            -0.035647 + 0.036879j], 'gain': 1., 'sensitivity': 1. }
    elif sensor == 'STS1':
        pz ={'zeros': [0.], 'poles': [-0.01234 - 0.01234j, \
            -0.01234 + 0.01234j], 'gain': 1., 'sensitivity': 1. }
    elif sensor == 'T240':
        pz ={'zeros': [0.], 'poles': [-0.0178231 - 0.017789j, \
            -0.0178231 + 0.017789j], 'gain': 1., 'sensitivity': 1. }
    else:
        pz = {'zeros': [-1. -1.j], 'poles': [-1. -1.j], 'gain': 1., 'sensitivity': 1.}


    return pz

def resi(x):
    h=x[1]
    f=x[0]
    paz = cornFreq2Paz(f,h)
    paz['zeros'] = [0]
    paz['sensitivity'] = x[2]
    trOUTsim = trOUT.copy()
    trOUTsim.simulate(paz_remove = paz)
    trOUTsim.trim(trOUTsim.stats.starttime + 50,trOUTsim.stats.endtime - 50)
    trOUTsim.detrend('constant')
    trOUTsim.normalize()
    trINCP = trIN.copy()
    trINCP.trim(trINCP.stats.starttime + 50,trINCP.stats.endtime - 50)
    trINCP.detrend('constant')
    trINCP.normalize()
    comp = sum((trOUTsim.data - trINCP)**2)
    print(comp)

    return comp


fres = open('resultsENH.csv','w')
fres.write('Station, Location, Channel, Year, Day, Time, h, hpert, lp, lppert, scale, resi, resipert \n')
fres.close()


for line in fin:
    
    year,day,time,sta,chan,loc,duration = line.strip().split(',')
    sta = sta.strip()
    loc = loc.strip()
    chan = chan.strip()
    duration = int(duration)
    print line
    #if duration < 100:
    #    continue
    if debug:
        print 'Cal for ' + sta + ' ' + chan + ' ' + loc
    mdgetstr = './mdget.py -n IC -l ' + loc + ' -c ' + chan + \
        ' -s ' + sta + ' -t ' + year + '-' + day + ' -o' + \
        ' \'instrument type\''
    if debug:
        print mdgetstr
    run,output = commands.getstatusoutput(mdgetstr)
    print output
    if debug:
        print output
    try:
        output = output.split(',')[4]
    except:
        print 'We have a problem with: ' + sta + ' ' + chan + ' ' + loc
        continue  
    if 'E300' in output:
        sensor = 'STS1'
        if debug:
            print 'We have an E300'
    elif 'Trillium' in output:
        if debug:
            print 'We have an T-240'
        sensor='T240'
        if not chan == 'BHZ':
            continue
    elif 'STS-1' in output:
        if debug:
            print 'We have an STS-1'
        sensor = 'STS1'
    elif 'STS-2' in output:
        if debug:
            print 'We have an STS-2'
        sensor = 'STS2'
        if not chan == 'BHZ':
            continue
    pz = pzvals(sensor)
    #try:
    if True:
        datastr = '/tr1/telemetry_days/' + net + '_' + sta + '/' + year + \
            '/' + year + '_' + day + '*/' + \
            loc + '_' + chan + '*.seed'
        datafiles = glob.glob(datastr)
        stOUT = Stream()    
        stime = UTCDateTime(year + '-' + day + 'T' + time ) - 5*60  
        for datafile in datafiles:
        
            stOUT += read(datafile,starttime = stime, endtime = stime + duration + 5*60 +500 )
        stOUT.merge()
        if debug:
            print(stOUT)
        # 2015,125,02:26:59.0000, WCI, BHZ, 00, 900
        #bc = '/xs0/seed/IU_WCI/2015/2015_125_IU_WCI/BC0.512.seed'
        #stime2 = UTCDateTime('2015-125T15:47:59') - 5*60
        bc = datastr.replace(loc + '_' + chan,'BC' + loc[0])
        stIN = read(bc,starttime = stime, endtime = stime + duration + 5*60  + 500)
        stIN.merge()
        print(stIN[0])
        print(stOUT[0])
        trIN = stIN[0]
        trOUT = stOUT[0]
        trOUT.filter('lowpass',freq=.1)
        trIN.filter('lowpass',freq=.1)
        trIN.detrend('constant')
        trIN.normalize()
        trOUT.detrend('constant')
        trOUT.normalize()
        temp=trOUT.copy()
        temp.trim(endtime = stime + int(duration/2.))
        if temp.max() < 0.0:
            trOUT.data = - trOUT.data


    #except:
    #    print 'Problem with : ' + sta + ' ' + chan + ' ' + loc
    #    continue

    
    
    #try:
    if True:
        f = 1. /(2*math.pi / abs(pz['poles'][0]))
        h = abs(pz['poles'][0].real)/abs(pz['poles'][0])
        sen = 10.0
        x = numpy.array([f, h, sen])
        if debug:
            print 'Using: h=' + str(h) + ' and f=' + str(f)
        bf = fmin(resi,x,xtol=10**-8,ftol=10**-3,disp=False)
        #bf = x    
        if debug:
            print 'Here is the best fit: ' + str(bf)
    #except:
    #    print 'Unable to calculate ' + sta + ' ' + chan + ' ' + loc
    #    continue



    #try:
    if True:


        pazNOM = cornFreq2Paz(f,h)
        pazNOM['zeros']=[0.]

        pazPERT = cornFreq2Paz(bf[0],bf[1])
        pazPERT['zeros']=[0]

        pazFK = pzvals('Notta')

        trOUTsimPert = trOUT.copy()
        trOUTsimPert.simulate(paz_remove = pazPERT)
        trOUTsimPert.trim(trOUTsimPert.stats.starttime + 50,trOUTsimPert.stats.endtime - 50)
        trOUTsimPert.detrend('constant')
        trOUTsimPert.normalize()



        trOUTsim = trOUT.copy()

        trOUTsim.simulate(paz_remove = pazNOM)
        trOUTsim.trim(trOUTsim.stats.starttime + 50,trOUTsim.stats.endtime - 50)
        trOUTsim.detrend('constant')
        trOUTsim.normalize()


        trIN.trim(trIN.stats.starttime + 50,trIN.stats.endtime - 50)
        trIN.detrend('constant')
        trIN.normalize()

        print(trOUTsim)
        print(trIN)
        compOUT = sum((trOUTsim.data - trIN.data)**2)
        compOUTPERT = sum((trOUTsimPert.data - trIN.data)**2)
        fres = open('results.csv','a')
        fres.write(sta + ', ' + loc + ', ' + chan + ', ' + stime.formatSEED() + ', ' + str(h) + ', ' + str(bf[1]) + ', ' + \
            str(f) + ', ' + str(bf[0]) + ', ' + str(bf[2]) + ', ' + str(compOUT) + ', ' + str(compOUTPERT) + '\n')
        fres.close()

    #except:
    #    print 'Unable to do calculation on ' + sta + ' ' + loc + ' ' + chan
    #    continue


    try:


        pltfig = plt.figure(1)
        plt.clf()
        t = numpy.arange(0,trOUTsim.stats.npts /trOUTsim.stats.sampling_rate,trOUTsim.stats.delta)
        plt.plot(t,trIN.data,'b',label = 'Input')
        plt.plot(t,trOUTsim.data,'k',label='h=' + str(round(h,6)) + ' f=' + str(round(f,6)) + ' resi=' + str(round(compOUT,6)))

        plt.plot(t,trOUTsimPert.data,'g',label = 'h=' + str(round(bf[1],6)) + ' f=' + str(round(bf[0],6))+ ' resi=' + str(round(compOUTPERT,6)))
        plt.legend(prop={'size':12},loc='center')
        plt.xlabel('Time (s)')
        plt.ylabel('Cnts normalized')
        #plt.xlim(0, duration + 10*60)
        plt.title('Step Calibration ' + trOUT.stats.station + ' ' + trOUT.stats.channel + ' ' + str(trOUT.stats.starttime.year) + ' ' + \
            str(trOUT.stats.starttime.julday).zfill(3))
        
        plt.savefig(trOUT.stats.station + chan + loc + year + day + 'step.jpg',format = "jpeg", dpi = 200)
    except:
        print 'Unable top plot: ' + sta + ' ' + loc + ' ' + chan
        continue
    
    

    
         


    
        


fin.close()








