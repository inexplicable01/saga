import os
import shutil



shutil.copytree('Graphics', 'dist/sagagui/Graphics')
#     except Exception as e:
#         print(e)
# if os.path.isfile('privateServerPackage/'+entry):
shutil.copy('settings.yaml', 'dist/sagagui/settings.yaml')

# os.mkdir('dist/SagaServerDeploy/SagaAPI')
appdata = os.getenv('appdata')
# shutil.rmtree(os.path.join(appdata,'SagaServer'))