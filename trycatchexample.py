import random
import sys

def givesomething():
        if random.random()<0.5:
            return 'hello'
        else:
            return 3

blah = givesomething()
try:
    print('asdf' + givesomething())
except TypeError:
    print(sys.exc_info()[0])
    print('asdf' + str(blah))
except NameError:
    print('your programmering made a mistake')
except:
    print('I dont expect his to happen at all')