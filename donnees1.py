import matplotlib.pyplot as plt
import numpy as np
import mysql.connector
from scipy.ndimage.filters import gaussian_filter

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password",
    database="tipe",
    )


curseur = db.cursor(buffered=True)


curseur.execute("SELECT DimensionSimX*DimensionSimY, DimensionSimX, DimensionSimY FROM Simulation WHERE comportement = 'Essaim de fourmis' ;")
data = curseur.fetchall()
n = len(data) #nombre de lignes de data
Surface, TailleX, TailleY = [], [], []
for ligne in data:
    Surface.append(ligne[0])
    TailleX.append(ligne[1])
    TailleY.append(ligne[2])

#Pour comportement d'essaim de fourmis :


Temps, N_Robots = [],[]
for i in range(n):
    X,Y = [], []
    curseur.execute("SELECT Temps,N_Robots FROM Simulation WHERE DimensionSimX*DimensionSimY = " + str(Surface[i]) +" AND DimensionSimX = "+str(TailleX[i])+ " AND DimensionSimY = "+str(TailleY[i]) + " AND comportement = 'Essaim de fourmis' ;")
    data = curseur.fetchone()
    Temps.append(data[0])
    N_Robots.append(data[1])
    
        

    #faire un plot heatmap 2D avec le n robot en couleur

fig, [ax1,ax3] = plt.subplots(nrows=2,ncols=1)
#fig = plt.figure(figsize = (30,21)) #rapport (10,7) triplé
N = 100
hist1 = ax1.hist2d(Surface, Temps, bins=N, cmap='plasma')[0] #https://stackoverflow.com/questions/56130052/how-can-i-apply-a-gaussian-blur-to-a-figure-in-matplotlib
hist1 = gaussian_filter(hist1, sigma = 5)
ax1.pcolormesh(hist1.T, cmap = "plasma", shading="gouraud")

ax1.set(axisbelow = True,
        title = "Essaim de fourmis",
        xlabel = "Surface [p^2]",
        ylabel = "Temps [s]")



#Pour comportement militaire :
    
curseur.execute("SELECT DimensionSimX*DimensionSimY, DimensionSimX, DimensionSimY FROM Simulation WHERE comportement = 'Militaire' ;")
data = curseur.fetchall()
n = len(data) #nombre de lignes de data
Surface, TailleX, TailleY = [], [], []
for ligne in data:
    Surface.append(ligne[0])
    TailleX.append(ligne[1])
    TailleY.append(ligne[2])

#Pour comportement d'essaim de fourmis :


Temps, N_Robots = [],[]
for i in range(n):
    X,Y = [], []
    curseur.execute("SELECT Temps,N_Robots FROM Simulation WHERE DimensionSimX*DimensionSimY = " + str(Surface[i]) +" AND DimensionSimX = "+str(TailleX[i])+ " AND DimensionSimY = "+str(TailleY[i]) + " AND comportement = 'Militaire' ;")
    data = curseur.fetchone()
    Temps.append(data[0])
    N_Robots.append(data[1])

    #faire un plot heatmap 2D avec le n robot en couleur
curseur.close()

hist3 = ax3.hist2d(Surface, Temps, bins=N, cmap='plasma')[0] 
hist3 = gaussian_filter(hist1, sigma = 5)
ax3.pcolormesh(hist3.T, cmap = "plasma", shading="gouraud")

ax3.set(axisbelow = True,
        title = "Militaire",
        xlabel = "Surface [p^2]",
        ylabel = "Temps [s]")

fig.tight_layout()
plt.show()
fig.savefig('fig2.png', dpi = 300)
fig.close()
