import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import mysql.connector
from mpl_toolkits.mplot3d import Axes3D

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password",
    database="tipe",
    #auth_plugin='mysql_native_password'
    )


curseur = db.cursor()
#'Essaim de fourmis'
curseur.execute("SELECT MAX(DimensionSimY) FROM Simulation WHERE comportement = 'Militaire' ; ")
maxY = curseur.fetchall()
maxY = int(maxY[0][0])
print(maxY)
curseur.execute("SELECT MAX(Temps) FROM Simulation WHERE comportement = 'Militaire' ; ")
maxT = curseur.fetchall()
maxT = int(maxT[0][0])

curseur.execute("SELECT PositionCibleX, PositionCibleY, Temps, N_Robots FROM Simulation WHERE comportement = 'Militaire' ;")
data = curseur.fetchall()
Cible, Temps, N = [],[],[]
for ligne in data:
    Cible.append([ligne[0], ligne[1]])
    Temps.append(ligne[2])
    N.append(ligne[3])

#https://stackoverflow.com/questions/44895117/colormap-for-3d-bar-plot-in-matplotlib-applied-to-every-bar


Cible, Temps, N = np.array(Cible), np.array(Temps), np.array(N)

fig = plt.figure()
ax = fig.add_subplot(1,1,1, projection = "3d")

hist, xedges, yedges = np.histogram2d(Cible[0], Cible[1], bins=(5,5))
xpos, ypos = np.meshgrid(xedges[:-1]+xedges[1:], yedges[:-1]+yedges[1:])

xpos = xpos.flatten()/2.
ypos = ypos.flatten()/2.
zpos = np.zeros_like (xpos)

dx = xedges [1] - xedges [0]
dy = yedges [1] - yedges [0]
dz = hist.flatten()

cmap = cm.get_cmap('inferno')
max_height = np.max(dz)
min_height = np.min(dz)

rgba = [cmap((k-min_height)/max_height) for k in dz]

ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=rgba, zsort="average")
plt.title("Essaim de fourmis")
plt.xlabel("Abscisse de la cible dans l'arène")
plt.ylabel("Ordonnée de la cible dans l'arène")
ax.set_xlim(0,maxY)
ax.set_ylim(0,maxY)
ax.set_zlim(0,maxT)
#plt.savefig("TIPE_fourmis_hist3d_0")
plt.show()
