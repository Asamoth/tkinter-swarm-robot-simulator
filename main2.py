#encoding: utf-8
import robot
import simu
import numpy as np
import sys 
import math
import random as rd
import string

def sqrt_int(X: int):  
    #de https://stackoverflow.com/questions/16266931/input-an-integer-find-the-two-closest-integers-which-when-multiplied-equal-th
    
    N = math.floor(math.sqrt(X))
    while bool(X % N):
        N -= 1
    M = X // N
    
    return M, N

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

def minimum(L):
    assert len(L)>0
    min= L[0]
    for i in range(len(L)):    
        if L[i]<min:
            min= L[i]
    return min

def amount(x,L):
    s=0
    for i in range(len(L)):
        if L[i]==x:
            s+=1
    return s

def remove_x(x,L):
    for i in range(amount(x,L)):
        L.remove(x)
        
def theta(position, center):
    x1 = position[0]
    y1 = position[1]
    x2 = center[0]
    y2 = center[1]
    return math.atan2(-(y2-y1), x2-x1)+np.pi #en radians
    #on ajoute pi pour que les robots regardent dans la direction opposée du centre initialement

#renvoie matrice de coordonnées initiales optimisées des robots
def spawn_robots(N_Robots, mx, my, r, largeur):
    X,Y = sqrt_int(N_Robots)
    if ((N_Robots <= 10) and (N_Robots!=7)) or ((N_Robots >= 10) and (X and Y != 1)):    
        #+ de place selon l'horizontale pour mettre des robots
        #du coup, il faut mettre le X,Y le plus petit pour l'horizontale
        A = min(X,Y)
        Spawns = np.zeros(shape=(N_Robots, 2))
        if A == X:
            B = Y
        else:
            B = X
        Spawns_coords_x = np.zeros(shape=(B,1))
        Spawns_coords_y = np.zeros(shape=(A,1))
        #on a A pour l'horizontale soit les y
        if B and A == 1:
            Spawns[0][0], Spawns[0][1] = mx, my
            
        if A%2 == 1: # A impaire donc on le centre sur milieu
            if A == 1:
                for i in range(N_Robots):    
                    Spawns[i][1] = my 
            else:
                Spawns_coords_y[0][0] = my
                for i in range(1, int((A-1)/2 + 1)):    
                    #on place les lignes restantes par rapport au centre
                    Spawns_coords_y[i][0], Spawns_coords_y[A-i][0] = my + i*r, my - i*r
                Spawns_coords_y.sort(axis=0)
                if B > 1:
                    for i in range(A):
                        for j in range(int((i/A)*N_Robots), int(((i+1)/A)*N_Robots)): 
                            #on a les A coordonnées possibles en y des robots en horizontales, 
                            #il nous faut les associer à tout les robots selon les lignes verticales
                            Spawns[j][1] = Spawns_coords_y[i][0]
        else:
            for i in range(0, int(A/2)):            
                Spawns_coords_y[i][0], Spawns_coords_y[A-i-1][0] = my + r/2 + r*(i), my - r/2 - r*(i)
            Spawns_coords_y.sort(axis=0)
            for i in range(A):
                        for j in range(int((i/A)*N_Robots), int(((i+1)/A)*N_Robots)):
                            #on a les A coordonnées possibles en y des robots en horizontales,
                            #il nous faut les associer à tout les robots selon les lignes verticales
                            Spawns[j][1] = Spawns_coords_y[i][0]
        if B%2 == 1: #B impaire donc on le centre sur milieu

            Spawns_coords_x[0][0] = mx
            for i in range(1, int((B-1)/2 + 1)):    
                #on place les lignes restantes par rapport au centre
                Spawns_coords_x[i][0], Spawns_coords_x[B-i][0] = mx + i*r, mx - i*r
            Spawns_coords_x.sort(axis=0)

            if A >= 1:
                for i in range(B):
                    for j in range(int((i/B)*N_Robots), int(((i+1)/B)*N_Robots)):
                        #on a les A coordonnées possibles en y des robots en horizontales,
                        #il nous faut les associer à tout les robots selon les lignes verticales
                        Spawns[j][0] = Spawns_coords_x[i][0]    
        else:
            for i in range(0, int(B/2)):            
                Spawns_coords_x[i][0], Spawns_coords_x[B-i-1][0] = mx + r/2 + r*(i), mx - r/2 - r*(i)                
            Spawns_coords_x.sort(axis=0)
            for i in range(B):
                        for j in range(int((i/B)*N_Robots), int(((i+1)/B)*N_Robots)):
                            Spawns[j][0] = Spawns_coords_x[i][0]

        Tempx = []
        Constx = []
        np.transpose(Spawns_coords_x)
        np.transpose(Spawns_coords_y)
        for i in range(N_Robots):
            Tempx.append(Spawns[i][1])      
            #on ajoute toutes les valeurs de y avec multiplicité dans une liste temporaire
            Constx.append(0)
            #on remplit la liste des valeurs de y ordonnées de zéros

        for i in range(A):
            mini = Tempx[0]                 
            Constx[i::A] = B*[mini]
            remove_x(mini,Tempx)

        for i in range(N_Robots):
            Spawns[i][1] = Constx[i]
        
        if Spawns[0][0]<largeur or Spawns[-1][0]>mx*2-largeur:
            print(Spawns[0][0],Spawns[-1][0])
            print("Problème selon l'horizontale")
            # os.exit(1)
            # raise SystemExit
            # sys.exit("Trop de robots/Marge entre robots trop grande, il manque de la place selon l'horizontale.")
            return False
        else:
            if Spawns[0][1]<largeur or Spawns[-1][1]>my*2-largeur:
                print(Spawns[0][1],Spawns[-1][1])
                print("Problème selon la verticale")
                # os.exit(1)
                # raise SystemExit
                #sys.exit("Trop de robots/Marge entre robots trop grande, il manque de la place selon la verticale.")
                return False
            else:
                return np.array(Spawns, int)    #convertis toutes les valeurs de floats en integers
    else:
        print("Nombre incorrect de robots")
        return False
        # os.exit(1)
        # # raise SystemExit
        # sys.exit("Il faut choisir un nombre entier de robots, inférieur à dix sauf sept, ou qui n'est pas un nombre premier.")

def main(utilisateur, Valeurs, Robots_N, X, Y):
    if utilisateur:
        comportement = input("Choisir un comportement d'essaim : \n A) Essaim de fourmis. B) Essaim d'oiseaux. C) Comportement militaire. [A/B/C]? : ")
        if comportement not in ["A","B","C"]:
            sys.exit("Les seules réponses acceptées sont A, B ou C.")
        elif comportement == ("B"):
            sys.exit("comportement pas encore fonctionnels")
        N_Robots = int(input("Il faut choisir un nombre entier de robots, inférieur à dix sauf sept, ou qui n'est pas un nombre premier. : "))
        resolution_x = float(input("Résolution de l'écran : \n Combien de pixels y a-t-il pour la largeur de l'écran : "))
        resolution_y = float(input("Résolution de l'écran : \n Combien de pixels y a-t-il pour la hauteur de l'écran : "))
        DPI = input("Est-ce que la DPI/PPI (Densité de Pixels par Pouce) de l'écran est connue ? \n O) Oui. N) Non. [O/N]? : ")
        if DPI == "N" :
            Q = input("Est-ce que la taille de la diagonale de l'écran est connue en pouce ? \n O) Oui. N) Non. [O/N]? : ")
            if Q == "N" : 
                cm = float(input("Taille de l'écran : \n Combien de centimètre compte la diagonale de l'écran : "))
                pouces = cm/2.54
            else:
                pouces = float(input("Taille de l'écran : \n Combien de pouces compte la diagonale de l'écran : "))
            DPI = math.sqrt(resolution_x**2 + resolution_y**2)/pouces #on utilise le théorème de pythagore pour connaître le nombre de pixels selon la diagonale de l'écran
        else:
            DPI = float(input("Quelle est la DPI/PPI (Densité de Pixels par Pouce) de l'écran : "))

    else:
        comportement = Valeurs
        pouces = 34
        resolution_x = int(X)
        resolution_y = int(Y)
        DPI = 109.68340725465096

    DPCM = DPI/2.54
    #DPI_r = DPI/72
    DPI_r = DPI/90 #densité de pixels par "inches" relatif à la densité par "inches" permettant de faire correspondre une distance réelle avec un nombre de pixel via Tkinter
    rapport_Tk = 90/72 #72 pixels/in étant la densité de pixels par inches par défaut de Tkinter
    rapport = 24 # echelle de réel/simulé
    #or on veut les grandeurs qui suivent exprimées en grandeurs simulées
    #mais elles sont exprimées en grandeurs réelles
    
    lim = min(resolution_x,resolution_y)/DPCM #en pixels
    l = lim *(1 - 1/8)  #largeur de la fenêtre du simulateur en centimètres, avec une marge de 1/5 de la largeur
    m = l*DPCM/rapport_Tk
    centre = (m/2, m/2)
    
    #appels de classe Robot:
    if not utilisateur:
        N_Robots = Robots_N
    
    v_extrema = (0.08,0.01) #cm/s grandeur simulée
    largeur = 22.7/rapport #cm ; longueur du robot ; grandeur réelle
    x = spawn_robots(N_Robots, centre[0], centre[1], 50*4, round(32.67))
    error = False
    if not isinstance(x,bool) == True:
        position_initiale = x
    else:
        error = True
    #position_initiale = spawn_robots(N_Robots, centre[0], centre[1], 50*4, round(32.67))
    print(error, "erreur ou pas sur le nombre de robot")
    if not error:
        rayon_roues = 7/rapport #cm ; grandeur réelle
        perception_min = 50/rapport # cm ; grandeur réelle
        perception = (100/rapport, math.radians(40)) #(cm ; grandeur réelle, radians)
        vélocité = (0.06,0.06) #cm/s ; grandeur simulée
        theta1 = []
        for i in range(N_Robots):
            theta1.append(theta(position_initiale[i], centre))
        robots = []
        cible_rayon=5 #pixels
        precision_ultrason = 5
        for i in range(N_Robots):
            robots.append(robot.Robot(position_initiale[i], vélocité, v_extrema, largeur, rayon_roues, perception_min, theta1[i], comportement, DPCM, rapport_Tk, cible_rayon, N_Robots, perception, precision_ultrason))
        
        #simulation graphique:
        path = "robot_model.png"
        N_Cibles = 1
        Var = False
        while Var == False:
            tags = tags_pixels(N_Robots,precision_ultrason, 5)
            if isinstance(tags,bool) == False: #si ce que retourne tags() n'est pas un boolean
                Var = True #alors chaque element de la liste Tags est unique car elle retourne des listes de caractères
        #le robot peut communiquer dans un rayon de 1 mètre et détecter les obstacles dans une plage de 2*40° à 1 mètre du capteur à ultrason
        simulateur = simu.Simulation(l,l,robots,N_Robots, N_Cibles, perception, precision_ultrason, path, tags[:N_Robots], tags[N_Robots:2*N_Robots], tags[2*N_Robots:], cible_rayon, position_initiale, perception_min, largeur, comportement, DPI_r, utilisateur)

    else:
        print("erreur")
if __name__ == "__main__":
    utilisateur = False
    if not utilisateur:
        n = 0
        N = 1000
        while n!=N:
            print()
            print(n, "Nième itération sur ", N)
            comportement_choice = ["A","C"]
            Valeurs = rd.choice(comportement_choice)
            
            Robots_N = 14
            
            FileX = open("TailleX.txt")
            X = FileX.read().splitlines()
            FileX.close()
            FailleY = open("TailleY.txt")
            Y = FailleY.read().splitlines()
            FailleY.close()
            
            assert len(X)==len(Y)
            i = rd.randint(0,len(X)-1)
            X = X[i]
            Y = Y[i]
            
            print(utilisateur)
            print(Robots_N, "nombre de robots")
            print(Valeurs, "comportement d'essaim")
            print(X,"X", Y, "Y")
            print()
            
            main(utilisateur, Valeurs, Robots_N, X, Y)
            n+=1
    else:
        Valeurs = ''
        Robots_N = None
        X,Y = None, None
        main(utilisateur, Valeurs,Robots_N,X,Y)