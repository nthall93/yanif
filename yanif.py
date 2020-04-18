import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime



def _integerInput(string):
    errorString = 'Error not integer.\n'+string
    inputStr = input(string)
    while not inputStr.isdigit():
        inputStr = input(errorString)

    return int(inputStr)


class player:
    def __init__(self, name):
        self.name = name
        self.stats = {
            'Total Score': 0,
            'Go Back Count': 0,
            'Yanif Count': 0,
            'False Yanif Count': 0
        }
        
        self.isOut = False
    
    def updateScore(self,roundScore, falseYanif = False):
        self.stats['Total Score'] += roundScore
        
        if self.stats['Total Score'] > 100:
            self.isOut = True
        
        elif ((roundScore > 0) & (self.stats['Total Score'] % 25 == 0) & (self.stats['Total Score'] > 0) & (not(falseYanif))): #roundScore > 0 to ensure no infinite gobacks
            self.stats['Total Score'] -= 25
            self.stats['Go Back Count'] += 1   
    
    def neededForGoback(self):
        print('{} needs {} for go back'.format(self.name, 25 - self.stats['Total Score'] % 25))
              
    def __repr__(self):
              return '{}: {}'.format(self.name, self.stats['Total Score'])
    
    def __str__(self):
              return self.name


class game:
    def __init__(self,players = None):
        
        if players is None:
            self.players = []
            playersCount = _integerInput("Enter amount of players: ")
            for i in range(playersCount):
                playerName = input("Enter player {}'s name: ".format(i+1))
                self.players.append(player(playerName))
                     
        else:    
            self.players = players
        
        
        cols = pd.MultiIndex.from_product([[p.name for p in self.players], ['Round Score','Total Score','Go Back Count','Yanif Count','False Yanif Count']])
        self.scoreBoard = pd.DataFrame(columns = cols, index=pd.Series(dtype='int', name = 'Round'))
        self.round = 1
        self.deal = self.players[0]
        
        inputStr = input("Click 'y' if you would like to start playing: ")
        
        if inputStr == 'y':
            self.newGame()
    
    
    
    def newGame(self):
        while len(self.players) > 1:
            self.newRound()
        
        filename = datetime.now().strftime('yanif-scores-%Y-%m-%d-%H-%M.csv')
        self.scoreBoard.to_csv(filename)

            
    def newRound(self):
        print('\n\n--------ROUND {}--------\n{} to deal'.format(self.round, self.deal))
        
        calledYanif = self._yanifCall()
        [p.neededForGoback() for p in self.players if p != calledYanif]
        scores = {}
        
        for p in self.players:
            scores[p] = _integerInput("Enter {}'s Score: ".format(p))
            
        scores = pd.Series(scores)
        
        
        self._evaluateScores(scores = scores, calledYanif = calledYanif)
        lostPlayersCount = self._updatePlayers()
        self.round += 1
        self._updateDeal(lostPlayersCount = lostPlayersCount)
            

        
    def _yanifCall(self):
        while True:
            inputStr = input("Enter player that called Yanif: ")
            for p in self.players:
                if inputStr == p.name:
                    return p
            print('Player not found!')
    
    
    def _evaluateScores(self, scores, calledYanif):
                isYanif = scores[calledYanif] < scores.drop(calledYanif).min()
                
                if isYanif:
                    print('{} successfully called Yanif'.format(calledYanif))
                    calledYanif.stats['Yanif Count'] += 1
                
                else:
                    print('{} was not successful when calling Yanif'.format(calledYanif))
                    calledYanif.stats['False Yanif Count'] += 1
                    scores[calledYanif] += 25
                    calledYanif.updateScore(scores[calledYanif], falseYanif = True)
                    scores[scores == scores.min()] = 0
                    
                for p, score in scores.drop(calledYanif).iteritems():
                    p.updateScore(score)
                    
                self._updateScoreBoard(scores)
                

                    
    def _updatePlayers(self):
        lostPlayers = [p for p in self.players if p.isOut]
        for p in lostPlayers:
                print('{} is out!'.format(p))
                self.players.remove(p)
        
        return len(lostPlayers)
    
    def _updateDeal(self, lostPlayersCount):
        self.deal = self.players[(self.round-1-lostPlayersCount) % len(self.players)]
        
    def _updateScoreBoard(self, scores):
        playerStats = {p.name:p.stats for p in self.players}
        for stats, roundScore in zip(playerStats.values(), scores):
            stats['Round Score'] = roundScore
        
        newRound = pd.DataFrame(playerStats).unstack()
        newRound.name = self.round
        
        self.scoreBoard = self.scoreBoard.append(newRound)
        
        #display table and graph
        display(self.scoreBoard)
        self.plotScores()
    
    def plotScores(self):
        #set up
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        #data
        ax.plot(self.scoreBoard.loc[:,(slice(None),'Total Score')],marker = 'o')

        #x axis
        ax.set_xlim([1,self.round])
        plt.xticks(np.arange(1,self.round+1))
        plt.ylabel('Total Score')

        #y axis
        ax.set_ylim([0,min(100,self.scoreBoard.max().max())])
        plt.yticks(np.arange(0,101,25))
        plt.xlabel('Round')

        #legend and grid
        ax.legend(labels = self.scoreBoard.columns.levels[0])
        ax.grid(b=None, which='major', axis='y', ls = '--')
        plt.show()
        
            
        

