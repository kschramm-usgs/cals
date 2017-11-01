#!/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import obspy
import re 

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
idebug=False
#idebug=True

action=[]
AevalCount=[]
AactRed=[]
ApreRed=[]
AstepSize=[]
AxNorm=[]
RevalCount=[]
RactRed=[]
RpreRed=[]
RstepSize=[]
RxNorm=[]
instName='STS2_TGUH_167_tableParams'
file=  instName+'.txt'

with open(file,'r') as f:
   mydat = f.read()
   lines = mydat.split('\n')
   for line in lines:
      if(re.search(',',line)):
         output = line.split(',')
         action.append(output[0])
         if(output[0] == 'Accepted'):
            AevalCount.append(float(output[1]))
            AxNorm.append(float(output[2]))
            ApreRed.append(float(output[3]))
            AactRed.append(float(output[4]))
            AstepSize.append(float(output[5]))
         else:
            RevalCount.append(float(output[1]))
            RxNorm.append(float(output[2]))
            RpreRed.append(float(output[3]))
            RactRed.append(float(output[4]))
            RstepSize.append(float(output[5]))


   plt.figure(figsize=(11,8.5))
   color='mh'
   plt.plot(AevalCount,AxNorm,color,label='xNorm',markersize=13) 
   plt.plot(RevalCount,RxNorm,color,markersize=15) 
   plt.plot(RevalCount,RxNorm,'kx',label='rejected',markersize=13,mew=2.5) 
   plt.xlabel('evaluation number')
   plt.ylabel('xNorm value')
   plt.legend(loc='lower right')
   plt.title('Change in xNorm vs evaluation for: '+instName)
   plt.savefig('pdfs/'+instName+'_xNorm.pdf',format='pdf')

   plt.figure(figsize=(11,8.5))
   plt.plot(AevalCount,ApreRed,'rs',label='preRed',markersize=13) 
   plt.plot(RevalCount,RpreRed,'rs',markersize=13) 
   plt.plot(RevalCount,RpreRed,'kx',markersize=13) 
   plt.plot(AevalCount,AactRed,'b.',label='actRed',markersize=20,alpha=0.5)
   plt.plot(RevalCount,RactRed,'b.',markersize=20,alpha=0.5)
   plt.plot(RevalCount,RactRed,'kx',label='rejected',markersize=13,mew=2.5)
   plt.xlabel('evaluation number')
   plt.ylabel('tolerance value')
   plt.legend(loc='best')
   plt.title('Change in tolerance vs evaluation for: '+instName)
   plt.savefig('pdfs/'+instName+'_Tols.pdf',format='pdf')
#
   plt.figure(figsize=(11,8.5))
   plt.plot(AevalCount,AstepSize,'gd',label='stepSize',markersize=13) 
   plt.plot(RevalCount,RstepSize,'gd',markersize=13) 
   plt.plot(RevalCount,RstepSize,'kx',label='rejected',markersize=13,mew=2.5) 
   plt.xlabel('evaluation number')
   plt.ylabel('step size')
   plt.legend()
   plt.title('Change in step size vs evaluation for: '+instName)
   plt.savefig('pdfs/'+instName+'_stepSize.pdf',format='pdf')
#
   plt.show()
