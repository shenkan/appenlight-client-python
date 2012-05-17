from webob import Request
import datetime

def asbool(obj):
    if isinstance(obj, (str, unicode)):
        obj = obj.strip().lower()
        if obj in ['true', 'y', 't', '1']:
            return True
        elif obj in ['false', 'n', 'f', '0']:
            return False
        else:
            raise ValueError(
                "String is not true/false: %r" % obj)
    return bool(obj)

def aslist(obj, sep=None, strip=True):
    if isinstance(obj, basestring):
        lst = obj.split(sep)
        if strip:
            lst = [v.strip() for v in lst]
        return lst
    elif isinstance(obj, (list, tuple)):
        return obj
    elif obj is None:
        return []
    else:
        return [obj]

def process_environ(environ, traceback=None, include_params=False):
    # form friendly to json encode
    parsed_environ = {}
    errormator_info = {}
    req = Request(environ)
    for key, value in req.environ.items():
        if key.startswith('errormator.') and key not in ('errormator.client',
                                                    'errormator.force_send',
                                                    'errormator.log',
                                                    'errormator.report'):
            errormator_info[key[11:]] = unicode(value)
        else:
            allowed_keys = ('HTTP_USER_AGENT', 'REMOTE_USER', 'REMOTE_ADDR',
                            'SERVER_NAME','CONTENT_TYPE',)
            if traceback and (key.startswith('HTTP') or key in allowed_keys):
                try:
                    if isinstance(value, str):
                        parsed_environ[key] = value.decode('utf8')
                    else:
                        parsed_environ[key] = unicode(value)
                except Exception as e:
                    pass
    # provide better details for 500's
    if include_params:
        parsed_environ['COOKIES'] = dict(req.cookies)
        parsed_environ['GET'] = dict([(k, req.GET.getall(k)) for k in req.GET])
        parsed_environ['POST'] = dict([(k, req.POST.getall(k))
                                       for k in req.POST])
    # figure out real ip
    if environ.get("HTTP_X_FORWARDED_FOR"):
        remote_addr = environ.get("HTTP_X_FORWARDED_FOR").split(',')[0].strip()
    else:
        remote_addr = (environ.get("HTTP_X_REAL_IP")
                       or environ.get('REMOTE_ADDR'))
    parsed_environ['REMOTE_ADDR'] = remote_addr
    errormator_info['URL'] = req.url
    return parsed_environ, errormator_info


def create_report_structure(environ, traceback=None, message=None,
            http_status=200, server='unknown server', include_params=False):
    (parsed_environ, errormator_info) = process_environ(environ, traceback,
                                                        include_params)
    report_data = {'client': 'Python', 'report_details': []}
    if traceback:
        exception_text = traceback.exception
        traceback_text = traceback.plaintext
        report_data['error_type'] = exception_text
        report_data['traceback'] = traceback_text
    report_data['http_status'] = 500 if traceback else http_status
    if http_status == 404:
        report_data['error_type'] = '404 Not Found'
    report_data['priority'] = 5
    report_data['server'] = (server or
                environ.get('SERVER_NAME', 'unknown server'))
    detail_entry = {}
    detail_entry['request'] = parsed_environ
    # fill in all other required info
    detail_entry['ip'] = parsed_environ.get('REMOTE_ADDR', u'')
    detail_entry['user_agent'] = parsed_environ.get('HTTP_USER_AGENT', u'')
    detail_entry['username'] = parsed_environ.get('REMOTE_USER',
                                            parsed_environ.get('username', ''))
    detail_entry['url'] = errormator_info.pop('URL', 'unknown')
    if 'request_id' in errormator_info:
        detail_entry['request_id'] = errormator_info.pop('request_id', None)
    detail_entry['message'] = message or errormator_info.get('message', u'')
    #conserve bandwidth pop keys that we dont need in request details
    exclude_keys = ('HTTP_USER_AGENT', 'REMOTE_ADDR', 'HTTP_COOKIE',
                    'errormator.client')
    for k in exclude_keys:
        detail_entry['request'].pop(k, None)
    report_data['report_details'].append(detail_entry)
    report_data.update(errormator_info)
    return report_data, errormator_info
