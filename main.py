import re
from datetime import datetime, timedelta

JOGADOR_PURO = True
JOGADOR_IA = False
SEM_PLAYER = None
File = "file.txt"

# Classe para cada círculo/posição do tabuleiro
class Circle:

    def __init__(self, x, y, player):
        self.X = x  # int
        self.Y = y  # int
        self.player = player  # bool -> None = vazio

    def copy(self):
        return Circle(self.X, self.Y, self.player)


# Classe do jogo inteiro
class Schema:
    COLUMNS = 7
    ROWS = 6
    MAX = 1 << 31

    def __init__(self):
        self.content = []  # []Circle

        # Cria um tabuleiro com 42 espaços vazios
        for x in range(0, self.COLUMNS):
            for y in range(0, self.ROWS):
                self.content.append(Circle(x, y, SEM_PLAYER))

    # Cria um clone do tabuleiro
    def copySchema(self):
        schema = Schema()
        schema.content = [self.content[i].copy() for i in range(42)]
        return schema

    # Retorna as posições do tabuleiro
    def getAt(self, x, y):
        if y * x < 0 or y >= self.ROWS or x >= self.COLUMNS:
            raise Exception("Invalid Index (getAt)")

        index = (self.ROWS - (y + 1)) * self.COLUMNS + x
        if len(self.content) > index:
            return self.content[index]
        else:
            raise Exception("Invalid Index (getAt)")

    # Configura uma posição do tabuleiro por X e Y
    def setAt(self, x, y, player):
        if y < 0 or y == self.ROWS or x < 0 or x == self.COLUMNS:
            raise Exception("Invalid Index (setAt)")

        index = (self.ROWS - (y + 1)) * self.COLUMNS + x
        if len(self.content) > index:
            self.content[index].player = player
        else:
            raise Exception("Invalid Index (setAt)")

    # Configura uma posição do tabuleiro por coluna
    def setAtCol(self, col, player):
        if col < 0 or col == self.COLUMNS:
            return "error"
        for y in range(self.ROWS):
            if self.getAt(col, y).player == SEM_PLAYER:
                self.setAt(col, y, player)
                return None
            elif y == self.COLUMNS - 1:
                return "error"

    # Printa o tabuleiro
    def printBoard(self):
        print("+---------------------+")
        print("|" + '\033[95m' + " 0  1  2  3  4  5  6 " + '\033[0m' + "|")
        print("+---------------------+")
        for y in range(self.ROWS - 1, -1, -1):
            board = ""
            for x in range(0, self.COLUMNS):
                circle = self.getAt(x, y)
                if circle.player == JOGADOR_IA:
                    board += '\033[91m' + " ● " + '\033[0m'  # VERMELHO; (96 = AZUL)
                elif circle.player == JOGADOR_PURO:
                    board += '\033[93m' + " ● " + '\033[0m'  # AMARELO;
                else:
                    board += " • "
            print("|" + board + "|")
        print("+---------------------+")

    # Calcula qualidade do jogo do tabuleiro para um player
    def scored(self, player):
        countOp = 0  # int
        ret, x, y = 0, 0, 0  # int

        # Horizontal
        for y in range(self.ROWS):
            count, spaces = 0, 0
            for x in range(self.COLUMNS):
                p = self.getAt(x, y).player
                if p == player:
                    count += 1
                elif p == (not player):
                    if count == 3 and spaces >= 1:
                        return self.MAX - 1
                    count = 0
                    spaces = 0
                else:
                    spaces += 1
            if count == 3 and spaces >= 1:
                return self.MAX - 1
            ret += pow(2, count)

        # Vertical
        for x in range(self.COLUMNS):
            count, spaces = 0, 0
            for y in range(self.ROWS):
                p = self.getAt(x, y).player
                if p == player:
                    count += 1
                elif p == (not player):
                    if count == 3 and spaces >= 1:
                        return self.MAX - 1
                    count = 0
                    spaces = 0
                else:
                    spaces += 1
            if count == 3 and spaces >= 1:
                return self.MAX - 1
            ret += pow(2, count)

        # Diagonal negativa (cima-esquerda para baixo-direita)
        while x < self.COLUMNS and y < self.ROWS:
            ix, iy = x, y
            count, spaces = 0, 0
            while ix < self.COLUMNS and iy >= 0:
                p = self.getAt(ix, iy).player
                if p == player:
                    count += 1
                elif p == (not player):
                    if count == 3 and spaces >= 1:
                        return self.MAX - 1
                    count = 0
                    spaces = 0
                else:
                    spaces += 1
                ix += 1
                iy -= 1
            if count == 3 and spaces >= 1:
                return self.MAX - 1
            ret += pow(2, count)
            if y == self.ROWS - 1:
                x += 1
                continue
            y += 1

        # Diagonal positiva (cima-direita para baixo-esquerda)
        x, y = self.COLUMNS - 1, 0
        while x >= 0 and y < self.ROWS:
            ix, iy = x, y
            count, spaces = 0, 0
            while ix >= 0 and iy >= 0:
                p = self.getAt(ix, iy).player
                if p == player:
                    count += 1
                elif p == (not player):
                    if count == 3 and spaces >= 1:
                        return self.MAX - 1
                    count = 0
                    spaces = 0
                else:
                    spaces += 1
                ix -= 1
                iy -= 1
            if count == 3 and spaces >= 1:
                return self.MAX - 1
            ret += pow(2, count)
            if y == self.ROWS - 1:
                x -= 1
                continue
            y += 1

        return ret

    # Valida uma vitória TODO: diagonal
    def won(self, player):
        # Verifica as posições horizontais
        for y in range(0, self.ROWS):
            wonRow = 0
            for x in range(0, self.COLUMNS):
                if self.getAt(x, y).player == player:
                    wonRow += 1
                    if wonRow >= 4:
                        return True
                else:
                    wonRow = 0
            wonRow = 0

        # Verifica as posições verticais
        for x in range(0, self.COLUMNS):
            wonCol = 0
            for y in range(0, self.ROWS):
                if self.getAt(x, y).player == player:
                    wonCol += 1
                    if wonCol >= 4:
                        return True
                else:
                    wonCol = 0
            wonCol = 0

        # Verifica as posições diagonais
        for x in range(0, self.COLUMNS - 3):
            for y in range(0, self.ROWS - 3):
                if self.getAt(x, y).player == player and self.getAt(
                        x + 1, y + 1).player == player and self.getAt(
                            x + 2, y + 2).player == player and self.getAt(
                                x + 3, y + 3).player == player:
                    return True

        return False

    # actual: profundidade atual, max: profundidade maxima, pos: posicao a ser jogada, min: booleano de min ou de max
    def minmax(self, axis, actual, maxDepth, player):
        list = []
        if actual == maxDepth:
            return (axis, self.scored(player))
        for x in range(0, self.COLUMNS):
            n = self.copySchema()
            if n.setAtCol(x, player) != "error":
                list.append((x, n.minmax(x, actual + 1, maxDepth, player)[1]))
        if len(list) <= 0:
            print("Empate, sem mais espaco disponiveis")
            exit(0)
        list = sorted(list, key=lambda tup: tup[1])
        #############> Liga o log do jogo <#############
#         print("\t"*actual, str(actual)+'.'+str(axis), "> max:", not player, list)
        ################################################
        ret = list[0 if player else 6]
        return ret[0], ret[1] + 0.01*(sum(tup[1] for tup in list)/7)

    # Verifica a próxima linha jogável
    def nextValidRow(self, x):
        for y in range(self.ROWS):
            if self.getAt(x, y).player == SEM_PLAYER:
                return True

    # Verifica a proxima linha vazia jogavel
    def nextEmptyRow(self, x):
        for y in range(self.ROWS):
            if self.getAt(x, y).player == SEM_PLAYER:
                return y
            elif y == self.COLUMNS - 1:
                return -1

    # Pega o input do usuario e tranforma em coluna
    def columnInput(self):
        move = re.sub(r'[^\d-]', '', input("Escolha uma coluna (0-6): "))
        while len(move) <= 0 or int(move) >= self.COLUMNS or int(
                move) < 0 or not self.nextValidRow(int(move)):
            move = input(
                "Esse input não é válido ou acoluna já está ocupada. Escolha novamente (0-6): "
            )
            move = re.sub(r'[^\d-]', '', move)
        return int(move)

    # Começa o jogo
    def startGame(self, startWith):
        while True:
            if not startWith:
                print("\n---------- Vez do usuário ----------\n")
                move = self.columnInput()
                self.setAtCol(move, JOGADOR_PURO)
                # print(self.scorePlayer(JOGADOR_PURO))
                if self.won(JOGADOR_PURO):
                    self.printBoard()
                    print("\n---------- Vitória do usuário ----------\n")
                    exit(0)

            else:
                print("\n------------- Vez da IA ------------\n")
                self.setAtCol(self.minmax(0, 0, 1, JOGADOR_IA)[0], JOGADOR_IA)
                if self.won(JOGADOR_IA):
                    self.printBoard()
                    print("\n------------- Vitória da IA -------------\n")
                    exit(0)

            self.printBoard()
            startWith = not startWith

	###########################
    #        Q-Learning
    ############################
    def trainQ(self, table, deepth, timeSecs):
        schema = Schema()
		alpha, upsilon = .7, .1
		counter = 0

		# Extrai a tabela do arquivo
        startAt, qTable = datetime.now(), {}
        content = open(File, "r").read()

        player = True
		while datetime.now() < datetime.now() + timedelta(seconds=10):
			idSchema = schema.getId()
			major = (-1, -1)
			for x in range(0, self.COLUMNS):
				n = schema.copySchema()
				n.setAtCol(x, player)

				score = n.scored(player)
				if score > major[1]:
					major = (x, score)
				qTable[idSchema][x] = qTable[idSchema][x] + alpha*(+upsilon*float64(score)-qTable[idSchema][x])

			if schema.won(player) or schema.won(not player):
				schema = Schema()
				counter += 1
				continue
			while  schema.setAtCol(rand.Int()%7, player) == "error" {

			}



jogo = Schema()
jogo.printBoard()
jogo.startGame(JOGADOR_IA)
