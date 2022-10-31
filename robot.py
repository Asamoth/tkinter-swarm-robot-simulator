#encoding: utf-8
import numpy as np
import math
import random as rd
import angles


class Robot:
    def __init__(self, position, vélocité, v_extrema, largeur, rayon_roues, perception_min, theta, comportement, DPCM, rapport, rayon_cible, N_Robots, perception, precision_ultrason):
        self.temps = []
        self.DPI = DPCM
        #pixels/cm
        self.l = 32.67 #pixels, valeur calibrée pour 34 DPI, 3440x1440
        self.r = rayon_roues*self.DPI/rapport  #rayon des roues
        #on a besoin du rapport pour faire correspondre ces distances avec celles utilisées pour Tkinter
        
        self.x = position[0]
        self.y = position[1]
        self.theta = theta
        
        self.perception = perception
        self.precision_ultrason = precision_ultrason
        
        self.largeur = None #valeur modifiée dans la classe de simulation
        
        self.vg = vélocité[0]*self.DPI/rapport
        self.vd = vélocité[1]*self.DPI/rapport
        
        self.maxspeed = v_extrema[0]*self.DPI/rapport
        self.minspeed = v_extrema[1]*self.DPI/rapport
        
        self.comportement = comportement
        self.N_Robots = N_Robots
        
        if self.comportement == "A":
            L = [self.theta-self.perception[1], self.theta+self.perception[1]]
            self.L = rd.uniform(L[0],L[1])
            self.L = math.radians(angles.normalize(np.degrees(self.L), 0.0, 360.0))
            self.état_précédent = 3*[False] #1 booléen pour reculer à gauche, à droite ou tout droit
            self.countdown1 = 3
            self.L_atteint = False
            self.next_L = False
            self.tourne_constant = [False,None]
            self.obstacle_collision = False
            
        if self.comportement == "C":
            self.min_dist = 2*rayon_cible-1 +self.l//2 #corresponds à la distance entre deux robots lorsqu'ils balayent le canvas avec une marge de 1 pixel
        else:
            self.min_dist = perception_min*self.DPI/rapport
        
        if self.comportement == "A" or self.comportement == "B":
            self.countdown = 4
        else:
            self.countdown = 2
            
        self.cible = False #True ou False, si le robot a repéré la cible
        self.cible1 = 0 #compteur qui permet de connaître la première itération pour laquelle le robot connaît la cible, utile dans la classe simu
        #pour changer de couleur les pixels qui représentent le capteur à ultrason, afin de communiquer à l'utilisateur si le robot connaît ou non la cible
        self.cible_x = None
        self.cible_y = None
        self.comportement = comportement # A pour "Essaim de fourmis", B pour "Essaim d'oiseaux", C pour "Comportement militaire"
        if self.comportement == "C":
            self.phase = [True, False, False, False, False, False, False, False, False]
            self.attente = [False, False, False]
            self.proximité_phase = False
            self.checked_attente = False
            self.x_stop = 0
            self.phase_précédente = 0
            self.robot_stop = False
            self.replacement = False
            self.cycle = True
        else:
            self.cycle = False
    def distance(self,A,B):
        A = np.array(A)
        B = np.array(B)
        return np.linalg.norm(A-B)
        
    def obstacles(self, points, dt, iteration, count_attente1, count_attente2, count_attente3):
        obstacle_proche = None
        distance = np.inf
        if self.comportement == "A": #Comportement de fourmis
            if not self.obstacle_collision:
                obstacle = self.precision_ultrason*[False]
                if len(points) > 1: #des données arrivent des capteurs à ultrasons
                    for iteration,point in enumerate(points,start=0) :
                        dist = self.distance([self.x,self.y], point) 
                        if distance > dist:
                            distance = dist
                            obstacle_proche = (point, distance)
                        if dist < self.min_dist + 10: #marge de 10 pixels arbitraire
                            obstacle[iteration] = True
                    if obstacle_proche[1] < self.min_dist:
                        N = sum(obstacle) #Nombre 
                        if obstacle_proche[0][0] < 10 or obstacle_proche[0][1] < 10 or obstacle_proche[0][1] > self.largeur-10 or obstacle_proche[0][0] > self.largeur - 10:
                            self.next_L = True
                            
                        if self.precision_ultrason == N:
                            #il y a collision sur toutes le zones, on recule tout droit
                            self.recule()
                            self.countdown -= dt
                        else:
                            n = self.precision_ultrason-1
                            if sum(obstacle[:round(n/3)]) > 0 and sum(obstacle[round(n/3)+1:])==0:
                                #si la zone ayant des obstacles proches est à gauche, on recule à gauche
                                self.recule_g()
                                self.countdown -= dt
                                self.état_précédent[0] = True
                                
                            elif sum(obstacle[round(n*2/3):]) > 0 and sum(obstacle[:round(n*2/3)-1])==0:
                                #si la zone ayant des obstacles proches est à droite, on recule à droite
                                self.recule_d()
                                self.countdown -= dt
                                self.état_précédent[2] = True
                                
                            elif sum(obstacle[round(n/3)+1:round(n*2/3)-1]) > 0 and sum(obstacle[:round(n/3)])==0 and sum(obstacle[round(n*2/3):])==0:
                                #si la zone ayant des obstacles proches est au milieu, on recule tout droit
                                self.recule()
                                self.countdown -= dt
                                self.état_précédent[1] = True
                                
                            else:
                                #plusieurs zones ont des obstacles trop proches, on recule donc tout droit
                                self.recule()
                                self.countdown -= dt
                                self.état_précédent[2] = True
           
                    elif sum(self.état_précédent) > 0 and self.countdown > 0:
                        #s'il y a un True dans la liste
                        if self.état_précédent[0]:
                            #l'état précédent était de reculer à gauche et il n'y a pas eu de nouvel obstacle depuis
                            self.countdown -= dt
                            self.recule_g()
                            
                        elif self.état_précédent[1]:
                            #l'état précédent était de reculer à droite et il n'y a pas eu de nouvel obstacle depuis
                            self.countdown -= dt
                            self.recule_d()
                            
                        else:
                            #l'état précédent était de reculer tout droit et il n'y a pas eu de nouvel obstacle depuis
                            self.countdown -= dt
                            self.recule()
                            
                    elif self.countdown1 > 0 and self.L_atteint:
                        #on avance pendant trois secondes si on a atteint la position angulaire de self.L
                        self.avance()
                        self.countdown1 -= dt
                    
                    else:
                        self.countdown = 3
                        self.countdown1 = 3
                        self.état_précédent = 3*[False]
                        #s'il n'a pas d'obstacle trop proche
                        if self.L - 0.03 <= self.theta <= self.L + 0.03:
                            #si la position angulaire souhaitée est atteinte
                            if not self.next_L:
                                #si l'obstacle le plus proche n'était pas un bord du canvas
                                L = [self.theta - self.perception[1], self.theta + self.perception[1]]
                            else:
                                #sinon, le robot peut tourner entièrement, pas seulement sur la plage angulaire de self.theta+-self.perception[1]
                                L = [0, 2*math.pi]
                                self.next_L = False
                            self.L = rd.uniform(L[0], L[1])
                            self.L = math.radians(angles.normalize(np.degrees(self.L), 0.0, 360.0))
                            self.L_atteint = True
                            self.tourne_constant = [False,None]
                        else:
                            #si on doit encore tourner pour atteindre la position angulaire souhaitée de self.L
                            self.L_atteint = False
                            self.theta = math.radians(angles.normalize(np.degrees(self.theta), 0.0, 360.0))
                            if abs(self.theta-self.L) > math.radians(40):
                                #les angles sont proches de la discontinité du 0° à 359°
                                if self.tourne_constant[0]:
                                    if self.tourne_constant[1] == "g":
                                        self.tourne_g()
                                    else:
                                        self.tourne_d()
                                elif math.degrees(self.theta) > 358 or math.degrees(self.theta) < 2:
                                    self.tourne_constant[0] = True
                                    if math.degrees(self.theta) < 2:
                                        if math.degrees(self.L) < 182:
                                            self.tourne_g()
                                            self.tourne_constant[1] = "g"
                                        else:
                                            self.tourne_d()
                                            self.tourne_constant[1] = "d"
                                    else:
                                        if math.degrees(self.L) < 178:
                                            self.tourne_d()
                                            self.tourne_constant[1] = "d"
                                        else:
                                            self.tourne_g()
                                            self.tourne_constant[1] = "g"
                                elif abs(math.degrees(self.theta) - (math.degrees(self.L)-360)) < abs(math.degrees(self.theta) - math.degrees(self.L)):
                                    self.tourne_d()
                                else:
                                    self.tourne_g()
                            else:
                                if self.L < self.theta:
                                    self.tourne_d()
                                else:
                                    self.tourne_g()
    
                else:
                    #s'il n'y a aucun obstacle repéré par le capteur à ultrason
                    if sum(self.état_précédent) > 0 and self.countdown > 0:
                        #mais que précédemment il y a eu un obstacle trop proche, on continue la séquence d'évitemment
                        #soit s'il y a un True dans la liste des états précédents
                        if self.état_précédent[0]:
                            #l'état précédent était de reculer à gauche et il n'y a pas eu de nouvel obstacle depuis
                            self.countdown -= dt
                            self.recule_g()
                            
                        elif self.état_précédent[1]:
                            #l'état précédent était de reculer à droite et il n'y a pas eu de nouvel obstacle depuis
                            self.countdown -= dt
                            self.recule_d()
                            
                        else:
                            #l'état précédent était de reculer tout droit et il n'y a pas eu de nouvel obstacle depuis
                            self.countdown -= dt
                            self.recule()
                            
                    elif self.countdown1 > 0 and self.L_atteint:
                        self.avance()
                        self.countdown1 -= dt
                        
                    else:
                        self.countdown = 3
                        self.countdown1 = 3
                        self.état_précédent = 3*[False]
                        if self.L - 0.03 <= self.theta <= self.L + 0.03:
                            L = [self.theta - self.perception[1], self.theta + self.perception[1]]
                            self.L = rd.uniform(L[0], L[1])
                            self.L = math.radians(angles.normalize(np.degrees(self.L), 0.0, 360.0))
                            self.L_atteint = True
                            self.tourne_constant = [False,None]
                        else:
                            self.L_atteint = False
                            self.theta = math.radians(angles.normalize(np.degrees(self.theta), 0.0, 360.0))
    
                            if abs(self.theta-self.L) > math.radians(40):
                                #les angles sont proches de la discontinité du 0° à 359°
                                if self.tourne_constant[0]:
                                    if self.tourne_constant[1] == "g":
                                        self.tourne_g()
                                    else:
                                        self.tourne_d()
                                elif math.degrees(self.theta) > 358 or math.degrees(self.theta) < 2:
                                    self.tourne_constant[0] = True
                                    if math.degrees(self.theta) < 2:
                                        if math.degrees(self.L) < 182:
                                            self.tourne_g()
                                            self.tourne_constant[1] = "g"
                                        else:
                                            self.tourne_d()
                                            self.tourne_constant[1] = "d"
                                    else:
                                        if math.degrees(self.L) < 178:
                                            self.tourne_d()
                                            self.tourne_constant[1] = "d"
                                        else:
                                            self.tourne_g()
                                            self.tourne_constant[1] = "g"
                                elif abs(math.degrees(self.theta) - (math.degrees(self.L)-360)) < abs(math.degrees(self.theta) - math.degrees(self.L)):
                                    self.tourne_d()
                                else:
                                    self.tourne_g()
                            else:
                                if self.L < self.theta:
                                    self.tourne_d()
                                else:
                                    self.tourne_g()
            else:
                #si il y a collision entre le robot et un des obstacles délimitant le canvas
                if self.theta == self.L:
                    self.obstacle_collision = False
                    L = [self.theta - self.perception[1], self.theta + self.perception[1]]
                    self.L = rd.uniform(L[0], L[1])
                    self.L = math.radians(angles.normalize(np.degrees(self.L), 0.0, 360.0))
                    self.L_atteint = True
                    self.tourne_constant = [False,None]
                
                else:
                    if self.L != 0:
                        if self.L - 0.03 < self.theta < self.L + 0.03:
                            self.theta = self.L
                        else:
                            self.tourne_d()
                    else:
                        if self.L < 0.03 or self.L > 357:
                            self.theta = self.L
                        else:
                            self.tourne_d()
            
        elif self.comportement == "B": #Comportement d'oiseaux
            if len(points) > 1: #des données arrivent des capteurs à ultrasons
                for point in points:
                    dist = self.distance([self.x,self.y], point) 
                    if distance > dist:
                        distance = dist
                        obstacle_proche = (point, distance)
                if obstacle_proche[1] < self.min_dist and self.countdown > 0:
                    #obstacle trop proche de robot, séquence de comportement d'évitement                    
                    if len(self.temps) == 2:    
                        self.countdown -= dt
                        self.temps.append(self.countdown)
                        del self.temps[0]
                        
                    else:
                        self.countdown -= dt
                        self.temps.append(self.countdown)
                        
                    self.recule_g()  
                    
                else:
                    if len(self.temps) == 2:
                        if self.temps[0]!=self.temps[1]!=4 and self.countdown>0:
                            self.countdown-=dt 
                            self.temps.append(self.countdown)
                            del self.temps[0]
                            self.recule_g()
                        else:
                            self.countdown = 4
                            self.temps.append(self.countdown)
                            del self.temps[0]
                            self.avance()
                    else:        
                        self.countdown = 4
                        self.temps.append(self.countdown)
                        self.avance()
                        
        else: #comportement militaire "C"
            if self.phase[0]: #rotation vers le haut
                self.stop()
                if self.theta == (np.pi/2 or -3*np.pi/2):
                    self.phase[0] = False
                    if not self.replacement:
                        if count_attente3 != 0 :
                            self.phase[8] = True
                            self.attente[2] = True
                            self.robot_stop = False
                        else:
                            self.phase[1] = True
                    else:
                        self.phase[1] = True
                elif (np.pi/2 -0.03 <= self.theta <= np.pi/2 + 0.03) or (-3*np.pi/2 -0.03 <= self.theta <= -3*np.pi/2 + 0.03):
                    self.theta = np.pi/2
                elif -np.pi/2 <= self.theta < np.pi/2 or self.theta < -3*np.pi/2 or 3*np.pi/2 <= self.theta:
                    self.tourne_g()
                else:
                    self.tourne_d()
                    
            elif self.phase[1]: #déplacement vers le haut ; regroupement        
                if not self.replacement:
                    if len(points) > 1: #détéction d'obstacle
                        for point in points:
                            dist = self.distance([self.x,self.y], point) 
                            if distance > dist:
                                distance = dist
                                obstacle_proche = (point, distance)
                        if obstacle_proche[1] < self.min_dist and self.countdown > 0:
                            if obstacle_proche[0][1] <= 10: #si la position selon l'axe des ordonnées de l'obstacle est très proche du bords
                                #alors on considère que le robot peut passer en phase[2] car la collision n'est pas avec un robot
                                self.phase[1] = False
                                self.phase[2] = True
                                self.countdown = 2
                                self.stop()
                            else:
                                if self.proximité_phase:
                                    #l'obstacle le plus proche est un robot qui est encore en train de se déplacer vers le haut ou qui se tourne vers la gauche
                                    #on attends qu'il passe
                                    self.countdown -= dt
                                    self.stop()
                                else:
                                    #l'obstacle le plus proche est un robot qui est soit en attente soit en train de se déplacer vers la gauche
                                    if self.checked_attente: #l'obstacle le plus proche est un robot qui ne bougera pas selon x, soit phase[4]
                                        self.countdown -= dt
                                        self.phase[1] = False
                                        self.phase[6] = True
                                        self.replacement = True
                                        self.checked_attente = False
                                    else:
                                        self.recule()
                        else:
                            if self.countdown == 2 and self.theta != np.pi/2:
                                #si le robot se déplace vers le haut en diagonale
                                self.avance_g()
                                #on se corrige en allant vers la gauche en avançant
                            else:
                                self.countdown = 2
                                self.avance()
                    else:
                        #s'il n'y a pas d'obstacle, on avance
                        self.avance()
                else:
                    print(self.y)
                    if 25 < self.y < 30:
                        self.phase[1] = False
                        self.phase[2] = True
                        self.replacement = False
                        self.stop()
                    elif len(points) > 1: #détéction d'obstacle
                        for point in points:
                            dist = self.distance([self.x,self.y], point) 
                            if distance > dist:
                                distance = dist
                                obstacle_proche = (point, distance)
                        
                        if obstacle_proche[1] < self.min_dist and self.countdown > 0:
                            if obstacle_proche[0][1] < 15 :
                                self.phase[1] = False
                                self.phase[2] = True
                                self.remplacement = False
                            else:
                                self.stop()
                                self.countdown -= dt
                        else:
                            self.avance()
                    else:
                        self.avance()

            elif self.phase[2]: #rotation vers la gauche
                self.stop()
                if self.theta == (np.pi or -np.pi):
                    self.phase[2] = False
                    self.phase[3] = True
                elif (np.pi -0.03 <= self.theta <= np.pi + 0.03) or ( -np.pi - 0.03 <= self.theta <= -np.pi + 0.03 ):
                    self.theta = np.pi
                elif 0 <= self.theta < np.pi or self.theta < -np.pi:
                    self.tourne_g()
                else:
                    self.tourne_d()
            
            elif self.phase[3]: #déplacement vers la gauche ; alignement
                if len(points) > 1: #détéction d'obstacle
                    for point in points:
                        dist = self.distance([self.x,self.y], point) 
                        if distance > dist:
                            distance = dist
                            obstacle_proche = (point, distance)
                    if obstacle_proche[1] < self.min_dist and self.countdown > 0 :
                        if obstacle_proche[0][0] <= 10 or self.checked_attente:
                            #si l'abscisse de l'obstacle est très petit (que le robot est le plus à gauche)
                            #ou si le robot le plus proche ne bouge plus
                            self.stop()
                            self.phase[3] = False
                            self.phase[4] = True
                            
                        elif self.proximité_phase:
                            self.stop()
                            self.countdown-=dt
                            self.proximité_phase = False
                        
                        else:
                            self.recule()
                            self.countdown -= dt
                    else:
                        self.countdown = 1.5
                        self.avance()
                else:
                    self.avance()
                            
          
            elif self.phase[4]: #rotation vers le bas 
                self.stop()
                if self.theta == (-np.pi/2 or 3*np.pi/2):
                    self.phase[4] = False
                    self.phase[5] = True
                    self.attente[0] = True
                    self.robot_stop = False
                    count_attente3 = 0
                    return count_attente3
                elif (-np.pi/2 -0.03 <= self.theta <= -np.pi/2 + 0.03) or ( 3*np.pi/2 -0.03 <= self.theta <= 3*np.pi/2 + 0.03 ):
                    self.theta = -np.pi/2
                elif -np.pi/2 < self.theta <= np.pi/2 or self.theta <= -3*np.pi/2 or 3*np.pi/2 < self.theta:
                    self.tourne_d()
                else:
                    self.tourne_g()
            
            elif self.phase[5]: #déplacement vers le bas
                if self.attente[0]:
                    self.stop()
                    count_attente1 += 1
                    count_attente2 = 0
                    self.attente[0] = False
                    return count_attente1, count_attente2
                if count_attente1 == self.N_Robots:
                    if len(points) > 1: #détéction d'obstacle
                        for point in points:
                            dist = self.distance([self.x,self.y], point) 
                            if distance > dist:
                                distance = dist
                                obstacle_proche = (point, distance)
                        if obstacle_proche[1] < self.min_dist:
                            if obstacle_proche[0][1] >= self.largeur - 15:  
                                self.stop()
                                self.phase[5] = False
                                self.phase[6] = True
                            else:
                                self.avance()
                        else:
                            self.avance()
                    else:
                        self.avance()
                else:
                    self.stop()

            
            elif self.phase[6]: #rotation vers la droite
                self.stop()
                if self.theta == 0:
                    self.phase[6] = False
                    self.phase[7] = True
                    self.attente[1] = True
                elif (-0.03 <= self.theta <= 0.03) or ( 2*np.pi - 0.03 <= self.theta <= 2*np.pi + 0.03 ) or ( -2*np.pi -0.03 <= self.theta <= -2*np.pi + 0.03 ):
                    self.theta = 0
                elif 0 < self.theta <= np.pi or self.theta <= -np.pi:
                    self.tourne_d()
                else:
                    self.tourne_g()
                    
            elif self.phase[7] : #déplacement vers la droite
                if not self.replacement:
                    if self.attente[1]:
                        count_attente3 += 1
                        self.x_stop = self.x + self.N_Robots*self.l #abscisse sur laquelle s'arrêtera le robot afin de balayer le canvas
                        self.attente[1] = False
                        if count_attente1 != 0:
                            self.phase_précédente = 0
                            if count_attente3 == self.N_Robots:
                                return count_attente1, count_attente3
                        elif count_attente2 != 0:
                            self.phase_précédente = 4
                            if count_attente3 == self.N_Robots:
                                return count_attente2, count_attente3
                        return count_attente3
                    if count_attente3 == self.N_Robots:
                        if self.x >= self.x_stop:
                            self.stop()
                            self.phase[7] = False
                            self.phase[self.phase_précédente] = True
                            
                        elif len(points) > 1: #détéction d'obstacle
                            for point in points:
                                dist = self.distance([self.x,self.y], point) 
                                if distance > dist:
                                    distance = dist
                                    obstacle_proche = (point, distance)
                            if obstacle_proche[1] < self.min_dist:
                                
                                if obstacle_proche[0][0] >= self.largeur - 15 or self.robot_stop:
                                    
                                    #si la valeur des abscisses de l'obstacle correspond au bord
                                    self.stop()
                                    self.phase[7] = False
                                    self.phase[self.phase_précédente] = True
                                    self.robot_stop = True #il faut que les autres robots s'arrêtent
                                
                                else:
                                    self.avance()
                            else:
                                self.avance()
                        else:
                            self.avance()
                    else:
                        self.stop()
                else:
                    if len(points) > 1: #détéction d'obstacle
                        for point in points:
                            dist = self.distance([self.x,self.y], point) 
                            if distance > dist:
                                distance = dist
                                obstacle_proche = (point, distance)
                        if obstacle_proche[1] < self.min_dist and self.countdown > 0:
                            if obstacle_proche[0][0] > self.largeur -10:
                                self.phase[7] = False
                                self.phase[0] = True
                                self.stop()
                            else:
                                self.stop()
                                self.countdown -= dt
                        else:
                            self.countdown = 2
                            self.avance()
                    else:
                        self.avance()
                            
            elif self.phase[8] : #déplacement vers le haut [dans le cycle]
                if self.attente[2]:
                    count_attente2 += 1
                    count_attente1 = 0
                    self.attente[2] = False
                    return count_attente1, count_attente2
                if count_attente2 == self.N_Robots:
                    count_attente3 = 0
                    if len(points) > 1: #détéction d'obstacle
                        for point in points:
                            dist = self.distance([self.x,self.y], point) 
                            if distance > dist:
                                distance = dist
                                obstacle_proche = (point, distance)
                        if obstacle_proche[1] < self.min_dist:
                            self.stop()
                            self.phase[8] = False
                            self.phase[6] = True
                            return count_attente3
                        else:
                            self.avance()
                            return count_attente3
                    else:
                        self.avance()
                        return count_attente3
                else:
                    self.stop()
    
    def stop(self):
        self.vd = 0
        self.vg = 0
        
    def tourne_g(self):
        
        self.vd = self.maxspeed
        self.vg = -self.maxspeed
        
    def tourne_d(self):
        
        self.vd = -self.maxspeed
        self.vg = self.maxspeed
        
    def randdir(self, n): #random direction
    
        self.vd = n
        self.vg = -n 
    
    def mouvement(self,g,d):
        self.vd = d
        self.vg = g
        
    def recule(self):
        
        self.vd = - self.maxspeed
        self.vg = - self.maxspeed
    
    def recule_g(self):
        
        #recule à gauche
        self.vd = - self.maxspeed
        self.vg = - self.maxspeed/8
    
    def recule_d(self):
        
        #recule à droite
        self.vd = - self.maxspeed/8
        self.vg = - self.maxspeed
    
    def avance(self):
        
        self.vd = self.maxspeed
        self.vg = self.maxspeed
    
    def avance_g(self):
        
        self.vd = self.maxspeed
        self.vg = self.maxspeed/2
    
    def avance_d(self):
        
        self.vd = self.maxspeed/2
        self.vg = self.maxspeed
        
    def cinématique(self, dt):
        #basé sur le modèle cinématique donnant la vitesse dx/dt et dy/dt, pour obtenir la position on multiplie par dt, temps mesuré entre
        #deux appels de la fonction self.update() pour chaque robot dans le modèle simu
        self.x += (self.r*(self.vg+self.vd)/2) * math.cos(self.theta) * dt
        self.y -= (self.r*(self.vg+self.vd)/2) * math.sin(self.theta) * dt
        self.theta += (self.vd - self.vg) / self.l * dt

        if self.theta>2*math.pi or  self.theta<-2*math.pi:  #[2pi]
            self.theta = 0

        self.vd = max(min(self.maxspeed, self.vd), self.minspeed)
        self.vg = max(min(self.maxspeed, self.vg), self.minspeed)
        
