import os
import shutil



shutil.copytree('Graphics/FileIcons', 'dist/sagagui/Graphics/FileIcons')
shutil.copytree('Graphics/StyleSheet', 'dist/sagagui/Graphics/StyleSheet')
shutil.copytree('Graphics/UI', 'dist/sagagui/Graphics/UI')
#     except Exception as e:
#         print(e)
# if os.path.isfile('privateServerPackage/'+entry):
shutil.copy('settings.yaml', 'dist/sagagui/settings.yaml')

# os.mkdir('dist/SagaServerDeploy/SagaAPI')
appdata = os.getenv('appdata')
# shutil.rmtree(os.path.join(appdata,'SagaServer'))

#
# shutil.copytree('Graphics', 'build/sagagui/Graphics')
# #     except Exception as e:
# #         print(e)
# # if os.path.isfile('privateServerPackage/'+entry):
# shutil.copy('settings.yaml', 'build/sagagui/settings.yaml')