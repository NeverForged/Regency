from source.regency import Regency
import pickle
import os

class rungame(object):
    def __init__(self, GameName, train=False, train_short=False, world='Birthright', dwarves=True, elves=True, goblins=True, gnolls=True, halflings=True, jupyter=True, IntDC=5, GameLength=40):
        '''
        Runner/Loader for Regency
        '''
        try:
            Season = 0
            Action = 1
            for a in os.listdir('games'):
                if GameName in a:
                    b = a.split('.')
                    c = b[0].split('_')
                    if int(c[1]) >= int(Season):
                        if int(c[2]) >= int(Action):
                            Season, Action = c[1], c[2]
            self.Game = pickle.load( open( 'games/' + GameName + '_' + str(Season) + '_' + str(Action) + '.pickle', "rb" ) )
            print('Continuing Game {} at Season {} Action {}'.format(GameName, Season, Action))
        except:
            self.Game = Regency(GameName, train, train_short, world, dwarves, elves, goblins, gnolls, halflings, jupyter, IntDC, GameLength)
            