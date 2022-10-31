import matplotlib.pyplot as plt
import numpy as np
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password",
    database="tipe"
    )
curseur = db.cursor()

curseur.execute("SELECT MAX(Temps) FROM Simulation WHERE comportement = 'Essaim de fourmis' ;")
maxA = curseur.fetchall()
curseur.execute("SELECT MAX(Temps) FROM Simulation WHERE comportement = 'Militaire' ;")
maxC = curseur.fetchall()
print(maxA,maxC)
data1,data3 = [],[]
for i in range(1,17):
    if i==1 or i==7 or i==11 or i==13:
        data1.append([])
        data3.append([])
    curseur.execute("SELECT Temps FROM Simulation WHERE comportement = 'Essaim de fourmis' AND N_Robots = " + str(i)+";")
    results = curseur.fetchall()
    data1.append([round(x[0]) for x in results])
    
    curseur.execute("SELECT Temps FROM Simulation WHERE comportement = 'Militaire' AND N_Robots = " + str(i)+";")
    results = curseur.fetchall()
    data3.append([round(x[0]) for x in results])
print(data1,data3,len(data1))

fig, [ax1,ax3] = plt.subplots(nrows=1,ncols=2)
bp1 = ax1.boxplot(data1, notch=False, sym="k+")

plt.setp(bp1["boxes"], color="black")
plt.setp(bp1["whiskers"], color="black")
plt.setp(bp1["fliers"], color="black")

ax1.yaxis.grid(True, 
                linestyle = "-",
                which = "major",
                color = "lightgrey",
                alpha = 0.5)
ax1.set(axisbelow = True,
        title = "Essaim de fourmis",
        xlabel = "Nombre de robots",
        ylabel = "Temps")
ax1.set_xlim(1,16)
ax1.set_ylim(0,int(maxA[0][0]))


bp3 = ax3.boxplot(data3, notch=False, sym="k+")

plt.setp(bp1["boxes"], color="black")
plt.setp(bp1["whiskers"], color="black")
plt.setp(bp1["fliers"], color="black")

ax3.yaxis.grid(True, 
                linestyle = "-",
                which = "major",
                color = "lightgrey",
                alpha = 0.5)
ax3.set(axisbelow = True,
        title = "Militaire",
        xlabel = "Nombre de robots",
        )
ax3.set_xlim(1,16)
ax3.set_ylim(0,int(maxC[0][0]))

fig.tight_layout()
plt.show()
fig.savefig('fig1.png', dpi = 300)
fig.close()
