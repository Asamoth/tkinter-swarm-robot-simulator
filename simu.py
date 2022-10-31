#encoding : utf-8
import tkinter as tk
import random as rd
import robot
import numpy as np
import math
import time
from PIL import ImageTk,Image
import string
from os import sys



test = True #Pour ne pas ajouter à la base de données des valeurs erronées en cas de tests

if test == False:
    import mysql.connector
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="password",
        database="tipe"
        )
    
    curseur = db.cursor()
    


class Simulation:
    def __init__(self, width, height, robots, N_Robots, N_cibles, perception, precision_ultrason, path, tags, img_nom, angle_nom, cible_rayon, position, perception_min, largeur, comportement, DPI_r, utilisateur):
        self.N_Robots = N_Robots
        self.N_cibles = N_cibles
        self.utilisateur = utilisateur
        self.p = 0 #pour detection d'obstacles
        self.r = 0 #pour cercles
        self.l = 0 #pour update   
        self.c = 0 #compteur pour les couleurs de cercle
        
        
        
        self.path = path
        self.robots = robots
        self.precision_ultrason = precision_ultrason
        self.tags = tags
        self.img_nom = img_nom
        self.angle_nom = angle_nom
        self.cible_rayon = cible_rayon
        self.position = position
        self.temps1 = []
        self.comportement = comportement # A pour "Essaim de fourmis", B pour "Essaim d'oiseaux", C pour "Comportement militaire"
        self.DPI = DPI_r
        self.N_count_cible = 0 #nombre de robots connaissant les coordonnées de la cible
        
        for i in range(self.precision_ultrason*self.N_Robots):
            angle_nom[i] = 0

        #self.FPS = []
        self.seuil = math.ceil(0.8 * self.N_Robots) #seuil atteint lorsque l'entier plus grand ou égal à 80% des robots connait les coordonnées de la cible

        self.root = tk.Tk()
        self.root.bind("<Button 1>", self.clique_souris)
        self.root.tk.call('tk', 'scaling', self.DPI)
                       
            
        
        self.width = self.root.winfo_fpixels(str(width)+"c") #conversion de cm en pixels
        self.height = self.root.winfo_fpixels(str(height)+"c")
        #self.perception = (self.root.winfo_fpixels(str(perception[0])+"c"), perception[1])
        self.perception = (143.90896921017404, perception[1])
        #valeur calibrée avec pouces=34, 3440x1440
        #self.largeur = round(self.root.winfo_fpixels(str(largeur)+"c")) #round arrondis à l'int le plus proche, int arrondis vers le bas pour un nombre positif
        self.largeur = round(32.67) #valeur obtenue par la méthode en dessus pour pouces=34, 3440x1440
        #ces grandeurs doivent être fixes pour mesurer l'impact de la taille du canvas sur l'efficacité du robot
        if self.largeur <=0 :
            quit()
            sys.exit("La largeur du robot est trop petite par rapport à l'échelle donnée. Il faut agrandir la taille de la fenêtre simulée à l'écran.")

        if self.comportement == "C":
            self.count_attente1 = 0
            self.count_attente2 = 0
            self.count_attente3 = 0
        else:
            self.count_attente1 = None
            self.count_attente2 = None
            self.count_attente3 = None
            
        self.options = {"padx" : 5, 
                        "pady" : 5}
        
        self.window = tk.Toplevel()
        self.window.title("Simulation")
        #self.window.withdraw()
        
        self.started = False
        
            
        self.marge = round(self.root.winfo_fpixels(str(perception_min)+"c") + 5)
        
        self.canvas_menu = tk.Canvas(self.root, width = self.width, height = self.height)
        self.draw_canvas_menu()
        self.canvas_menu.pack(self.options)
        
        self.canvas_simu = tk.Canvas(self.window, width=self.width, height=self.height, bg="white")
        self.canvas_simu.pack(self.options)
        
        self.frame = tk.Frame(self.window, width=100, bg="green") #on crée une boite pour y organiser les boutons start, stop et quit
        self.frame.place(x=self.width/2)
        self.frame.pack()
        
        

        self.drawing = self.create()

        self.canvas_simu.create_rectangle(self.width-5,0,self.width,self.height, fill="green") #côté droit du simulateur
        self.canvas_simu.create_rectangle(5, self.height-5, self.width-5,self.height, fill="green") #côté du bas
        self.canvas_simu.create_rectangle(5,0,self.width-5,5, fill="green") #côté du haut
        self.canvas_simu.create_rectangle(0,0,5,self.height, fill="green") #côté de gauche

        self.create_cibles()
        #self.canvas_simu.create_oval(1000,1000,1000,1000, fill="red")
        for iteration,robotx in enumerate(self.robots,start=1):
            robotx.largeur = self.width
            if self.comportement == "C":
                if iteration == 1:
                    self.min_perception = 2*self.cible_rayon -1 + robotx.l//2
            else:
                if iteration == 1:
                    self.min_perception = self.root.winfo_fpixels(str(perception_min)+"c")
            self.cercle_création(robotx)
            
        if utilisateur:
            self.window.withdraw()
            start_button = tk.Button(self.frame, text = "Start", command = self.start)
            start_button.pack(side=tk.LEFT)
        
        else:
            self.root.withdraw()
            self.start()
            
        quit_button = tk.Button(self.frame, text = "Quit", command = self.bouttonpressé())
        quit_button.pack(side=tk.RIGHT)
        
        self.root.mainloop()
        print("mainloop closed")

        
    def temps(self):
        self.tps = self.N_Robots*[0]
        self.starttime = time.time() #l'instant qu'on utilise pour calculer le temps total mis par le programme       
        for i in range(self.N_Robots):      
            self.tps[i] = time.time()
         
    def create(self):
        img = Image.open(self.path)
        img = img.resize((self.largeur,self.largeur))
        for iteration,robotx in enumerate(self.robots, start=0):
            self.img_nom[iteration]= ImageTk.PhotoImage(img)
            return {robotx : self.canvas_simu.create_image(robotx.x, robotx.y, anchor = tk.CENTER, image=self.img_nom[iteration]) for robotx in self.robots}
    
    def draw_canvas_menu(self):
        x_bouton, y_bouton = self.width/2, self.height*(1/2 - 1/4.32) #valeur arbitraire
        x_quit, y_quit = self.width/2, self.height*(1/2 + 1/4.32)
        
        play = self.canvas_menu.create_text(x_bouton, y_bouton, anchor = tk.N, text="Lancer simulation", fill="#26b4ca", font=("Arial", 17, "bold"))
        quit = self.canvas_menu.create_text(x_quit, y_quit, anchor = tk.N, text="Quitter", fill="#26b4ca", font=("Arial", 17, "bold"))
        
        self.x1, self.y1, self.x2, self.y2 = self.canvas_menu.bbox(play) 
        self.x3, self.y3, self.x4, self.y4 = self.canvas_menu.bbox(quit)
        
        self.canvas_menu.create_polygon(self.x1, self.y1, self.x2, self.y1, self.x2, self.y2, self.x1, self.y2, fill="", width=2, activeoutline="#26b4ca")    #outline1
        self.canvas_menu.create_polygon(self.x3, self.y3, self.x4, self.y3, self.x4, self.y4, self.x3, self.y4, fill="", width=2, activeoutline="#26b4ca")    #outline2
        
    def clique_souris(self,evenement):
        x=evenement.x
        y=evenement.y
        
        if x in range(self.x1,self.x2):
                    if y in range(self.y1,self.y2):
                        #simulation
                        self.root.withdraw()
                        self.window.deiconify()  

        if x in range(self.x3,self.x4):
                    if y in range(self.y3,self.y4):
                        self.root.destroy()
    
    def bouttonpressé(self):
        self.root.destroy()
    
    def start(self):
        if not self.started:
            self.started = True
            self.temps()
            self.boucle()
            
    def boucle(self):
        while self.started: #boucle while au lieu de if statement résout le problème de stack overflow et de limite de récursivité
            self.update()
            #self.update(self.quitbutton)
        if not self.started and self.N_count_cible != 0:
            print("destroy")
            # self.window.destroy
            self.root.destroy()
            
    def update(self):
        for iteration,robotx in enumerate(self.robots, start=0):
            temps2 = time.time()
            dt = temps2 - self.tps[iteration] #on mesure le temps entre chaque itération du code
            self.tps[iteration] = temps2
            
            if self.comportement == "A":
                coordonnées = self.canvas_simu.coords(self.drawing[robotx])
                x1,y1,x2,y2 = coordonnées[0]-self.largeur, coordonnées[1]-self.largeur,coordonnées[0]+self.largeur, coordonnées[1]+self.largeur
                L = self.canvas_simu.find_overlapping(x1,y1,x2,y2)
                if self.N_Robots+1 in L or self.N_Robots+2 in L or self.N_Robots+3 in L or self.N_Robots+4 in L:
                    #il y a collision avec le robot et les obstacles qui définissent les limites du canvas
                    if robotx.x < self.largeur + 20:
                        robotx.obstacle_collision = True
                        if robotx.y < self.largeur + 20:
                            robotx.L = math.radians(315)
                        elif robotx.y > self.height - self.largeur - 20:
                            robotx.L = math.radians(45)
                        else:
                            robotx.L = math.radians(0)
                    elif robotx.x > self.width - self.largeur - 20 :
                        robotx.obstacle_collision = True
                        if robotx.y < self.largeur + 10:
                            robotx.L = math.radians(225)
                        elif robotx.y > self.height - self.largeur - 20:
                            robotx.L = math.radians(135)
                        else:
                            robotx.L = math.radians(90)
            
            if not robotx.cible:
                A = self.canvas_simu.coords(self.N_Robots + 4 + 1) #Id canvas correspondant à la cible
                if self.drawing[robotx] in self.canvas_simu.find_overlapping(A[0],A[1], A[2], A[3]): #si il y a collision entre le robot et (le rectangle enveloppant) la cible
                    robotx.cible = True
                    robotx.cible_x = A[0] + self.cible_rayon
                    robotx.cible_y = A[1] + self.cible_rayon
                    
                    self.N_count_cible += 1
                    
            if self.N_count_cible >= self.seuil:
                temps = time.time() - self.starttime
                if test == False:
                    if self.comportement == "A":
                        self.comportement = "Essaim de fourmis"
                    elif self.comportement == "B":
                        self.comportement = "Essaim d\'oiseaux"
                    else:
                        self.comportement = "Militaire"
                    curseur.execute("INSERT INTO Simulation (comportement, N_Robots, N_Cibles, PositionCibleX, PositionCibleY, DimensionSimX, DimensionSimY, Temps) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", 
                                    (self.comportement,
                                     self.N_Robots, 
                                     self.N_cibles, 
                                     self.canvas_simu.coords(self.N_Robots + self.N_cibles + 4)[0]+self.cible_rayon,
                                     self.canvas_simu.coords(self.N_Robots + self.N_cibles + 4)[1]+self.cible_rayon, 
                                     self.width, 
                                     self.height,
                                     temps ))
                    #On ajoute à notre base de donnée les données que l'on veut stocker
                    db.commit()
                    print("pas d'erreur", temps)
                    self.started = False
                    break
                    #break nécéssaire, sinon la boucle continue pour le nombre de robot restant avec de terminer la boucle while
                else:
                    print(temps)
                    self.started = False
                    break
            self.dist_robot(robotx,robotx.cycle)
            robotx.cinématique(dt)
            self.rotation(robotx, iteration)
            self.canvas_simu.coords(self.drawing[robotx], robotx.x, robotx.y)
            self.cercle(robotx,iteration)
            # if self.comportement == "A":
            #     robotx.cinématique_inverse(robotx.L, dt)
            nuage_de_point = self.détection_obstacle(robotx.x, robotx.y, robotx.theta, self.drawing[robotx], iteration, robotx) 
            if robotx.cycle: #si on est en comportement militaire "C"
                #Des disjonctions de cas en fonction des phases sont nécessaires car la fonction modifie et retourn des compteurs différents en fonction de la phase
                if robotx.phase[4] and robotx.theta == (-np.pi/2 or 3*np.pi/2):
                    self.count_attente3 = robotx.obstacles(nuage_de_point, dt, iteration, self.count_attente1, self.count_attente2, self.count_attente3)
                elif robotx.phase[5]:
                    if robotx.attente[0]:
                        self.count_attente1, self.count_attente2 = robotx.obstacles(nuage_de_point, dt, iteration, self.count_attente1, self.count_attente2, self.count_attente3)
                    else:
                        robotx.obstacles(nuage_de_point, dt, iteration, self.count_attente1, self.count_attente2, self.count_attente3)
                elif robotx.phase[7]:
                    if robotx.attente[1]:
                        if self.count_attente3 == self.N_Robots - 1: 
                            if self.count_attente1 != 0:
                                self.count_attente1, self.count_attente3 = robotx.obstacles(nuage_de_point, dt, iteration, self.count_attente1, self.count_attente2, self.count_attente3)
                            elif self.count_attente2 != 0:
                                self.count_attente2, self.count_attente3 = robotx.obstacles(nuage_de_point, dt, iteration, self.count_attente1, self.count_attente2, self.count_attente3)
                        else:
                            self.count_attente3 = robotx.obstacles(nuage_de_point, dt, iteration, self.count_attente1, self.count_attente2, self.count_attente3)
                    else:
                        robotx.obstacles(nuage_de_point, dt, iteration, self.count_attente1, self.count_attente2, self.count_attente3)
                elif robotx.phase[8]:
                    if robotx.attente[2]:  
                        self.count_attente1, self.count_attente2 = robotx.obstacles(nuage_de_point, dt, iteration, self.count_attente1, self.count_attente2, self.count_attente3)
                    else:
                        if self.count_attente2 == self.N_Robots:
                            self.count_attente3 = robotx.obstacles(nuage_de_point, dt, iteration, self.count_attente1, self.count_attente2, self.count_attente3)
                        else:
                            robotx.obstacles(nuage_de_point, dt, iteration, self.count_attente1, self.count_attente2, self.count_attente3)
                else:
                    robotx.obstacles(nuage_de_point, dt, iteration, self.count_attente1, self.count_attente2, self.count_attente3)
            else:
                robotx.obstacles(nuage_de_point, dt, iteration, self.count_attente1, self.count_attente2, self.count_attente3)
            self.canvas_simu.update()
    
    def rotation(self, robotx, iteration):
        img = Image.open(self.path)
        img = img.resize((self.largeur,self.largeur)) #rotate utilise des degrés
        self.img_nom[iteration] = ImageTk.PhotoImage(img.rotate(math.degrees(robotx.theta))) #expand=True, fillcolor="white"
        self.drawing[robotx] = self.canvas_simu.create_image(robotx.x, robotx.y, anchor = tk.CENTER, image=self.img_nom[iteration])
                
    
    def cercle_création(self, robotx):
        angle1 = robotx.theta - self.perception[1]
        angle2 = robotx.theta + self.perception[1]
        r1 = self.perception[0]
        r2 = self.min_perception
        precision = 10
        points1,points2 = [],[]
        for angle in np.linspace(angle1, angle2, precision):
            points1.append(robotx.x + r1*math.cos(angle))
            points1.append(robotx.y - r1*math.sin(angle))
            points2.append(robotx.x + r2*math.cos(angle))
            points2.append(robotx.y - r2*math.sin(angle))
        self.canvas_simu.create_line(points1,dash=(2,2), state="hidden")
        self.canvas_simu.create_line(points2, dash=(2,2), state="hidden")
        
    def cercle(self, robotx, iteration):
        #On peut déduire l'id canvas de l'arc en connaissant l'ordre de création des objets sujets de self.update()
        IdArc1 = self.N_Robots + 4 + self.N_cibles + 1 + 2*iteration
        IdArc2 = self.N_Robots + 4 + self.N_cibles + 2 + 2*iteration
        angle1 = robotx.theta - self.perception[1]
        angle2 = robotx.theta + self.perception[1]
        precision = 10
        r1 = self.perception[0]
        r2 = self.min_perception
        points1,points2 = [],[]
        for angle in np.linspace(angle1, angle2, precision):
            points1.append(robotx.x + r1*math.cos(angle))
            points1.append(robotx.y - r1*math.sin(angle))
            points2.append(robotx.x + r2*math.cos(angle))
            points2.append(robotx.y - r2*math.sin(angle))
        self.canvas_simu.coords(IdArc1,*points1)
        self.canvas_simu.coords(IdArc2,*points2)
        
        if robotx.cible1 == 1 and self.c==0:
            self.canvas_simu.itemconfig(IdArc1, fill="orange")
            self.canvas_simu.itemconfig(IdArc2, fill="orange")
            self.c = 1
            
        
        if self.r < self.N_Robots:
            self.canvas_simu.tag_lower(IdArc1)
            self.canvas_simu.tag_lower(IdArc2)
            self.canvas_simu.itemconfig(IdArc1, state="normal")
            self.canvas_simu.itemconfig(IdArc2, state="normal")
            self.r += 1
    
    def distance(self,A,B):
        A = np.array(A)
        B = np.array(B)
        return np.linalg.norm(A-B)
        
    def dist_robot(self, robotx, cycle): #cycle est un booléen étant True lors d'un comportement militaire où on recherche encore la cible
            #on mets dans une liste les Ids canvas des robots autre que celui sujet de la boucle actuelle
            #de la fonction update()
            if self.N_count_cible == 0 and not cycle: #aucun robot ne connait encore la cible
                return
            if cycle:
                if robotx.phase[0] or robotx.phase[2] or robotx.phase[4] or robotx.phase[6]:
                    #pas besoin de connaître l'état des voisins lors des phases de rotation
                    return
            idRobot = self.drawing[robotx]
            if not cycle:
                if not robotx.cible: #le robot actuel ne connaît pas encore la position de la cible ; on peut cependant la lui communiquer
                    ids = [self.drawing[roboty] for roboty in self.robots if roboty.cible and robotx!=roboty] #on ne veut que les ids des robots connaissant la cible
                else:
                    ids = [self.drawing[roboty] for roboty in self.robots if not roboty.cible and robotx!=roboty] #on ne veut que les ids des robots ne connaissant la cible pour la leur communiquer
            else: #si on en cours de cycle lors d'un comportement militaire, on veut tout les robots dans ou sur le cercle de perception
                ids = [self.drawing[roboty] for roboty in self.robots if robotx!=roboty]
            pointRobot = self.canvas_simu.coords(idRobot)
            points = [self.canvas_simu.coords(id) for id in ids]
            
            
            
            R = [] #liste des ids des robots se trouvant dans le cercle de perception du robot et remplissant le critère précédent
            if cycle:
                min = (np.inf,np.nan) #distance puis id qui correspond au robot 
                
            for iteration,point in enumerate(points, start=0):
                if self.distance(pointRobot,point) <= self.perception[0]:
                    R.append(ids[iteration])
            if cycle:
                for iteration,point in enumerate(points, start=0):
                    dist = self.distance(pointRobot,point)
                    if dist <= self.perception[0]:
                        if dist <= min[0] :
                            min = (dist, ids[iteration])          
            if cycle:
                if np.isnan(min[1]) == False: #il y a des robots dans ou sur le cercle de perception
                    n = self.N_Robots + 4 + 1 #id de la cible
                    cible = (self.canvas_simu.coords(n)[0] + self.cible_rayon, self.canvas_simu.coords(n)[1] + self.cible_rayon) #car coords[0] et coords[1] sont les coordonnées du point en haut à gauche du rectangle enveloppant un oval
                    for iteration,roboty in enumerate(self.robots):
                        if self.drawing[roboty] == min[1]:
                            if robotx.phase[1]:
                                if roboty.phase[1] or roboty.phase[2]:
                                    robotx.proximité_phase = True
                                    robotx.checked_attente = False
                                elif roboty.phase[4] or roboty.phase[5]:  #si le robot ne bouge pas car en attente ou en rotation
                                    robotx.checked_attente = True
                                    robotx.proximité_phase = False
                                else:
                                    robotx.checked_attente = False
                                    robotx.proximité_phase = False
                            elif robotx.phase[3]:
                                if (roboty.phase[4]) or (roboty.phase[5] and not roboty.attente[0]):
                                    robotx.checked_attente = True
                                    robotx.proximité_phase = False
                                elif roboty.phase[3]:
                                    robotx.checked_attente = False
                                    robotx.proximité_phase = True
                                else:
                                    robotx.checked_attente = False
                                    robotx.proximité_phase = False
                              
            if len(R)!=0: #il y a des robots dans ou sur le cercle de perception
                n = self.N_Robots + 4 + 1 #id de la cible
                cible = (self.canvas_simu.coords(n)[0] + self.cible_rayon, self.canvas_simu.coords(n)[1] + self.cible_rayon) #car coords[0] et coords[1] sont les coordonnées du point en haut à gauche du rectangle enveloppant un oval
                for iteration,roboty in enumerate(self.robots):
                    for RobotId in R:
                        if self.drawing[roboty] == RobotId: #permet de connaître l'objet robot associé à son id
                            if not robotx.cible:
                                if robotx.cycle:
                                    if robotx.robot_stop:
                                        roboty.robot_stop = True
                                    elif roboty.robot_stop:
                                        robotx.robot_stop = True
                                        
                                if roboty.cible:
                                    robotx.cible = True
                                    robotx.cible_x = cible[0]
                                    robotx.cible_y = cible[1]
                                    self.N_count_cible += 1
                                    break #une fois qu'un seul des robots dans le cercle a communiqué les coordonnées de la cible, pas besoin de continuer
                            else:
                                if robotx.cycle:
                                    if robotx.robot_stop:
                                        roboty.robot_stop = True
                                    elif roboty.robot_stop:
                                        robotx.robot_stop = True
                                roboty.cible = True
                                roboty.cible_x = cible[0]
                                roboty.cible_y = cible[1]
                                self.N_count_cible += 1
                                #pas de return cas le robot doit communiquer les coordonnées à chacun des robots à portée
                           
    def theta(position1, position2):
        x1 = position[0]
        y1 = position[1]
        x2 = position2[0]
        y2 = position2[1]
        return math.atan2(-(y2-y1), x2-x1) #en radians
    
            
    def détection_obstacle(self,x,y,theta, IdCanvas, iteration, roboty):
        obstacles = []
        x1, y1 = x, y
        angle1 = theta - self.perception[1]
        angle2 = theta + self.perception[1]
        if roboty.cible1 == 0:
            #le robot ne connaissait pas encore la cible, les pixels seront noirs
            couleur = "black"
            if roboty.cible:
                #si le robot connaît maintenant la cible
                couleur = "orange"
                roboty.cible1 = 1
        else:
            #sinon, on les mets en bleu afin de lire sur la simulation quels robots connaissent la cible en temps réel
            couleur = "orange"
            
        if self.p!=0: #si on a déjà dessiné les pixels du capteur lors d'une itération précédente, on les supprimes pour chaque nouvelle itération
            self.canvas_simu.delete(self.tags[iteration]) #tag "donnée" correspondant uniquement aux pixels des capteurs à ultrasons
        #interpolation linéaire
        for N_angle,angle in enumerate(np.linspace(angle1, angle2, self.precision_ultrason), start=0):
            x2 = x1 + self.perception[0] * math.cos(angle) #math.cos utilise des radians
            y2 = y1 - self.perception[0] * math.sin(angle)
            for i in range(0, 25): #rajouter des zeros améliore la précision du capteur
                #m varie de 0.00 à 1.00
                m = i/25
                x = int(x2 * m + x1 * (1-m))
                y = int(y2 * m + y1 * (1-m))
                if 0 < x < self.width and 0 < y < self.height:
                    self.canvas_simu.create_oval(x,y,x,y, width=0, fill=couleur, tag=self.tags[iteration]) #on crée un pixel noir assigné à un nom unique aux coordonées x,y
                    #print("Numero selon angle : ", i,", Numero du robot : ", iteration,", Numero de l'angle : ", N_angle, ", Id du pixel : ",self.canvas_simu.find_all()[-1], " test id canvas : ", self.precision_ultrason*100*iteration + 100*N_angle + i + N_Robots + 4 + iteration + 2)
                    TempVar = self.canvas_simu.find_overlapping(x,y,x,y)
                    w=0
                    k=[self.N_Robots + 1, self.N_Robots + 2, self.N_Robots + 3, self.N_Robots + 4] #liste des obstacles ATTENTION CAUSE DES PROBLEMES
                    if len(TempVar)>1: #soit si il y a des objets en collision avec le pixel noir 
                        for robotx in self.robots:
                            IdRobotCanvas = self.drawing[robotx]
                            if IdRobotCanvas != IdCanvas: #soit un capteur d'un robot ne peut pas entrer en collision avec ce-dernier
                                k.append(IdRobotCanvas) #on obtient une liste n'ayant que les id de canvas des objets pouvant faire des collisions
                        for element in TempVar:                            
                            if element in k: #c'est à dire que le pixel venant d'être créer entre en collision avec un robot
                                obstacles.append([x,y])
                                Id_Canvas = self.canvas_simu.find_all()[-1] #l'id du pixel en collision corresponds au dernier de la liste canvas.find_all()
                                self.canvas_simu.coords(Id_Canvas, x-2, y-2, x+2, y+2)
                                self.canvas_simu.itemconfig(Id_Canvas, fill="red")
                                #si le pixel noir entre en collision, il grandit et devient rouge pour visibilité
                                w+=1
                                break #pas besoin de continuer à vérifier chaque élement car on a déjà trouver une collision sur cette coordonnée
                    if w!=0:
                        break #pas besoin de continuer selon cet angle car on a trouvé une collision
        self.p=1
        return obstacles
    
    def create_cibles(self):
        coords_cible = self.cibles()
        for i in range(np.shape(coords_cible)[0]):
            self.canvas_simu.create_oval(coords_cible[i][0]-self.cible_rayon,coords_cible[i][1]-self.cible_rayon,coords_cible[i][0]+self.cible_rayon, coords_cible[i][1]+self.cible_rayon, fill="red")

    def cible(self):
        #coordonnees aletoires avec 10 pixels de marge avec les bords du canvas
        #on dessine un rectangle autour de la zone au centre ou les robots spawnent pour l'exclure de la
        #zone ou les ciblent vont pouvoir spawner
        condition = False
        i = 0
        while condition!=True:
            #x = rd.randrange(self.cible_rayon+self.largeur+10, int(self.width-self.cible_rayon-10))
            x = rd.randrange(round(self.marge), round(self.width - self.marge))
            #y = rd.randrange(self.cible_rayon+10, int(self.height-self.cible_rayon-10))
            y = rd.randrange(round(self.marge), round(self.height - self.marge))
            i+=1
            if not (self.position[0][0]-self.cible_rayon-self.marge <x< self.position[-1][0]+self.cible_rayon+self.marge and self.position[0][1]-self.cible_rayon-self.marge<y<self.position[-1][1]+self.cible_rayon+self.marge):
                return [x,y]

    def cibles(self):
        cible_coords =[]
        for i in range(self.N_cibles):
            #il faut ajouter a une liste les tuples coordonnees des cibles quand on les crées pour
            #pas que des cibles puissent se spawner les uns sur les autres
            if i==0:
                cible_coords.append(self.cible())
            else:
                condition=False
                while condition == False:
                    [x,y] = self.cible()
                    c = 0
                    for j in range(np.shape(cible_coords)[0]):
                        if not (cible_coords[j][0]-2*self.cible_rayon-self.marge<x<cible_coords[j][0]+2*self.cible_rayon+self.marge and cible_coords[j][1]-2*self.cible_rayon-self.marge<y<cible_coords[j][1]+2*self.cible_rayon+self.marge):
                            c+=1
                    if c==np.shape(cible_coords)[0]:
                        cible_coords.append([x,y])
                        condition=True
        return cible_coords

#on teste le module:
if __name__ == "__main__":
    
    def tags_pixels(N_Robots, N_angle, N_lettres):
        T = []
        lettres = string.ascii_lowercase
        for i in range(N_Robots*(2+N_angle)):
            #on veut N_Robots noms pour les images des robots
            #on veut encore N_Robots autres noms pour les tags des capteurs propre à chaque robot
            #on veut finalement N_Robots*N_angle noms pour chaque angle de chaque robot
            T.append("".join(rd.choice(lettres) for j in range(N_lettres)))
    
        for elements in T:
            if T.count(elements) > 1: #on vérifie l'unicité de chaque élément de la liste une fois celle-ci établie
                return False
        return T
    comportement = "C" #Comportement Militaire
    rapport = 24 # echelle de réel/simulé
    #or on veut les grandeurs qui suivent exprimées en grandeurs simulées
    #mais elles sont exprimées en grandeurs réelles
    l= 25 #largeur de la fenêtre du simulateur en centimètres
    path = "robot_model.png"
    m = 1200/2
    N_Robots = 5
    N_Cibles = 1
    precision_ultrason = 3
    cible_rayon = 5
    largeur = 1 #cm
    DPI=110
    DPCM = DPI/2.54
    DPI_r = DPI/72
    Var = False
    while Var == False:
        tags = tags_pixels(N_Robots,precision_ultrason, 5)
        if isinstance(tags,bool) == False: #si ce que retourne tags() n'est pas un boolean
            Var = True #alors chaque element de la liste Tags est unique car elle retourne des listes de caractères
    v_extrema = (0.08,0.01) #cm/s grandeur simulée
    largeur = 22.7/rapport #cm ; longueur du robot ; grandeur réelle
    rayon_roues = 7/rapport #cm ; grandeur réelle
    perception_min = 50/rapport # cm ; grandeur réelle
    vélocité = (0.06,0.06) #cm/s ; grandeur simulée
    position = [[m-60,m/4],[m,m],[m+60,3*m/2]]
    position = np.transpose(position)
    perception = (200/rapport, math.radians(40)) #(cm ; grandeur réelle, radians)
    theta1 = [math.radians(-90), math.radians(-90), math.radians(0), math.radians(90)]
    robots = [robot.Robot(position[i], vélocité, v_extrema, largeur, rayon_roues, perception_min, theta1[i], comportement, DPCM) for i in range(N_Robots)]
    simu = Simulation(l,l,robots,N_Robots, N_Cibles, perception, precision_ultrason, path, tags[:N_Robots], tags[N_Robots:2*N_Robots], tags[2*N_Robots:], cible_rayon, position, perception_min, largeur, comportement, DPI_r)