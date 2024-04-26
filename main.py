from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window 
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
from kivymd.uix.textfield import MDTextFieldHelperText
from kivymd.uix.label import MDLabel
import re,os, time
from kivy.properties import StringProperty, NumericProperty, Property
from kivymd.uix.screen import MDScreen  

try:
    import vm_aarch64_linux_android as vm
except:
    try:
        import vm_arm_linux_androideabi as vm
    except:
        try:
            import vm_x86_64_linux_android as vm
        except:
            try:
                import vm_linux_x86_64 as vm
            except:
                print('Nothing loaded')

import sqlite3

class MainScreen(MDScreen):
	pass

class LoggedinScreen(MDScreen):
	pass

def tryquery(self,query1,query2):
    cur = self.cur
    try:
        v = cur.execute(query1).fetchall()
    except Exception as e:
        cur.execute(query2)

def execqueryifnotexist(self,query1,query2):
    cur = self.cur
    try:
        v = cur.execute(query1).fetchall()
        if len(v) == 0:
            cur.execute(query2)
            self.con.commit()
    except Exception as e:
        v = 1

def execquery(self,query1):
    cur = self.cur
    try:
        cur.execute(query1)
        if len(v) == 0:
            cur.execute(query2)
            self.con.commit()
    except Exception as e:
        v = 1

def checkqueryifexist(self,query1):
    cur = self.cur
    try:
        v = cur.execute(query1).fetchall()
        if len(v) == 0:
            return [0]
        else:
            return [1,v[0]]
    except Exception as e:
        return [0]
        
class attendanceApp(MDApp):
    def loadkv(self):
        Builder.load_file('loggedin.kv')
    
    def build(self):
        # Window.size = [300, 500]
        self.theme_cls.primary_palette = "Turquoise"
        self.ids = self.root.get_screen("prelogin").ids
        
        con = sqlite3.connect("techris-vin.db")
        cur = con.cursor()
        self.cur = cur
        self.con = con
        tryquery(self,"SELECT * from users","CREATE TABLE users(email text)")
        tryquery(self,"SELECT * from settings","CREATE TABLE settings(key text, value)")
        execqueryifnotexist(self,'SELECT * FROM SETTINGS WHERE key = "curemail"', 'INSERT INTO SETTINGS (key,value) VALUES ("curemail","")')
        execqueryifnotexist(self,'SELECT * FROM SETTINGS WHERE key = "curotp"', 'INSERT INTO SETTINGS (key,value) VALUES ("curotp","")')
        return
    
    def on_start(self):
        super().on_start()
        result = checkqueryifexist(self,'SELECT * FROM SETTINGS WHERE key = "curemail"')
        if len(result) > 1:
            if not result[1][1] == '':
                self.root.current = 'loggedin'

    def updatetimertext(self,dt):
        self.ids.resendcounter.text = "You can resend the OTP in " + str(self.seconds) + " seconds"
        self.seconds -= 1
        if self.seconds < 0:
            self.otpcountdown.cancel()
            self.ids.resendcounter.text = ""
            if vm.check(self):
                self.ids.resendotpbutton.pos_hint  = {"center_x": .7, "center_y": 0.12}
                self.ids.validatebutton.pos_hint  = {"center_x": .25, "center_y": 0.12}
            
    def resettext(self,dt):
        self.ids.v2.text = ''

    def getotp(self):
        email = self.ids.otpemail.text
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        
        suppress_check = 0
        
        if(re.fullmatch(regex, email)) or suppress_check:
            v = 1    
            if vm.check(self):
                self.ids.v2.text = 'Sending OTP'
                self.ids.v2.text_color = 'white'
                self.ids.otpbutton.disabled = True
                Clock.schedule_once(self.sendmail,1)
        else:
                name = StringProperty()
                name = 'vinayagar'
                self.ids.v2.text = 'Enter valid E-mail'
                
                try :
                    Clock.schedule_once(self.resettext,2)
                except Exception as e:
                    v = 1

    def sendmail(self,dt):    
        self.ids.otpbutton.text = 'Sending OTP'
        
        result = vm.sm(self)
        self.ids.otpbutton.disabled = False

        if result[0] == 0:
            self.ids.v2.text_color = 'red'
            self.ids.v2.text = 'Error in sending OTP. Try later'
            try :
                Clock.schedule_once(self.resettext,2)
            except Exception as e:
                v = 1
        else:
            if len(result) == 2:
                self.cur.execute('UPDATE settings SET value = "' + str(result[1]) + '" WHERE key = "curotp"')
                self.con.commit()
            
            self.ids.otpbutton.pos_hint  = {"center_x": .5, "center_y": -0.32}
            self.ids.validatebutton.pos_hint  = {"center_x": .5, "center_y": 0.12}
            self.ids.otpreceived.pos_hint = {"center_x": .5, "center_y": .25} 
            self.ids.v2.text_color = 'red'
            self.ids.v2.text = ''
            if vm.check(self):
                self.ids.resendcounter.text = "You can resend the OTP in 60 seconds"
                self.seconds = 60
                self.otpcountdown = Clock.schedule_interval(self.updatetimertext, 1)

    def resettoemail(self):
        self.ids.v2.text = ''
        self.ids.otpbutton.pos_hint  = {"center_x": .5, "center_y": 0.25}
        self.ids.validatebutton.pos_hint  = {"center_x": .5, "center_y": -0.28}
        self.ids.otpreceived.pos_hint = {"center_x": .5, "center_y": -.25} 
        self.ids.resendcounter.text = ""
        self.ids.resendotpbutton.pos_hint  = {"center_x": .7, "center_y": -0.28}
        self.getotp()
    
    def logout(self):
        vm.lo(self)
        


    def validateotp(self):
        otp = self.ids.otpreceived.text
        otpdb = checkqueryifexist(self,'SELECT * FROM SETTINGS WHERE key = "curotp"')[1][1]
             
        if otp == str(otpdb):
            try :
                self.otpcountdown.cancel()
            except :
                v = 1
            self.cur.execute('UPDATE settings SET value = "' + self.ids.otpemail.text  + '" WHERE key = "curemail"')
            self.con.commit()
            self.root.current = 'loggedin'
        else:
            self.ids.otpreceived.text = 'Wrong OTP'
            
app = attendanceApp()
app.run()