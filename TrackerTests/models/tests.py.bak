# coding: utf8

# import WebClient from Gluon
from gluon.contrib.webclient import WebClient

# connect to tracker app
client = WebClient('http://127.0.0.1:8000/tracker/default/',
                   postbacks=True)

# this runs all tests and returns them as a list
def run_tests():
    results = []
    results.append(test1())
    results.append(test2())
    results.append(test3())
    results.append(test4())
    results.append(test5())
    return results

# test 1 is a basic test of the title
def test1():
    # get the first page and test title
    client.get('index')
    assert('Project Tracker' in client.text)
    return 'Test 1 passed.'

# db table to use to store whether the user has been registered yet or not
db.define_table('testuser',
                Field('name', 'string'),
                Field('registered', 'boolean', default=False))

# test 2 is a basic test of the user registration or login
def test2():
    client.get('index')
    # register new test user
    testuser = db(db.testuser.name=='Homer').select().first()
    if testuser and testuser.registered:
            data = dict(email='hsimpson@mail.com',
            password='test',
            _formname='login')
            client.post('user/login', data=data)
    else:
        data = dict(first_name='Homer',
            last_name='Simpson',
            email='hsimpson@mail.com',
            password='test',
            password_two='test',
            _formname='register')
        client.post('user/register', data=data)
        db.testuser.update_or_insert(name='Homer',registered=True)
    assert('Welcome Homer' in client.text)
    # logout of the tracker app
    client.get('user/logout')
    return 'Test 2 passed.'

# test 3 is a basic login and logout test
def test3():
    # login again
    data = dict(email='hsimpson@mail.com',
            password='test',
            _formname='login')
    client.post('user/login', data=data)
    # logout of the tracker app
    client.get('user/logout')
    assert('Welcome to Project Tracker,' in client.text)
    return 'Test 3 passed.'

db.define_table('testproject',
                Field('title', 'string'),
                Field('counter','integer'))

# test 4 is a basic test of creating a new project
def test4():
    # login again
    data = dict(email='hsimpson@mail.com',
            password='test',
            _formname='login')
    client.post('user/login', data=data)
    client.get('new_project')
    testproject = db(db.testproject.title=='test').select().first()
    if testproject and testproject.counter:
        counter = testproject.counter + 1
        title = 'Functional Test Project #' + str(counter)
        data = dict(title=title)
        db(db.testproject.title=='test').update(counter=counter)
    else:
        title = 'Functional Test Project #' + str(1)
        data = dict(title=title)
        db.testproject.update_or_insert(title='test',counter=1)
    client.post('new_project', data=data)
    assert('Functional Test Project' in client.text)
    return 'Test 4 passed.'

# test 5 is a basic test of adding new tasks to the project
def test5():
    counter = db(db.testproject.title=='test').select().first()
    title = 'Functional Test Project #' + str(counter)
    data = dict(project=title, newtask='new test task',
                user='Simpson', assignto='Simpson')
    client.post('call/xmlrpc/addtask_rpc', data=data)
    assert(200==client.status)
    # logout of the tracker app
    client.get('user/logout')
    return 'Test 5 passed.'
