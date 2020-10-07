from aiohttp import web
from mako.template import Template

import os
from os import listdir
from os.path import isfile, isdir, join

template = Template(filename="skin/basic/main.html")
files_path = os.path.realpath("./files")

def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]
    
async def mainHandle(req):
    path = req.rel_url.query.get('path', "")
    path = join(files_path, path[1:])
    
    if not os.path.realpath(path).startswith(files_path):
        path = files_path
    
    if not isdir(path):
        return web.HTTPNotFound()
        
    datas=[]
    
    for f in os.listdir(path):
        ff=join(path, f)
        if isfile(ff):
            datas.append({"name":f, "type":"file", "path":remove_prefix(ff, files_path)})
        else:
            datas.append({"name":f, "type":"dir", "path":remove_prefix(ff, files_path)})
    
    return web.Response(text=template.render(datas=datas), content_type='text/html', headers={'Server': 'noname'})

async def downloadHandle(req):
    path = req.rel_url.query.get('path', '')
    
    if not path:
        return web.HTTPBadRequest()
        
    path = join(files_path, path[1:])
    
    if not os.path.realpath(path).startswith(files_path):
        return web.HTTPBadRequest()
        
    if isfile(path):
        return web.FileResponse(path, headers={'Content-Disposition': 'Attachment;filename={}'.format(os.path.basename(path)), 'Server': 'noname'})
    elif isdir(path):
        return web.HTTPBadRequest()

app = web.Application()
app.add_routes([web.get("/", mainHandle), web.get("/download", downloadHandle)])
web.run_app(app)
