import os
import commands
from operator import itemgetter

max_processes = 60

# all users listed in /etc/passwd are to be excluded
def get_user_blacklist():
  filename = "/etc/passwd"
  userids = []
  f = open(filename, 'r')
  lines = f.readlines()
  f.close()
  for line in lines:
    if line.strip() != '':
      userids.append(line.split(':')[2])
  return userids

# map user names to user ids using the extended passwd file
# (getent passwd), including ldap information
def get_user_mapping():
  mapping = {}
  stdout = commands.getoutput('getent passwd')
  lines = stdout.splitlines()
  for line in lines:
    fields = line.split(':')
    mapping[fields[2]] = fields[0]
  return mapping
    
def create_process_list():
  global max_processes
  processes = [{} for n in range(max_processes)]
  stdout = commands.getoutput('ps axo pid,uid,pcpu,pmem,vsize,cmd --sort=-pcpu,-pmem')
  ps_lines = stdout.splitlines()
  userid_blacklist = get_user_blacklist()
  user_mapping = get_user_mapping()
  pids = []
  count = 0
  for ps in ps_lines[1:]:
    ps_fields = ps.split()
    if ('<defunct>' not in ps) and (ps_fields[1] not in userid_blacklist):
      p = {}
      p['pid'] = ps_fields[0]
      pids.append(p['pid'])
      p['user'] = user_mapping[ps_fields[1]]
      p['pcpu'] = ps_fields[2]
      p['pmem'] = ps_fields[3]
      p['vsize'] = ps_fields[4]
      p['cmd'] = ps_fields[5]
      p['vsizepeak'] = commands.getoutput('cat /proc/%s/status | tr \\\\0 \\\\n | grep VmPeak | grep -oE "[[:digit:]]{1,}"' % ps_fields[0])
      if 'No such file or' in p['vsizepeak']:
        p['vsizepeak'] = 0
      processes[count] = p
      count += 1
      if count >= (max_processes-1):
        break

  tmp = {}
  stdout = commands.getoutput('top -b -n 1')
  top_lines = stdout.splitlines()[7:]
  for line in top_lines:
    top_fields = line.split()
    pid = top_fields[0]
    cpu = top_fields[8]
    if pid in pids:
      tmp[pid] = cpu

  for ps in processes:
    if 'pid' in ps and ps['pid'] in tmp:
      ps['cpu'] = tmp[ps['pid']]

  return processes
    
def ps_handler(name):
  global max_processes
  processes = create_process_list()
  i = 0
  for p in processes:
    value = ''
    if p:
      #value += '%s|%s|%s|%s|%s|%s|%s,' % (p['pid'], p['cmd'], p['user'], p['pcpu'], p['pmem'],p['vsize'], p['vsizepeak'])
      value += '%s|%s|%s|%s|%s|%s|%s,' % (p['pid'], p['cmd'], p['user'], p['cpu'], p['pmem'],p['vsize'], p['vsizepeak'])
      value = value.strip().strip(',')
    cmd = 'gmetric '
    cmd += '--name="ps-%d" ' % i 
    cmd += '--value="%s" ' % value
    cmd += '--type="string" '
    cmd += '--slope=zero '
    cmd += '--tmax=0 '
    cmd += '--dmax=0 '
    os.system(cmd)
    i += 1
  return ''

def metric_init(params):
  global descriptors
  descriptors = []
  d = {
    'name': 'ps',
    'call_back': ps_handler,
    'time_max': 0,
    'value_type': 'string',
    'units': '',
    'slope': 'zero',
    'format': '%s',
    'description': 'Process Data',
    'groups': 'health'
  }
  descriptors.append(d)
  return descriptors
 
def metric_cleanup():
  '''Clean up the metric module.'''
  pass
 
# This code is for debugging and unit testing
if __name__ == '__main__':
  print create_process_list()
  #metric_init(None)
  #for d in descriptors:
  #  v = d['call_back'](d['name'])
  #  print 'value for %s is %s' % (d['name'], v)

