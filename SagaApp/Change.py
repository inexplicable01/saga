from Config import typeOutput,typeRequired, typeInput, colorscheme
from SagaGuiModel.SyncScenario import *
from SagaApp.FileObjects import FileTrack
from PyQt5.QtGui import *

class Change():
    def __init__(self, fileheader, filetype):
        self.fileheader = fileheader
        self.filetype = filetype
        self.reason = []

        self.nffiletrack:FileTrack = None
        self.lffiletrack:FileTrack = None
        self.wffiletrack:FileTrack = None

        self.uffiletrack:FileTrack = None
        self.newerframeexists = False
        self.md5changed = None
        self.alterinput = False

        self.inputscenariono = None
        self.reqoutscenariono = None
        self.conflict = None

    def writeStatus(self):
        if self.newerframeexists:
            if self.filetype==typeInput:
                return str(self.inputscenariono) + '  '  + input_nf_scen[self.inputscenariono]
            else:
                return str(self.reqoutscenariono) + '  '  +regoutnewframescen[self.reqoutscenariono]
        else:
            if self.filetype==typeInput:
                if self.alterinput:
                    return 'Saga currently does not support Input editing.  Please save your edited input as a working/output file.'
                else:
                    if self.inputscenariono==7:
                        status =''
                        if self.uffiletrack.lastupdated==self.wffiletrack.connection.Rev:
                            status = status + 'Current version of input file synced to upstream.'
                        else:
                            status = status + 'Current input is using ' + self.wffiletrack.connection.Rev + ' ' \
                                    'and upstream input file was last updated in ' + self.uffiletrack.lastupdated
                        if self.lffiletrack.connection.Rev!=self.wffiletrack.connection.Rev:
                            status= status + ' Your Input rev has been updated since the last commit of this container'
                        else:
                            status = status + '.  Your Input Rev has not changed since the last commit of this container.'
                        return status
                    elif self.inputscenariono==6:
                        return  input_local_scen.format(self.fileheader)
                    elif self.inputscenariono==5:
                        status = ''
                        if self.uffiletrack.lastupdated==self.wffiletrack.connection.Rev:
                            status = status + 'Current version of input file synced to upstream.'
                        else:
                            status = status + 'Current input is using ' + self.wffiletrack.connection.Rev + ' ' \
                                    'and upstream input file was last updated in ' + self.uffiletrack.lastupdated
                    else:
                        return 'Upstream is missing an output for this container.  Requires techncial assistance.'



            else:
                if self.reqoutscenariono==3:
                    if self.md5changed:
                        return self.fileheader + ' edited locally.'
                    else:
                        return self.fileheader + ' unchanged'
                elif self.reqoutscenariono==2:
                    return regoutlocalscren[self.reqoutscenariono].format(self.fileheader)
                elif self.reqoutscenariono==1:
                    return regoutlocalscren[self.reqoutscenariono]


                return str(self.reqoutscenariono) + '  '  +regoutlocalscren[self.reqoutscenariono]

    def worthNoting(self):
        # worthNoting=False
        if self.md5changed:
            return True
        return False

    def writeHTMLStatus(self):
        text = ''
        # text = text + '<span style = "color:white"> ' + change.writeStatus() + '</span>, '

        if self.md5changed:
            text = text + '<span style = "color:white"> ' + self.writeStatus() + '</span>,  '
        # for reason in self.reason:
        #     hexcolor = QColor(colorscheme[reason]).name()
        #     text = text + '<span style = "color:' + hexcolor + '"> ' + reason + '</span>, '

        return text



# if scenariono == 1:
#     c.description = REQOUT_SCENARIO1
# elif scenariono == 2:
#     c.description = REQOUT_SCENARIO2
# elif scenariono == 3:
#     # if c.wffiletrack.md5==c.nffiletrack.md5:
#     c.description = REQOUT_SCENARIO3
#     # else:
#     # c.description = 'This file header was added indeoendetly and is creating a conflict in your container.'
# elif scenariono == 4:
#     c.description = REQOUT_SCENARIO4
# elif scenariono == 5:
#     c.description = REQOUT_SCENARIO5
#     c.conflict = True
# elif scenariono == 6:
#     c.description = REQOUT_SCENARIO6
#     c.conflict = True
# elif scenariono == 7:
#     c.description = REQOUT_SCENARIO7

# else:## Need to sync lf, wf
#     if not inlf and inwf:  # check if fileheader is in the refframe,
#         # If not in frame, that means user just added a new fileheader
#         # Scenrario 1
#         c[fileheader].reason.append(LOCALFILEHEADERADDED)
#     elif inlf and not inwf:  # check if fileheader is in the refframe,
#         # If not in workingframe, that means user just removed a fileheader
#         # Scenrario 2
#         c[fileheader].reason.append(LOCALFILEHEADERREMOVED)
#     elif inlf and inwf:  # if in both frames
#         if lf.filestrack[fileheader].md5 != wf.filestrack[fileheader].md5:
#             c[fileheader].reason.append(MD5CHANGED)
#     else:
#         raise('Should not be coming to this')

# if scenariono==1111:
#     # if wf.filestrack[fileheader].md5 in upstreamcont.filemd5history[fileheader].keys():
#     #     c = self.SyncInputFiletrack(wf.filestrack[fileheader], uf.filestrack[fileheader],
#     #                                 upstreamcont, c, nf.filestrack[fileheader])
#     # else:
#     #     c.description(USERCREATEDALTEREDINPUT)
#     c.description(USERCREATEDALTEREDINPUT)
#     # print('newer frame exists, compare all 4')
# elif scenariono==14:
#     # print('WF removed the fileheader but this still exists in new rev, whats LF rev, NF rev, Conflict arise')
#     c.needdecisionfromuser = True
#     c.description = INPUT_NEWFRAME_SCENARIO14
# elif scenariono==13:
#     c.description(INPUT_NEWFRAME_SCENARIO13)
#     # print('newer frame added a fileheader but this work frame also added this fileheader too')
# elif scenariono==1100:
#     # c.needdecisionfromuser = True
#     #sync
#     c.description = INPUT_NEWFRAME_SCENARIO12
# elif scenariono==0111: # newer frame exists, but doesnt have this fileheader
#     # if wf.filestrack[fileheader].md5 in upstreamcont.historyofoutput(fileheader).keys():
#     #     c = self.SyncInputFiletrack(wf.filestrack[fileheader], uf.filestrack[fileheader],
#     #                                 upstreamcont, c)
#     # else:
#     #     c.needdecisionfromuser = True
#     #     c.description(USERCREATEDALTEREDINPUT)
#     c.description = INPUT_NEWFRAME_SCENARIO7
# elif scenariono==0110:
#     c.needdecisionfromuser = False
#     c.description(INPUT_NEWFRAME_SCENARIO6)
#     # print(INPUT_NEWFRAME_SCENARIO6)
# elif scenariono==0101:
#     c.description(INPUT_NEWFRAME_SCENARIO5)
#     # print('Input added local.  Is wf filetrack synced to Upstream?, newer frame exists, but doesnt involve this fileheader')
# else:
#     print('Currently, unsupported.  Upstream Frame somehow deleted ')

# else: ## Need to sync lf, wf, uf
#     # 8 * innf + 4 * inuf + 2 * inlf + inwf
#     scenariono = 4 * inuf + 2 * inlf + inwf
#     if scenariono==7:
#         if wf.filestrack[fileheader].md5 in upstreamcont.historyofoutput(fileheader).keys():
#             c = self.SyncInputFiletrack(wf.filestrack[fileheader], uf.filestrack[fileheader],
#                                         upstreamcont, c, newestexist=True)
#         else: # pass#compare the md5 of wf and uf
#             c.needdecisionfromuser = True
#             c.description(USERCREATEDALTEREDINPUT)
#     elif scenariono==6:
#         c.needdecisionfromuser = False #
#         c.description = INPUT_LOCALFRAME_SCENARIO6
#         print('working Frame input has been removed')
#     elif scenariono==5:
#         if wf.filestrack[fileheader].md5 in upstreamcont.historyofoutput(fileheader).keys():
#             wfuprevnum = numofRev(wf.filestrack[fileheader].lastupdated)
#             ufrevnum = numofRev(uf.filestrack[fileheader].lastupdated)
#             if wfuprevnum == ufrevnum:
#                 c.needdecisionfromuser = False
#                 c.description = INPUT_LOCALFRAME_SCENARIO5A
#             else:
#                 c.needdecisionfromuser = True
#                 c.description = INPUT_LOCALFRAME_SCENARIO5B
#         else:
#             c.needdecisionfromuser = True
#             c.description(USERCREATEDALTEREDINPUT)
#         print('Input added local.  Is wf filetrack synced to Upstream?')
#     else:
#         print('Currently unsupported.')

