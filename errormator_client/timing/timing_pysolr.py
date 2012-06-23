from errormator_client.utils import import_module, deco_func_or_method
from errormator_client.timing import time_trace

import pysolr

def add_timing(min_duration=0.5):
    module = import_module('pysorl')

    def general_factory(slow_call_name):
        def gather_args(*args, **kwargs):
            return {'type':slow_call_name, }
    
    def gather_args_search(q, *args, **kwargs):
        return {'type':'Solr.search', 'statement':q}

    def gather_args_more_like_this(q, *args, **kwargs):
        return {'type':'Solr.search', 'statement':q}
    
    deco_func_or_method(module, 'Solr.search', time_trace,
                          gather_args_search, min_duration)
    
    deco_func_or_method(module, 'Solr.add', time_trace,
                          general_factory('Solr.add'), min_duration)

    deco_func_or_method(module, 'Solr.commit', time_trace,
                          general_factory('Solr.commit'), min_duration)

    deco_func_or_method(module, 'Solr.delete', time_trace,
                          general_factory('Solr.delete'), min_duration)
    
    deco_func_or_method(module, 'Solr.extract', time_trace,
                          general_factory('Solr.extract'), min_duration)

    deco_func_or_method(module, 'Solr.more_like_this', time_trace,
                        gather_args_more_like_this, min_duration)
  
    deco_func_or_method(module, 'Solr.suggest_terms', time_trace,
                        general_factory('Solr.commit'), min_duration)
  
  
