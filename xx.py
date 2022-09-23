import time
import pyautogui as gui
import keyboard
import pyperclip
from PIL import Image
from PIL.PngImagePlugin import PngInfo

def test_param(step, name, default):
    #Automatically add parameter to the step
    try:
        test = step.params[name]
    except Exception as e:
        print("    No param: "+name+" found intializing with value: "+str(default))
        step.params[name]=default

def find_in_window(imgsrc,bbox=None,tries=30,wait=1,scroll=0):
    # return the co-ordinates of the found image or None
    # ToDo: bbox
    
    for loop in range(tries):
        #if imgsrc is list all items in list will be tested
        if type(imgsrc)==list:
            for image in imgsrc:
                print("trying to locate img: "+str(image)+" try "+str(loop))
        else:
            print("trying to locate img: "+str(imgsrc)+" try "+str(loop))
        #enable scrolling while looking for specific image    
        if not(scroll==0):
            gui.scroll(scroll*-1)
        try:
            out = gui.locateOnScreen(imgsrc, confidence=0.8)
            if out!=None:
                return out
        #pics/0_3_addressBar.png
        except Exception as e:
            print(e)
        
        time.sleep(wait)
    # if function times out no location is found    
    return None

class step:
    """
    # setup
    # per record
    # cleanup
    """
    def __init__(self, img=None, scrollable=False, pre = None, script= None, timeout=90):
        #ToDo: init with load file
        self._img = img
        self._scroll = scrollable
        # test if image path is valid, if not raise ValueError and do not construct an object
        self._pre_script = pre
        self.found_loc = None #1st image found location
        if script==None:
            # Default script parameter if step instance is just created
            self._script = 'loc=[[0,0]]\r\nif self.found_loc==None:\r\n    print("  Image Not Found")\r\nelse:\r\n    print("  Image Found @: "+str(self.found_loc))'
        else:
            self._script = script
        self._flags = [False,False,False,False] #mark,show,mark,quit
        self.timeout = timeout
        self.markers = []
        self.params = {} # Default parameters defined in PNG
            
    def _reset_mark(self):
        self._flags[0] = True
        
    def _reset_show(self):
        self._flags[1] = True
        
    def _reset_marker(self):
        self._flags[2] = True
        
    def _reset_quit(self):
        self._flags[3] = True
    
    def capture(self):
        print("Capture images and (input) positions for step construction")
        print("[alt]  - mark image corner (top left to right bottom)")
        # ToDo: add recapture image option
        print("[w]    - show captured image")
        print("[m]    - add click or input marker, print variable as string")
        # ToDo: update marker with multiselect
        print("[q]    - stop capture")
        
        hkey_0 = keyboard.add_hotkey('alt', self._reset_mark)
        hkey_1 = keyboard.add_hotkey('w', self._reset_show)
        hkey_2 = keyboard.add_hotkey('m', self._reset_marker)
        hkey_3 = keyboard.add_hotkey('q', self._reset_quit)
        
        prev = [0,0]
        top_right_corner = [0,0]
        
        while True:
            pos = gui.position()
            # if [alt] is pressed / mark corner
            if self._flags[0]==True:
                self._flags[0]=False
                print(" -> pos: "+str(pos.x)+","+str(pos.y))
                #get_color(pos.x,pos.y)
                self._img = gui.screenshot(region=(prev[0],prev[1],pos.x-prev[0],pos.y-prev[1]))
                top_right_corner = prev
                prev=[pos.x,pos.y]
            
            # if [w] is pressed / view image  
            if self._flags[1]==True:
                self._flags[1]=False
                self._img.show()
            
            # if [m] is pressed / add marker 
            if self._flags[2]==True:
                self._flags[2]=False
                self.markers.append(gui.Point(pos.x-top_right_corner[0],pos.y-top_right_corner[1]))
                markers_str = "loc=["
                for marker in self.markers:
                    markers_str=markers_str+"["+str(marker.x)+","+str(marker.y)+"],"
                    
                self.markers_str = markers_str[:-1]+"]"
                # update the script markers
                cutpoint = self._script.find('\r')
                self._script = self.markers_str+self._script[cutpoint:]
                print(self.markers_str)
                           
            # if [q] is pressed / end capture   
            if self._flags[3]==True:
                self._flags[3]=False
                keyboard.remove_all_hotkeys()
                return
            
            # Be gentele to your CPU ;)
            time.sleep(0.1)
    
    def run(self):
        # run pre script
        if not(self._pre_script == None):
            exec(self._pre_script)
        # find image
        self.found_loc = None
        self.found_loc=find_in_window(self._img, tries=self.timeout, scroll=self._scroll)
        # run main script
        if not(self._script == None):
            exec(self._script)
    
    def copy(self):
        out = self.step2string()
        pyperclip.copy(out)
        print("    Scripts copied")
        
    def step2string(self):
        # if pre script is used
        if self._pre_script==None:
            pre = ""
        else:
            pre = self._pre_script
            
        out = "#pre script\r\n"+pre+"\r\n#script\r\n"+self._script
        return(out)
    
    def string2step(self,inp):
        # split string into pre and normal script (pre script 1st with starting line [#pre script] and script later staring with [#script] line )
        pre = inp[inp.find('\n'):inp.find('#script')].strip()
        # if pre script is empty
        if pre=='':
            pre=None
            
        scr = inp[inp.find('#script')+9:].strip()
        
        return(pre,scr)
        
    def paste(self):
        in_string = pyperclip.paste()
        pre,src=self.string2step(in_string)
        if pre==None:
            print("No pre script....")
        else:
            print("Pre script:\n\r"+pre)
        print(src)
        question = multiselect([['Keep',0],['Cancel',1]], header='Update scripts?',footer="--")
        selection = question.get()
        if selection[1]==0:
            self._pre_script = pre
            self._script = src
            print("    Scripts updated")
        else:
            print("    Scripts NOT updated")
    
    def savePNG(self,file_name):
        if self._img == None:
            print("    Capture image 1st before exporting, nothing to export yet...")
            return
        
        metadata = PngInfo()
        metadata.add_text("EMPpayload", self.step2string())
        
        # if file name does not have an extension
        if not(file_name[-4:]=='.png'):
            file_name=file_name+'.png'
            
        self._img.save(file_name, pnginfo=metadata)
    
    def loadPNG(self,file_name):
        target_image = Image.open(file_name)
        payload = target_image.text["EMPpayload"]
        print(payload)
        pre,scr = self.string2step(payload)
        self._pre_script = pre
        self._script = scr
        self._img = target_image
        print("Image sucessfully loaded")
    
    def showimg(self):
        self._img.show()

class workflow:
    # ToDo: Pickup Function
    # ToDo: Save/Load - every step params should be saved
    # ToDo: TmpFolder - when script is ran, temp folder is generated and once finished if empty deleted
    # ToDo: Local Stored Parameters???
    def __init__(self):
        self.steps = []
        self._current_step = 0
    
    def load_folder(self, path2folder):
        pass
    
    def run(self):
        steps_total = len(self._steps)
        for index in range(steps_total):
            try:
                self.steps[index].run()
                self._current_step = index
            except Exception as e:
                print(e)
    #workflow->step


class multiselect:  
    def __init__(self, items, header=None, footer=None, q='', default_answ=None, width=72):
        if type(items)!=list:
            items = []
        self.items = items
        self.header = header
        self.footer = footer
        self.q = q
        self.default_answ = default_answ
        self.width = width
    
    def _shortcutlist(self):
        """
        Create a list of shortcuts to check item in list
        """
        out_list=[]
        item_nr = 0
        for item in self.items:
            try:
                out_list.append(item[1])
            except Exception as e:
                out_list.append(item_nr)
            item_nr = item_nr+1
            
        return out_list
                
    
    def get(self):
        count = 0
        
        # draw header
        if not(self.header==None):
            label_len=len(self.header)+2
            spacer='-'*int((self.width-label_len)/2)
            print(spacer+" "+self.header+" "+spacer)
        
        for item in self.items:
            try:
                print(str(count)+" ["+str(item[1])+"] "+str(item[0]))
            except Exception as e:
                print(str(count)+" ["+str(count)+"] "+str(item[0]))
            count = count+1
        
        # draw footer
        if not(self.footer==None):
            footer_len=len(self.footer)+2
            spacer='-'*int((self.width-footer_len)/2)
            print(spacer+" "+self.footer+" "+spacer)
            
        # draw answer promt
        default_answ_str = None
        if self.default_answ==None:
            default_answ=len(self.items)-1
        else:
            default_answ=self.default_answ
            
        for item in self.items:
            if str(item[1])==str(default_answ):
                default_answ = item[1]
                default_answ_str = item[0]
                break
        
        ret_val = input(self.q+str(default_answ)+"("+str(default_answ_str)+"): ")
        
        if ret_val=='':
            return default_answ_str, default_answ
        
        else:
            ret_val = ret_val[0]
            
            # try to convert input into int
            try:
                ret_val = int(ret_val)
            except Exception as e:
                pass
                #print(e)
                #print("keeping answer as string")
                
            if ret_val in self._shortcutlist():
                answer = []
                for item in self.items:
                    if str(item[1])==str(ret_val):
                        answer = item
                        break

                return answer[0], answer[1]
            else:
                return None, None

test = step()
w = workflow()