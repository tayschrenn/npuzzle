import copy
import math
import time
from collections import defaultdict
import json
import time
from queue import PriorityQueue
from operator import itemgetter
import core

def heuristic2(puzzle_size, puzzle, end):
    finalScore = 0
    for x, row in enumerate(puzzle):
        for y, val in enumerate(row):
            if val != 0:
                xtarget = (val-1) // puzzle_size
                ytarget = (val-1) % puzzle_size
                finalScore += abs(xtarget - x) + abs(ytarget - y)
    return finalScore

def manhattan(puzzle_size, puzzle, end):
    finalScore = 0
    for x, row in enumerate(puzzle):
        for y, val in enumerate(row):
            if val != 0:
                xtarget = end[val][0]
                ytarget = end[val][1]
                finalScore += abs(xtarget - x) + abs(ytarget - y)
    return finalScore

def euclidian(puzzle_size, puzzle, end):
    finalScore = 0
    for x, row in enumerate(puzzle):
        for y, val in enumerate(row):
            if val != 0:
                xtarget = end[val][0]
                ytarget = end[val][1]
                finalScore += math.sqrt(math.pow(abs(xtarget - x), 2) + math.pow(abs(ytarget - y), 2))
    return finalScore

def misplaced(puzzle_size, puzzle, end):
    finalScore = 0
    for x, row in enumerate(puzzle):
        for y, val in enumerate(row):
            if val != 0:
                xtarget = end[val][0]
                ytarget = end[val][1]
                if not (xtarget == x and ytarget == y):
                    finalScore += 1
    return finalScore

def heuristicSelect(puzzle_size, puzzle, end, heuristic):
    if heuristic == "manhattan":
        return manhattan(puzzle_size, puzzle, end)
    elif heuristic == "euclidian":
        return euclidian(puzzle_size, puzzle, end)
    elif heuristic == "misplaced":
        return misplaced(puzzle_size, puzzle, end)

def getLowestFScore(puzzle_size, openSet, fScore):
    lowest = 1000
    toReturn = None
    for s_json, s in openSet.items():
        if fScore[s_json] < lowest:
            lowest = fScore[s_json]
            toReturn = s
    return toReturn

def isValid(x, y, puzzle_size):
    return (x >= 0 and x < puzzle_size
        and y >= 0 and y < puzzle_size)

def findEmptyCase(puzzle):
    for x, row in enumerate(puzzle):
        for y, case in enumerate(row):
            if case == 0:
                return (x, y)
    return None

def deepcopy(current):
    l = []
    for i in current:
        l.append(list(i))
    return l

def getNeighbors(puzzle_size, current):
    x0, y0 = findEmptyCase(current)

    tests = [
        (x0 + 1, y0),
        (x0 - 1, y0),
        (x0, y0 + 1),
        (x0, y0 - 1)
    ]

    newSets = []
    for test in tests:
        x, y = test
        if isValid(x, y, puzzle_size):
            newSet = deepcopy(current)
            newSet[x0][y0] = newSet[x][y]
            newSet[x][y] = 0
            newSets.append(newSet)

    return newSets

def p(puzzle):
    for x, row in enumerate(puzzle):
        print(row)
    print()

def reconstruct(cameFrom, current):
    total = [current]
    totalLen = 1
    while True:
        current_json = json.dumps(current)
        try:
            current = cameFrom[current_json]
        except:
            break
        total.append(current)
        totalLen += 1
    return (totalLen, reversed(total))

def solve(puzzle_size, start, end, heuristic, force):
    start_json = json.dumps(start)

    start_fScore = heuristicSelect(puzzle_size, start, end, heuristic)

    openSet = PriorityQueue()
    openSet.put((start_fScore, start_json))
    openSetLen = 1
    openSetHash = {}
    openSetHash[start_json] = start
    closedSet = {}
    closedSetLen = 0
    cameFrom = {}
    gScore = defaultdict(lambda: 9999)
    gScore[start_json] = 0
    fScore = defaultdict(lambda: 9999)
    fScore[start_json] = start_fScore

    nSelectedStates = 0
    nMaxStates = 0

    while openSet:
        score, current_json = openSet.get()
        current = openSetHash[current_json]
        del openSetHash[current_json]
        openSetLen -= 1
        nSelectedStates += 1

        nStates = openSetLen + closedSetLen
        if nStates > nMaxStates:
            nMaxStates = nStates

        if force == "0":
            if fScore[current_json] == gScore[current_json]:
                return (nSelectedStates, nMaxStates, reconstruct(cameFrom, current))
        else:
            if fScore[current_json] == 0:
                return (nSelectedStates, nMaxStates, reconstruct(cameFrom, current))

        closedSet[current_json] = current
        closedSetLen += 1

        for neighbor in getNeighbors(puzzle_size, current):
            neighbor_json = json.dumps(neighbor)
            if neighbor_json in closedSet:
                continue

            tentative_gScore = gScore[current_json] + 1
            if not neighbor_json in openSetHash:
                cameFrom[neighbor_json] = current
                gScore[neighbor_json] = tentative_gScore
                if force == "0":
                    fScore[neighbor_json] = gScore[neighbor_json] + heuristicSelect(puzzle_size, neighbor, end, heuristic)
                elif force == "1":
                    fScore[neighbor_json] = gScore[neighbor_json] * heuristicSelect(puzzle_size, neighbor, end, heuristic)
                elif force == "2":
                    fScore[neighbor_json] = heuristicSelect(puzzle_size, neighbor, end, heuristic)
                openSet.put((fScore[neighbor_json], neighbor_json))
                openSetHash[neighbor_json] = neighbor
                openSetLen += 1
            elif tentative_gScore >= gScore[neighbor_json]:
                continue

    return None
