# coding=utf-8
__author__ = 'arlequin'


class Klass:
    def __init__ (self, name):
        self.students = {}
        self.name = name

class Student:
    def __init__ (self,stuno,name):
        self.course = []
        self.name = name
        self.stuno = stuno

    def addCourse(self, c):
        self.course.append(c)

class Course:
    def __init__ (self, name, score, notes):
        self.name = name
        self.score = score
        self.notes = notes


with open("transcript.csv") as xscj:
    lines = xscj.readlines()


klasses = {}


for line in lines:
    try:
      lst = line.split(',')
    except :
        pass
    else:

        length = len(lst)
        if length != 7:
            continue

        xh = lst[0].strip()
        xm = lst[1].strip()
        xzb = lst[2].strip()
        kcmc = lst[3].strip()
        xf = lst[4].strip()
        zscj = lst[5].strip()
        bz = lst[6].strip()

        grade = klasses.setdefault(xzb,Klass(xzb))
        student = grade.students.setdefault(xh,Student(xh,xm))


        if bz == '缺考':
             zscj = '缺考'
        elif bz == '无效':
            zscj = '缺考'
        elif bz == '缓考':
            zscj = '缓考'

        course = Course(kcmc,zscj,bz)
        student.addCourse(course)

lines = None

import sys
encode_type = sys.getfilesystemencoding()

for gk, gv in klasses.items():

    gked = gk + '.csv'
    gkec = gked.decode('UTF-8').encode(encode_type)

    csvof = open(gkec, 'w')
    header = '学号,姓名,班级,'+\
             '课程1,成绩1,课程2,成绩2,课程3,成绩3,课程4,成绩4,课程5,成绩5,'+\
             '课程6,成绩6,课程7,成绩7,课程8,成绩8,课程9,成绩9,课程10,成绩10,'+\
             '课程11,成绩11,课程12,成绩12,课程13,成绩13,课程14,成绩14,课程15,成绩15,' +\
             '课程16,成绩16,课程17,成绩17,课程18,成绩18'
    csvof.write(header.decode('UTF-8').encode(encode_type))

    for sk, sv in gv.students.items():
        stucse = '{0},{1},{2}'.format(sv.stuno, sv.name,gk)

        i = 1
        for cse in sv.course:
            stucse += ',' + cse.name + ',' + cse.score
            i += 1

        if i < 18:
            stucse += ', , '*(18-i+1)

        stucse += '\n'
        stucseec = stucse.decode('UTF-8').encode(encode_type)
        csvof.write(stucseec)

    csvof.close()


