
import os
import sys
from SagaGuiModel.DevConstants import waichak,userclogin,jimmy,octtester, testerlogin, novtester
# BASE = "http://fatpanda1985.pythonanywhere.com/"
# BASE = "http://10.0.0.227:9500/"
BASE = "http://127.0.0.1:5000/"
sourcecodedirfromconfig = os.path.abspath(os.path.dirname(__file__))
ServerOrFront = 'FrontEnd'
APPDATASAGAGUIDIR = 'SagaGui'

# with open('C:/Users/waich/AppData/Roaming/SagaDesktop/testing.txt', 'a+') as file:
#     file.write('\n'+sourcecodedirfromconfig+'\n\n\n')
chosenlogin = testerlogin
debugmode=False
if len(sys.argv)>1:
    if 'debug' ==sys.argv[1]:
        try:
            if sys.argv[2]=='waichak':
                chosenlogin=waichak
            elif sys.argv[2]=='userc':
                chosenlogin=userclogin
            elif sys.argv[2]=='jimmy':
                chosenlogin=jimmy
            elif sys.argv[2]=='october':
                chosenlogin=octtester
            elif sys.argv[2]=='november':
                chosenlogin=novtester
        except:
            pass

BANNEDNAMES=['EMPTY']

