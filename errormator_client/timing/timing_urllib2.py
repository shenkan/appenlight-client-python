from errormator_client.utils import import_module, deco_func_or_method
from errormator_client.timing import time_trace

def add_timing(min_duration=0.5):
    module = import_module('urllib2')

    def gather_args_open(opener, url, *args, **kwargs):
        if not isinstance(url, basestring):
            g_url = url.get_full_url()
        else:
            g_url = url
            
        return {'type':'urllib2.OpenerDirector.open', 'parameters':g_url}
    
    deco_func_or_method(module, 'OpenerDirector.open', time_trace,
                          gather_args_open, min_duration)
