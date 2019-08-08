from source.regency import Regency
import pickle 

class rungame(object):
    def __init__(self, GameName, train=False, train_short=False, world='Birthright', dwarves=True, elves=True, goblins=True, gnolls=True, halflings=True, jupyter=True, IntDC=5, GameLength=40):
        '''
        Runner/Loader for Regency
        '''
        try:
            self.Game = pickle.load( open( 'worlds/' + GameName + '.pickle', "rb" ) )
            print('Continuing Game')
        except:
            self.Game = Regency(GameName, train, train_short, world, dwarves, elves, goblins, gnolls, halflings, jupyter, IntDC, GameLength)
            