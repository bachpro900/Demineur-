import random
import os
import sys
from PyQt5.QtWidgets import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from time import *
import time
import sqlite3

########################################
############  Class Case   #############
########################################
class Case:
  def __init__(self, grille, x, y):
    self.__grille = grille
    self.__x = x
    self.__y = y
    self.__B= self.__grille.getNbBombes()
    self.__valeur = 0
    self.__etat = False
    self.__bouton = QPushButton()
    self.setButtonSize()
    self.__bouton.clicked.connect(self.__clicked)
    #self.__bouton.clicked.connect(self.__getNbCasesVisibles)
    self.__bouton.setContextMenuPolicy(Qt.CustomContextMenu)
    self.__taguee = False
    self.__bouton.customContextMenuRequested.connect(self.__right_click)
    
    
  def setButtonSize (self):
    if self.__B == 10:
      self.__bouton.setFixedSize(55,55)
    else:
      self.__bouton.setFixedSize(35,35)


  def get_bouton(self):
    return self.__bouton

  def __right_click(self):
    if self.__taguee:
        self.__grille.nbBombeTaguees -=1
        self.__bouton.setIcon(QIcon()) 
    else:
        self.__grille.nbBombeTaguees +=1
        self.__bouton.setIcon(QIcon('drapeau.png'))
        self.__bouton.setIconSize(QSize(50,20))  
    self.__taguee = not self.__taguee
    self.__grille.updateCompteurTaguees()    


  def __clicked (self):
    if not self.__taguee and self.__grille.debutJeu == True:      
      if self.__valeur != -1 :
        self.__grille.nbCasesVisibles +=1

      self.__grille.tour(self.__x, self.__y)

    
  def afficher (self):
    self.__etat = True

    if  not self.__grille.is_gameover() and self.__grille.is_winner():
      self.__grille.getFenetreWinner()
      self.__bouton.setEnabled(False) # rend le bouton non cliquable     
      if self.__valeur == -1:
          self.__bouton.setIcon(QIcon('bombe.png'))
          self.__bouton.setIconSize(QSize(80,100))  
      elif self.__valeur == 0:
          #self.__bouton.setFlat(True) # sert à effacer les bordures du bouton 
          self.__bouton.setText(str(''))
      else:
          self.__bouton.setText(str(self.__valeur))
          self.__bouton.setStyleSheet('QPushButton {color: green;}')


    elif not self.__taguee and not self.__grille.is_gameover(): # j'affiche pas les cases taguées      
      self.__bouton.setEnabled(False)       
      if self.__valeur == -1:
          self.__bouton.setIcon(QIcon('bombe.png'))
          self.__bouton.setIconSize(QSize(80,100))  
      elif self.__valeur == 0: 
          self.__bouton.setText(str(''))
      else:
          self.__bouton.setText(str(self.__valeur))
          self.__bouton.setStyleSheet('QPushButton {color: green;}')


    elif self.__grille.is_gameover() : # si fin du jeu, on affiche tout
      self.__bouton.setEnabled(False)
      self.__grille.getFenetreGameOver()
      if self.__valeur == -1:
          self.__bouton.setIcon(QIcon('bombe.png'))
          self.__bouton.setIconSize(QSize(80,100))
          
      elif self.__valeur == 0: 
          self.__bouton.setText(str(''))
      else:
          self.__bouton.setText(str(self.__valeur))
    

  # methode qui retourne True quand une case est visible (sont etat est True)
  def is_visible (self):
    return self.__etat

  # methode pour passer une case vide a une case conteant une bombe
  def set_bombe(self):
    self.__valeur = -1
    #self.__etat = True

  def incrementer_valeur (self):
    self.__valeur +=1

  # methode qui verifie si une case contient une bombe   
  def is_bombe (self):
    return self.__valeur < 0

  # methode qui verifie si une case est vide
  def is_vide (self):
    return self.__valeur == 0

 # compteur de nombres de cases visibles
  '''
  def __getNbCasesVisibles(self):
    if self.__etat == True and self.__valeur != -1 :
      self.__grille.nbCasesVisibles +=1
  '''
      
 
########################################
############  Class Grille #############
########################################
class Grille:
  def __init__(self, nb_lignes, nb_colonnes, nb_bombes):
    self.__L = nb_lignes
    self.__W = nb_colonnes
    self.__B = nb_bombes
    self.debutJeu = False
    self.__fin_du_jeu = False
    self.partieGagnee = False
    self.nbBombeTaguees = 0
    self.nbCasesVisibles = 0
    self.nbCasesVisiblesWinner = 0
    
    self.__casesTaguees = QLabel("0") # à faire le rendre non editable
    #self.__casesTaguees.setReadOnly(True)
    self.__casesTaguees.setFixedSize(90,30)
    self.__casesTaguees.setStyleSheet('background-color: red')
    
    self.__msgGameOver = QPushButton( "    * ⵜⵅⴻⵙⵕⴻⵟ, ⵉⴼⵓⴽ ⴻⵍ ⵄⴻⵠ *    ")
    self.__msgGameOver.setWindowTitle(" ")
    self.__msgGameOver.setFixedSize (400,50)
    self.__msgGameOver.setStyleSheet('QPushButton {color: red;background-color: black; font-size: 30px}') 
    self.__msgGameOver.setDisabled(True)
    
    self.__msgWinner = QPushButton( "    * Bien joué *    ")
    self.__msgWinner.setWindowTitle(" ")
    self.__msgWinner.setFixedSize (400,50)
    self.__msgWinner.setStyleSheet('QPushButton {color: green;background-color: white; font-size: 30px}') 
    self.__msgWinner.setDisabled(True)

    self.__widget = QWidget()
    self.__grille = QGridLayout() 
    self.__widget.setLayout(self.__grille)
    self.__cases = [ [ Case(self, j, i) for i in range(self.__W) ] for j in range(self.__L) ]
    self.initialiser()
    
  def getNbBombes(self):
    return self.__B

  def getWidget (self):
      return self.__widget

  def getCaseTaguesCompteurWidget(self):
    return self.__casesTaguees
    
  def updateCompteurTaguees(self):
    self.__casesTaguees.setText(str(self.nbBombeTaguees))
  
  def initialiser(self):
    self.__ajouter_bombes()
    self.__ajouter_nombres()
    #creation de la grille de boutons		
    for i in range (self.__L):
      for j in range (self.__W):
        self.__grille.addWidget(self.__cases[i][j].get_bouton(), i, j)
    self.__grille.setHorizontalSpacing(0)
    self.__grille.setVerticalSpacing(0)           

  # incrementer les voisins
  def __incrementer_voisins(self,i,j) :
    for x in range (i-1 if i >0 else i, (i+1 if i<self.__L-1 else i)+1):
      for y in range (j-1 if j>0 else j, (j+1 if j<self.__W-1 else j)+1):  
        if not self.__cases[x][y].is_bombe(): 
          self.__cases[x][y].incrementer_valeur()
          
  #ajouter les nombres
  def __ajouter_nombres (self):
    for i in range(self.__L):
      for j in range(self.__W):         
        if self.__cases[i][j].is_bombe():
          self.__incrementer_voisins(i, j)

  # placement des bombes
  def __ajouter_bombes(self): 
    cases_bombes = random.sample(range(self.__L*self.__W), self.__B)
    for c in cases_bombes : 
      self.__cases[int(c/self.__W)][c%self.__W].set_bombe()
      #print (int(c/self.__W), c%self.__W)

  def __decouvrir_voisins(self, x, y) :
    for i in range (x-1 if x >0 else x, (x+1 if x<self.__L-1 else x)+1):
      for j in range (y-1 if y>0 else y, (y+1 if y<self.__W-1 else y)+1):    
        if (x!=i or y!=j) and not self.__cases[i][j].is_visible() :
          self.__cases[i][j].afficher()
          self.nbCasesVisibles += 1
          if self.__cases[i][j].is_vide() :
            self.__decouvrir_voisins(i, j)


  def is_gameover(self):
    return self.__fin_du_jeu    
  def getFenetreGameOver(self):
      self.__msgGameOver.show()


  def is_winner(self):
    if self.nbCasesVisibles == self.__L*self.__W - self.__B:
      self.partieGagnee = True
      return True 
  def getFenetreWinner(self):
      self.__msgWinner.show()

        

  def tour(self, x, y):
    case = self.__cases[x][y]
    case.afficher()    
    if case.is_bombe():
      self.__fin_du_jeu = True    
      for ii in range(self.__L):
        for jj in range (self.__W):
          self.__cases[ii][jj].afficher()
      
    elif case.is_vide() :
      self.__decouvrir_voisins(x,y)
    
    elif self.is_winner():
        for ii in range(self.__L):
            for jj in range (self.__W):
                self.__cases[ii][jj].afficher()
  
  def getNbCasesVisibles (self):
    return self.nbCasesVisibles
  

################################
######## Classe Demineur ########
################################
class Demineur:
  def __init__(self, nb_lignes, nb_colonnes, nb_bombes):
    self.__L=nb_lignes
    self.__W=nb_colonnes
    self.__B=nb_bombes    
    self.__TecouleFormate= ""
    self.__grille = Grille(nb_lignes, nb_colonnes, nb_bombes)
    self.__fenetre = QWidget() 
    self.__fenetre.setWindowTitle("Demineur")    
    self.__divers = QWidget()
    #self__divers.setObjectName("bordure") #donner un nom à l'objet et ainsi controller que l'objet et non pas ce qui contient
    #self__divers.setStyleSheet('QWidget#bordure {border: 1px solid red;}')
    self.__divers.setFixedSize(400,165)
    
    self.__diversLayout = QGridLayout() # layout pour organiser les widgets (boutons...) dans le widget divers
    self.__diversLayout.setHorizontalSpacing(0)
    self.__position = QHBoxLayout()
    self.__position.addLayout(self.__diversLayout)
    
    
    
    self.__BDD = BDD(self, self.__L,self.__W, self.__B)

    
    # Label du nombre de bombes
    self.__NbBombes=QLabel(" Nombre de bombes :   %s" %nb_bombes)
    self.__NbBombes.setFixedSize(200,30)
    self.__NbBombes.setStyleSheet('background-color: green; font-size: 15px ')
    

    # Label du nombre de bombes taguées
    self.__NbBombesTaguees=QLabel(" Bombes taguées :")
    self.__NbBombesTaguees.setFixedSize(110,30)
    self.__NbBombesTaguees.setStyleSheet('background-color: red')
    

    # Création des actions du menu déroulant
    self.__recommencerDebutant=QAction("Débutant")
    self.__recommencerDebutant.triggered.connect(self.__recommencerPartieDebutant)

    self.__recommencerIntermediaire=QAction("Intermédiaire")
    self.__recommencerIntermediaire.triggered.connect(self.__recommencerPartieIntermediaire)

    self.__recommencerExpert=QAction("Expert")
    self.__recommencerExpert.triggered.connect(self.__recommencerPartieExpert)

    #création de la barre de menu
    self.__barreMenu = QMenuBar() 
    self.__barreMenu.setFixedSize(390,30)
    self.__barreMenu.setStyleSheet(' font-size: 18px') 
    self.__recommencerBarreMenu = self.__barreMenu.addMenu("                              Niveau                             ") # ajout de l'entrée (self.__recommencerBarreMenu)
    self.__recommencerBarreMenu.addAction(self.__recommencerDebutant)
    self.__recommencerBarreMenu.addAction(self.__recommencerIntermediaire)
    self.__recommencerBarreMenu.addAction(self.__recommencerExpert)
    
    
    # Label du chrono
    self.__labelChrono = QTextEdit("00:00")
    self.__labelChrono.setStyleSheet(' background-color: white; font-size: 15px ')
    self.__labelChrono.setFixedSize(189,30)
    self.__labelChrono.setFixedHeight(30)
    self.__labelChrono.setReadOnly(True)  
    self.__labelChrono.setAlignment(Qt.AlignCenter)  
      


    # Champs de saisie du nom du joueur
    self.labelNomJoueur = QLineEdit()
    self.labelNomJoueur.setFixedSize(279,30)
    self.labelNomJoueur.setText(self.__BDD.getJouerActuel())
    self.__labelJoueur = QLabel(" Joueur :")
    self.__labelJoueur.setStyleSheet('QLabel {background-color: white ; font-size: 20px; color : black}')
    self.__labelJoueur.setFixedSize(110,30)
    

    # Bouton Commencer
    self.boutonCommencer = QPushButton("Commencer")
    self.boutonCommencer.setStyleSheet('background-color : yellow ; color: blue; font-size: 20px; border-color : red; border-style: outset ; border-width: 5px')
    self.boutonCommencer.setFixedSize(390,30)
    
    #self.boutonCommencer.clicked.connect(self.getNomJoueur)
    self.boutonCommencer.clicked.connect(self.getDebutJeu)
    self.boutonCommencer.clicked.connect(self.Timer)
    #self.boutonCommencer.clicked.connect(self.__BDD.setBddInfo)

    #bouton meilleur score:
    self.__score = QPushButton("Meilleur score")
    self.__score.setFixedSize(190,30)
    self.__score.setStyleSheet('background-color : blue ; font-size: 18px')
    self.__score.clicked.connect(self.afficherMeilleurScore)


  
    self.__diversLayout.addWidget(self.__NbBombes,0,0,1,2)
    self.__diversLayout.addWidget(self.__labelChrono,0,2,1,1)
    self.__diversLayout.addWidget(self.__NbBombesTaguees,1,0,1,1)
    self.__diversLayout.addWidget(self.__grille.getCaseTaguesCompteurWidget(),1,1)
    self.__diversLayout.addWidget(self.__score,1,2,1,1)
    self.__diversLayout.addWidget(self.__labelJoueur,2,0)
    self.__diversLayout.addWidget(self.labelNomJoueur,2,1,1,2)
    self.__diversLayout.addWidget(self.__barreMenu,3,0,1,3)
    self.__diversLayout.addWidget(self.boutonCommencer,4,0,1,3)

    








    # Insertion des widgets dans la fenetre principale
    #self__divers.setLayout(self.__diversLayout)
    #self__divers.setLayout(self.__layoutBombesTagueesChrono)
    self.__divers.setLayout(self.__position)   
    self.__layout = QGridLayout()   # layout principale où mettre le layout Grille, et layout informationn diverses
    
    
    self.__layout.addWidget(self.__divers) 
    self.__layout.addWidget(self.__grille.getWidget())    
    self.__fenetre.setLayout(self.__layout)


    
    self.__fenetre.show()
    self.center()
    

  
  def center(self):
    
      resolutionFenetre = self.__fenetre.frameGeometry()
      pointCentre = QDesktopWidget().availableGeometry().center()
      resolutionFenetre.moveCenter(pointCentre)
      self.__fenetre.move(resolutionFenetre.topLeft())


  
  def __recommencerPartieDebutant(self):
      self.__init__(8 ,8,10)
      #self.labelNomJoueur.setText(self.__BDD.getJouerActuel())
      
  
  def __recommencerPartieIntermediaire(self):
      self.__init__(16 ,16,40)
      #self.labelNomJoueur.setText(self.__BDD.getJouerActuel())
      
  
  def __recommencerPartieExpert(self):
      self.__init__(16 ,32,99)
      #self.labelNomJoueur.setText(self.__BDD.getJouerActuel())


  def Timer (self):
    
    self.timer = QTimer(self.__fenetre)
    self.__tDebut=QTime.currentTime()
    self.timer.timeout.connect(self.chronometre)
    self.timer.start(1000)
    

  def chronometre(self):
    #if self.__grille.is_gameover() == False and self.__grille.partieGagnee == False:
    currentTime = QTime.currentTime()
    tDebutEnSecondes= self.__tDebut.minute()*60 + self.__tDebut.second()
    tinstantT_EnSeconde=currentTime.minute()*60 + currentTime.second()
    Tecoule = tinstantT_EnSeconde-tDebutEnSecondes
    self.TecouleSeconde = Tecoule
    print (self.TecouleSeconde)
    minutes,secondes = divmod(Tecoule,60)
    self.__TecouleFormate = "           %02d:%02d"%(minutes,secondes)       
    self.__labelChrono.setText(self.__TecouleFormate)
    if self.__grille.is_gameover() == True or self.__grille.partieGagnee == True:
      self.timer.stop()
      self.updateBDD()
            

  
  def getDebutJeu(self):
    self.__grille.debutJeu = True
    return self.__grille.debutJeu

  def getChrono(self):
    return int(self.TecouleSeconde)


  def updateBDD (self):
    self.__BDD.setBddInfo()


  def getnbCasesVisibles(self):
    return self.__grille.getNbCasesVisibles()


  def getMeilleurScore (self):
    self.msgMeillerScore = QPushButton()
    self.msgMeillerScore.setWindowTitle ("Meilleur score")
    self.msgMeillerScore.setFixedSize (450,130)
    self.msgMeillerScore.setStyleSheet('QPushButton {background-color: yellow; font-size: 23px; color : black}')    
    self.msgMeillerScore.setText(self.__BDD.getMeilleurScore())
    
  
  def afficherMeilleurScore(self):
    self.getMeilleurScore()    
    self.msgMeillerScore.show()
    self.msgMeillerScore.setDisabled(True)
    #self.getMeilleurScore.center()


class BDD:
  def __init__(self, Demineur, nb_lignes, nb_colonnes, nb_bombes):
    self.__L=nb_lignes
    self.__W=nb_colonnes
    self.__B=nb_bombes
    self.__Demineur = Demineur
    self.joueurActuel = ""
    self.connection= sqlite3.connect("BddJoueurs.db")
    self.curseur=self.connection.cursor()
    

  def getNiveau(self):
    if self.__B == 10:
      return "Débutant"
    elif self.__B == 40:
      return "Intermédiaire"
    else:
      return "Expert"

    
  def setBddInfo (self):
    
    joueur = self.__Demineur.labelNomJoueur.text()
    niveau = self.getNiveau()
    chrono=self.__Demineur.getChrono()
    nbCasesVisibles=self.__Demineur.getnbCasesVisibles()
    requette = "insert into Joueurs (Joueur, Niveau, Chrono, CasesVisibles) values (?,?,?,?)"
    self.curseur.execute(requette,(joueur,niveau, chrono, nbCasesVisibles))
    self.connection.commit() #permet d'envoyer la requette __ ne sert que pour l'écriture (et pas pour y lire)
    #self.connection.close()

  
  def getJouerActuel(self):
    requette = "SELECT Joueur from Joueurs ORDER BY id DESC LIMIT 1"
    joueur = self.curseur.execute(requette)
    for j in joueur:
      self.joueurActuel = j[0]
    
    return self.joueurActuel


  def getMeilleurScore (self):
    a=[]
    req = "SELECT Joueur, Niveau,Chrono , MAX(CasesVisibles) from Joueurs WHERE Chrono = (SELECT Min(Chrono) from Joueurs) "
    resultat = self.curseur.execute(req)

    for i in resultat:
      joueur= i[0]
      niveau=i[1]
      chrono=i[2]
      nb=i[3]
      print ("j= ",joueur ,"n= ",niveau ,"c= ", chrono,"nb= ", nb)
      
    text = " Joueur : %s \n Niveau : %s \n Chrono : %s secondes \n Cases visibles : %d " % (joueur, niveau, chrono, nb)
    return text 
    

      
################################
############  Main #############
################################
app = QApplication(sys.argv)
demineur= Demineur (14,14, 5)
app.exec_()