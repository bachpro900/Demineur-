import sqlite3

connection = sqlite3.connect("BddJoueurs.db") # création d'une connection à la BDD
curseur = connection.cursor() # méthode qui permet de naviguer dans la BDD via les requettes SQL
requette = "create table Joueurs (id integer primary key autoincrement, Joueur text, Niveau text, Chrono integer, CasesVisibles integer )" # création de la table SQL
#requette = "insert into Joueurs (Joueur, Niveau, Chrono, CasesVisibles) values ('trrrr', 'Débutant', '1:32', 56)"
#☺requette = "SELECT * from Joueurs WHERE Durée = '4:33'"


#requette = "SELECT Joueur from Joueurs ORDER BY id DESC LIMIT 1"
#r=curseur.execute(requette) # éxecuter la requette ____ le resultat r est de type classe Cursor

curseur.execute(requette)
connection.commit() # permet d'envoyer la requette __ ne sert que pour l'écriture (et pas pour y lire)
'''

for i in r:
    print (i[0])
    print(type(i[0]))
'''

connection.close()

