import socket, json, time
from threading import Thread
from clon import clon

class ball(clon):
    def __init__(self, x, y, mx, my):
        self.x = x
        self.y = y
        self.mx = mx
        self.my = my
        self.l_pos = 5
        self.r_pos = 5

class bot(object):
    def __init__(self, name, speed):
        self.name = name
        self.speed = speed#botun hareket hizi(ne kadar yuksek ise zorluk o kadar yuksek)

class player(object):
    def __init__(self, name, c, upkey, downkey):
        self.name = name
        self.c = c
        self.upkey = upkey#yukari gitmek icin basilacak tus
        self.downkey = downkey#asagi ''  " "
        
    def controller_stream(self):
        control_input = self.c.recv(1024).decode("utf-8")
        if not control_input:
            return 0
                
        control_input = json.loads(control_input)
        key = control_input["data"]
            
        if key == self.upkey:
            return "up_pressed"
            
        if key == self.downkey:
            return "down_pressed"
                
sizex = 30
sizey = 20
cursorsize = 3
fps = 60 # frame per second
tps = 20 # tick per second
x = 10
y = 10
mx = 1
my = 1
            
class game():
    def __init__(self, ball):
        self.scr = curses.initscr()
        self.ball = ball
        self.r_loop = 0
        self.l_loop = 0
        
    def r_wait(self):
        while not self.r_loop >=1:
            pass
        self.r_loop -= 1
        
    def l_wait(self):
        while not self.l_loop >=1:
            pass
        self.l_loop -= 1
        
    def l(self, value):
        self.ball.l_pos = value
        self.l_loop += 1
        
    def r(self, value):
        self.ball.r_pos = value
        self.r_loop += 1
        
        
    def draw_left(self):
        win = curses.newwin(sizey, 3, 1, 1)
        while 1:
            win.clear()
            for i in range(cursorsize):
                i -= 1
                win.addstr(i + self.ball.l_pos, 1, "I")
                
            win.refresh()
            self.l_wait()
                            
                        
    def draw_right(self):
        win = curses.newwin(sizey, 3, 1, 3+sizex)
        while 1:
            win.clear()
            for i in range(cursorsize):
                i -= 1
                win.addstr(i+self.ball.r_pos, 1, "I")
                
            win.refresh()
            self.r_wait()
        
    def draw_center(self):
        win = curses.newwin(sizey, sizex, 1, 3)
        while 1:
            win.clear()
            win.border(0)
            win.addstr(self.ball.y, self.ball.x, "X")
            time.sleep(1/fps)
    
    def game_logic(self):
        while 1:
            value = self.collision_detection()
            if not value:#carpisma yok oldugu gibi devam et
                self.ball.x += self.ball.mx
                self.ball.y -= self.ball.my
                
            else:
                if value[0] == "both":
                    pass
                    
                if value[0] == "pcollision":
                    pcollision = value[1]
                    if pcollision[0] == "right":
                        self.ball.x = 1
                        self.ball.mx = 1
                        self.ball.my = pcollision[1]
                        
                    if pcollision[0] == "left":
                        self.ball.x = sizex - 1
                        self.ball.mx = -1
                        self.ball.my = pcollision[1]
                        
                if value[0] == "ecollusion":
                    if ecollusion == "top":
                        self.ball.y = 1
                        self.ball.my *= -1
                        
                    if ecollision == "bot":
                        self.ball.y = sizey-1
                        self.ball.my *= -1
                        
            time.sleep(1/tps)
            
    def collision_detection(self):#collision detectionda yontem olarak aposteriori yontemi yani simulasyonu bi adim ileri alma yontemi kullanicagiz
        #uc cesit carpisma olabilir
        #1) topun herhangi bir koseye carpmasi: top herhangi bir kenara carparsa yalnizca y eksenindeki momentum degerlerinin carpmaya gore tersi alinir, y momentumunun buyuklugu degismez
        #2) topun herhangi bir oyuncuya carpmasi: top herhangi bir oyuncuya carparsa x eksenindeki momentumunun hem buyullugu hem de yonu degisir
        #3) topun hem bir oyuncu hem de bir kenara ayni anda carpmasi(kose olusumu): top eger ikis8ne birden ayni anda carparsa(ayni tick icersinde) carptigi koseye gore carpma acisinin tam tersine dogru, momentum buyuklugu degismeden firlar
        xaposteriori = self.ball.x + self.ball.mx
        yaposteriori = self.ball.y + self.ball.my
        pcollision = False # player collision(oyuncu)
        ecollision = False # edge collision (kenar)
        #eger ecollision bir string, pcollision bir tuple olarak donerse top koseye carpmis mi diye kontrol edilir
        #eger iki deger de False donerse top, bu tick icerisinde herhangi bir carpmaya ugramamis, aynen devam ediyor demektir
       
       #ilk once top, kenara carpmis mi diye kontrol ediyoruz 
        if yaposteriori <= 1:
            ecollision = "top"#ust kenara carpmis
            
        if yaposteriori >= sizey - 1:
            ecollision = "bot"#alt kenara carpmis
            
        #daha sonra herhangi bir oyuncuya carpmis mi, carptiysa hangi bolumune carpmis doye kontrol ediyoruz
        
        # I 1
        # I 0        Oyuncunun carptigi bolgesine gore topta meydana gelecek ymomentumu degisimi
        # I -1
        
        if xaposteriori <=1:
            if yaposteriori <= self.ball.l_pos + (cursorsize-1)/2 and yaposteriori >= self.ball.l_pos - (cursorsize-1)/ 2:
                pcollision = "left", self.l_pos - yaposteriori
                
            else:
                pass # sag oyuncu skor
                
        if xaposteriori >= sizex -1:
            if yaposteriori <= self.ball.r_pos + (cursorsize-1)/2 and yaposteriori >= self.ball.r_pos -(cursorsize - 1)/2:
                pcollision = "right", self.r_pos - yaposteriori                
        
            else:
                pass # sol oyuncu skor
                
        if not pcollision and not ecollision:
            return False #carpma yok
            
        if pcollision and ecollision: #koseye carpma
            if ecollision =="top":
                if pcollision[0] == "left":#sol ust kose
                    self.ball.x = 1
                    self.ball.y = 1
                    self.ball.mx = 1
                    self.ball.my = -1
                    
                if pcollision[0] == "right":#sag ust kose
                    self.ball.x = sizex -1
                    self.ball.y = 1
                    self.ball.mx = -1
                    self.ball.my = -1
                    
            if ecollision == "bot":
                if pcollision[0] == "left":#sol alt kose
                    self.ball.x = 1
                    self.ball.y = sizey-1
                    self.ball.mx = 1
                    self.ball.my = 1
                    
                if pcollision[0] == "right":#sag alt kose
                    self.ball.x = sizex - 1
                    self.ball.y = sizey - 1
                    self.ball.mx = -1
                    self.ball.my = 1
            return ("both", 0)
            
        if pcollision:#yalnizca oyuncuya carpma
            return ("pcollusion", pcollision)
            
        if ecollision:#yalnizca kenara carpma
            return ("ecollision", ecollision)
            
        

class game_server(object):
    def __init__(self, addr, game_obj):
        self.game_obj = game_obj
        self.game_obj.ball.dump()
        self.players = {}#bu sozlukte iki key olucak left ve right left soldaki oyuncu right sagdaki
        #bu sozlugun degerleri ya bir player objesi ya da bir bot obkesi olucak
        self.clients = []
        self.pos_empty = ["left", "right"] #kullanicinin girebilecegi pozisyonlar
        self.ready_list = {"right":False, "left":False} #hazir olan kullanicilar
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((addr[0], addr[1]))
        print("binded and started")
        self.s.listen(3)
        self.client_thread()

    def client_thread(self, count=2):
         for i in range(count):
             Thread(target = self.client_handler).start()       

    def client_handler(self):#Gelen Baglantilar Bu Fonksiyon ile karsilanicak
        c, addr = self.s.accept()
        name = None#oyuncu adi
        pos = None#oyuncu pozisyonu
        control_scheme = None#kontrol tuslari
        ready = False
        self.clients.append(c)
        print(str(addr), "connected")
        while not name:
            self.sender(c, "sv_message", "Lutfen Isminizi Giriniz.")
            feedback = self.listen(c)
            name = feedback["data"]
            
        while not pos:
            if len(self.pos_empty) == 2:
                self.sender(c, "sv_message", "Lufen Bir Pozisyon Girin left/right")
                feedback = self.listen(c)
                feedback = feedback["data"]
                if feedback in self.pos_empty:
                    pos = feedback
                    self.pos_empty.remove(pos)
                    continue
                    
            if len(self.pos_empty) == 1:
                self.sender(c, "sv_mesage", "{} pozisyonuna girmek icin y yazin".format(self.pos_empty[0]))
                feedback = self.listen(c)
                feedback = feedback["data"]
                if feedback in self.pos_empty:
                    pos = feedback
                    self.pos_empty(pos)
                    continue
                    
        while not control_scheme:
            self.sender(c, "sv_message", "lutfen bir kontrol semasi seciniz\n1)  w/s\n2)  u/j")
            feedback = self.listen(c)
            feedback = feedback["data"]
            if feedback == "1":
                control_scheme = ["w", "s"]
                
            if feedback == "2":
                control_scheme = ["u", "j"]
                                        
        player_obj = player(name, c,control_scheme[0], control_scheme[1])
        self.players[pos] = player_obj
        if len(self.pos_empty) == 1:
            self.sender(c, "sv_message", "Karsi tarafa bot atmak icin e tusuna basin")
            feedback = self.listen(c)
            feedback = feedback["data"]
            if feedback == "e":
                self.players[self.pos_empty[0]] = bot("easy_bot", .5)
                
        while not ready:
            self.sender(c, "sv_message", "Hazir olmak icin e tusuna basin")
            feedback = self.listen(c)
            feedback = feedback["data"]
            if feedback == "e":
                ready = True
                self.ready(pos)
                

    def ready(self, pos, state = True):
        self.ready_list[pos] = state
        case = True
        for i in self.ready_list:
            if not self.ready_list == True:
                case = False
            
        if case:
            for i in range(5):
                for c in self.clients:
                    self.sender(c, "sv_message", "Oyun {} icinde basliyacak".format(str(5-i)))
                    time.sleep(1)
                    
    def game(self):
        for c in self.clients:
            self.sender(c, "game_ready", True)
        
        Thread(self.game_obj.game_logic).start()
        while 1:
            time.sleep(2)
            feedback = self.game_obj.ball.dump()
            for c in self.clients:
                self.sender(c, "refresh", feedback)
                
    def sender(self, c, tag, data):
        c.send(bytes(json.dumps({"tag":tag, "data":data})+"\n", "utf-8"))
            
        
        
    def listen(self, c):
        package = c.recv(1024).decode("utf-8")
        if not package:
            return 0
        package = json.loads(package)
        return package


            
class client(object):
    def __init__(self, addr, game_obj):
        self.socketqueue = []
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("connecting..")
        self.s.connect((addr[0], addr[1]))
        Thread(target = self.listener).start()
        self.sender()
        
    def sender(self):
        package = input(">>")
        package = {"tag":"setup_feedback", "data":package}
        package = json.dumps(package)+"\n"
        self.s.send(bytes(package, "utf-8"))
        
    def draw_canvas(self):
        
        
    def key_input(self):
        
        
    def listener(self):
        while 1:
            if self.socketqueue == [""]:
                self.socketqueue = []
            if self.socketqueue == []:
                subqueue = self.s.recv(1024).decode("utf-8")
                if not subqueue:
                    print("baglanti koptu")
                    exit()
                subqueue = subqueue.split("\n")
                self.socketqueue += subqueue
                
            package = self.socketqueue.pop(0)
            package = json.loads(package)
                            
            tag = package["tag"]
            data = package["data"]
            
            if tag=="sv_message":
                print(data)
                
            if tag == "game_ready":
                
                
def server_main():
    ball_obj = ball(x, y, mx, my)
    game_obj = game(ball_obj)
    game_server_obj = game_server(("localhost", 1221), game_obj)
    
def client_main():
    ball_obj = ball(x, y,x, my)
    game_obj = game(ball_obj)
    client_obj = client(("localhost", 1222), game_obj)
                        
            
    
        
