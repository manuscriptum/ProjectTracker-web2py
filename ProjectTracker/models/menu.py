# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('web',SPAN(2),'py'),XML('&trade;&nbsp;'),
                  _class="brand",_href="http://www.web2py.com/")
response.title = T('Project Tracker')
response.subtitle = 'Project Management Application'

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Kevin Westropp <mail@kevinpatrickwestropp.com>'
response.meta.description = 'An App for Managing Projects'
response.meta.keywords = 'lists, todo, project management'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
   (T('Home'), False, URL('default', 'index'), []),
   (T('Projects'), False, None, [
   (T('New Project'), False, URL('default', 'new_project'), []),
   (T('My Projects'), False, URL('default', 'user_projects'), []),
   (T('All Projects'), False, URL('default', 'projects'), []),
   ]),
   ]
