import random

from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import sys
import string
import sqlite3



def readwords():   #reads in all of the words 7and splits them into appropriate lists depending on length
    file=open("englishwords.txt","r")
    data=file.read().split("\n")
    short=[]
    medium=[]
    long=[]

    for i in data:
        if len(i)<5:
            short.append(i)
        elif len(i)>4 and len(i)<7:
            medium.append(i)
        elif len(i)>7:
            long.append(i)

    return data,short,medium,long #returns 4 different lists, all containing sets of words, lengths corresponding to given names


# bubble sort algorithm for sorting the scores
# orders them in descending order, for the leaderboard

def bubblesort(arr):
    for i in range(len(arr) + 1):
        for j in range(1, len(arr)):  #standard bubblesort algorithm
            if arr[j] > arr[j - 1]:
                arr[j], arr[j - 1]=arr[j - 1], arr[j]
    return arr


#this bubblesort is specially made for 2d arrays
def bubblesort2d(arr):
    for i in range(len(arr) + 1):
        for j in range(1, len(arr)):
            try:

                if arr[j][1] > arr[j - 1][1]:
                    arr[j], arr[j - 1]=arr[j - 1], arr[j]
            except IndexError:
                pass

    return arr


class Queue:         #This is the queue that we will use for the speed typing part of the game 

    regularwords, easy, medium, hard = readwords()
    lists={'regularscores':[regularwords], 'mediumscores':[easy,medium], 'hardscores':[medium,hard]}
    
    def __init__(self,difficulty):
        self.items=[]
        self.choice=self.lists[difficulty]

        for i in self.choice:
                self.items.extend(i) #appending the two lists to self.items

        random.shuffle(self.items)
        
    def isempty(self):
        if not self.items:
            return True
        else:
            return False

    def additem(self,item):
        self.items.append(item)

    def takeitem(self):

        return self.items.pop(0)

    def queuelength(self):
        return len(self.items)


    
class learntotype:
    
    def __init__(self,master,username,password):
        self.master=master
        self.master.geometry("700x700")
        self.username=username
        self.password=password

        self.makekeyboard()
        self.master.bind("<KeyPress>",self.onkeypress)
        self.master.bind("<KeyRelease>",self.onkeyrelease)

    def makekeyboard(self):
        row1=["q","w","e","r","t","y","u","i","o","p"]
        row2 = ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";"]
        row3 = ["z", "x", "c", "v", "b", "n", "m", ",", ".", "?"]
        self.rows=[]
        self.rows.append(row1)
        self.rows.append(row2)
        self.rows.append(row3)

        columnnum=0
        rownum=0

        self.labeldict={}


        for i in self.rows:
            rownum+=1
            columnnum=0
            for j in i:

                label=Label(self.master,text=j,fg="white",bg="grey",bd=3,relief="solid",font="Helvetica 10",width=8)
                label.grid(row=rownum,column=columnnum)
                self.labeldict[j]=label
                columnnum+=1


    def onkeypress(self,event):
        keypress=event.char
        self.labeldict[keypress].configure(bg="green")


    def onkeyrelease(self,event):
        keypress=event.char
        self.labeldict[keypress].configure(bg="grey")


class typinggame:  # CLASS LOADED ONCE THE USER SUCCESSFULY LOGS IN TO THE GAME

    def __init__(self, master, username):

        self.master=master
        self.keys=list(string.ascii_lowercase)
        self.regularqueue=Queue("regularscores")
        self.mediumqueue=Queue("mediumscores")
        self.hardqueue=Queue("hardscores")
        self.queues={"regularscores":self.regularqueue, "mediumscores":self.mediumqueue, "hardscores":self.hardqueue} #a dictionary of the queues, each one is referenced with the current game difficulty.
        
        
        
        self.wordcounter=0
        self.labelsgenerated=0

        self.textlabel1str=StringVar()
        self.textlabel2str=StringVar()
        self.currentwordstr=StringVar()

        self.difficulty="regularscores" #default difficulty is regular, so regular text will be generated at the start 
        self.username=username  

        self.set_window_properties() #configures background and properties of window

        self.wordsused=[] #stores the words used in a run of the game
        self.playerwords=[]  #stores all words the user inputs during a run of the game.

        self.makewidgets()  #makes all widgets on the window.






    def makewidgets(self):
        self.master.update()
        self.x,self.y=self.master.winfo_width(),self.master.winfo_height()
        self.x=self.x//2
        self.y=self.y//2

        self.maketextlabels()
        self.filllabelstart()

        self.counter=30   #timer variable set to ,  will count down
        self.stop=False  #stop Boolean is false so that the timer can run/stop at command

        self.timerlabel=Label(self.master,
                              borderwidth=10,
                              fg="white",
                              bg="black",
                              text=self.counter,
                              font="Helvetica 20",
                              bd=4,
                              relief="groove")



        self.userlabel = Label(self.master, text="Logged in as {}".format(self.username.title()),
                               font="Helvetica 17")  # displays the users name capitalized

        self.difficultyvar = StringVar()
        self.difficultyvar.set(
            self.difficulty.title())  # making the difficulty a stringvar, this way I can update the text in the label without having to access it directly.
        self.difficultylabel = Label(self.master, textvariable=self.difficultyvar)

        self.entrybox = Entry(self.master, width=10,
                              font="Helvetica 20",bg="grey",fg="black")  # entrybox where the user will input their attempt
        self.entrybox.bind("<Key>", self.starttimerandunbind)  # When the user presses any key, the timer will start
        self.entrybox.bind("<space>", self.gameloop)



        self.logoutbutton = Button(self.master, width=10, height=5, text="Log Out", bg='black', fg="white",font="Helvetica 15",
                                   command=self.logout)  # Button That allows the user to go back to the login screen

        # button that allows the user to reset the timer, they will also be given the option to generate new text
        self.resetbutton = Button(self.master, text="Reset Game", height=3, command=self.resetgame, bg='#001d26',
                                  fg="#23beeb")

        # Runs the 'leaderboard' method which makes a ttk notebook.
        # This notebook contains leaderboards and graphs for each different gamemode
        self.leaderboardbutton = Button(self.master, text="Scores", height=3, command=self.leaderboard)

        # The following buttons generate their respective text difficulties, they do this by
        # changing self.difficulty to regular/easy/medium/hard, and then running a function that will generate that certain
        # type of text

        self.regulartextbutton = Button(self.master, text="Regular Text", width=10, command=self.makeregular, height=2,
                                        bg='#001d26', fg="#23beeb")
        
        self.mediumtextbutton = Button(self.master, text="Medium Text", width=10, command=self.makemedium, height=2,
                                       bg='#001d26', fg="#23beeb")
        self.hardtextbutton = Button(self.master, text="Hard Text", width=10, command=self.makehard, height=2,
                                     bg='#001d26', fg="#23beeb")
        self.titlelabel=Label(self.master,text="Speed Type Racer",font="Helvetica 25",bg="#478cad",fg="black",bd=5,relief="groove").place(x=self.x,y=self.y-250,anchor=CENTER)

        self.entrybox.place(x=self.x,y=self.y,anchor=CENTER) #place entrybox directly in the center 

        self.timerlabel.place(x=self.x+100,y=self.y,anchor=CENTER) #place timerlabel to the right of the entrybox

        self.regulartextbutton.place(x=self.x-100,y=self.y+100,anchor=CENTER) 
        self.mediumtextbutton.place(x=self.x,y=self.y+100,anchor=CENTER)   #alligning difficulty buttons beneath the entry box.
        self.hardtextbutton.place(x=self.x+100,y=self.y+100,anchor=CENTER)
        
        self.logoutbutton.grid(row=0,column=0)  #putting log out button at top left of screen
        self.resetbutton.place(x=self.x+200,y=self.y,anchor=CENTER)  #reset button is to the left of the entry box.

        self.leaderboardbutton.place(x=self.x-150,y=self.y,anchor=CENTER)

    #This method sets the properties of the window (resolution/background)
    def set_window_properties(self):
        self.master.configure(bg="dark grey")
        self.master.protocol("WM_DELETE_WINDOW", self.closewindow)
        self.master.title("Login to game")
        x,y = 680, 680
        centrewindow(self.master,x,y)
        self.master.resizable(False,False)
        self.backgroundimage=PhotoImage(file="./Pictures/background.png")
        self.backgroundlabel=Label(self.master,image=self.backgroundimage)
        self.backgroundlabel.place(x=0,y=0,relwidth=1,relheight=1)


    def checkvalid(self,*args):
        pass

    def gameloop(self,*args):

        word=self.entrybox.get()
        if any(c.isalpha() for c in word):  #checks if there are any letters in the string
            self.wordcounter+=1             #if there are no letters, then we dont append it to the list
            self.currentwordnum+=1
            self.updatecurrentword()
            word=word.strip(" ")

            self.entrybox.delete(0,END)
            self.playerwords.append(word)
            if self.wordcounter % 5 ==0:  #once we hit the 5th word, we then change the lines 
                self.settextlabels()
        else:
            self.entrybox.delete(0,END)



        
        
    def makeregular(self):
        self.resetgame()
        if self.difficulty!='regularscores':
            self.difficulty='regularscores'
            print("Regular Queue now in use")            

        self.wordsused=[]
        self.playerwords=[]


        if self.labelsgenerated>0:
            self.filllabelstart()
                                             

    def makemedium(self):
        self.resetgame()
        if self.difficulty!="mediumscores":
            self.difficulty='mediumscores'

            print("Medium Count now in use")
        self.wordused=[]
        self.playerwords=[]

        if self.labelsgenerated>0:
            self.filllabelstart()
                


    def makehard(self):
        self.resetgame()
        if self.difficulty!="hardscores":
            self.difficulty='hardscores'
            print("Hard Queue now in use")                                    
        self.wordsused=[]
        self.playerwords=[]

        if self.labelsgenerated>0:
            self.filllabelstart()
                
    #This method checks the length of the currently used queue. If the length is <15, then we could run into some index errors, and so we reset the queue.
    def checkqueuelength(self):
        if self.queues[self.difficulty].isempty():
            self.queues[self.difficulty]=Queue(self.difficulty)




    def maketextlabels(self):   #This makes the labels at the start of the game (in the init method)
        self.textlabel1=Label(self.master,textvariable=self.textlabel1str,font="Helvetica 20",bg="#565753",fg="white",bd=4,relief="solid")
        self.textlabel2=Label(self.master,textvariable=self.textlabel2str,font="Helvetica 20",bg="#565753",fg="white",bd=4,relief="solid")
        self.currentwordlabel=Label(self.master,textvariable=self.currentwordstr,font="Helvetica 25",bg="#565753",fg="white",bd=4,relief="solid")

        self.textlabel1.place(x=self.x,y=self.y-190,anchor=CENTER)
        self.textlabel2.place(x=self.x,y=self.y-135,anchor=CENTER)
        self.currentwordlabel.place(x=self.x,y=self.y-50,anchor=CENTER)
        print("placed")

    def updatecurrentword(self):
        self.currentwordstr.set(self.wordsused[self.currentwordnum])

    def filllabelstart(self):   #This is ran each time the game resets, it fills in the labels with their base text
        self.wordcounter=0
        self.wordsused = []
        self.playerwords = []
        self.currentwordnum=0

        self.textlabel1list=[]
        self.textlabel2list=[]
        
        for i in range(5):
            self.checkqueuelength()
            
            self.textlabel1list.append(self.queues[self.difficulty].takeitem())
            self.textlabel2list.append(self.queues[self.difficulty].takeitem()) #append 5 words to each list


        self.wordsused.extend(self.textlabel1list)
        self.wordsused.extend(self.textlabel2list)  #appending the newly generated words to the words used list that will be used to calculate a score.


        self.textlabel1string=" ".join(self.textlabel1list)
        self.textlabel2string=" ".join(self.textlabel2list)  #convert them to strings
        
        self.textlabel1str.set(self.textlabel1string)
        self.textlabel2str.set(self.textlabel2string)   #set them to the stringVars() which are the textvariables in the label
        self.currentwordstr.set(self.wordsused[self.currentwordnum])

        self.labelsgenerated+=1
        
    def settextlabels(self):     #This sets the text of the label mid game, by swapping the stringvars of label1 and 2, and then generating new text for the 2nd


        self.textlabel2list=[]
        self.textlabel1str.set(self.textlabel2string) #setting the string of label 1 to the string of label 2, so we can add another line 

        for i in range(5):
            self.textlabel2list.append(self.queues[self.difficulty].takeitem())   #swapping 1 and 2, and then generating another one for 2 

        self.wordsused.extend(self.textlabel2list)
        self.textlabel2string=" ".join(self.textlabel2list)
        self.textlabel2str.set(self.textlabel2string)

        

    #generates the leaderboard for the player. This includes the button that links to the graph
    def leaderboard(self):
        difficulties=['regularscores','mediumscores','hardscores'] #list of table names, used to fetch scores from given tables
        titles=['Regular Scores','Medium Scores', 'Hard Scores']   #Titles which will be used on the leaderboards of each tab 

        tabcounter=0  #this will be added to the name of each tab 
        leaderboard=Toplevel(self.master)   #This leaderboard is dependent on the game window, if the user logs out then this will close (privacy)
        nbook=ttk.Notebook(leaderboard) #Tkinter notebook, with tabs, each leaderboard is a tab 
        for i in range(len(difficulties)):  #iterate through the different score tables 
            
            tabcounter+=1

            frame=ttk.Frame(nbook) #make a frame in the notebook, This is where the scores will go
            
            self.scores=get_score_function(difficulties[i],self.username) #get the scores for the given difficulty
            self.scores_ordered=bubblesort(self.scores)  #bubble sort them to go in descending order
            self.difficultyforgraph=difficulties[i]
            

            if i==0:                                        #i=0 is regularscores table 
                comm=self.make_regular_graph
            elif i==1:                                          #i=1 is the medium score table 
                comm=self.make_medium_graph
            else:                                           #=2 is the hard graph table 
                comm=self.make_hard_graph



            #comm is the  function for the given graph
            graphbutton=Button(frame,text='Graph',command=comm)  #Button for the graph, each tab in the notebook will have one 
            graphbutton.pack()
            
            space=Label(frame) #making a space between the graph button and the leaderboard scores 
            space.pack()

            titlelabel=Label(frame,text=titles[i])
            titlelabel.pack()


            for i in self.scores_ordered:   #iterate through the scores 
                label=Label(frame,text=i,borderwidth=1,fg="#478cad",bg="black",font="Helvetica 15")  #give each score a label and put it into the frame 
                label.pack()

    
            
            nbook.add(frame,text="Tab {}".format(tabcounter)) #add the frame to the notebook, tab name increments by 1 each time 



        nbook.pack()
            



#Graph Methods 
##########################################################################
    def make_regular_graph(self):
        self.scoresbase=get_score_function('regularscores',self.username)
        self.scores=[]
        for i in self.scoresbase:
            self.scores.append(i[0])

        self.scores=self.scores[::-1]
        
        xlist=[]
        for i in range(1,len(self.scores)+1): #making an xlist that is of same length as self.scorelist, this way we can graph it 
            xlist.append(i)

        plt.scatter(xlist,(self.scores))
        plt.title("Graph showing your scores in regular difficulty")
        plt.xlabel("Attempts")
        plt.ylabel("Numerical score (wpm)")
        plt.show()

        
    def make_medium_graph(self):
        self.scoresbase=get_score_function('mediumscores',self.username)
        self.scores=[]
        for i in self.scoresbase:
            self.scores.append(i[0])

        self.scores=self.scores[::-1]
        xlist=[]
        for i in range(1,len(self.scores)+1): #making an xlist that is of same length as self.scorelist, this way we can graph it 
            xlist.append(i)

        plt.scatter(xlist,(self.scores))
        plt.title("Graph showing your scores in medium difficulty")
        plt.xlabel("Attempts")
        plt.ylabel("Numerical score (wpm)")
        plt.show()



    def make_hard_graph(self):
        self.scoresbase=get_score_function('hardscores',self.username)
        self.scores=[]
        for i in self.scoresbase:
            self.scores.append(i[0])

        self.scores=self.scores[::-1]

        xlist=[]   
        for i in range(1,len(self.scores)+1): #making an xlist that is of same length as self.scorelist, this way we can graph it 
            xlist.append(i)

        plt.scatter(xlist,(self.scores))
        plt.title("Graph showing your scores in hard difficulty")
        plt.xlabel("Attempts")
        plt.ylabel("Numerical score (wpm)")
        plt.show()
        


#############################################################################################################################



    def resetgame(self):


        self.filllabelstart()
        self.stoptimer()  #this sets self.stop to True, thereby stopping the timer from running
        self.master.focus()  #focuses the user on the window, taking them out of the entry box 
        self.entrybox.bind("<Key>", self.changestoptofalse) #when the user hits a key, self.stop will set to False, allowing the timer to start again.
        self.resettimer() #Runs a method that will reset the timer and clear the entrybox



    # if the user presses yes, then the game window will close, and an instance of the login window will open
    def logout(self):
        if messagebox.askokcancel("Quit", "Do you want to log out? "):
            self.master.destroy()
            loginwindow=Tk()
            loop=Login(loginwindow)
            loginwindow.mainloop()

    # starts the timer and unbinds button-1, this way they can't spam the function as this would mess up the timing
    def starttimerandunbind(self, *args):

        self.entrybox.unbind("<Key>")   #unbinds <key> from starting the timer. If we did not include this, then each keypress would cause another instance of the timer to start, messing up our timer completely
        self.starttimer()  # calls the starttimer function from within here

    # starts the games timer
    def starttimer(self, *args):
        if self.stop == False and  self.counter>0:  #if the timer is not set to stop, and the counter is >0, then the timer will decrement by one 
            self.counter-=1
            self.timerlabel.configure(text=self.counter)
            self.master.after(1000, self.starttimer)
        

        elif self.stop==True and self.counter>0:  #self.stop is True when the user hits the resettimer button, this way the timer will stop when we hit it.
                                                    #we need this as we dont just call calcscore() when self.stop==True, we call it when the counter  is =0.
            pass                                    #without this, the calcscore() method would call when we hit the resetbutton     
        
        else:
            self.calculatescore()  #if self.stop==True 

        # stops the timer by setting the boolean "stop" to=True

    def stoptimer(self, *args):
        self.stop=True

    # Clears the entry box, so the user can't cheat. also sets the timer to 0, and updates the label accordingly
    def resettimer(self):
        self.entrybox.delete(0, END)
        self.counter=30
        self.timerlabel.configure(text=(self.counter))

    # changes the state of stop variable so that the timer can start again when the user clicks the entry box
    def changestoptofalse(self, *args):
        self.stop=False
        self.entrybox.unbind("<Key>")
        self.starttimer()


###################################################################################################################
        #SAVING SCORES INTO THE SCORE TABLES 


    #save a score in the regularscores table 
    def save_regular_score(self):

        #inserting the name, score, and guess of the user on this score into the table
        c.execute("INSERT INTO regularscores VALUES(:username,:scores,:words)",{'username':self.username, 'scores':self.wpm, 'words':self.guess})
        conn.commit()




    #save a score in the medium scores table
    def save_medium_score(self):

        #inserting the name, score, and guess of the user on this score into the table
        c.execute("INSERT INTO mediumscores VALUES(:username,:scores,:words)",{'username':self.username, 'scores':self.wpm, 'words':self.guess})
        conn.commit()



    #save a score in the hardscores table 
    def save_hard_score(self):

        #inserting the name, score, and guess of the user on this score into the table
        c.execute("INSERT INTO hardscores VALUES(:username,:scores,:words)",{'username':self.username, 'scores':self.wpm, 'words':self.guess})
        conn.commit()




    #self.difficulty matches one of the keys in the dictionary. The corresponding method is ran, and the score is saved in the correct table
    def save_score_function(self,difficulty):
        save_funcs={'regularscores':self.save_regular_score, 'mediumscores':self.save_medium_score, 'hardscores':self.save_hard_score}
        if messagebox.askyesno("Save score", "Would you like to save your score?"):
            save_funcs[difficulty]()
        



#################################################################################################################

    # ran after the user hits enter on the entry box to calculate their score and WPM
    def calculatescore(self, *args):

        self.stoptimer()  # stops the timer from running
        self.master.focus()  # takes focus off of the entrybox
        self.score=0  #set score to 0 
        self.entrybox.bind("<Key>",
                           self.changestoptofalse)  # binds button 1 to a method that will allow the timer to start again
        

            
        self.maxscore=len(self.playerwords)  # setting the maximum attainable score to the length of the phrase (words)
            
        self.guess=self.playerwords


        print("Your guess",self.guess)
        print("The computer words",self.wordsused)





        #if len(self.guess)>len(self.wordsused):
            #for i in range(len(self.guess)-len(self.wordsused)):
               # self.wordsused.append(" ")

                    
        for i in range(len(self.guess)):
            if self.wordsused[i] == self.guess[i]:
                self.score+=1  # if the words in the positions are equal score+=1
            else:
                pass
                    #print("You got", self.wordsused[i], "wrong")  # tells the user via the console what they got wrong

        self.wpm=(self.score / 30) * 60  # calculate the users WPM (words per minute)
        self.wpm=round(self.wpm, 4)  # round the wpm to 2dp as there is no need for any more

        scorelabel=Label(self.master, text="You got {} words correct at {} WPM".format(self.score, self.wpm), fg="black",
                            bg="light blue", font="Helvetica 15")
        scorelabel.place(x=self.x, y=self.y-300,anchor=CENTER)
        self.master.after(3000, lambda: scorelabel.destroy())  # after 3 seconds, get rid of the pop-up label
            
        self.guess=" ".join(self.guess) # converting it back to a string so that it can be stored in the database 

        self.wordsused=[]
        self.playerwords=[]
        self.resettimer()  # reset the timer
        self.save_score_function(self.difficulty)  # ask the user if they want to save the score

     #if self.resettimervar is True, then the main part of the method ^^^^^ does not need to run, but we still need to reset the label and the word counter in order for the program to
        #work properly. We also reset the timervar to False so that the main part of the method can run, should the user try to save a score.
        self.filllabelstart()
        self.wordcounter=0



    def closewindow(self):
        if messagebox.askyesno("Quit game", "Do you want to quit the game entirely"):
            self.master.destroy()  # destroy the game window if the user clicks the X






#NOT BEING USED RIGHT NOW
class player:

    def __init__(self, username,name, password):
        self.username=username
        self.name=name
        self.password=password
        self.regularscores=[0]
        self.easyscores=[0]
        self.mediumscores=[0]
        self.hardscores=[0]
        self.scores=[0]  # append a 0 to the score so that we can iterate without errors






# TKINTER WINDOW THE THE LOGIN MENU
class Login:
    def __init__(self, master):  # TK window, pass in the root instance

        self.mask=True  #Boolean Mask, for hiding/showing the password
        
        self.master=master
        
        self.set_window_properties()        #sets the properties, such as the resolution, resizability etc
        
        self.makewidgets()            #Makes all the widgets on the screen


    def makewidgets(self):
        self.username=Entry(self.master, width=20, font="Helvetica 15", bg="black", fg="white")  # username entry box
        self.username.insert(0,"Username")
        self.username.bind("<Return>", self.focuspassword)
        self.username.bind("<FocusIn>", self.clearusername)  # bindings to the entry box
        self.username.bind("<Down>", self.downtopassword)



        self.password=Entry(self.master, width=20, show="*", font="Helvetica 15", bg="black", fg="white")  # pw enty box

        self.password.insert(0,"Password")

        self.password.bind("<Up>", self.uptousername)
        self.password.bind("<Return>", self.attemptlogin)
        self.password.bind("<FocusIn>",self.clearpassword)

        
        self.master.update()
        x,y=self.master.winfo_width(),self.master.winfo_height()
        print(x,y)

        x=x//2
        y=y//2


        self.welcomelabel=Label(self.master, text="Login Menu",
                                font="Helvetica 18",
                                fg="white",
                                bg="#565753",
                                bd=4,

                                relief="solid")



        self.loginbutton=Button(self.master, text="Log In", font="Helvetica 15", width=10, command=self.attemptlogin,fg="white",bg="#565753",bd=10,relief="groove")
        
        self.maskbutton=Button(self.master, text="Show Password", font="Helvetica 15", command=self.maskpassword,fg="white",bg="#565753",bd=10,relief="groove")
        
        self.makenewuserbutton=Button(self.master, text="Make New User", font="Helvetica 15", command=self.makenewuser,fg="white",bg="#565753",bd=10,relief="groove")
        
        self.printusers=Button(self.master,text="Print users",font="Helvetica 15", command=printallplayers,fg="white",bg="#565753",bd=10,relief="groove")



        
        self.username.place(x=x,y=y-50,anchor=CENTER)

        self.password.place(x=x,y=y,anchor=CENTER)

        self.welcomelabel.place(x=x,y=y-100,anchor=CENTER)

        self.loginbutton.place(x=x,y=y+50,anchor=CENTER)

        self.maskbutton.place(x=x+225,y=y,anchor=CENTER)

        self.makenewuserbutton.place(x=x,y=y+125,anchor=CENTER)

        self.printusers.place(x=x+225,y=y+75,anchor=CENTER)


        self.leaderboard1()

    def refreshplayernames(self):
        playernames=[]
        c.execute("SELECT username FROM players")
        x=c.fetchall()
        for i in x:
            playernames.append([i[0]])
        return playernames

    def leaderboard1(self):
        noteStyler=ttk.Style()
        noteStyler.configure("TNotebook",background="black",borderwidth=0)
        noteStyler.configure("TFrame",background="black")

        difficulty=["regularscores","mediumscores","hardscores"]
        title=["Regular","Medium","Hard"]
        notebook=ttk.Notebook(self.master,style="TNotebook")


        for i in range(len(difficulty)):
            playernames=self.refreshplayernames()


            for j in range(len(playernames)):

                scores=get_score_function(difficulty[i],playernames[j][0])

                if len(scores)>1:
                    scores=bubblesort(scores)
                    playernames[j].extend(scores[0])
                elif len(scores)==1:
                    playernames[j].extend(scores[0])

            playernames=bubblesort2d(playernames)
            frame=ttk.Frame(notebook,width=5,style="TFrame")
            labelcounter=0

            Label(frame,text=title[i],font="Helvetica 20",fg="black",bg="grey",width=10).pack()
            for x in range(len(playernames)):
                if len(playernames[x])>1:
                    labelcounter+=1
                    Label(frame,text=playernames[x][0].title() + " With a score of "+playernames[x][1]+ " WPM",font="Helvetica 12",fg="black",bg="grey",bd=3,relief="groove").pack()
            if labelcounter==0:
                Label(frame,text="No scores",font="Helvetica 12",fg="black",bg="grey",bd=3,relief="groove",width=20).pack()

            labelcounter=0
            notebook.add(frame,text=title[i])
        notebook.grid(row=0,column=0)
        print(notebook.grid_slaves(row=0,column=0))





    def leaderboard(self):
        self.namelist=[]
        c.execute("SELECT username FROM players")
        self.names=c.fetchall()
        for i in self.names:
            self.namelist.append([i[0]])


        for i in range(len(self.namelist)):
            name=self.namelist[i][0]
            c.execute("SELECT score FROM regularscores WHERE username=:name",{'name':name})
            self.scores=c.fetchall()
            print(self.scores)

            #This takes the score list, bubblesorts it, and puts the highest value into the 2d array with the respective name.
            self.namelist[i].extend(bubblesort(self.scores)[0])



        self.namelist=bubblesort2d(self.namelist) #Bubblesorting the list of names according to their scores

        print(self.namelist)

        self.leaderboardframe=Frame(self.master,width=10)

        self.titlelabel=Label(self.leaderboardframe,text="Leaderboard",bg="black",fg="white")
        self.titlelabel.pack()

        self.canvas=Canvas(self.master,width=50,background="grey",height=10)
        self.frame=Frame(self.canvas,background="black")


        self.canvas.grid(row=0,column=0)
        self.frame.pack()

        titlelabel=Label(self.frame,text="Leaderboard",bg="grey",fg="black",font="Helvetica 25",bd=3,relief="groove")
        titlelabel.pack()
        Label(self.frame,bg="black").pack()

        for i in range(len(self.namelist)):
            x=self.namelist[i][0].title() + " With Score Of " +self.namelist[i][1]+ " WPM"
            Label(self.frame,text=x,bg="grey",fg="black",font="Helvetica 10",bd=3,relief="groove").pack()


        
    def set_window_properties(self):
        self.master.configure(bg="dark grey")
        self.master.title("Login to game")
        x, y= 680, 680
        centrewindow(self.master,x,y) #this will centre the window, function is outside of the classes.
        self.master.resizable(False,False)
        self.backgroundimage=PhotoImage(file="./Pictures/background.png")
        self.backgroundlabel=Label(self.master,image=self.backgroundimage)
        self.backgroundlabel.place(rely=0.5,relx=0.5,anchor=CENTER)




    #used to mask the password that the user enters.
    def maskpassword(self, *args):
        if self.mask == False:
            self.password.configure(show="*")
            self.maskbutton.configure(text="Show Password")
            self.mask=True

        elif self.mask == True:
            self.password.configure(show="")
            self.maskbutton.configure(text="Mask Password")
            self.mask=False

    def uptousername(self, *args):
        self.username.focus()

    def downtopassword(self, *args):
        self.password.focus()

    def clearusername(self, *args):
        self.username.delete(0, END)

    def clearpassword(self,*args):
        self.password.delete(0,END)

    def focuspassword(self, *args):
        self.password.focus()

    def attemptlogin(self,*args):
        #Begin by appending the username and password to a list, can then be used to compare to the details we select from the database
        self.play=False
        pusername=self.username.get()
        ppassword=self.password.get()
        x=selectplayer(pusername,ppassword)  #here we select any records that have the username and password entered



        if x!=[]:  #selectplayer() will return [] only if there are no records. If it does not return [] then we have records that do match, and so the user can login
            self.play==True
            print("You can play")
            self.master.destroy()
            root2=Tk()
            game=typinggame(root2,pusername)


        else:
            self.play==False
            print("Go away hacker")



        #fetches the username and password that have been entered, and creates an account
    def makenewuser(self):
        pusername=self.username.get()
        ppassword=self.password.get()
        #if the user tries to make a user with no inputs, then it doesn't make a user.
        if pusername !="" or ppassword != "":
            c.execute("SELECT username FROM players WHERE username=:username",{'username':pusername}) #select any usernames that match the one entered by the user
            x=c.fetchall()
            if x==[]:
                insertplayer(pusername,ppassword)
            else:
                print("User exists")



    #gets rid of the go away label after a second
    def unpackgoawaylabel(self):
        self.master.after(1000, self.goawaylabel.destroy())






def insertplayer(pusername,ppassword):   #will insert a new record into the player table with the given detail parameters
    c.execute("INSERT INTO players VALUES(:pusername,:ppassword)",{'pusername':pusername, 'ppassword':ppassword})
    conn.commit()


#selects the username and password of a player,used to attempt logins
def selectplayer(pusername,ppassword):
    c.execute("SELECT username,password FROM players WHERE username=:username AND password=:password",{'username': pusername, 'password': ppassword})
    player=c.fetchall()
    conn.commit()
    return player

#This method prints out all of the players in the "players" table, this is for testing purposes only
def printallplayers():
    c.execute("SELECT * FROM players")
    x=c.fetchall()
    for i in x:
        print(i)

##################################################################################################################
# SELECTING SCORES FROM THE TABLES FOR THE LEADERBOARDS/GRAPHS

def get_regular_scores(username):
    # selecting all scores from the given table, with the players username

    c.execute("SELECT score FROM regularscores WHERE username=:pusername", {'pusername': str(username)})
    scores=c.fetchall()

    return scores

def get_medium_scores(username):
    # selecting all scores from the given table, with the players username

    c.execute("SELECT score FROM mediumscores WHERE username=:pusername", {'pusername': username})
    scores=c.fetchall()

    return scores

def get_hard_scores(username):
    # selecting all scores from the given table, with the players username

    c.execute("SELECT score FROM hardscores WHERE username=:pusername", {'pusername': username})
    scores=c.fetchall()

    return scores

    # This method contains a dictionary with the different score grabbing functions
    # each function has a key, this key matches the difficulty the user is on.
    # Using our key, we select the correct method and run it
    # we then save the scores in the variable 'scores' and return it

def get_score_function(difficulty,username):
    funcs={'regularscores': get_regular_scores, 'mediumscores': get_medium_scores,
            'hardscores': get_hard_scores}
    scores=funcs[difficulty](username)

    return scores


def maketables():
    c.execute("""CREATE TABLE IF NOT EXISTS players(
                username text PRIMARY KEY NOT NULL,
                password text NOT NULL)""")

    c.execute("""CREATE TABLE IF NOT EXISTS regularscores(
                username text NOT NULL,
                score text NOT NULL,
                words text NOT NULL,
                FOREIGN KEY (username) REFERENCES players(username))""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS mediumscores(
                username text NOT NULL,
                score text NOT NULL,
                words text NOT NULL,
                FOREIGN KEY (username) REFERENCES players(username))""")

    c.execute("""CREATE TABLE IF NOT EXISTS hardscores(
                username text NOT NULL,
                score text NOT NULL,
                words text NOT NULL,
                FOREIGN KEY (username) REFERENCES players(username))""")
    
    conn.commit()
    

#This function will centre the window on the users screen, regardless of their resolution (as long as their res is bigger than that of the window)
def centrewindow(root,windowx,windowy):
    screenx,screeny=root.winfo_screenwidth(),root.winfo_screenheight()
    xplacement,yplacement=((screenx//2)-windowx//2),((screeny//2)-windowy//2)
    root.geometry("%dx%d+%d+%d" %(windowx,windowy,xplacement,yplacement))


if __name__ == '__main__':
    conn=sqlite3.connect("Gamedatabase.db")
    conn.execute("PRAGMA foreign_keys=1")
    c=conn.cursor()
    maketables() #this attempts to create the tables, if they already exist then it will not make them...


    root=Tk()
    loginmenu=Login(root)
    root.mainloop()


