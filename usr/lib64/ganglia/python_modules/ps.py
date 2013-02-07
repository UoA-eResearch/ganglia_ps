import os
import commands

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
  processes = []
  stdout = commands.getoutput('ps axo pid,uid,pcpu,pmem,size,vsize,share,comm')
  lines = stdout.splitlines()
  userid_blacklist = get_user_blacklist()
  user_mapping = get_user_mapping()
  for line in lines[1:]:
    fields = line.split()
    if ('<defunct>' not in line) and (fields[1] not in userid_blacklist):
      p = {}
      p['pid'] = fields[0]
      p['user'] = user_mapping[fields[1]]
      p['pcpu'] = fields[2]
      p['pmem'] = fields[3]
      p['size'] = 'N/A'
      p['vsize'] = fields[5]
      p['share'] = 'N/A'
      p['cmd'] = fields[7] 
      p['data'] = 'N/A'
      processes.append(p)
  return processes

def ps_handler(name):
  i = 0
  processes = create_process_list()
  for p in processes:
    value = "pid=%s, cmd=%s, user=%s, %%cpu=%s, %%mem=%s, size=%s, data=%s, shared=%s, vm=%s" % (
        p['pid'], p['cmd'], p['user'], p['pcpu'], p['pmem'], p['size'], p['data'], p['share'],p['vsize'])
    cmd = 'gmetric '
    cmd += '--name="ps-%d" ' % i
    cmd += '--value="%s" ' % value
    cmd += '--type="string" '
    cmd += '--slope=zero '
    cmd += '--tmax=10 '
    cmd += '--dmax=10 '
    os.system(cmd)
    i += 1

  return ''


def metric_init(params):
  global descriptors
  descriptors = []
  d = {
    'name': 'ps',
    'call_back': ps_handler,
    'time_max': 60,
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
  metric_init(None)
  for d in descriptors:
    v = d['call_back'](d['name'])
    print 'value for %s is %s' % (d['name'], v)


