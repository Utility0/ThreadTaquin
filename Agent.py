from threading import Thread, Semaphore

from Messages import Messages, Master, Order, Request

from Colors import Colors

import time

from random import shuffle, choice

class Agent(Thread):
    semaphore = Semaphore(1)
    isSetup = False

    maxIdSize = 0

    gridSize = (None, None)
    grid = None
    gridObjective = None

    def randomMovement():
        ## Get a blank position
        blankPositions = []
        for x in range(Agent.gridSize[0]):
            for y in range(Agent.gridSize[1]):
                if Agent.grid[x][y] == None:
                    blankPositions.append((x,y))
        blank = choice(blankPositions)
        ## Get a random neighbor
        neighbors = []
        if blank[0] > 0:
            neighbors.append((blank[0]-1, blank[1]))
        if blank[0] < Agent.gridSize[0]-1:
            neighbors.append((blank[0]+1, blank[1]))
        if blank[1] > 0:
            neighbors.append((blank[0], blank[1]-1))
        if blank[1] < Agent.gridSize[1]-1:
            neighbors.append((blank[0], blank[1]+1))
        shuffle(neighbors)
        neighbor = neighbors[0]
        ## Swap
        if Agent.grid[neighbor[0]][neighbor[1]] != None:
            Agent.grid[neighbor[0]][neighbor[1]].position = blank
            Agent.grid[blank[0]][blank[1]] = Agent.grid[neighbor[0]][neighbor[1]]
            Agent.grid[neighbor[0]][neighbor[1]] = None


    def printGrid():
        assert Agent.isSetup, "Grid not initialized"
        print('+' + ((('-' * Agent.maxIdSize) + '+') * Agent.gridSize[0]))
        # print('+' + '-' * (Agent.gridSize[0] * (Agent.maxIdSize))+ '+' *(Agent.gridSize[0] - 1)  + '+')
        for x in range(Agent.gridSize[0]):
            print('|', end="")
            for y in range(Agent.gridSize[1]):
                if Agent.grid[x][y] == None:
                    print(" " *(Agent.maxIdSize-1)+ ".|", end="")
                else:
                    print(str(Agent.grid[x][y])+"|", end="")
            print()
            print('+' + ((('-' * Agent.maxIdSize) + '+') * Agent.gridSize[0]))

    def initGrid(gridSize):
        assert not Agent.isSetup, "Grid already initialized"
        Agent.isSetup = True
        Agent.gridSize = gridSize
        Agent.grid = [[None for y in range(gridSize[1])] for x in range(gridSize[0])]
        Agent.gridObjective = [[None for y in range(gridSize[1])] for x in range(gridSize[0])]

    messageStack = []

    def isMessage() -> bool:
        return len(Agent.messageStack) > 0
    
    def pushMessage(message: Messages) -> Messages:
        Agent.messageStack.append(message)
        return message
    
    def popMessage() -> Messages | None:
        if Agent.isMessage():
            return Agent.messageStack.pop()
        return None
    
    def peekMessage() -> Messages | None:
        if Agent.isMessage():
            return Agent.messageStack[-1]
        return None
    
    master = None
    

    def __init__(self, id, position, objective):
        assert Agent.isSetup, "Grid not initialized"
        assert Agent.grid[position[0]][position[1]] == None, "Position already occupied"
        assert Agent.gridObjective[objective[0]][objective[1]] == None, "Objective already occupied"
        assert position[0] < Agent.gridSize[0] and position[1] < Agent.gridSize[1], "Position out of bounds"
        assert objective[0] < Agent.gridSize[0] and objective[1] < Agent.gridSize[1], "Objective out of bounds"

        super().__init__()
        self.id = id
        self.position = position
        self.objective = objective
        self.isRunning = True


        if len(str(id)) > Agent.maxIdSize:
            Agent.maxIdSize = len(str(id))

        Agent.grid[position[0]][position[1]] = self
        Agent.gridObjective[objective[0]][objective[1]] = self

    def run(self):
        while self.isRunning:
            self.semaphore.acquire()
            self.update()
            self.semaphore.release()
            time.sleep(0.01)

    def update(self):
        if not Agent.isMessage():
            if self.position == self.objective:
                return
            else:
                Agent.pushMessage(Master(self, self))
                Agent.master = self
        else:
            message = Agent.peekMessage()
            if message.receiver != self:
                return
            else:
                if message.type == Messages.TYPES['MASTER']:
                    self.updateMaster()
                elif message.type == Messages.TYPES['REQUEST']:
                    self.updateRequest()
                elif message.type == Messages.TYPES['ORDER']:
                    self.updateOrder()
                else:
                    assert False, "Unknown message type"
                return

    def updateMaster(self):
        ## Is Master ##
        if self.position == self.objective:
            ## Is at objective ##
            Agent.master = None
            Agent.popMessage()
            return
        else:
            ## Doit se déplacer ##
            path = self.pathFinding(self.objective)[1]
            if Agent.grid[path[0]][path[1]] != None:
                ## Si il y a un agent demande à bouger ##
                Agent.pushMessage(Order(self, self, path))
                Agent.pushMessage(Request(self, Agent.grid[path[0]][path[1]], None, None, None))
            else:
                self.move(path)
        pass

    def updateRequest(self):
        ## Is Request ##
        Agent.popMessage()
        ## Trouver l'emplacement vide le plus proche ##
        obj = self.findClosestEmpty()
        #print('Agent', self.id, ' a ', self.position, 'trouve un emplacement vide à', obj, ' : ', Agent.grid[obj[0]][obj[1]])
        ## Envoyer l'ordre ##
        path = self.pathFinding(obj)
        while len(path) > 1:
            if Agent.grid[path[0][0]][path[0][1]] == None:
                return
            Agent.pushMessage(Order(self, Agent.grid[path[0][0]][path[0][1]], path[1]))
            path.pop(0)

        pass

    def updateOrder(self):
        #print('Agent', self.id, 'reçoit un ordre à position, self.position')
        ## Is Order ##
        message = Agent.popMessage()
        ## Se déplacer ##
        self.move(message.direction)
        pass

    def findClosestEmpty(self):
        pos = self.position;
        emptyCoords = []
        for x in range(Agent.gridSize[0]):
            for y in range(Agent.gridSize[1]):
                if Agent.grid[x][y] == None:
                    emptyCoords.append((x, y))
        ## Trier par distance de Manhattan ##
        emptyCoords.sort(key=lambda x: abs(x[0] - pos[0]) + abs(x[1] - pos[1]))
        # print(emptyCoords)
        return emptyCoords[0]

    def move(self, position):
        #print('Agent', self.id, 'se déplace de', self.position, 'à', position)
        print('Agent', self.id, 'se déplace de', self.position, 'à', position)
        if Agent.grid[position[0]][position[1]] != None:
            print('Agent', self.id, 'est bloqué par', Agent.grid[position[0]][position[1]].id)
            raise Exception('Agent', self.id, 'est bloqué par', Agent.grid[position[0]][position[1]].id)
        Agent.grid[self.position[0]][self.position[1]] = None
        self.position = position
        Agent.grid[self.position[0]][self.position[1]] = self
        Agent.printGrid()

    def pathFinding(self, objective):
        ## A* algorithm ##
        openList = []
        closedList = []
        ghf = {}
        parent = {}

        openList.append(self.position)
        ghf[self.position] = (0, 0, 0)
        parent[self.position] = None

        while len(openList) > 0:
            # On prend le noeud avec le plus petit f
            currentNode = openList[0]
            for node in openList:
                if ghf[node][2] < ghf[currentNode][2]:
                    currentNode = node

            # Si le noeud est notre objectif
            if currentNode == objective:
                path = []
                while currentNode != None:
                    path.append(currentNode)
                    currentNode = parent[currentNode]
                path.reverse()
                return path

            # On ajoute le noeud à la liste fermée
            openList.remove(currentNode)
            closedList.append(currentNode)

            # On regarde les voisins
            l = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            shuffle(l)
            for direction in l:
                neighbor = (currentNode[0] + direction[0], currentNode[1] + direction[1])
                if neighbor[0] < 0 or neighbor[1] < 0 or neighbor[0] >= Agent.gridSize[0] or neighbor[1] >= Agent.gridSize[1]:
                    continue
                if neighbor in closedList:
                    continue
                if Agent.grid[neighbor[0]][neighbor[1]] == Agent.master:
                    continue
                if Agent.grid[neighbor[0]][neighbor[1]] != None:
                    # On calcule les valeurs g, h et f
                    difficulty = Agent.gridSize[0] * Agent.gridSize[1]
                    if Agent.grid[neighbor[0]][neighbor[1]].objective == (neighbor[0], neighbor[1]):
                        difficulty += max(Agent.gridSize[0], Agent.gridSize[1])*2
                    g = ghf[currentNode][0] + difficulty
                    h = abs(neighbor[0] - objective[0]) + abs(neighbor[1] - objective[1])
                    f = g + h
                else:
                    # On calcule les valeurs g, h et f
                    g = ghf[currentNode][0] + 1
                    h = abs(neighbor[0] - objective[0]) + abs(neighbor[1] - objective[1])
                    f = g + h

                # Si le noeud est déjà dans la liste ouverte
                if neighbor in openList:
                    if ghf[neighbor][2] > f:
                        ghf[neighbor] = (g, h, f)
                        parent[neighbor] = currentNode
                else:
                    openList.append(neighbor)
                    ghf[neighbor] = (g, h, f)
                    parent[neighbor] = currentNode


    
    
    def __str__(self):
        strId = ' ' * (Agent.maxIdSize - len(str(self.id))) + str(self.id)
        if self.objective == self.position:
            return f"{Colors.OKGREEN}{strId}{Colors.ENDC}"
        else:
            return f"{Colors.FAIL}{strId}{Colors.ENDC}"

        

if __name__ == '__main__':
    maxSize = (10, 10)
    Agent.initGrid(maxSize)

    agents = []
    possiblePositions = [(i, j) for i in range(maxSize[0]) for j in range(maxSize[1])]
    possibleObjectives = [(i, j) for i in range(maxSize[0]) for j in range(maxSize[1])]
    couples = list(zip(possiblePositions, possibleObjectives))
    # shuffle(couples)
    for i in range((maxSize[0] * maxSize[1] )-1):
    # for i in range(80):
        agents.append(Agent(i, couples[i][0], couples[i][1]))
    for _ in range(1000):
        Agent.randomMovement()



    for i in agents:
        i.start()
     
    start = time.time()
    isDone = False
    while not isDone:
        for i in agents:
            if i.objective != i.position:
                isDone = False
                break
            else:
                isDone = True
                end = time.time()

    for i in agents:
        i.isRunning = False
    time.sleep(.1)
    print(end - start)
    