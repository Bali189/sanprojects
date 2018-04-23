import os
import time
import datetime
import subprocess

def IsDone():
        reloutput=[]
	outputlist=[]
        done = 1
        with open("ldev.txt", "r") as numfid:
                for line in numfid:
                        outputlist[:] = []
                        line.strip()
			hrcmserialnum = line[23:28]
			Ldev = line[32:36]
			#print(hrcmserialnum)
			Ldev = Ldev[:2] + ':' + Ldev[2:]
			if(hrcmserialnum == '0dd4e'):
   				hrcminst = '10000'
			elif(hrcmserialnum == 'd1b6'):
    				hrcminst = '2100'
			elif(hrcmserialnum == '642a9'):
                                hrcminst = '710'
			elif(hrcmserialnum == '64286'):
                                hrcminst = '711'
                        getcap = subprocess.Popen("export HORCMINST="+hrcminst+";raidcom get ldev -ldev_id "+Ldev+"", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                        output, err = getcap.communicate()
			#print(err)
			#print('LDEV:'+Ldev , 'Hrcminst:'+hrcminst)
			outputlist = output.splitlines()
                        for i, v in enumerate(outputlist):
                                if 'LDEV :' in v:
                                	ldev = line.strip()
                                elif 'VOL_Capacity(BLK)' in v:
                                	volingb = outputlist[i].split(":")[1].strip()
                                	volingbMB = ((int(volingb) * 512)/1024/1024/1024)
                                	volingbMB = round(float(volingbMB),2)
                                elif 'Used_Block(BLK)' in v:
                                	capa = outputlist[i].split(":")[1].strip()
					capainmb = ((int(capa) * 512)/1024/1024/1024)
					capainmb = round(float(capainmb),2)
				elif 'Serial#  :' in v:
					Serialnum = outputlist[i].split(":")[1].strip()
					if(Serialnum == '356654'):
						Serial = 'or1vsp2'
					elif(Serialnum == '410246'):
						Serial = 'or1hds02(SZ2)'
					elif(Serialnum == '410281'):
						Serial = 'or1hds01(SZ1)' 
                        reloutput.append([Serial,ldev,str(volingbMB),capainmb])
		print("----------------------------------------------------------------------------------------------")
		print("| Array\t\t|LDEV \t\t\t\t\t\t| Volume(GB)\t| UsedCapacity(GB)|")
		print("----------------------------------------------------------------------------------------------")
		for xs in reloutput:
			print("  \t|  ".join(map(str,xs)))
		print("----------------------------------------------------------------------------------------------")
			#print(xs)
        return done
IsDone()
