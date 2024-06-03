from datetime import datetime, timedelta
import pickle
import random
import re

SEM_PLAYER = None

TIPOPESSOA = 0
TIPOQLEARNING = 1
TIPOMINIMAX = 2
TIPORANDOM = 3

MAX = 1 << 31

COLUMNS = 7
ROWS = 6

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

    def __init__(self, jogador1, jogador2):
        self.content = []  # []Circle
        self.jogador1 = jogador1 # TipoJogador - Int
        self.jogador2 = jogador2 # TipoJogador - Int
        self.round = 0 # Int

        # Cria um tabuleiro com 42 espaços vazios
        for x in range(0, COLUMNS):
            for y in range(0, ROWS):
                self.content.append(Circle(x, y, SEM_PLAYER))

    # Cria um clone do tabuleiro 
    def copySchema(self):
        schema = Schema(self.jogador1, self.jogador2)
        schema.content = [self.content[i].copy() for i in range(42)]
        return schema

    # Copia o mesmo esquema porém inverte todas as peças de um jogador para outro
    def invertSchema(self):
        ret = self.copySchema()
        for i in range(len(self.content)):
            if self.content[i].player is not None:
                ret.content[i].player = not ret.content[i].player
        return ret
    
    # Retorna as posições do tabuleiro
    def getAt(self, x, y):
        if y * x < 0 or y >= ROWS or x >= COLUMNS:
            raise Exception("Invalid Index (getAt)")

        index = (ROWS - (y + 1)) * COLUMNS + x
        if len(self.content) > index:
            return self.content[index]
        else:
            raise Exception("Invalid Index (getAt)")

    # Configura uma posição do tabuleiro por X e Y
    def setAt(self, x, y, player):
        if y < 0 or y == ROWS or x < 0 or x == COLUMNS:
            raise Exception("Invalid Index (setAt)")

        index = (ROWS - (y + 1)) * COLUMNS + x
        if len(self.content) > index:
            self.content[index].player = player
        else:
            raise Exception("Invalid Index (setAt)")

    # Configura uma posição do tabuleiro por coluna
    def setAtCol(self, col, player):
        if col < 0 or col == COLUMNS:
            return "error"
        for y in range(ROWS):
            if self.getAt(col, y).player == SEM_PLAYER:
                self.setAt(col, y, player)
                return None
            elif y == COLUMNS - 1:
                return "error"

    # Printa o tabuleiro
    def printBoard(self):
        print("+---------------------+")
        print("|" + '\033[95m' + " 0  1  2  3  4  5  6 " + '\033[0m' + "|")
        print("+---------------------+")
        for y in range(ROWS - 1, -1, -1):
            board = ""
            for x in range(0, COLUMNS):
                circle = self.getAt(x, y)
                if circle.player == None:
                    board += " • "
                elif circle.player:
                    board += '\033[91m' + " ● " + '\033[0m'  # VERMELHO; (96 = AZUL)
                else:
                    board += '\033[93m' + " ● " + '\033[0m'  # AMARELO;
            print("|" + board + "|")
        print("+---------------------+")

    # Calcula qualidade do jogo do tabuleiro para um player
    def scored(self, player):
        ret = 0  # int

        # Horizontal
        for y in range(ROWS):
            count, spaces = 0, 0
            for x in range(COLUMNS):
                p = self.getAt(x, y).player
                if p == player:
                    count += 1
                elif p == (not player):
                    if count == 3 and spaces >= 1:
                        return MAX - 1
                    count = 0
                    spaces = 0
                else:
                    spaces += 1
            if count == 3 and spaces > 1:
                return MAX - 1
            ret += pow(2, count)

        # Vertical
        for x in range(COLUMNS):
            count, spaces = 0, 0
            for y in range(ROWS):
                p = self.getAt(x, y).player
                if p == player:
                    count += 1
                elif p == (not player):
                    if count == 3 and spaces >= 1:
                        return MAX - 1
                    count = 0
                    spaces = 0
                else:
                    spaces += 1
            if count == 3 and spaces >= 1:
                return MAX - 1
            ret += pow(2, count)


        x, y = 0, 0
        # Diagonal negativa (cima-esquerda para baixo-direita)
        while x < COLUMNS and y < ROWS:
            ix, iy = x, y
            count, spaces = 0, 0
            while ix < COLUMNS and iy >= 0:
                p = self.getAt(ix, iy).player
                if p == player:
                    count += 1
                elif p == (not player):
                    if count == 3 and spaces >= 1:
                        return MAX - 1
                    count = 0
                    spaces = 0
                else:
                    spaces += 1
                ix += 1
                iy -= 1
            if count == 3 and spaces >= 1:
                return MAX - 1
            ret += pow(2, count)
            if y == ROWS - 1:
                x += 1
                continue
            y += 1

        # Diagonal positiva (cima-direita para baixo-esquerda)
        x, y = COLUMNS - 1, 0
        while x >= 0 and y < ROWS:
            ix, iy = x, y
            count, spaces = 0, 0
            while ix >= 0 and iy >= 0:
                p = self.getAt(ix, iy).player
                if p == player:
                    count += 1
                elif p == (not player):
                    if count == 3 and spaces >= 1:
                        return MAX - 1
                    count = 0
                    spaces = 0
                else:
                    spaces += 1
                ix -= 1
                iy -= 1
            if count == 3 and spaces >= 1:
                return MAX - 1
            ret += pow(2, count)
            if y == ROWS - 1:
                x -= 1
                continue
            y += 1

        return ret

    # Valida uma vitória TODO: diagonal
    def won(self, player):
        # Verifica as posições horizontais
        for y in range(0, ROWS):
            wonRow = 0
            for x in range(0, COLUMNS):
                if self.getAt(x, y).player == player:
                    wonRow += 1
                    if wonRow >= 4:
                        return True
                else:
                    wonRow = 0
            wonRow = 0

        # Verifica as posições verticais
        for x in range(0, COLUMNS):
            wonCol = 0
            for y in range(0, ROWS):
                if self.getAt(x, y).player == player:
                    wonCol += 1
                    if wonCol >= 4:
                        return True
                else:
                    wonCol = 0
            wonCol = 0

        # Verifica as posições diagonais
        for x in range(0, COLUMNS - 3):
            for y in range(0, ROWS - 3):
                if self.getAt(x, y).player == player and self.getAt(
                        x + 1, y + 1).player == player and self.getAt(
                            x + 2, y + 2).player == player and self.getAt(
                                x + 3, y + 3).player == player:
                    return True

        return False

    # actual: profundidade atual, max: profundidade maxima, pos: posicao a ser jogada
    def minmax(self, axis, actual, maxDepth, player):
        list = []
        if actual == maxDepth:
            return (axis, self.scored(not player))
        for x in range(0, COLUMNS):
            n = self.copySchema()
            if n.setAtCol(x, player) is None:
                list.append((x, n.minmax(x, actual + 1, maxDepth, player)[1]))
        if len(list) <= 0 and actual == 0: 
            print("Empate, sem mais espaco disponiveis")
            exit(0)
        list = sorted(list, key=lambda tup: tup[1])
        #############> Liga o log do jogo <#############
        # print("\t"*actual, str(actual)+'.'+str(axis), "> max:", player, list)
        ################################################
        ret = list[6 if player else 0]
        return ret[0], ret[1] + 0.01*(sum(tup[1] for tup in list)/7)

    # Verifica a próxima linha jogável
    def nextValidRow(self, x):
        for y in range(ROWS):
            if self.getAt(x, y).player == SEM_PLAYER:
                return True

    # Verifica a proxima linha vazia jogavel
    def nextEmptyRow(self, x):
        for y in range(ROWS):
            if self.getAt(x, y).player == SEM_PLAYER:
                return y
            elif y == COLUMNS - 1:
                return -1

    # Pega o input do usuario e tranforma em coluna
    def columnInput(self):
        move = re.sub(r'[^\d-]', '', input("Escolha uma coluna (0-6): "))
        while len(move) <= 0 or int(move) >= COLUMNS or int(
                move) < 0 or not self.nextValidRow(int(move)):
            move = input(
                "Esse input não é válido ou acoluna já está ocupada. Escolha novamente (0-6): "
            )
            move = re.sub(r'[^\d-]', '', move)
        return int(move)

    # Começa o jogo
    def startGame(self):
        qTable = {}
        atual = self.jogador1
        jogador = True
        if self.jogador1 == TIPOQLEARNING or self.jogador2 == TIPOQLEARNING:
            try:
                with open(File, 'rb') as f:
                    content = f.read()
                    if len(content) > 0:
                        qTable = pickle.loads(content)
            except Exception as e:
                raise RuntimeError(f"Failed to read or decode the file: {e}") from e
        while True:
            if atual is TIPOPESSOA:
                print("\n---------- Vez do usuário ----------\n")
                move = self.columnInput()
                self.setAtCol(move, jogador)
                if self.won(jogador):
                    self.printBoard()
                    print("\n---------- Vitória do usuário ----------\n")
                    exit(0)
                    
            elif atual is TIPOMINIMAX:
                print("\n------------- Vez da IA.MinMax ------------\n")
                self.setAtCol(self.minmax(0, 0, 4, jogador)[0], jogador)
                if self.won(jogador):
                    self.printBoard()
                    print("\n------------- Vitória da IA.MinMax -------------\n")
                    exit(0)

            elif atual is TIPOQLEARNING:
                print("\n------------- Vez da IA.QLearning ------------\n")
                id, espelhada = self.getId()
                bestCol = 0
                if qTable is None:
                    bestCol = random.randint(0, 7)
                    print("null found ===============================")
                else:
                    for i in range(len(qTable[id])):
                        if qTable[id][i] > qTable[id][bestCol]:
                            bestCol = i
                    if espelhada:
                        bestCol = 6 - bestCol
                    print("encontrou ===============================")
                _ = self.setAtCol(bestCol, jogador)
                if self.won(jogador):
                    self.printBoard()
                    print("\n------------- Vitória da IA.QLearning -------------\n")
                    exit(0)

            else:
                print("\n------------- Vez da IA.Aleatória ------------\n")
                err = self.setAtCol(random.randint(0, 7), jogador)
                while err == "error": 
                    err = self.setAtCol(random.randint(0, 7), jogador)
                if self.won(jogador):
                    self.printBoard()
                    print("\n------------- Vitória da IA.Aleatória -------------\n")
                    exit(0)

            self.round += 1
            self.printBoard()
            jogador = not jogador
            atual = self.jogador1 if jogador else self.jogador2


    ###################################
    #           Q-Learning            #
    ###################################

    def trainQ(self, table, deepth, timeSecs):
        schema = Schema(TIPORANDOM, TIPORANDOM)
        alpha, upsilon = .7, .1
        counter = 0

        # Extrai a tabela do arquivo
        startAt, qTable = datetime.now(), {}
        try:
            with open(File, 'rb') as f:
                content = f.read()
                if len(content) > 0:
                    qTable = pickle.loads(content)
        except Exception as err:
            raise RuntimeError(f"Failed to read or decode the file: {err}") from err

        player = True
        while datetime.now() < startAt + timedelta(seconds=timeSecs):
            if schema.round > deepth:
                schema = Schema(schema.jogador1, schema.jogador2)
                counter += 1
                if counter%50000 == 0:
                    try:
                        buf1 = pickle.dumps(qTable)
                        print("Done!!!")
                        with open(table, 'wb') as f:
                            f.write(buf1)
                    except Exception as err:
                        raise RuntimeError(err) from err
                        
            idSchema = schema.getId()
            major = (-1, -1)
            for x in range(0, COLUMNS):
                n = schema.copySchema()
                if n.setAtCol(x, player) is not None:
                    continue
                
                score = n.scored(player)
                if score > major[1]:
                    major = (x, score)
                if qTable[id] is None:
                    qTable[id] = [0, 0, 0, 0, 0, 0, 0]
                qTable[idSchema][x] = qTable[idSchema][x] + alpha*(upsilon*score-qTable[idSchema][x])

            if schema.won(player) or schema.won(not player):
                schema = Schema(schema.jogador1, schema.jogador2)
                counter += 1
                continue
            err = schema.setAtCol(random.randint(0, 7), player) 
            while err == "error":
                err = schema.setAtCol(random.randint(0, 7), player) 
            player = not player
            schema.round += 1

        # Salva tabela no arquivo
        try:
            buf1 = pickle.dumps(qTable)
            print("Done!!!")
            with open(table, 'wb') as f:
                f.write(buf1)
        except Exception as err:
            raise RuntimeError(err) from err

    def getId(self):
        ret0, ret1 = 0, 0
        arr = [0, 0, 0, 0, 0, 0, 0]
        quick_access3 = [1, 3, 9, 27, 81, 243, 729]
        quick_access729 = [1, 729, 531441, 387420489, 282429536481, 205891132094649, 150094635296999140]

        for x in range(COLUMNS):
            for y in range(ROWS):
                n = 0
                p, err = self.getAt(x, y)
                if err:
                    raise RuntimeError(err)
                if p.player is not None:
                    n = 2
                    if not p.player:
                        n = 1
                arr[x] += quick_access3[y] * n

        for i, n in enumerate(arr):
            ret0 += quick_access729[i] * n
            ret1 += quick_access729[6 - i] * n

        if ret0 < ret1:
            return ret0, False
        return ret1, True

jogo = Schema(TIPOMINIMAX, TIPORANDOM)
jogo.printBoard()
jogo.startGame()
# jogo.setAtCol(0, JOGADOR_IA)
# jogo.scored(JOGADOR_IA)
