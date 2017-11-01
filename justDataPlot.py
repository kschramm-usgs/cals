#!/bin/env python

from obspy.core.utcdatetime import UTCDateTime
import numpy as np
import matplotlib.pyplot as plt
import obspy
import pylab
from cycler import cycler

def rms(x):
   return np.sqrt(np.mean(np.power(x,2)))


def readAline(data):
   import re 
   if(re.search(',',data)):
      outputData=(np.fromstring(data,sep=','))
   else:
      outputData=data.strip()
   return outputData

def readAcomplexline(data):
   data.rstrip(']')
   data.lstrip('[')
   c_strs = data.split(',')
   tmpData=map(lambda x:x.replace(" ",""),c_strs)
   outputData=[]
   for value in tmpData:
      outputData.append(complex(value))
   outputArray=np.array(outputData)   
   
   return outputArray

def toComplex(field):
   return complex(field.replace(' ',''))


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
idebug=False
#idebug=True

polesToFit=[]
PAZpercD=[]
tmp1=[]
oldPoles=[]
stepData=[]
prevAmp=[]
prevPhase=[]
residAmp=[]
residPhase=[]
smallnessPAZ=[]
javaResid=[]
Jacobian1=[]
Jvalues1=[]
JRMS=[]
initialJacobian1=[]
initialJvalues1=[]
initialJRMS=[]
stopCheckStep=[]
stopCheckInst=[]
stopCheckModel=[]
LastIter=26
instName='STS2_GSN4_285_tolsEQ1e-10'
file=  instName+'.txt'

#file='/home/kschramm/java/asl_sensor_suite/STS6_6pole.txt'
#file='/home/kschramm/java/asl_sensor_suite/STS6_4pole.txt'

with open(file,'r') as f:
   mydat = f.read()
   mydat = mydat.replace("[","")
   mydat = mydat.replace("]","")
   lines = mydat.split('\n')
   j=11
   initialCurve=readAline(lines[j])
   #if(idebug):plt.plot(initialCurve)
   #if(idebug):plt.show()
   j=j+1
   if(idebug):print('the value of j after initial vals= '+str(j))
   initialPAZ=readAline(lines[j])
   j=j+1
   if(idebug):print('the value of j after inital paz= '+str(j))
   initialGuess=readAline(lines[j])
   stepData=initialGuess
   j=j+1
   if(idebug):print('start reading step  1 of jacobian info: '+str(j))

   numPAZ=len(initialPAZ)
   for PAZ in initialPAZ:
      initialJacobian1.append(readAline(lines[j]))
      if(idebug):print('At Jacobian1: the value of j = '+str(j)+str(initialJacobian1))
      j=j+1

      tmp1=(readAline(lines[j]))
      initialJvalues1.append(np.array(tmp1))
      if(idebug):print('At Jvalues: the value of j = '+str(j)+str(initialJvalues1))
      j=j+1

      tmp2=readAline(lines[j])
      #print(tmp2)
      
      initialJRMS.append(float(tmp2))
      if(idebug):print('At RMS: the value of j = '+str(j)+str(initialJRMS))
      j=j+1

   if(idebug):print('initialJvalues'+str(initialJvalues1)+' at j = '+str(j))
   javaResid.append(float(readAline(lines[j])))
   residual=float(readAline(lines[j]))
   j=j+1
   if(idebug):print('the value of j = '+str(j))
   if(idebug):print('initialresid'+str(javaResid))
    
#iterate
#break up the initial curve
   halfway = int(len(initialCurve)/2)
   initialAmp=initialCurve[0:halfway]
   amp=initialAmp
   initialPhase=initialCurve[halfway+1:]
   phase=initialPhase
   initialGAmp=initialGuess[0:halfway]
   initialGPhase=initialGuess[halfway+1:]
#set a few variables prior to looping
   amp=initialAmp
   phase=initialPhase
   PAZToFit=initialPAZ
   if(idebug):print('initial len: '+str(len(amp)))
   if(idebug):print('starting iteration loop')
#break up line into amplitude and phase components
   for i in range(int(len(lines)/2-5)):
      step=i+1
#save old values
      oldPAZ=PAZToFit
      oldAmp=amp
      oldPhase=phase
# read poles and zeros
      PAZToFit=readAline(lines[j])
      if(idebug):print('this is paz to fit '+str(PAZToFit))
      j=j+1
      if(idebug):print('the value of j = '+str(j))

      for ii in range(len(initialPAZ)):
         pazRes=PAZToFit[ii]-initialPAZ[ii]
         pazAvg=(PAZToFit[ii]+initialPAZ[ii])/2.
         PAZpercD.append(float(pazRes/pazAvg))
      if(idebug):print('this is paz to fit '+str(PAZToFit))
# read step data
      oldStepData=stepData
      stepData=readAline(lines[j])
      j=j+1
      if(idebug):print('the value of j = '+str(j))
# need to break up the step data inro amp and phase
      halfway = int(len(stepData)/2)
      amp=stepData[0:halfway]
      phase=stepData[halfway+1:]
      if(idebug):print('the length of amp '+str(len(amp)))
# take difference and sum up to see if we hit the test criteria
      diffStep=(stepData-oldStepData)**2
      diffModel=(stepData-initialGuess)**2
      diffInst=(stepData-initialCurve)**2
      stopCheckInst.append(np.abs(np.sum(diffInst)))
      stopCheckModel.append(np.abs(np.sum(diffModel)))
      stopCheckStep.append(np.abs(np.sum(diffStep)))
      diffAmp=(amp-oldAmp)**2
      stopCheckAmp=np.abs(np.sum(diffAmp))
      diffPhase=(phase-oldPhase)**2
      stopCheckPhase=np.abs(np.sum(diffPhase))
      #print('stop check: '+str(stopCheckStep)+', '+str(stopCheckAmp)+', '+str(stopCheckPhase))
      if(stopCheckStep[step-1]<=1e-15):
         print('sum of difference squared lt cost tolerance at step '+str(step))

# read jacobian
      for ii in range(len(initialPAZ)):
         if(idebug):print('assigning jacobian signs: '+str(ii))
         if(idebug):print(readAline(lines[j]))
         Jacobian1.append(readAline(lines[j]))
         j=j+1
         if(idebug):print('the value of j = '+str(j))
         tmp1=(readAline(lines[j]))
         Jvalues1.append(np.array(tmp1))
         j=j+1
         if(idebug):print('the value of j = '+str(j))
         JRMS.append(readAline(lines[j]))
         if(idebug):print(JRMS)
         j=j+1
      if(idebug):print('old J resid'+str((javaResid)))
      if(idebug):print('javaResid:'+str(readAline(lines[j])))
# read residual
      javaResid.append(float(readAline(lines[j])))
      prevRes=residual
      residual = (float(readAline(lines[j])))
      if(step==LastIter):
         compResid=float(readAline(lines[j]))
      if(np.abs(residual-prevRes)<=1e-15):
         print(abs(residual-prevRes))
         print('residual difference between steps lt cost tolerance at step '+str(step))
      j=j+1
      if(idebug):print('the value of j = '+str(j))
      if(idebug):print('Jvalues'+str((Jvalues1[0])))


   # if you want to look at changes relative to the input response
      residAmp=amp-initialAmp
      meanAmp=np.sum(residAmp**2)
      residPhase=phase-initialPhase
      meanPhase=np.sum(residPhase**2)
      residPAZ=PAZToFit-initialPAZ
      if(idebug):print(meanAmp, meanPhase)

      plt.figure(figsize=(11,8.5))
      plt.subplot(2,1,1)
      plt.semilogx(initialGAmp,'r.',label='Input Response',linewidth=6.0)
      #plt.semilogx(0.95*initialGAmp,':r',label='5 % Input Response')
      #plt.semilogx(1.05*initialGAmp,':r',label='5 % Input Response')
      plt.semilogx(initialAmp,'b.',label='Inst. Output',linewidth=5.0)
      plt.semilogx(amp,'lime',label='step '+ str(step),linewidth=4.0)
      plt.semilogx(residAmp,'crimson',label='difference from Inst Output, resid = '+str(residual))
      plt.title('Amplitude: '+instName)
      #plt.legend(bbox_to_anchor=(0,.01),loc=2,borderaxespad=0.)
      plt.legend()

      plt.subplot(2,1,2)
      plt.semilogx(initialGPhase,'r',label='Input Response',linewidth=6.0)
      plt.semilogx(initialPhase, 'b',label='Inst. Output ',linewidth=5.0)
      plt.semilogx(phase, 'lime', label='step '+ str(step),linewidth=4.0)
      plt.semilogx(residPhase,'crimson',label='difference from Inst Output')
      plt.title('Phase: '+instName)
      #plt.legend(bbox_to_anchor=(0,.01),loc=2,borderaxespad=0.)
      plt.legend()

      #plt.subplot(1,3,3)
      #plt.plot(initialPAZ,'^',label='Input Zeros and Poles',markersize=12)
      #plt.plot(PAZToFit,'s',label='step '+str(step))
      #plt.plot(residPAZ, 'o', label='difference from input')
      #plt.title("Zero and Poles")
      #plt.legend(bbox_to_anchor=(0,.01),loc=2,borderaxespad=0.)

      #plt.show()
      plt.savefig('pdfs/'+instName+'_'+str(step).zfill(2)+'.pdf',format='pdf')
      #plt.close()
      
      if(len(lines)-1 == j): break
   
   if(idebug):print("Number of steps = "+str(step))
   javaResid=np.array(javaResid)
   plt.figure(figsize=(11,8.5))
   plt.semilogy(javaResid)
   plt.title('Residuals from Java: '+instName)
   plt.savefig('pdfs/'+instName+'_Residuals.pdf',format='pdf')
   #plt.show()

   residDiff=np.diff(javaResid)
   residDiffFromFitResid=javaResid-compResid
   plt.figure(figsize=(11,8.5))
   plt.subplot(2,1,1)
   plt.plot(residDiff,label='change by step',linewidth=5.0)
   plt.plot(residDiffFromFitResid,label='change from best fit residual',linewidth=4.0)
   plt.legend()
   plt.title('Residual difference between iterations: '+instName)
   #plt.xlim(7,len(residDiff))
   plt.subplot(2,1,2)
   plt.plot(stopCheckStep,'lime',label='cost Function by step',linewidth=5.0)
   plt.plot(stopCheckModel,'r',label='sum of squared difference from Input Resp',linewidth=5.0)
   plt.plot(stopCheckInst,'b',label='sum of squared difference from Inst Output',linewidth=4.0)
  # plt.plot(residDiffFromFitResid,label='change from best fit residual')
  # #plt.ylim(-0.5, 0.5)
   plt.legend()
   plt.savefig('pdfs/'+instName+'_ResidualDiff.pdf',format='pdf')
   #plt.show()
   

# plot up the number of positve and negative values in the jacobian
   toPlot=False
   if(toPlot):
      width=1/len(PAZToFit)
      plotstep=1
      pazStart=2
      pazEnd=2+len(PAZToFit-1)
      if(idebug):print(step)
      for nstep in range(step):
         plt.figure(figsize=(11,8.5))
         jstepVals=Jvalues1[pazStart:pazEnd]
         pazStart+=len(PAZToFit)
         pazEnd+=len(PAZToFit)
         if(idebug):print('len jstepVals'+str(len(jstepVals)))
         for ii in range(len(jstepVals)):
             if(idebug):print(plotstep)
             plotstep+=width
             if(idebug):print('jstepval'+str(jstepVals))
             stepVal=jstepVals[ii]
             if(idebug):print('stepval'+str(stepVal))
             plt.bar(plotstep,stepVal[0],width,color='k')
             plt.bar(plotstep,stepVal[1],width,bottom=stepVal[0],color='r')
         if(idebug):print(ii)
         plt.title('Sign of jacobian values: '+instName)
         plt.savefig('pdfs/'+instName+'_'+str(nstep)+'_jacobianSign.pdf',format='pdf')
   #plt.legend()

   NUM_COLORS=len(PAZToFit)
   cm=pylab.get_cmap('gist_rainbow')
   plt.figure(figsize=(11,8.5))
   for jj in range( len(PAZToFit)):
      for ii in range(len(PAZpercD)):
         valuesIwant=PAZpercD[jj:len(PAZpercD):len(PAZToFit)]
      plt.plot(np.array(valuesIwant)*100,label=(initialPAZ[jj]),)
   plt.legend()
   plt.title('Percent diff of PAZ real and imag components: '+instName)
   plt.savefig('pdfs/'+instName+'_PAZPercDiff.pdf',format='pdf')

   plt.figure(figsize=(11,8.5))
   print(len(JRMS))
   for jj in range( len(PAZToFit)):
      for ii in range(len(PAZpercD)):
         valuesIwant=JRMS[jj:len(PAZpercD):len(PAZToFit)]
      plt.plot(np.array(valuesIwant),label=(initialPAZ[jj]),linewidth=6.0)
   plt.legend()
   plt.title('RMS of Jacobian for PAZ real and imag components: '+instName)
   plt.savefig('pdfs/'+instName+'_PAZPercDiff.pdf',format='pdf')

   plt.show()
