
#################################################################################################
#												#
#				$$$SAN PROVISIONING AUTOMATION$$$				#
#												#
################################################################################################

script_ver = 3

import sys, subprocess, os, datetime, string, time, re 

time_stamp = datetime.datetime.today().strftime("%m-%d-%Y %H:%M")

################################### Global Declaration #########################################

raidcom_cmd = '/HORCM/usr/bin/raidcom '
ldevs = []
hosts = []
log_file_location = '/root/storage/'
cl_ports_odd = []
cl_ports_even = []
ldevs_free = []
hostgroup_free = []
pools = []

tier_perf = 6
tier_std = 7

ldev_min = 8
ldev_max = 3999

std_cu_limit = 18431

cl_pair_limit = 3

##################################### Host Mode ################################################

hm_linux = 'LINUX' #00
hm_solaris = 'SOLARIS' #09
hm_windows = 'WIN_EX' # 0c
hm_vmware = 'VMWARE_EX' #21
hm_aix = 'AIX'
hmo_cluster = '2 '
hmo_vmware = '54 63'
hmo_windows = '40 '
hmo_aix = '2 '


###################################### Begin Func ##############################################
def fn_checkArray():

   arrayTestcmd = subprocess.Popen(raidcom_cmd + ' get resource ' + ' -IM' + str(horcm_instance), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
   output, err = arrayTestcmd.communicate()
   arrayTest = output
   arrayTest_temp = []
   arrayTest_temp = string.split(arrayTest)
   if arrayTest_temp[8] == 'Locked':
       print ('The array is currently Locked by', arrayTest_temp[10], 'The script can not continue.')
       exit()
   else:
      pass
   return;
  
def fn_lockArray():

    arrayLockcmd = subprocess.Popen(raidcom_cmd + ' lock resource ' + ' -IM' + str(horcm_instance), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, err = arrayLockcmd.communicate()
    arrayLock = output
    print ('array', horcm_instance, 'is now locked')
    return;

def fn_unlockArray():

    arrayunLockcmd = subprocess.Popen(raidcom_cmd + ' unlock resource ' + ' -IM' + str(horcm_instance), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, err = arrayunLockcmd.communicate()
    arrayunLock = output
    print ('array', horcm_instance, 'is now unlocked')
    print ('********************************\n\n')
    return;
      
def fn_createLdev():
    for ldev in ldevs:  
       ldevCreate = subprocess.Popen(raidcom_cmd + ' add ldev -ldev_id ' + hex(ldev.number) + ' -pool ' + str(ldev.pool) + ' -capacity ' + str(ldev.size) + ' -IM' + str(horcm_instance), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
       output, err = ldevCreate.communicate()
       time.sleep(3) # wait 3 sec 
       ldevSetName = subprocess.Popen(raidcom_cmd + ' modify ldev -ldev_id ' + hex(ldev.number) + ' -ldev_name ' + str(ldev.name) + ' -IM' + str(horcm_instance), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) 
       output, err = ldevSetName.communicate()
    return;

   

def fn_createHostGroup():
   
   y = 1
   for cl in cl_ports_odd:
      createHG_odd = raidcom_cmd + ' add host_grp -port ' + str(cl.name) + ' -host_grp_name ' + str(hostname) + ' -IM' + str(horcm_instance)
      output = os.popen(createHG_odd)
      cl_odd_temp = output
      for line in cl_odd_temp:   # array returns 3(0x3)  dec & hex so you need to split them to get the value
         line = line.strip()
         groupfields = line.split()
         gid_temp = groupfields[4].split('(')
         cl.gid = gid_temp[0]
         print ('Created host group ' + str(hostname) + ' on ' + cl.name + '-' + cl.gid)
      y = y + 2 # p1, p3 odd fabric
      
   y = 2
   for cl in cl_ports_even:
      createHG_even = raidcom_cmd + ' add host_grp -port ' + str(cl.name) + ' -host_grp_name ' + str(hostname) + ' -IM' + str(horcm_instance)
      output = os.popen(createHG_even)
      cl_even_temp = output
      for line in cl_even_temp:
         line = line.strip()
         groupfields = line.split()
         gid_temp = groupfields[4].split('(')
         cl.gid = gid_temp[0]
         print ('Created host group ' + str(hostname) + ' on ' + cl.name + '-' + cl.gid)
      y = y + 2 # p2, p4 odd fabric
      
   return;
 
def fn_addPwwnHostGroup():

   y = 1
   for cl in cl_ports_odd:
      for pwwn in cl.pwwn_list:
         addPwwn_odd = raidcom_cmd + ' add hba_wwn -port ' +  str(cl.name) + '-' + cl.gid + ' ' + str(hostname) + ' -hba_wwn ' + pwwn.pwwn + ' -IM' + str(horcm_instance)
         output = os.popen(addPwwn_odd)
         time.sleep(30) # wait 10 sec
         setPwwn_odd = raidcom_cmd + ' set hba_wwn -port ' +  str(cl.name) + '-' + cl.gid + ' ' + str(hostname) + ' -hba_wwn ' + pwwn.pwwn + ' -wwn_nickname ' + str(pwwn.alias) + ' -IM' + str(horcm_instance)
         output = os.popen(setPwwn_odd)
         print ('pwwn - ' + pwwn.pwwn + ' added to ' + str(hostname) + ' on ' + cl.name + '-' + cl.gid)
      y = y + 2 # p1, p3 odd fabric
    
   y = 2  #used to increment between multiple HBA's on a host _p2, _p4
   for cl in cl_ports_even:
      for pwwn in cl.pwwn_list:
         addPwwn_even = raidcom_cmd + ' add hba_wwn -port ' +  str(cl.name) + '-' + cl.gid + ' ' + str(hostname)+ ' -hba_wwn ' + pwwn.pwwn + ' -IM' + str(horcm_instance)
         output = os.popen(addPwwn_even)
         time.sleep(30) # wait 10 sec
         setPwwn_even = raidcom_cmd + ' set hba_wwn -port ' +  str(cl.name) + '-' + cl.gid + ' ' + str(hostname) + ' -hba_wwn ' + pwwn.pwwn + ' -wwn_nickname ' + str(pwwn.alias) + ' -IM' + str(horcm_instance)
         output = os.popen(setPwwn_even)
         print ('pwwn - ' + pwwn.pwwn + ' added to ' + str(hostname) + ' on ' + cl.name + '-' + cl.gid)
      y = y + 2 # p2, p4 odd fabric
      
   return;

def fn_addLdevHostGroup():

   y = 1  #used to increment between multiple HBA's on a host _p1, _p3
   for cl in cl_ports_odd:
      for ldev in ldevs:
		ldevAddHG_odd = subprocess.Popen(raidcom_cmd + ' add lun -port ' + cl.name + ' ' + hostname  + ' -ldev_id ' + hex(ldev.number) +' -IM' + str(horcm_instance), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	 	output, err = ldevAddHG_odd.communicate()
	 	print ('LDEV ' + hex(ldev.number) + ' added to ' + cl.name + ' host group-' + hostname)
      y = y + 2 # x = p1, p3 odd fabric
      
   y = 2  #used to increment between multiple HBA's on a host _p2, _p4
   for cl in cl_ports_even:
      for ldev in ldevs:
         ldevAddHG_even = subprocess.Popen(raidcom_cmd + ' add lun -port ' + cl.name + ' ' + hostname +  ' -ldev_id ' + hex(ldev.number) +' -IM' + str(horcm_instance), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
         output, err = ldevAddHG_even.communicate()
         print ('LDEV ' + hex(ldev.number) + ' added to ' + cl.name + ' host group-' + hostname)
      y = y + 2 # x = p2, p4 even fabric
      
   return;

def fn_inputLdevSize():

   global ldev_size, ldev_name
   ldev_size = raw_input("What size LDEV do you want to create?  (min 8G / max 3990G) - ")
   if ldev_size.endswith('G'):  #test for valid input as well as min/max ldev size
       ldev_size_temp = int(ldev_size.rstrip('G'))
       if ldev_size_temp < ldev_min or ldev_size_temp > ldev_max:  
           print ('size outside GE standards')
           exit()
       if ldev_naming == 'manual':
          ldev_name = raw_input("Enter the name for this LDEV (typically host name for a LDOM) ")  # this way the LDOM name is registered on the LDEV.
   else:
       print ('LDEV input syntax error')
       exit()
   return;

def fn_updateLogFile():

   log_file = log_file_location + 'now_' + ticket_num + '.log'
   file = open(log_file, 'a+')
   file.write ('\n\n**** Start of Job ****')
   file.write ('\nTime stamp: ' + time_stamp)
   file.write ('\nService Num: ' + ticket_num)
   file.write ('\nEngineers Name: ' + sso_id)
   file.write ('\nHost name: ' + hostname)
   y = 1  #used to increment between multiple HBA's on a host _p1, _p3
   for cl in cl_ports_odd:
      for pwwn in cl.pwwn_list:
         file.write('\npwwn - ' + pwwn.pwwn + ' added to ' + str(hostname)+ ' on ' + cl.name + '-' + cl.gid)
      y = y + 2 # p1, p3 odd fabric
       
   y = 2  #used to increment between multiple HBA's on a host _p2, _p4    
   for cl in cl_ports_even:
      for pwwn in cl.pwwn_list:
         file.write('\npwwn - ' + pwwn.pwwn + ' added to ' + str(hostname)+ ' on ' + cl.name + '-' + cl.gid)  
      y = y + 2 # p2, p4 odd fabric
       
   file.write ('\nThe following LDEVs were created.\n\n')
   for ldev in ldevs:
      getLDEV = subprocess.Popen(raidcom_cmd + ' get ldev -ldev_id ' + hex(ldev.number) + ' -fx -IM' + str(horcm_instance), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
      output, err = getLDEV.communicate()
      file.write ('\n' + output) 
   file.write('\n\n**** End of Job ****\n\n')
   file.close()
   command = ("mail -r ITAutomation@adobe.com -s '"'COMPLETED - SAN_Provisioning'"' %s < %s" % ('bramamur@adobe.com',log_file))
   os.system(command)
   return; 

def fn_updateLogFile_new():

   log_file = log_file_location + 'now_' + ticket_num + '.log'
   file = open(log_file, 'a+')
   file.write ('\n\n**** Start of Job ****')
   file.write ('\nTime stamp:  ' + time_stamp)
   file.write ('\nService Num:  ' + ticket_num)
   file.write ('\nEngineers Name: ' + sso_id)
   file.write ('\nHost name: ' + hostname)
   y = 1
   for cl in cl_ports_odd:
      y = y + 2

   y = 2
   for cl in cl_ports_even:
      y = y + 2 # p2, p4 odd fabric

   file.write ('\nThe following LDEVs were created.\n\n')
   for ldev in ldevs:
      getLDEV = subprocess.Popen(raidcom_cmd + ' get ldev -ldev_id ' + hex(ldev.number) + ' -fx -IM' + str(horcm_instance), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
      output, err = getLDEV.communicate()
      file.write ('\n' + output)
   file.write('\n\n**** End of Job ****\n\n')
   file.close()
   command = ("mail -r ITAutomation@adobe.com -s '"'COMPLETED - SAN_Provisioning'"' %s < %s" % ('bramamur@adobe.com',log_file))
   os.system(command)
   return;

def fn_setHostMode():

   for cl in cl_ports_odd:
      y = 1  # p1, p3 odd fabric
      # Set Host Mode
      if hm_option != None:
         setHM_odd = subprocess.Popen(raidcom_cmd + ' modify host_grp -port ' + str(cl.name) + '-' + cl.gid + ' -host_grp_name ' + str(hostname) + '_p' + str(y) + ' -host_mode ' + str(host_mode) + ' -host_mode_opt ' + str(hm_option) + ' -IM' + str(horcm_instance), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
      else:
         setHM_odd = subprocess.Popen(raidcom_cmd + ' modify host_grp -port ' + str(cl.name) + '-' + cl.gid + ' -host_grp_name ' + str(hostname) + '_p' + str(y) + ' -host_mode ' + str(host_mode) + ' -IM' + str(horcm_instance), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
         output, err = setHM_odd.communicate()
      y = y + 2 # x = p1, p3 odd fabric
      
   for cl in cl_ports_even:
      y = 1
      if hm_option != None:  #run cmd with Host Mode options
         setHM_even = subprocess.Popen(raidcom_cmd + ' modify host_grp -port ' + str(cl.name) + '-' + cl.gid + ' -host_grp_name ' + str(hostname)+ ' -host_mode ' + str(host_mode) + ' -host_mode_opt ' + str(hm_option) + ' -IM' + str(horcm_instance), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
      else:
         setHM_even = subprocess.Popen(raidcom_cmd + ' modify host_grp -port ' + str(cl.name) + '-' + cl.gid + ' -host_grp_name ' + str(hostname) + ' -host_mode ' + str(host_mode) + ' -IM' + str(horcm_instance), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
      output, err = setHM_even.communicate()
      y = y + 2 # x = p2, p4 odd fabric
      
   return;

def  fn_findFreeLdev():

   global ldevs_free
   x=0
   while x < std_cu_limit:  # create list of all possible ldev #'s later the script will remove the ones that are in use.
      ldevs_free.append(x)
      x=x+1
   find_free_ldev_cmd = raidcom_cmd + ' get ldev -ldev_list defined ' + ' -IM' + str(horcm_instance) + ' | grep ^LDEV\ :' 
   output = os.popen(find_free_ldev_cmd)
   print ('\nlooking for a free LDEV...')
   for line in output:  #find the last LDEV in use on the array that is less than 18432 (47:ff) 
      line = line.strip()
      groupfields = line.split()
      used_ldev = groupfields[2]
      if re.search('\d+', used_ldev):
         if int(used_ldev) < std_cu_limit:
            ldevs_free.remove(int(used_ldev))  
   sorted(ldevs_free)
   return;
   
   
def  fn_listhostgroup():
   global hostgroup_free

   hostgroup_free_cmd = raidcom_cmd + ' get host_grp -port ' +str(adapter_name) 
   output = os.popen(hostgroup_free_cmd)
   print ('\nlooking for list of hostgroup...')
   for line in output:
        line = line.strip()
	print (line)
        groupfields = line.split()
        port = groupfields[0]
        gid = groupfields[1]
	group_name = groupfields[2]
	serialnum = groupfields[3]
	hmd = groupfields[4]
	hmd_bits = ""
        hostgroup_free.append(hostgroupobj(port, gid, group_name, serialnum, hmd, hmd_bits))
   return;


def fn_findPools():
    
   get_pools = raidcom_cmd + ' get dp_pool ' + ' -IM' + str(horcm_instance)
   output_pools = os.popen(get_pools)
   for line in output_pools:
      line = line.strip()
      groupfields = line.split()
      pid = groupfields[0]
      av_cap = groupfields[3]
      tp_cap = groupfields[4]
      tl_cap = groupfields[10]
      name = ''
      if re.search('\d+', pid):
         av_cap = int(av_cap) / 1024 / 1024  
         tp_cap = int(tp_cap) / 1024 / 1024
         tl_cap = int(tl_cap) / 1024 / 1024
         sub_free_cap = (tp_cap * 1.2) - tl_cap
         pools.append(poolObj(pid, name, av_cap, tp_cap, tl_cap, sub_free_cap ))  #data is in TB
   
   get_pool_name = raidcom_cmd + ' get pool -key opt ' + ' -IM' + str(horcm_instance)
   output_pool_name = os.popen(get_pool_name)
   pool_name = []
   for line in output_pool_name:
      line = line.strip()
      groupfields = line.split()
      pid = groupfields[0]
      name = groupfields[3]
      if re.search('\d+', pid):
         pool_name.append(poolObj(pid, name))  
         #print pid, name
         
   for pool in pools: 
      for pool_n in pool_name:
         if pool_n.pid == pool.pid:
            pool.name = pool_n.name
   return;
    
class LdevObj(object):
   """__init__() functions the class constructor"""
   def __init__(self, number=None, name=None, size=None, tier=None, pool=None, array=None):
      self.number = number
      self.name = name
      self.size = size
      self.tier = tier
      self.pool = pool
      self.array = array
      
class clPortObj(object):
   """__init__() functions the class constructor"""
   def __init__(self, name=None, pwwn_list=[], gid=None):
     self.name = name
     self.pwwn_list = pwwn_list
     self.gid = gid
     
class pwwnObj(object):
   """__init__() functions the class constructor"""
   def __init__(self, pwwn=None, alias=None):
     self.pwwn = pwwn
     self.alias = alias

class poolObj(object):
   """__init__() functions the class constructor"""
   def __init__(self, pid=None, name=None, free_capacity=None, phy_size=None, sub_capacity=None, sub_free_cap=None):
     self.pid = pid
     self.name = name
     self.free_capacity = free_capacity
     self.phy_size = phy_size
     self.sub_capacity = sub_capacity
     self.sub_free_cap = sub_free_cap
     
class hostgroupobj(object):
   """__init__() functions the class constructor"""
   def __init__(self, port=None, gid=None, group_name=None, serialnum=None, hmd=None, hmd_bits=None):
     self.port = port
     self.gid = gid
     self.group_name = group_name
     self.serialnum = serialnum
     self.hmd = hmd
     self.hmd_bits = hmd_bits
          
##########################################################################################################################################      
## 								Main code 								##
##########################################################################################################################################

if len(sys.argv) < 2: 
       print ('You forgot to include the HORCM instance for the array')
       print ('  - example ')
       print ('  - script aborted - ')
       sys.exit()

horcm_instance = sys.argv[1]  #import horcm instance from cmd line.

fn_checkArray();

os.system('clear')
print ('\n****************************************************************')
print ('\n   This Script Will Create LUNs to Existing or New Host Group')
print ('\n   and devices on a Hitachi G1000,Gx00 & VSP Storage Arrays.')
print ('\n****************************************************************\n\n')

fn_lockArray();

ticket_num = raw_input("Enter the Request Number: ")
sso_id = raw_input("Enter Engineers Name:  ")

hostcreate = raw_input("Do you want to add lun to (E)xisting or (N)ew Host Group: ")

if hostcreate == "N":
	hostname = raw_input("Enter the hostname for the host or cluster? (e.g. or1hbn001 or or1hbn001_or1hbn002): ")
elif hostcreate == "E":
	adapter_name = raw_input("Enter the adapter name: ")
	fn_listhostgroup();   # returns list of host groups in storage array 
    	hostname = raw_input("Enter the hostname: ");

if hostcreate == "N":
	host_mode_input = raw_input("Enter the host OS type e.g. (L)inux, (S)olaris, (V)Mware, (W)indows, (A)ix: ")
host_count = 1 # set default node count = 1
if hostcreate == "N":
	cluster_input = raw_input("Is this a cluster? (y)es / (n)o ")
	if host_mode_input  == "L" or host_mode_input == "l":  # check for valid host mode options
		if cluster_input == "yes" or cluster_input == "y":
			host_mode = hm_linux
      			hm_option = hmo_cluster
   		else:
      			host_mode = hm_linux
      			hm_option = None
	elif host_mode_input == "S" or host_mode_input == "s":
		if cluster_input == "yes" or cluster_input == "y":
      			host_mode = hm_solaris
      			hm_option = hmo_cluster
   		else:
      			host_mode = hm_solaris 
      			hm_option = None
	elif host_mode_input == "V" or host_mode_input == "v":
   		if cluster_input == "yes" or cluster_input == "y":
      			host_mode = hm_vmware
      			hm_option = hmo_vmware
   		else:
      			host_mode = hm_vmware 
      			hm_option = hmo_vmware
	elif host_mode_input == "W" or host_mode_input == "w":
   		if cluster_input == "yes" or cluster_input == "y":
      			host_mode = hm_windows
      			hm_option = hmo_windows + hmo_cluster
   		else:
      			host_mode = hm_windows
      			hm_option = hmo_windows

        elif host_mode_input == "A" or host_mode_input == "a":
                if cluster_input == "yes" or cluster_input == "y":
                        host_mode = hm_aix
                        hm_option = hmo_cluster
                else:
                        host_mode = hm_aix
                        hm_option = hmo_aix 
	else:
    		print ('host or cluster mode syntax error')
		fn_unlockArray();
		exit()

	if cluster_input == "yes" or cluster_input == "y":
		host_count = raw_input("Enter the number of Host(s) to be in the cluster? - ")

    
fn_findPools();  # print out pool capacity details

print ('Array - ' + horcm_instance + ' has the following pools.\n')
print ('*******************************************************************************************')
print ("| POOL_ID     |  POOL_NAME                                          | FREE_CAPACITY (TB)")
print ('-------------------------------------------------------------------------------------------')
for pool in pools:
    print('| '+pool.pid+' '*(12-len(pool.pid))+'|'+pool.name+' '*(53-len(pool.name))+'|'+str(pool.sub_free_cap)+' '*(20-len(str(pool.sub_free_cap)))+'|')

print ('*******************************************************************************************\n')
ldev_pool = raw_input("Enter the pool ID you want to use: ")

ldev_count = raw_input ("Enter the Number of LDEVs you want to create for the new host: ")
if int(ldev_count) == 1:
   ldev_same = "yes"   
else:
   ldev_same = raw_input("Will the LDEVs all be the same size (y)es or (n)o ")
   
ldev_name_option = raw_input ("Do you want to manually control LDEV names? (auto will use host name). (y)es or (n)o ")
if ldev_name_option == "yes" or ldev_name_option == "y":
   ldev_naming = 'manual'
elif ldev_name_option == "no" or ldev_name_option == "n":
   ldev_naming = 'auto'
else:
   print ('ldev name mode syntax error')
   fn_unlockArray();
   exit()  
   
fn_findFreeLdev(); 

if ldev_same == "yes" or ldev_same == "y":
    fn_inputLdevSize();
    i = 0
    while i < int(ldev_count):
       ldev_num_temp = ldevs_free[0]
       ldevs.append(LdevObj(ldev_num_temp)) 
       ldevs[i].size = ldev_size
       ldevs[i].pool = ldev_pool
       if ldev_naming == 'auto': 
          ldevs[i].name = hostname
       else:
          ldevs[i].name = ldev_name
       ##ldevs[i].tier = tier
       ldevs[i].number = ldev_num_temp
       ldevs_free.remove(ldev_num_temp)
       i = i + 1
   
elif ldev_same == "no" or ldev_same == "n":
   i = 0
   while i < int(ldev_count):
      ldev_num_temp = ldevs_free[0]
      fn_inputLdevSize();
      ldevs.append(LdevObj(ldev_num_temp))
      ldevs[i].size = ldev_size
      ldevs[i].pool = ldev_pool
      if ldev_naming == 'auto':
         ldevs[i].name = hostname
      else:
         ldevs[i].name = ldev_name
      ##ldevs[i].tier = tier
      ldevs[i].number = ldev_num_temp
      ldevs_free.remove(ldev_num_temp)
      i = i + 1
   
cl_count = raw_input ("Enter the Number of CHA Pairs required for this host or cluster: ")
if int(cl_count) > int(cl_pair_limit):
   print ('\n\nHosts are limited to 3 pair or 6 HBAs.')  
   fn_unlockArray();
   exit()

for i in range(int(cl_count)):
   print ('Create pair :', i+1)
   cl_port_p1 = raw_input ("Enter the ODD CL-Port to be used (ex. CL5-A): ")
   cl_ports_odd.append(clPortObj(cl_port_p1))
      
   cl_port_p2 = raw_input ("Enter the EVEN CL-Port to be used (ex. CL6-A): ")
   cl_ports_even.append(clPortObj(cl_port_p2))
   print ('*****************************************************************')
   
if hostcreate == "N":   
   
	for cl in cl_ports_odd:
   		print ('CL ODD Port ', cl.name)
   		cl.pwwn_list = []
   	for x in range(int(host_count)):  # loop through host count
      		pwwn_p1 = raw_input ("Enter the host pwwn (eg. 5000000000000000): ")  
      		pwwn_alias_p1 = raw_input ("Enter the pwwn alias (eg. or1hbn001_px): ")
      		cl.pwwn_list.append(pwwnObj(pwwn_p1, pwwn_alias_p1)) 
   
	for cl in cl_ports_even:
   		print ('CL EVEN Port ', cl.name)
   		cl.pwwn_list = []
   	for x in range(int(host_count)):
      		pwwn_p2 = raw_input ("Enter the host pwwn (eg. 9000000000000000): ")  
      		pwwn_alias_p2 = raw_input ("Enter the pwwn alias (eg. or1hbn002_px): ")
      		cl.pwwn_list.append(pwwnObj(pwwn_p2, pwwn_alias_p2)) 
   

os.system('clear')
print ('\nThe script is about to provision storage.\n')
print ('REQ No= ', ticket_num)
print ('Host= ' + hostname + ' will be added to HDS array xxx' + horcm_instance , '\n')
for cl in cl_ports_odd:
	print ('   Port-' + str(cl.name))
	if hostcreate == "N":
		print (len(cl.pwwn_list))
   		for pwwn in cl.pwwn_list:  
      			print ('        pwwn-' + str(pwwn.pwwn) + ' alias-' + str(pwwn.alias))
      
for cl in cl_ports_even:
	print ('   Port-' + str(cl.name))
	if hostcreate == "N":
		print (len(cl.pwwn_list))
   		for pwwn in cl.pwwn_list:  
       			print ('        pwwn-' + str(pwwn.pwwn) + ' alias-' + str(pwwn.alias))
       
print ('\n')
for ldev in ldevs:
   print ('  LDEV-', hex(ldev.number), ' Size-', ldev.size, 'in pool #', ldev.pool)
print ('\n**** Warning ****\n')
print ('Are you sure you want to continue? \n\n**** Warning ****\n')
input = raw_input("Enter (y)es to continue (n)o to abort: ")
if input == "yes" or input == "y":
   pass
elif input == "no" or input == "n":
   print ("Script aborted.")
   fn_unlockArray();
   exit()

if hostcreate == "N":   
	fn_createHostGroup();
	print ('Waiting 30 sec for Host Groups to be created.')
	time.sleep(30) # wait 30 sec

	fn_setHostMode();

	fn_addPwwnHostGroup();
 
fn_createLdev();
print ('Waiting 30 sec for LDEVs to be created ...')
time.sleep(30) # wait 30 sec


fn_addLdevHostGroup();

fn_unlockArray();

if hostcreate == "N":
	fn_updateLogFile();
else:

	fn_updateLogFile_new();

print ('Script Finished.')

############################################## FINISH ########################################################################
