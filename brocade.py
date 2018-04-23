import paramiko
import os
import sys
import time
import datetime
import string
import re
import operator

cl_pair_limit = 3
cl_ports_odd =[]
cl_ports_even = []
cmdlist = []
gencmdlist = []
zonepwwnalias = []
pwwnformatted=''
log_file_location = '/Users/bramamur/desktop/'
oddswitchname='sjwtf1b01'
evenswitchname='sjwtf2b01'


class clPortObj(object):  #  list of hosts that can access devices.  1 host std multiple for VMware / RAC clusters. Reference back to class clPairObj
   """__init__() functions the class constructor"""
   def __init__(self, name=None, pwwn_list=[], gid=None):
     self.name = name
     self.pwwn_list = pwwn_list
     self.gid = gid
     
class pwwnObj(object):  #  list of pwwn & alias.  Reference back to class clPairObj - pwwn_list
   """__init__() functions the class constructor"""
   def __init__(self, pwwn='', alias=''):
     self.pwwn = pwwn
     self.alias = alias

hostcreate = input("Do you want to create a New Zone (N) or Exising (E)  :")
if hostcreate == "E" or hostcreate == "e":
	print ('You do not require any zoning \n')
	exit()
print('Select the Storage Array from the below list :')
print ('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
storagearray = {
'1': 'or1vsp01',
'2': 'or1vsp02',
'3': 'or1hds04',
'4': 'or1hds01',
'5': 'or1hds02',
'6': 'sj1vsp03',
'7': 'sj1hds39',
'8': 'sj1hds40',
'9': 'sj1vsp02',
'10': 'indhds08',
'11': 'du1hds002'}
storagearr_sorted = sorted(storagearray.items(), key=operator.itemgetter(1))

for key,value in storagearr_sorted:
	print ('\t\t'+value)


storagearrayinput = input("Enter the Storage Array :")


if(storagearrayinput.startswith('or')):
	oddswitchname = 'sjwtf1b01'
	evenswitchname = 'sjwtf2b01'
	confname_odd = 'SJ_Lab_1'
	confname_even= 'SJ_Lab_2'
elif(storagearrayinput.startswith('sj1')):
	oddswitchname = 'sjet2f1b07'
	evenswitchname = 'sjet2f2b07'
	confname_odd = 'active_fabric1'
	confname_even= 'active_fabric2'
elif(storagearrayinput.startswith('ind')):
	oddswitchname = 'indf1sw04'
	evenswitchname = 'indf2sw04'
	confname_odd = 'active_fab1'
	confname_even= 'active_fab2'
elif(storagearrayinput.startswith('du')):
	oddswitchname = 'du1bf1010'
	evenswitchname = 'du1bf2010'
	confname_odd = 'active_config1'
	confname_even= 'active_config2'

cluster_input = input("Is this a cluster? (y)es / (n)o ")
if cluster_input == "yes" or cluster_input == "y":
		host_count = input("How many hosts will be in the cluster? - ")

cl_count = input("How many CL Pairs are required for this host or cluster? ")
if int(cl_count) > int(cl_pair_limit):  ## pair limit of 3 or 6 HBA's per host
   print ('\n\nHosts are limited to 3 pair or 6 HBAs.  Review with Storage Engineering Team for 4 or more pairs')  
   exit()

for i in range(int(cl_count)):  # enter array port and host pwwn
   print ('Create pair #', i+1) # plus 1 added because range starts at 0
   cl_port_p1 = input ("Enter the ODD CL-Port to be used (ex. cl5-a) ? ")
   cl_ports_odd.append(clPortObj(cl_port_p1))
      
   cl_port_p2 = input("Enter the EVEN CL-Port to be used (ex. cl6-a) ? ")
   cl_ports_even.append(clPortObj(cl_port_p2))
   print ('*****************************************************************')


def fn_pwwn_formatting(wwpn):
	pwwnformatted =''
	if(wwpn.find(';') != -1):
		wwpnlist = wwpn.split(';')
	else:
		wwpnlist=[]
		wwpnlist.append(wwpn)
	for i in wwpnlist:
		if(i.find(':') == -1):
			j = iter(i)
			n = ':'.join(a+b for a,b in zip(j, j))
		else:
			n = i
		if(pwwnformatted !=''):
			pwwnformatted = pwwnformatted+';'+n
		else:
			pwwnformatted = pwwnformatted+n
	#print (pwwnformatted)
	return pwwnformatted

def fn_command_alizonecreate(cl_ports=[]):
	cmdlist=[]
	for cl in cl_ports:
		for pwwn in cl.pwwn_list:
			pwwnformatted = fn_pwwn_formatting(str(pwwn.pwwn))
			alicreatecommand = 'alicreate "'+ str(pwwn.alias)+'", "' + pwwnformatted+'"\n'
			cmdlist.append(alicreatecommand)
			zonepwwnalias = str(pwwn.alias).split('_')
			zonecreatecommand = 'zonecreate "'+str(zonepwwnalias[0])+'", "'+str(pwwn.alias)+';'+storagearrayinput+'_'+cl.name+'"\n'
			cmdlist.append(zonecreatecommand)
	return cmdlist
	
def fn_general_command(cl_ports=[],flag=''):
	gencmdlist = []
	zonename =''
	for cl in cl_ports:
		for pwwn in cl.pwwn_list:
			if(zonename != ''):
				zonename += ';'
			zonepwwnalias = str(pwwn.alias).split('_');
			zonename = zonename + zonepwwnalias[0]	
	if(flag == 'O'):
		confname = confname_odd
	elif(flag == 'E'):
		confname = confname_even
	cfgaddcommand = 'cfgadd "'+confname+'", "'+zonename+'"\n'
	gencmdlist.append(cfgaddcommand)
	gencmdlist.append('cfgsave\n')
	gencmdlist.append('yes\n')
	gencmdlist.append('cfgenable "'+confname+'"\n')
	gencmdlist.append('yes\n')
	gencmdlist.append('exit\n')
	return gencmdlist

def fn_printcommands():
	cmdlist = []
	print('Commands to be executed in Switch - '+ oddswitchname+': \n')
	print('########################################################\n')
	cmdlist = fn_command_alizonecreate(cl_ports_odd)
	gencmdlist = fn_general_command(cl_ports_odd,'O')
	for cmd in cmdlist:
		print (cmd)
	for gen in gencmdlist:
		print (gen)
	cmdlist[:] = []
	gencmdlist[:] = []
	print('Commands to be executed in Switch - '+ evenswitchname+': \n')
	print('########################################################\n')
	cmdlist = fn_command_alizonecreate(cl_ports_even)	
	gencmdlist = fn_general_command(cl_ports_even,'E')
	for cmd in cmdlist:
		print (cmd)
	for gen in gencmdlist:
		print (gen)
		
	execu = input('\nIf you want to continue execution enter (y)es or to abort say (n)o :\n')
	if(execu == 'n' or execu =='N' ):
		exit()
	return

def fn_createaliaszone(hostnameserver = '',cl_ports=[]):
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(hostnameserver,port=22,username='admin',password='Z$v7SDi_')
	channel = ssh.invoke_shell()
	channel_data = str()
	while not channel.recv_ready():
		time.sleep(3)
	channel_bytes = channel.recv(9999)
	channel_data = channel_bytes.decode("utf-8")
	log_file = log_file_location + 'Zoning_' + time_stamp + '.log'
	file = open(log_file, 'a+')
   
	
	cmdlist = []
	gencmdlist = []
	
	if(flag == 'O'):
		#fn_printcommands()
		file.write ('\n\n************* Started executing Fabric A : ' +hostnameserver+'***************')
		print ('\nConnection established to Fabric A: '+hostnameserver+'\n')
		print('####################Starting odd ports########################')
	elif(flag == 'E'):
		file.write ('\n\n************* Started executing Fabric A : ' +hostnameserver+' ***************')
		print ('\nConnection established to Fabric B: '+hostnameserver)
		print('###################Starting even ports #######################')
	file.write ('\nScript Start Time : ' + time_stamp)

	cmdlist[:] = []	
	gencmdlist[:] = []
	cmdlist = fn_command_alizonecreate(cl_ports)
	gencmdlist = fn_general_command(cl_ports,flag)
	
	# Alicreate , Zonecreate commands 
	for cmd in cmdlist:
		file.write('\nCurrently Executing :  '+cmd)
		if channel_data.endswith(hostnameserver+':admin> '):
			channel.send(cmd)
		while not channel.recv_ready():
			time.sleep(3)
		channel_bytes=channel.recv(9999)
		channel_data=channel_bytes.decode("utf-8")
		time.sleep(5)
	index = 0

	# save,add,enable and exit commands 
	for gencmd in gencmdlist:
		file.write('\nCurrently Executing :  '+gencmd)
		#print(channel_data)
		index += 1
		if(index == 3 or index == 5):
			textendswith = '(yes, y, no, n): [no] '
		else:
			textendswith = hostnameserver+':admin> '
		if channel_data.endswith(textendswith):
			channel.send(gencmd)
		while not channel.recv_ready():
			time.sleep(3)
		channel_bytes=channel.recv(9999)
		channel_data=channel_bytes.decode("utf-8")
	if(flag == 'O'):
		#fn_printcommands()
		file.write ('\n\n************* End of Fabric A ***************')
	elif(flag == 'E'):
		file.write ('\n\n************* End of Fabric B ***************')
	time_stamp_end = datetime.datetime.today().strftime("%m-%d-%Y %H:%M")

	file.write ('\nScript End Time : ' + time_stamp_end)

	ssh.close()
	return	


for cl in cl_ports_odd:
   	print ('CL ODD Port ', cl.name)
   	cl.pwwn_list = []
name1 = re.compile(r'[a-zA-Z0-9]+_')
for x in range(int(host_count)):  # loop through host count
    pwwn_p1 = input("Enter the host pwwn (eg. 1111111111111111) ? ")
    pwwn_alias_p1 = input("Enter the pwwn alias (eg. sj1hba001_P1) ?") #ask the user for input.
    while not name1.match(pwwn_alias_p1):
    	print ("Invalid Input ! Enter with _")
    	pwwn_alias_p1 = input("Enter the pwwn alias (ex sj1hba001_P1) ?") #ask the user for input.
    cl.pwwn_list.append(pwwnObj(pwwn_p1, pwwn_alias_p1))

for cl in cl_ports_even:
   	print ('CL EVEN Port ', cl.name)
   	cl.pwwn_list = []
name2 = re.compile(r'[a-zA-Z0-9]+_')
for x in range(int(host_count)):  # loop through host count
    pwwn_p2 = input("Enter the host pwwn (eg. 2222222222222222) ? ")  
    pwwn_alias_p2 = input("Enter the pwwn alias (eg. sj1hba001_P1) ? ")
    while not name2.match(pwwn_alias_p2):
    	print ("Invalid Input ! Enter with _")
    	pwwn_alias_p2 = input("Enter the pwwn alias (ex sj1hba001_P1) ?") #ask the user for input.
    cl.pwwn_list.append(pwwnObj(pwwn_p2, pwwn_alias_p2))

flag='O' 
time_stamp = datetime.datetime.today().strftime("%m-%d-%Y %H:%M")
fn_createaliaszone(oddswitchname,cl_ports_odd)
print('##############End of odd ports############################\n')    	     
print('##############script sleeping for 1 minute##########################\n')    	     

time.sleep(60)
flag='E'
fn_createaliaszone(evenswitchname,cl_ports_even)
print('##############End of even ports##########################\n')    	     

print('################End of script###########################\n')
