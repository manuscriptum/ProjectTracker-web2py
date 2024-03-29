# coding: utf8
# db_lists.py by Kevin Westropp
# main data model for project tracker

# import datetime for dates and times
import datetime

# second db for running background tasks
db_background = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])

# import the scheduler for running tasks
from gluon.scheduler import Scheduler
scheduler = Scheduler(db_background)

# db history
auth.enable_record_versioning(db)

# database definition for new project
db.define_table('project',
                Field('title', requires=IS_NOT_EMPTY()),
                Field('created_by', 'reference auth_user', default=auth.user_id, writable=False),
                Field('date_created', 'datetime', default=request.now, writable=False),
                Field('date_updated', 'datetime', default=request.now, writable=False),
                format = '%(title)s')

# can't have multiple lists with the same title in database
db.project.title.requires = IS_NOT_IN_DB(db, db.project.title)
#db.project.id.readable = db.project.id.writable = False;

# db definition for project comments
db.define_table('project_comment',
                Field('project_id', 'reference project', requires=IS_IN_DB(db, db.project.id, '%(title)s'), writable=False, readable=False),
                Field('author', 'reference auth_user', default=auth.user_id, writable=False),
                Field('date_posted', 'datetime', default=request.now, writable=False),
                Field('body', 'text', requires=IS_NOT_EMPTY()),
                Field('attachment', 'upload'))

db.project_comment.id.readable = db.project_comment.id.writable = False

# status for todo items
STATUS = ('completed','accepted','rejected','pending')

# db definition for todo items
db.define_table('item',
                Field('project_id', 'reference project', requires=IS_IN_DB(db, db.project.id, '%(title)s'), writable=False, readable=False),
                Field('created_by', 'reference auth_user', default=auth.user_id, writable=False),
                Field('date_created', 'datetime', default=request.now, writable=False),
                Field('assign_to', 'reference auth_user'),
                Field('due', 'datetime'),
                Field('expiration_date','datetime', default=request.now + datetime.timedelta(days=28)),
                Field('status', requires=IS_IN_SET(STATUS), default='pending'),
                Field('body', 'text', requires=IS_NOT_EMPTY()),
                Field('tags', 'list:reference tag'))

db.item.id.readable = db.item.id.writable = False

# db definition for tags
db.define_table('tag',
                Field('title', requires=IS_NOT_EMPTY()))

db.tag.id.readable = db.tag.id.writable = False

# db definition for item comments
db.define_table('item_comment',
                Field('item_id', 'reference item', requires=IS_IN_DB(db, db.project.id, '%(title)s'), writable=False, readable=False),
                Field('author', 'reference auth_user', default=auth.user_id, writable=False),
                Field('date_posted', 'datetime', default=request.now, writable=False),
                Field('body', 'text', requires=IS_NOT_EMPTY()),
                Field('attachment', 'upload'))

db.item_comment.id.readable = db.item_comment.id.writable = False

# to ensure the id doesn't show up in forms
db.item.id.readable = db.item.id.writable = False;

# db definition for collaborators, shows the users who have created items on a particular list
db.define_table('collaborator',
                Field('project_id', 'reference project', requires=IS_IN_DB(db, db.project.id, '%(title)s'), writable=False, readable=False),
                Field('collaborator', 'reference auth_user'))

db.collaborator.id.readable = db.collaborator.id.writable = False;

TRIGGER = ('daily','weekly','monthly')

# db definition for email reminders, settings can be altered by user
db.define_table('reminder',
                Field('author', 'reference auth_user', default=auth.user_id, writable=False),
                Field('item_id', 'reference item', requires=IS_IN_DB(db, db.project.id, '%(title)s'), writable=False, readable=False),
                Field('reminders', requires=IS_IN_SET(TRIGGER), default='weekly'),
                Field('last_sent', 'datetime', default=request.now))

db.reminder.id.readable = db.reminder.id.writable = False;
db.reminder.last_sent.readable = db.reminder.last_sent.writable = False;
db.reminder.author.readable = db.reminder.author.writable = False;

# db definition for rss feed entries, each update is considered an entry
db.define_table('rss_entry',
    Field('project_id', 'reference project', requires=IS_IN_DB(db, db.project.id, '%(title)s'), writable=False, readable=False),
    Field('item_id', 'reference item', requires=IS_IN_DB(db, db.project.id, '%(title)s'), writable=False, readable=False),
    Field('author', 'reference auth_user', default=auth.user_id, writable=False),
    Field('title', 'text'),
    Field('link', 'string'),
    Field('description', 'text'),
    Field('created_on','datetime'),
    Field('updated_on', 'datetime'))

db.rss_entry.id.readable = db.rss_entry.id.writable = False;

## Scheduler Tasks to run
def run_remindertasks():
    dailytask = run_dailyreminders()
    weeklytask = run_weeklyreminders()
    monthlytask = run_monthlyreminders()
    return dict(dailytask=dailytask, weeklytask=weeklytask, monthlytask=monthlytask)

# queues the daily reminder task scheduler
def run_dailyreminders():
    task = scheduler.queue_task('send_remindersdaily', start_time=datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,23,30,30,30), stop_time=datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,23,59,59,59))
    return task

# queues the daily reminder task scheduler
def run_weeklyreminders():
    task = scheduler.queue_task('send_remindersweekly', start_time=datetime.datetime.today() + 2, stoptime=datetime.datetime.today() + 6)
    return task

# queues the daily reminder task scheduler
def run_monthlyreminders():
    task = scheduler.queue_task('send_remindersmonthly', start_time=datetime.datetime.today().month + 1, stoptime=datetime.datetime.today().day + 7)
    return task


## Scheduler Functions

#method to check if dailyreminders have been sent
def dailyreminder_sent(reminder):
    if reminder.last_sent.day == datetime.datetime.today().day:
        return True;
    else:
        return False;

#method to check if weeklyreminders have been sent
def weeklyreminder_sent(reminder):
    if (reminder.last_sent.day%7) == (datetime.datetime.today().day%7):
        return True;
    else:
        return False;

#method to check if monthlyreminders have been sent
def monthlyreminder_sent(reminder):
    if reminder.last_sent.month == datetime.datetime.today().month:
        return True;
    else:
        return False;

# method to send daily reminders
def send_remindersdaily():
    reminders = db(db.reminder.reminders=='daily').select()
    for reminder in reminders:
        if dailyreminder_sent(reminder)==False:
            send_reminder('This is a daily reminder for the item: ' + reminder.item_id, get_body(reminder.item_id), reminder.author, reminder.item_id)
            reminder.last_sent = datetime.datetime.now()

# method to send weekly reminders
def send_remindersweekly():
    reminders = db(db.reminder.reminders=='weekly').select()
    for reminder in reminders:
        if weeklyreminder_sent(reminder.item_id)==False:
            send_reminder('This is a weekly reminder for the item: ' + reminder.item_id, get_body(reminder.item_id), reminder.author)
            reminder.last_sent = datetime.datetime.now()

# method to send montly reminders
def send_remindersmonthly():
    reminders = db(db.reminder.reminders=='monthly').select()
    for reminder in reminders:
        if monthlyreminder_sent(reminder.item_id)==False:
            send_reminder('This is a monthly reminder for the item: ' + reminder.item_id, get_body(reminder.item_id), reminder.author)
            reminder.last_sent = datetime.datetime.now()

## Functions for DB

# method for getting formatted user - first + last name + hyperlink to email
def get_user(auth_user):
    if auth_user==auth.user.id:
        return A(T('You'), _href=URL('default', 'user_projects'))
    else:
        return A(T(auth_user.first_name + " " + auth_user.last_name), _href='mailto: ' + auth_user.email)

# method for getting just the username, first and last
def get_username(auth_user):
    return auth_user.first_name + " " + auth_user.last_name

# method for getting progress bar visual width
def date_progress(created, due):
    diff = datetime.datetime.now().toordinal() - created.toordinal()
    if diff < 1:
        diff = 1
    base = due.toordinal() - created.toordinal()
    final = float(diff) / float(base)
    return final*100

# method to add rss feed entry for item
def new_feedentry(project_id, item_id, user):
    item = db(db.item.id==item_id).select().first()
    link = URL('default', 'item', args=[project_id, item_id], scheme=True, host=True)
    title = 'New Task: ' + item.body
    description = 'Created by: ' + get_username(item.created_by) + ' and assigned to: ' + get_username(item.assign_to)
    db.rss_entry.update_or_insert(project_id=project_id, item_id=item_id, author=user, link=link, title=title, description=description, created_on=request.now, updated_on=request.now)

# method to update rss feed entry for item
def update_feedentry(project_id, item_id, user):
    item = db(db.item.id==item_id).select().first()
    link = URL('default', 'item', args=[project_id, item_id], scheme=True, host=True)
    title = 'Updated Task: ' + item.body
    description = 'Created by: ' + get_username(item.created_by) + ' and assigned to: ' + get_username(item.assign_to)
    db.rss_entry.update_or_insert(project_id=project_id, item_id=item_id, author=user, link=link, title=title, description=description, updated_on=request.now)

#method to add a new task, calls other functions to update different dbs
def add_task(project_id, item_id, item_body, user_created, user_assigned):
    #update the date for tracking when changes occur
    db(db.project.id==project_id).update(date_updated=request.now)
    #collabortor for showing all the collaborators of a particular list
    update_collaborators(user_created, user_assigned, project_id)
    # membership for only the assigned user and the created user
    group_id = auth.add_group(item_id, 'Group for the todo: ' + item_body)
    auth.add_membership(group_id, user_created)
    auth.add_membership(group_id, user_assigned)
    # add email reminders for both of the users
    update_reminder(user_created, user_assigned, item_id, project_id)

# method to update the reminders and send out initial reminders
def update_reminder(user_created, user_assigned, item_id, project_id):
    # add email reminders for both of the users
    db.reminder.update_or_insert(author=user_created,item_id=item_id)
    db.reminder.update_or_insert(author=user_assigned,item_id=item_id)
    # send initial email reminder to assigned user and creator
    send_reminder('Project Tracker: You have created a new task.', get_body(item_id), user_created)
    send_reminder('Project Tracker: You have have been assigned a new task.', get_body(item_id), user_assigned)

#collabortor for showing all the collaborators of a particular list
def update_collaborators(user_created, user_assigned, project_id):
    db.collaborator.update_or_insert(collaborator=user_created,project_id=project_id)
    db.collaborator.update_or_insert(collaborator=user_assigned,project_id=project_id)

# method to send out email reminders
def send_reminder(subject, body, username):
    user = db(db.auth_user.id==username).select().first()
    mail.send(user.email, subject, body)

# method to build body of email for reminders
def get_body(item_id):
    item = db(db.item.id==item_id).select().first()
    context = dict(item=item)
    message = response.render('message.html', context)
    return message

# method to update expiration date to include due date if assigned
def update_expiration(due, item_id):
    datedue = due + datetime.timedelta(days=28)
    db(db.item.id==item_id).update(expiration_date=datedue)
