# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

from xmlrpclib import ServerProxy

def index():
    if request.vars.project and request.vars.newtask and request.vars.user and request.vars.assignto and request.vars.via:
        if request.vars.via=='xml':
            redirect('http://127.0.0.1:8000/tracker/default/call/xml/addtask/' + request.vars.project + '/' + request.vars.newtask + '/' + request.vars.user + '/' + request.vars.assignto + '/', client_side=True)
        elif request.vars.via=='json':
            redirect('http://127.0.0.1:8000/tracker/default/call/json/addtask/' + request.vars.project + '/' + request.vars.newtask + '/' + request.vars.user + '/' + request.vars.assignto + '/', client_side=True)
        elif request.vars.via=='xmlrpc':
            server = ServerProxy('http://127.0.0.1:8000/tracker/default/call/xmlrpc')
            returned = server.addtask_rpc(request.vars.project, request.vars.newtask, request.vars.user, request.vars.assignto)
            response.flash = returned
    else:
        response.flash = T("Welcome to the Tracker Client Application!")
    return dict()

def call():
    return service()

'''
def user():
    return dict(form=auth())

@cache.action()
def download():
    return response.download(request, db)

@auth.requires_signature()
def data():
    return dict(form=crud())
'''
