import urllib


# url_str = "http://www.163.com/mail/index.htm"

# print('protocol:',url.scheme)
# print('hostname:',url.hostname)
# print('port:',url.port)
# print ('path:',url.path)

# i = len(url.path) - 1
# while i > 0:
#     if url.path[i] == '/':
#         break
#     i = i - 1
# print ('filename:',url.path[i+1:len(url.path)])

def getPath(originalPath="",pathSeg=""):
    if pathSeg.startswith("http"):
        return pathSeg
    url = urllib.parse.urlparse(originalPath)
    return url.scheme+"://"+url.hostname+pathSeg
