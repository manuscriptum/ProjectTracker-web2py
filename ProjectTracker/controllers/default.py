# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Project Tracker Application
## This is the default controller for the Project Tracker App
## By. Kevin Patrick Westropp
## - index is the default action/page of the application
## - user is required for authentication and authorization
## - new_project provides a form for new project creation
## - project displays the list requested, can see items if assigned to or created, none otherwise
## - item displays the item for the assigned user or created by the user, can update the status of the item
## - projects diplays all the projects in the DB/application
## - user_projects displays your created lists, any actions assigned to you and any created action items
## - post_itemcomment adds a new comment
## - post_projectcomment adds a new project comment
## - add_attachment adds an attachment to a comment
## - upload is for uploading a new attachment inplace of a comment
## - downloads are for downloading attachments uploaded into the system
## - call exposes all registered services (none by default)
#########################################################################

# default loading page, greets the user
def index():
    response.flash = T("Welcome to Project Tracker!")
    response.title = T('Project Tracker')
    return dict(message=T('Welcome to Project Tracker, a project management application.'))

# method for registering and logging in
def user():
    return dict(form=auth())

# method/page for creating a new list
@auth.requires_login()
def new_project():
    response.title = T('Project Tracker')
    form = SQLFORM(db.project, fields =['title']).process()
    form.element(_type='submit')['_class']='btn btn-success'
    form.add_button('Home', URL('default', 'index'), _class='btn btn-danger')
    if form.accepted:
        response.flash = 'New Project Created: ' + form.vars.title
        db.collaborator.update_or_insert(collaborator=auth.user,project_id=form.vars.id)
        redirect(URL('project', args=form.vars.id))
    elif form.errors:
        response.flash = 'Error creating a new project. Please be sure to include a title.'
    return dict(form=form)

# method/page for seeing a project and related todo items
@auth.requires_login()
def project():
    project = db.project(request.args(0,cast=int)) or redirect(URL('new_project'))
    db.item.project_id.default = project.id
    form = SQLFORM(db.item, fields=['body', 'due', 'assign_to'], labels={'body':'Todo','due':'Due Date', 'assign_to':'Assign Task to'}, submit_button='Add Task').process()
    form.element(_type='submit')['_class']='btn btn-inverse'
    if form.accepted:
        # call add task to update the db with this info
        add_task(project.id, form.vars.id, form.vars.body, auth.user, form.vars.assign_to)
        new_feedentry(project.id, form.vars.id, auth.user)
        new_feedentry(project.id, form.vars.id, form.vars.assign_to)
        response.flash = 'Added New Task.'
        # update expiration date to include due date if assigned
        if form.vars.due:
            update_expiration(form.vars.due, form.vars.id)
    elif form.errors:
        response.flash = 'Error Adding New Task.'
    items = db(db.item.project_id==project.id).select()
    collaborators = db(db.collaborator.project_id==project.id).select()
    return dict(items=items, project=project, form=form, collaborators=collaborators)

# post comment method to post a new project comment via AJAX
@auth.requires_signature()
def post_projectcomment():
    project_id = request.args(0, cast=int)
    commentform = SQLFORM(db.project_comment, fields=['body'], labels={'body':'Comment'}, submit_button='Add Comment', _method='POST').process()
    commentform.element(_type='submit')['_class']='btn btn-small btn-inverse'
    if commentform.accepted:
        db(db.project_comment.id==commentform.vars.id).update(project_id=project_id)
        response.flash = "New Project Comment Added"
    elif commentform.errors:
        response.flash = "Error Adding New Comment"
    projectcomments = db(db.project_comment.project_id==project_id).select()
    return dict(commentform=commentform, projectcomments=projectcomments, project_id=project_id)

# method/page for viewing an item
@auth.requires_membership(request.args(1))
def item():
    project = db.project(request.args(0,cast=int)) or redirect(URL('default','index'))
    item = db.item(request.args(1,cast=int)) or redirect(URL('default','index'))
    form = SQLFORM(db.item, item, fields=['status'], labels={'status':'Update Status'}, submit_button='Update').process()
    form.element(_type='submit')['_class']='btn btn-inverse'
    if form.accepted:
        update_feedentry(project.id, form.vars.id, auth.user)
        response.flash = "Status Updated."
    elif form.errors:
        response.flash = 'Error Updating Status.'
    item = db.item(request.args(1,cast=int))
    return dict(item=item, project=project, form=form)

# post comment method to post a new project comment via AJAX
@auth.requires_signature()
def post_itemcomment():
    project_id = request.args(0, cast=int)
    item_id = request.args(1, cast=int)
    page = request.args(2, cast=int)
    commentform = SQLFORM(db.item_comment, fields=['body'], labels={'body':'Comment'}, submit_button='Add Comment', _method='POST').process()
    commentform.element(_type='submit')['_class']='btn btn-small btn-inverse'
    if commentform.accepted:
        db(db.item_comment.id==commentform.vars.id).update(item_id=item_id)
        response.flash = "New Task Comment Added"
    elif commentform.errors:
        response.flash = "Error Adding New Comment"
    comments_per_page = 3
    limitby = (page * comments_per_page, (page+1) * comments_per_page+1)
    itemcomments = db(db.item_comment.item_id==item_id).select(limitby=limitby)
    return dict(commentform=commentform, itemcomments=itemcomments, project_id=project_id, item_id=item_id, page=page, comments_per_page=comments_per_page)

# method/page to see workspace - all projects
@auth.requires_login()
def projects():
    grid = db(db.project).select()
    return dict(grid=grid)

# method/page for seeing the projects that you are collaborating on
@auth.requires_login()
def user_projects():
    project_ids = db(db.collaborator.collaborator==auth.user).select(db.collaborator.project_id, distinct=True)
    projects = []
    for project_id in project_ids:
        projects.append(db.project(project_id.project_id))
    assigned_items = db(db.item.assign_to==auth.user).select()
    created_items = db(db.item.created_by==auth.user).select()
    return dict(projects=projects, project_ids=project_ids, assigned_items=assigned_items, created_items=created_items)

# page/method for adding attachments to comments
@auth.requires_login()
def add_attachment():
    commenttype = request.args(0, cast=int) or redirect('default', 'index')
    project_id = request.args(1, cast=int) or redirect('default', 'index')
    comment_id = request.args(2, cast=int) or redirect('default','index')
    item_id = request.args(3, cast=int)
    if commenttype==1:
        form = SQLFORM(db.project_comment, comment_id, fields=['attachment'], labels={'attachment':'File Attachment'}, submit_button='Add Attachment').process()
        if form.accepted:
            response.flash = "Attachment Added"
            redirect(URL('default','project', args=project_id))
        elif form.errors:
            response.flash = "Error Adding Attachment"
    elif commenttype==2:
        form = SQLFORM(db.item_comment, comment_id, fields=['attachment'], labels={'attachment':'File Attachment'}, submit_button='Add Attachment').process()
        if form.accepted:
            response.flash = "Attachment Added"
            redirect(URL('default','item', args=[project_id, item_id]))
        elif form.errors:
            response.flash = "Error Adding Attachment"
    else:
        redirect('default', 'index')
    return dict(form=form)

# page/method for uploading attachments and/or comments
@auth.requires_login()
def upload():
    commenttype = request.args(0, cast=int) or redirect('default', 'index')
    project_id = request.args(1, cast=int) or redirect('default', 'index')
    item_id = request.args(2, cast=int)
    if commenttype==1:
        db.project_comment.project_id.default = project_id
        form = SQLFORM(db.project_comment, fields=['attachment'], labels={'attachment':'File Attachment'}, submit_button='Add Attachment').process()
        if form.accepted:
            response.flash = "Attachment Added"
            redirect(URL('default','project', args=project_id))
        elif form.errors:
            response.flash = "Error Adding Attachment"
    elif commenttype==2:
        db.item_comment.item_id.default = item_id
        form = SQLFORM(db.item_comment, fields=['attachment'], labels={'attachment':'File Attachment'}, submit_button='Add Attachment').process()
        if form.accepted:
            response.flash = "Attachment Added"
            redirect(URL('default','item', args=[project_id, item_id]))
        elif form.errors:
            response.flash = "Error Adding Attachment"
    else:
        redirect('default', 'index')
    return dict(form=form)

# page/method for changing the reminder settings for each item
@auth.requires_login()
def reminder():
    project_id = request.args(0, cast=int) or redirect('default', 'index')
    item_id = request.args(1, cast=int) or redirect('default', 'index')
    reminder = db((db.reminder.item_id==item_id)&(db.reminder.author==auth.user.id)).select().first()
    form = SQLFORM(db.reminder, reminder.id, field=['reminders'], labels={'reminders':'Send Reminders'}, submit_button='Update Reminder').process()
    form.element(_type='submit')['_class']='btn btn-inverse'
    if form.accepted:
        session.flash = "Reminder Updated"
        redirect(URL('default','user_projects'))
    elif form.errors:
        session.flash = "Error Updating Reminder"
        redirect(URL('default','user_projects'))
    return dict(form=form, reminder=reminder, project_id=project_id, item_id=item_id)

# method to subscribe to rss feed for your updates to a specific project
@auth.requires_login()
def projectfeed():
    #project_id = request.vars.partialstr if request.vars else None
    project_id = request.vars.values()[0]
    project = db.project(project_id) or redirect('default', 'index')
    return dict(title='Project Feed: ' + project.title,
                link=URL('default','project', args=project.id, scheme=True, host=True),
                description='Project Tracker Feed for ' + project.title,
                entries=db((db.rss_entry.author==auth.user)&(db.rss_entry.project_id==project.id)).select().as_list())

# method to add tasks via REST(xml/json)
# format accepted as ?project=ProjectName&newtask=Todo&user=UserLastName&assignto=AssigneeLastName
# or /ProjectName/Todo/UserLastName/AssigneeLastName/
@service.xml
@service.json
def addtask(project, newtask, user, assignto):
    if len(project) and len(newtask) and len(user) and len(assignto):
        thisproject = db(db.project.title==project).select().first()
        if thisproject:
            thisuser = db(db.auth_user.last_name==user).select().first()
            if thisuser:
                assignedto = db(db.auth_user.last_name==assignto).select().first()
                if assignedto:
                    ret = db.item.validate_and_insert(body=newtask, project_id=thisproject.id, created_by=thisuser, assign_to=assignedto)
                    if ret.errors:
                        raise HTTP(500, DIV(XML('Error! - Did not add task. This is an internal server error, please try again later.'), A(' Click to Go Back', _href=request.env.http_referer)))
                    else:
                        # call add task to update the db with this info
                        add_task(thisproject.id, ret.id, newtask, thisuser, assignedto)
                        # finally respond with xml receipt
                        respond = DIV(XML('Success! - Project= ' + thisproject.title +
                                  '; New Task Added= ' + newtask +
                                  '; created by= ' + get_username(thisuser) +
                                  '; assigned to= ' + get_username(assignedto) +
                                  '.'), A(' Click to Go Back', _href=request.env.http_referer))
                    raise HTTP(200, respond)
                else:
                    raise HTTP(400, DIV(XML('Error! - Did not add task. Please make sure the assigned name is correct and try again.'), A(' Click to Go Back', _href=request.env.http_referer)))
            else:
                raise HTTP(400, DIV(XML('Error! - Did not add task. Please make sure the user name is correct and try again.'), A(' Click to Go Back', _href=request.env.http_referer)))
        else:
            raise HTTP(400, DIV(XML('Error! - Did not add task. Please make sure the project name is correct and try again.'), A(' Click to Go Back', _href=request.env.http_referer)))
    else:
        raise HTTP(400, DIV(XML('Error! Did not add task. Please check your variables and try again.'), A(' Click to Go Back', _href=request.env.http_referer)))

# method to add tasks via Remote Procedure Calls(xmlrpc)
# format accepted as (project=*Name of project, newtask=*To do, user=*Last/Sir Name of person creating task, assignto=*Last/Sir Name of person being assigned the task)
@service.xmlrpc
def addtask_rpc(project, newtask, user, assignto):
    if len(project) and len(newtask) and len(user) and len(assignto):
        thisproject = db(db.project.title==project).select().first()
        if thisproject:
            thisuser = db(db.auth_user.last_name==user).select().first()
            if thisuser:
                assignedto = db(db.auth_user.last_name==assignto).select().first()
                if assignedto:
                    ret = db.item.validate_and_insert(body=newtask, project_id=thisproject.id, created_by=thisuser, assign_to=assignedto)
                    if ret.errors:
                        return 'Error! - Did not add task. This is an internal server error, please try again later.'
                    else:
                        # call add task to update the db with this info
                        add_task(thisproject.id, ret.id, newtask, thisuser, assignedto)
                        # finally respond with rpc receipt
                        return 'Success! - Project= ' + thisproject.title + '; New Task Added= ' + newtask + '; created by= ' + get_username(thisuser) + '; assigned to= ' + get_username(assignedto) + '.'
                else:
                   return 'Error! - Did not add task. Please make sure the assigned name is correct and try again.'
            else:
                return 'Error! - Did not add task. Please make sure the user name is correct and try again.'
        else:
            return 'Error! - Did not add task. Please make sure the project name is correct and try again.'
    else:
        return 'Error! Did not add task. Please check your variables and try again.'

## builtin helper methods for common actions

# method for downloading files from the db
@cache.action()
def download():
    return response.download(request, db)

# method to expose services
def call():
    return service()

#method to expose data as grid via crud
@auth.requires_signature()
def data():
    return dict(form=crud())
