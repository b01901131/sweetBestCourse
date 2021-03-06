#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os   
import collections
import Tkinter as tkinter
from tktable import *
from initial import *
from login import *
from util import *
#from hover import *
import State
import Course
from operator import itemgetter
import pdb
import copy

class GUI:
    def __init__(self):
        self.bi_show = []
        self.fu_shuan_bi_show = []
        self.class_time = []
        self.courses, self.general_courses, self.PE_courses = readCoursePickle()
        self.EmptyState = State.State()
        self.InitialState = State.State()
        self.nextState = State.State() 
        self.lastStates = []
        self.total_score = 31

    def test_cmd(self, event):
        if event.i == 0:
            return '%i, %i' % (event.r, event.c)
        else:
            return 'set'

    def initVar(self):
        self.root = tkinter.Tk()
        self.root.wm_title("NTU Best Course")
        self.var = ArrayVar(self.root)
        for y in range(-1, 15):
            index = "%i,%i" % (y, -1)
            self.var[index] = index
            if y == -1:
                self.var[index] = ""
            elif 0 <= y <= 10:
                self.var[index] = y
            else:
                self.var[index] = chr(54+y)
        for x in range(-1,6):
            index = "%i,%i" % (-1, x)
            self.var[index] = index
            if x == -1:  self.var[index] = ""
            elif x == 0: self.var[index] = "ㄧ"
            elif x == 1: self.var[index] = "二"
            elif x == 2: self.var[index] = "三"
            elif x == 3: self.var[index] = "四"
            elif x == 4: self.var[index] = "五"
            elif x == 5: self.var[index] = "六"
        self.var["-1,6"] = "其他課程"

    def clearVar(self):
        for x in range(0, 7):
            for y in range(0, 15):
                index = "%i,%i" % (y, x)
                self.var[index] = ""

    def browsecmd(self, event):
        index = self.test.index('active')
        if self.var[index] != "":
            time = "%s" % chr(65+int(index[2]))+chr(48+int(index[0]))
            course_name, teacher = self.var[index].encode('utf-8').split(" \n")
            self.test.bind("<BackSpace>", lambda event, arg=[False, index, course_name, teacher, time]: self.delete(event, arg))
            self.test.bind("<Tab>", lambda event, arg=[True, index, course_name, teacher, time]: self.delete(event, arg))
            self.test.bind("<Return>", lambda event, arg=[index, course_name, teacher, time]: self.display(event, arg))
            self.test.bind("<Key>", lambda event, arg=[course_name, teacher, time]: self.adjust(event, arg))

    def adjust(self, event, arg):
        course_name, teacher, time = arg
        result = ""
        for c in self.nextState.taken:
            if c.name == course_name and c.teacher == teacher:
                if time in c.time or "%s \n%s" % (course_name, teacher) in self.info_classes:
                    if event.char == "=":
                        self.nextState.likeCourse(c)
                        result = "與[%s]相關課程喜好程度上升" % c.name+"\n%.2f"%c.favor
                    elif event.char == "-":
                        self.nextState.dislikeCourse(c)
                        result = "與[%s]相關課程喜好程度下降" % c.name+"\n%.2f"%c.favor
        average_sweet = sum([c.GPA for c in self.nextState.taken])/float(len(self.nextState.taken))
        self.info_label.config(text="總學分數: %d" % self.nextState.credit+"\n負擔指標: %.2f"%self.nextState.loading+"\n歷年平均GPA: %.2f\n"%average_sweet+result)
        

    def display(self, event, arg):
        menu = tkinter.Menu(self.root, tearoff=0)
        index, course_name, teacher, time = arg
        for c in self.nextState.taken:
            if c.name == course_name and c.teacher == teacher:
                if time in c.time or "%s \n%s" % (course_name, teacher) in self.info_classes:
                    menu.add_command(label="教師: %s" % c.teacher)
                    menu.add_command(label="課號: %s" % c.ID)
                    menu.add_command(label="平均GPA: %.2f / 4.3" % c.GPA)
                    menu.add_command(label="課程重度: %.2f / 10.00" % c.class_load)
                    menu.add_command(label="老師重度: %.2f / 10.00" % c.teacher_load)
                    menu.add_command(label="課程星數: %.2f / 5.00" % c.class_stars)
                    menu.add_command(label="老師星數: %.2f / 5.00" % c.teacher_stars)
                    hot = [recc for recc in [c.class_possibility, c.teacher_possibility] if recc not in [None]]
                    if sum([recc for recc in hot if recc not in [None]]) > 0:
                        score = sum(hot) / len(hot) * 100
                        print score
                        menu.add_command(label="熱門度: %.2f %%" % score)
        menu.post(390+110*(int(index[2])+1), 90+34*(int(index[0])+1))

    def delete(self, event, arg):
        index, course_name, teacher, time = arg[1:]
        cmd = False
        if time[0] == "G":
            cmd = True
        trialState, times, course = self.nextState.deleteCourse(course_name, teacher, time, cmd)
        if trialState != None:
            self.lastStates.append(copy.deepcopy(self.nextState))
            self.nextState = copy.deepcopy(trialState)
            for t in times:
                t_index = "%i,%i" % (int(t[1]), (int(ord(t[0])-65)))
                self.var[t_index] = ""
            if cmd:
                self.var[index] = ""
            if arg[0]:
                self.nextState.likeCourse(course)
                result = "與[%s]相關課程喜好程度上升" % course.name+"\n%.2f"%course.favor
            else:
                self.nextState.dislikeCourse(course)
                result = "與[%s]相關課程喜好程度下降" % course.name+"\n%.2f"%course.favor
        else:
            self.info_label.config(text="刪除失敗QQ")
        average_sweet = sum([c.GPA for c in self.nextState.taken])/float(len(self.nextState.taken))
        self.info_label.config(text="總學分數: %d" % self.nextState.credit+"\n負擔指標: %.2f"%self.nextState.loading+"\n歷年平均GPA: %.2f\n"%average_sweet+result)
       
    def loginMethod(self):
        self.info_label.config(text="登入中...")
        self.bi_show, self.fu_shuan_bi_show = Initial(self.user_field.get(), self.grade_field.get())
        self.takenCourses,toGraduate_unorderd = Login(self.user_field.get(), self.pswd_field.get())
        self.InitialState.setPersonDepart("EE")
        exceptions = ['EE4049']
        self.ruleOutTaken(exceptions) #rule out the taken classes
        # --- customize courses ---
        self.depart_courses = []
        self.non_depart_courses = []
        for course in self.courses:
            if self.InitialState.personDepart in course.ID and len(course.ID)==6:
                self.depart_courses.append(course)
            else:
                self.non_depart_courses.append(course)
        self.InitialState.setCategorizedCourses(self.depart_courses,self.non_depart_courses,self.general_courses,self.PE_courses)
        del self.depart_courses, self.non_depart_courses
        # --- deal with personal toGraduate ---
        self.toGraduate = [[b for b in self.bi_show if b not in self.takenCourses]]
        self.toGraduate.append(toGraduate_unorderd[4:])
        self.toGraduate.append(toGraduate_unorderd[0][0])#系上選修
        self.toGraduate.append(toGraduate_unorderd[1][0])
        self.toGraduate.append(toGraduate_unorderd[2][0])
        self.toGraduate.append(toGraduate_unorderd[3][0])
        self.InitialState.setLoadingLimit(200.0)
        self.InitialState.setPersonDistrib(self.toGraduate)
        self.InitialState.transformID()
        #---set value in display---
        self.bi_show_credit = 0
        past_ID = []
        for c in self.toGraduate[0]:
            if c.ID in past_ID:
                continue
            else:
                self.bi_show_credit+=c.credit
                past_ID.append(c.ID)
        dis1 = self.bi_show_credit+sum([group[0].credit for group in self.toGraduate[1]])
        dis2,dis3,dis4,dis5 = self.toGraduate[2],self.toGraduate[3],self.toGraduate[4],self.toGraduate[5]
        print "toGraduate:",dis1,",",dis2,",",dis3,",",dis4,",",dis5
        print len(self.toGraduate[1])
        while dis1 > 15:
            self.toGraduate[1].pop()
            dis1 = self.bi_show_credit+sum([group[0].credit for group in self.toGraduate[1]])
        print len(self.toGraduate[1])
        if (dis1+dis2+dis3+dis4+dis5) > 25:
            ratio = (25-dis1)/float(dis2+dis3+dis4+dis5)#get a math.floor()
            dis2 = int(ratio*dis2)
            dis3 = int(ratio*dis3)
            dis4 = int(ratio*dis4)
            dis5 = int(ratio*dis5)
        print "toGraduate:",dis1,",",dis2,",",dis3,",",dis4,",",dis5
        self.shibi_spin.delete(0)
        self.shibi_spin.insert(0,dis1)
        self.shish_spin.delete(0)
        self.shish_spin.insert(0,dis2)
        self.shush_spin.delete(0)
        self.shush_spin.insert(0,dis3)
        self.tonsh_spin.delete(0)
        self.tonsh_spin.insert(0,dis4)
        self.sport_spin.delete(0)
        self.sport_spin.insert(0,dis5) 
        self.sweet_scale.set(5)
        self.load_scale.set(3)
        self.star_scale.set(3)
        self.load_limit.set(dis1+dis2+dis3+dis4+dis5)
        self.InitialState.setPersonDistrib(self.toGraduate)
        self.nextState = copy.deepcopy(self.InitialState)
        self.nextState.setLoadingLimit(self.load_scale.get())
        self.info_label.config(text="登入完成！")
        #print self.toGraduate
        #self.bi_show.append(self.fu_shuan_bi_show[0])通識
        #self.to_show = [course for course in self.bi_show if course not in self.takenCourses]
        #self.updateBishow2Table(self.to_show)

    def loadMethod(self):
        self.checkLogin()
        course = self.nextState.findCourse(self.loadC_field.get(),self.loadT_field.get())
        '''
        sweety_dict = readSweetyCsv()
        course_info = sweety_dict[(self.loadC_field.get(), self.loadT_field.get())][0]
        course_info[6:] = map(int, course_info[6:])
        course = Course.Course(self.loadC_field.get(), self.loadT_field.get(), course_info[3], \
                        course_info[0], course_info[6:], course_info[2])
        '''
        if course!=None and self.nextState.canTake(course):
            self.nextState.generateSuccessor(course)
            print "Course %s loaded" % self.loadC_field.get()
            self.updateTable()
        else: 
            self.info_label.config(text="無法帶入課程")

    def searchMethod(self):
        self.checkLogin() 
        self.clearVar()
        self.nextState.clearCourses()
        self.nextState.setSweetW(self.sweet_scale.get())
        self.nextState.setLoadW(self.load_scale.get())
        self.nextState.setStarW(self.star_scale.get())
        dis1 = self.bi_show_credit+sum([group[0].credit for group in self.toGraduate[1]])
        dis2,dis3,dis4,dis5 = int(self.shish_spin.get()), int(self.shush_spin.get()), int(self.tonsh_spin.get()), int(self.sport_spin.get())
        self.nextState.setCustomDistrib(dis2,dis3,dis4,dis5)
        self.nextState.setLoadingLimit(self.load_limit.get()*10.0)
        self.credit_limit = dis1+dis2+dis3+dis4+dis5
        self.courseCount = 0
        while(self.nextState.credit <= self.credit_limit):
            trialState = self.nextState.greedySearch()
            if not trialState:
                print "Fininshed optimzed greedy!"
                print self.courseCount,"courses added !!!"
                break
            else:
                self.courseCount += 1
                self.lastStates.append(copy.deepcopy(self.nextState))
                self.nextState = copy.deepcopy(trialState)
        self.updateTable()
        print "Loading =",self.nextState.loading, "while loading_limit =",self.nextState.loading_limit
        print "Credit =",self.nextState.credit
        print "Course taken:"
        for c in self.nextState.taken:
            print c
        average_sweet = sum([c.GPA for c in self.nextState.taken])/float(len(self.nextState.taken))
        self.info_label.config(text="總學分數: %d" % self.nextState.credit+"\n負擔指標: %.2f"%self.nextState.loading+"\n歷年平均GPA: %.2f"%average_sweet)
        
    def infoUpdate(self, cmd):
        if cmd == "show courses not in table":
            table_classes = []
            for y in range(0, 15):
                for x in range(0, 6):
                    if self.var["%i,%i" % (y,x)] != "":
                        table_classes.append(self.var["%i,%i" % (y,x)].encode('utf-8'))
            taken_classes = []
            for c in self.nextState.taken:
                taken_classes.append("%s \n%s" % (c.name,c.teacher))
            self.info_classes = [_class for _class in taken_classes if _class not in table_classes]
            for i in range(len(self.info_classes)):
                self.var["%i,6" % i] = self.info_classes[i]              


    def ruleOutTaken(self,exceptions):
        for taken in self.takenCourses:
            flag=0
            if taken in exceptions: #add exceptions here
                continue
            for c in self.courses:
                if taken==c.ID:
                    print c
                    self.courses.remove(c)
                    flag=1
            for c in self.general_courses:
                if taken==c.ID:
                    print c
                    self.general_courses.remove(c)
                    flag=1
            for c in self.PE_courses:
                if taken==c.ID:
                    print c
                    self.PE_courses.remove(c)
                    flag=1
            if flag!=1:
                print "!!! Can't find:",taken

    def updateTable(self):
        self.clearVar()
        for c in self.nextState.taken:
            for t in c.time:
                index = "%i,%i" % (int(t[1]), (int(ord(t[0])-65)))
                self.var[index] = "%s \n%s" % (c.name, c.teacher)
        self.infoUpdate("show courses not in table")
    
    def checkLogin(self):
        if self.bi_show == []:
            self.info_label.config(text="請先登入！")

    def prevStep(self):
        if len(self.lastStates) > 0:
            if self.nextState not in self.lastStates:
                tmp = copy.deepcopy(self.nextState)
                self.nextState = self.lastStates[-1]
                self.lastStates.append(tmp)
            else:
                self.nextState = self.lastStates[(self.lastStates.index(self.nextState)) - 1]
            self.updateTable()
        else:
            self.info_label.config(text="請先登入！")

    def nextStep(self):
        if len(self.lastStates) >0:
            if self.nextState == self.lastStates[-1]:
                self.info_label.config(text="無法下一步囉 嫩！")
            else:
                self.nextState = self.lastStates[(self.lastStates.index(self.nextState)) + 1]
                self.updateTable()
        else:
            self.info_label.config(text="請先登入！")

    def updateScore(self):
        if (31-self.total_score) >= 0:
            self.total_score = int(self.shibi_spin.get()) + int(self.shish_spin.get()) + \
                               int(self.shush_spin.get()) + int(self.tonsh_spin.get()) + int(self.sport_spin.get())
            self.shibi_spin.config(to=(2*31-self.total_score))
            self.shish_spin.config(to=(2*31-self.total_score))
            self.shush_spin.config(to=(2*31-self.total_score))
            self.tonsh_spin.config(to=(2*31-self.total_score))
            self.sport_spin.config(to=(2*31-self.total_score))
            if self.total_score >= 31:
                self.shibi_spin.config(to=self.shibi_spin.get())
                self.shish_spin.config(to=self.shish_spin.get())
                self.shush_spin.config(to=self.shush_spin.get())
                self.tonsh_spin.config(to=self.tonsh_spin.get())
                self.sport_spin.config(to=self.sport_spin.get())

    def createTable(self):
        self.user_label = tkinter.Label(self.root, text="帳號：")
        self.user_label.grid(row=0, column=0)
        self.user_field = tkinter.Entry(self.root, width=15)
        self.user_field.grid(row=0, column=1, columnspan=3)
    
        self.pswd_label = tkinter.Label(self.root, text="密碼：")
        self.pswd_label.grid(row=1, column=0)
        self.pswd_field = tkinter.Entry(self.root, width=15, show="*")
        self.pswd_field.grid(row=1, column=1, columnspan=3)

        self.grade_label = tkinter.Label(self.root, text="年級：")
        self.grade_label.grid(row=2, column=0)
        self.grade_field = tkinter.Entry(self.root, width=15)
        self.grade_field.grid(row=2, column=1, columnspan=3)

        self.loadC_label = tkinter.Label(self.root, text="帶入課號：")
        self.loadC_label.grid(row=4, column=0)
        self.loadC_field = tkinter.Entry(self.root, width=10)
        self.loadC_field.grid(row=4, column=1)
        self.loadT_label = tkinter.Label(self.root, text="教師：")
        self.loadT_label.grid(row=4, column=2)
        self.loadT_field = tkinter.Entry(self.root, width=6)
        self.loadT_field.grid(row=4, column=3)
        self.load_button = tkinter.Button(self.root, text="帶入", command=self.loadMethod)
        self.load_button.grid(row=4, column=4)

        self.shibi_label = tkinter.Label(self.root, text="系必")
        self.shibi_label.grid(row=5, column=0)
        self.shibi_spin = tkinter.Spinbox(self.root, from_=0, to=self.total_score, command=self.updateScore, width=4)
        self.shibi_spin.grid(row=6, column=0)

        self.shish_label = tkinter.Label(self.root, text="系選")
        self.shish_label.grid(row=5, column=1)
        self.shish_spin = tkinter.Spinbox(self.root, from_=0, to=self.total_score, command=self.updateScore, width=4)
        self.shish_spin.grid(row=6, column=1)

        self.shush_label = tkinter.Label(self.root, text="選修")
        self.shush_label.grid(row=5, column=2)
        self.shush_spin = tkinter.Spinbox(self.root, from_=0, to=self.total_score, command=self.updateScore, width=4)
        self.shush_spin.grid(row=6, column=2)

        self.tonsh_label = tkinter.Label(self.root, text="通識")
        self.tonsh_label.grid(row=5, column=3)
        self.tonsh_spin = tkinter.Spinbox(self.root, from_=0, to=self.total_score, command=self.updateScore, width=4)
        self.tonsh_spin.grid(row=6, column=3)

        self.sport_label = tkinter.Label(self.root, text="體育")
        self.sport_label.grid(row=5, column=4)
        self.sport_spin  = tkinter.Spinbox(self.root, from_=0, to=self.total_score, command=self.updateScore, width=4)
        self.sport_spin.grid(row=6, column=4)
        
        self.sweet_scale  = tkinter.Scale(self.root, label="甜度", from_=5, to=-5)
        self.sweet_scale.grid(row=7, column = 0)
        self.load_scale   = tkinter.Scale(self.root, label="重度", from_=5, to=-5)
        self.load_scale.grid(row=7, column = 1)
        self.star_scale   = tkinter.Scale(self.root, label="星評", from_=5, to=-5)
        self.star_scale.grid(row=7, column = 2)
        self.load_limit = tkinter.Scale(self.root, label="重度上限", from_=31, to=0)
        self.load_limit.grid(row=7, column = 4)
        
        self.search_button = tkinter.Button(self.root, text="搜尋最佳課程", command=self.searchMethod)
        self.search_button["width"] = 20
        self.search_button.grid(row=8, column=1, columnspan=3)

        self.nextstep_button = tkinter.Button(self.root, text="下一步", command=self.nextStep)
        self.nextstep_button.grid(row=15, column=3)

        self.prevstep_button = tkinter.Button(self.root, text="上一步", command=self.prevStep)
        self.prevstep_button.grid(row=15, column=1)

        self.info_label = tkinter.Label(self.root, text="請先登入")
        self.info_label.grid(row=9, column=1, columnspan=3)
        
        self.login_button = tkinter.Button(self.root, text="登入", command=self.loginMethod)
        self.login_button.grid(row=2, column=4)
    
        self.quit_button = tkinter.Button(self.root, text="離開", command=self.root.destroy)
        self.quit_button.grid(row=16, column=4)
    

        self.test = Table(self.root,
                     rows=25,
                     cols=8,
                     state='disabled',
                     width=890,
                     maxwidth=1000,
                     height=1000,
                     rowheight=2,
                     colwidth=18,
                     titlerows=1,
                     titlecols=1,
                     roworigin=-1,
                     colorigin=-1,
                     selectmode='browse',
                     #bordercursor='sss',
                     #selecttype='row',
                     rowstretch='unset',
                     colstretch='last',
                     browsecmd=self.browsecmd,
                     flashmode='on',
                     variable=self.var,
                     usecommand=0,
                     command=self.test_cmd)
        #self.var["%i,%i" % (-1, -1)].bind("<Enter>",self.Display)
        self.test.grid(row=0, column=5, rowspan=30)
        self.test.tag_configure('sel', background='yellow')
        self.test.tag_configure('active', background='blue')
        self.test.tag_configure('title', anchor='w', bg='red', relief='sunken')
        self.root.mainloop()


gui = GUI()
gui.initVar()
gui.createTable()
