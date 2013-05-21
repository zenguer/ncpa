import os
import json
import logging
import psutil
import time
import sys

def dirs_in_directory(module_file):
    dirname = os.path.dirname(module_file)
    return [x for x in os.listdir(dirname) if os.path.isdir(dirname + '/' + x)]
    

def generic_getter(name, lat):
    
    def gen(location):
        stat = {}
        for mod in lat:
            module = '%s.%s' % (location, mod)
            __import__(str(module))
            stat[mod] = sys.modules[module].get(location)
        return {name : stat}
    
    return gen

def enumerate_plugins(*args, **kwargs):
    try:
        builtins  = ['check_memory', 'check_swap', 'check_cpu']
        externals = [x for x in os.listdir('plugins') if os.path.isfile('plugins/%s' % x)]
        count = len(builtins + externals)
        return json.dumps({     'builtins' : builtins,
                                'externals' : externals,
                                'count' : count })
    except Exception, e:
        logging.exception(e)
        return json.dumps({'error' : str(e)})
    
def enumerate_processes(*args, **kwargs):
    procs = psutil.process_iter()
    request = kwargs.get('request', {})
    header = ('USER', 'PID', 'CPU', 'MEM', 'VSZ', 'RSS', 'START', 'COMMAND')
    try:
        num = int(request.args.get('top', None))
    except:
        num = float('Inf')
    skip = int(request.args.get('skip', 20))
    extracted_procs = []
    for proc in procs:
        if skip > 0:
            skip = skip - 1
            continue
        num = num - 1
        if num < 0:
            break
        extracted_procs.append([    str(proc.username),
                                    str(proc.pid),
                                    str(proc.get_cpu_percent()),
                                    str(proc.get_memory_percent()),
                                    str(proc.get_memory_info().vms),
                                    str(proc.get_memory_info().rss),
                                    str(time.ctime(proc.create_time)),
                                    str(proc.exe)
                                ])
    try:
        sortby = request.args.get('sortby', None)
        index = header.index(sortby)
    except Exception,e :
        index = 4
    extracted_procs.sort(key=lambda x: x[index], reverse=True)
    return json.dumps({     'header' : header,
                            'procs'  : extracted_procs })
    