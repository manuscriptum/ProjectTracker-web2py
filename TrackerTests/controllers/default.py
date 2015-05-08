# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

# basic index test suite
def index():
    return dict()

# method for running and displaying results of functional tests
def tests():
    results = run_tests()
    return dict(results=results)

'''
def user():
    return dict(form=auth())
'''

'''
@cache.action()
def download():
    return response.download(request, db)
'''

def call():
    return service()

@auth.requires_signature()
def data():
    return dict(form=crud())
