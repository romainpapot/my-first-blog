#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import print_function
from random import randint

###############################################################################
# Constantes globales

MINE = '*'    # Dessin d'une mine
FLAG = '!'    # Drapeau
NOFLAG = '.'  # Case cachée normale
NOTHING = ' ' # Case vide

class Cell(object):
    """
    Classe modélisant une case du champ de mines.

    """
    def __init__(self):
        """
        Initialisation des attributs.

        """
        self.mine = False  # La case contient-elle une mine ?
        self.flag = False  # Y-a t'il un drapeau posé sur cette case ?
        self.show = False  # La case est-elle visible ?
        self.value = 0     # Combien de cases adjacentes contiennent une mine ?

    def __str__(self):
        """
        Retourne un caractère symbolisant l'état de la case.

        """
        if self.show:
            return str(self.value) if self.value else NOTHING
        else:
            return FLAG if self.flag else NOFLAG

class Field(object):
    """
    Classe modélisant un champ de mines.

    """
    def __init__(self, rows, cols, n_mines):
        """
        Initialisation du champ de mines.

        rows: nombre de lignes
        cols: nombre de colonnes
        n_mines: nombre de mines

        """
        if rows < 1 or cols < 1:
            raise ValueError('rows et cols doivent être positifs')
        if n_mines > rows * cols:
            raise ValueError('trop de mines')
        self.rows = rows
        self.cols = cols
        self.n_mines = n_mines
        self.hidden = rows * cols  # nombre de cases cachées
        self.flagged = 0           # nombre de cases portant un drapeau
        self.gameover = False
        self.cells = []
        self._init_cells()         # initialisation des cases
        # remplissage aléatoire du champ de mines
        for _ in xrange(n_mines):
            idx = randint(0, rows * cols -1)
            while self.cells[idx].mine:
                idx = randint(0, rows * cols -1)
            row = idx // cols
            col = idx - row * cols
            self.cells[idx].mine = True
            self._count_mines(row, col)

    def _init_cells(self):
        """
        Initialisation des cases.
        Cette fonction pourra être surchargée si une classe fille désire
        utiliser une autre classe pour les cases. (voir interface)

        """
        self.cells = [Cell() for _ in xrange(self.rows * self.cols)]

    def _count_mines(self, row, col):
        """
        Incrémente les compteurs de mines autour de la case (row, col)
        row: numéro de ligne de la case.
        col: numéro de colonne de la case.

        """
        for r in xrange(max(row-1, 0), min(row+2, self.rows)):
            for c in xrange(max(col-1, 0), min(col+2, self.cols)):
                self.cells[r * self.cols + c].value += 1

    @property
    def won(self):
        """
        Propriété (s'utilise comme un attribut 'won' en lecture seule).
        Retourne True si la partie est gagnée, False sinon.

        """
        return self.n_mines == self.hidden

    def flag_cell(self, row, col):
        """
        Pose un drapeau sur la case à la position (row, col) et incrémente le
        compteur de drapeaux posés.
        Effectue l'inverse si un drapeau est déjà présent sur cette case.
        Ne fait rien si la case n'est pas masquée.

        row: numéro de ligne de la case.
        col: numéro de colonne de la case.

        """
        cell = self.cells[row * self.cols + col]
        if not cell.show:
            cell.flag = not cell.flag
            if cell.flag:
                self.flagged += 1
            else:
                self.flagged -= 1

    def play_cell(self, row, col):
        """
        Joue ("creuse") la case à la position (row, col).
        row: numéro de ligne de la case.
        col: numéro de colonne de la case.

        """
        cell = self.cells[row * self.cols + col]
        # si la case porte un drapeau ou si elle est déjà découverte,
        # ne rien faire
        if cell.show or cell.flag:
            return
        # si la case porte une mine, la partie est terminée.
        if cell.mine:
            self.gameover = True
        # sinon...
        else:
            # on découvre la case
            cell.show = True
            self.hidden -= 1
            # si la case est nulle, on creuse aussi son voisinage
            if cell.value == 0:
                for r in xrange(max(row-1, 0), min(row+2, self.rows)):
                    for c in xrange(max(col-1, 0), min(col+2, self.cols)):
                        self.play_cell(r, c)
            # enfin, on regarde si la partie est gagnée
            self.gameover = self.won

    def __str__(self):
        """
        Retourne une représentation du champ de mines sous forme de string,
        pour l'affichage.

        """
        str_grid = '+' + '-' * self.cols + '+'
        for idx, cell in enumerate(self.cells):
            ch_line = idx % self.cols
            if ch_line == 0:
                str_grid += '\n|'
            if self.gameover and cell.mine:
                str_grid += MINE
            else:
                str_grid += str(cell)
            if ch_line == self.cols-1:
                str_grid += '|'
        str_grid += '\n+' + '-' * self.cols + '+'
        return str_grid

class Game(object):
    """
    Classe gérant l'exécution du jeu.

    """
    def __init__(self, rows, cols, n_bombs):
        """
        Initialisation du jeu.

        """
        self.field = Field(rows, cols, n_bombs)
        self.flag = False   # mode 'creusage' ou 'drapeau'

    def run(self):
        """
        Exécution du jeu.

        """
        prompt = "[c : creuser, d : drapeau, q : quitter]\n{0} > "
        while not self.field.gameover:
            print(self.field)
            entree = raw_input(
                    prompt.format('drapeau' if self.flag else 'creuser'))
            self.parse_input(entree.strip().lower())
        print(self.field)
        if self.field.won:
            print('Gagné !')
        else:
            print('BOOM ! Perdu')

    def parse_input(self, in_str):
        """
        Traite la saisie de l'utilisateur.

        """
        if in_str == 'q':
            raise SystemExit
        if in_str == 'c':
            self.flag = False
            return
        if in_str == 'd':
            self.flag = True
            return
        try:
            row, col = [int(num) for num in in_str.split()]
            if self.flag:
                self.field.flag_cell(row, col)
            else:
                self.field.play_cell(row, col)
        except (ValueError, TypeError):
            print('Entrée invalide : 2 nombres attendus')
        except IndexError:
            print('Entrée invalide : [0 <= ligne < {0}] [0 <= colonne < {1}]\
                    '.format(self.field.rows, self.field.cols))

if __name__ == '__main__':
    g = Game(5, 5, 3)
    g.run()
