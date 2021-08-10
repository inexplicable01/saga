from Config import typeOutput,typeRequired, typeInput, colorscheme
from SagaGuiModel.SyncScenario import *
from SagaApp.FileObjects import FileTrack
from SagaApp.Container import Container
from PyQt5.QtGui import *
import re

def numofRev(rev):
    m = re.search('Rev(\d+)', rev)
    if m:
        return int(m.group(1))
    else:
        return 0

class Change():
    def __init__(self, fileheader, filetype, thiscontainer:Container):
        self.fileheader = fileheader
        self.filetype = filetype
        self.reason = []

        self.nffiletrack:FileTrack = None
        self.lffiletrack:FileTrack = None
        self.wffiletrack:FileTrack = None

        self.uffiletrack:FileTrack = None
        self.upcont:Container= None

        self.newerframeexists = False
        self.md5changed = None

        self.alterinput = False
        self.missinginput = False

        self.inputscenariono = None
        self.reqoutscenariono = None

        self.wf_synced_uf = None
        self.nf_synced_uf = None
        self.wf_synced_nf = None
        # self.action = {'main':None}

        # self.needresolve = False
        self.conflict = False
        self.noteworthy = False

    def md5comparison_LF_WF_NF(self):
        if self.lffiletrack.md5 == self.wffiletrack.md5:
            if self.wffiletrack.md5 == self.nffiletrack.md5:
                self.wf_synced_nf=True
                return 'Everything is in sync'
            else:
                self.wf_synced_nf = False
                self.conflict = True
                return 'Newest version of {} has been updated.  Need to Resolve'
        else:
            if self.wffiletrack.md5 == self.nffiletrack.md5:## local frame
                self.wf_synced_nf = True
                return 'Current version of {} is identical to Updated Newest Frame. No Conflict.'
            else:
                if self.lffiletrack.md5 != self.nffiletrack.md5:
                    self.conflict = True
                    self.wf_synced_nf = False
                    return 'Newest frame of {} has been updated, while you have also update.  Need to Resolve Conflict.'
                else:
                    self.wf_synced_nf = False
                    self.conflict = True
                    return 'Newest frame of {} has not taken into account your changes.   Need to Resolve Conflict.'

    def SyncInputFiletrack(self):
        # UF Rev,WF Rev, NF Rev)
        # upstreamupdated = False
        wfuprevnum = numofRev(self.wffiletrack.connection.Rev)
        ufrevnum = numofRev(self.uffiletrack.lastupdated)
        if self.newerframeexists:
            if self.nffiletrack:
                nfuprevnum = numofRev(self.nffiletrack.connection.Rev)
                if wfuprevnum == ufrevnum:
                    self.wf_synced_uf = True
                    if wfuprevnum == nfuprevnum:  # tri1
                        return THREEINPUT_SCENA.format(self.fileheader)
                    else:  # NF is out of sync although wrking frame is in sync.
                        self.noteworthy=True
                        self.nf_synced_uf = True
                        return THREEINPUT_SCENB.format(self.fileheader)
                else:  # wfuprevnum != ufrevnum:
                    # upstreamupdated = True
                    self.wf_synced_uf = False
                    if wfuprevnum==nfuprevnum:
                        self.noteworthy=True
                        self.nf_synced_uf = False
                        self.wf_synced_nf = True
                        return THREEINPUT_SCENC.format(self.fileheader)
                        # pass  # WF and NF are at the same frame but not the same with upstream, no conflict.  Does WF want to update?
                    elif ufrevnum == nfuprevnum:# WF not eual to UF and NF same as UF means that NEwest frame is updated.   most likely newest frame has updated sync.
                        self.conflict = True
                        self.nf_synced_uf = True
                        self.wf_synced_nf = False
                        return THREEINPUT_SCEND.format(self.fileheader)
                    else:
                        self.conflict=True
                        self.nf_synced_uf = False
                        self.wf_synced_nf = False
                        return THREEINPUT_SCENE.format(self.fileheader)
            else:
                if wfuprevnum == ufrevnum:
                    self.wf_synced_uf = True
                    return 'Input working frame reference in sync with upstream frame'
                else:
                    self.wf_synced_uf = False
                    self.noteworthy= True
                    return 'Input frame not in sync with upstream frame'


    def analysisState(self):
        if self.filetype==typeInput:
            if self.alterinput:
                self.conflict = True
                self.description ='Saga currently does not support Input editing.  Please save your edited input as a working/output file.'
            else:
                if self.inputscenariono==10:
                    status =''
                    if self.uffiletrack.lastupdated==self.wffiletrack.connection.Rev:
                        status = status + 'Current version of input file synced to upstream.'
                    else:
                        self.noteworthy = True
                        status = status + 'Current input is using ' + self.wffiletrack.connection.Rev + ' ' \
                                'and upstream input file was last updated in ' + self.uffiletrack.lastupdated

                    if self.lffiletrack.connection.Rev!=self.wffiletrack.connection.Rev:
                        self.noteworthy = True
                        status= status + ' Your Input rev has been updated since the last commit of this container'
                    else:
                        status = status + 'Your Input Rev has not changed since the last commit of this container.'
                    self.description=  status
                elif self.inputscenariono==9:
                    self.noteworthy = True
                    self.description= '{} removed from working frame'.format(self.fileheader)
                elif self.inputscenariono==8:
                    status = ''
                    if self.uffiletrack.lastupdated==self.wffiletrack.connection.Rev:
                        status = status + 'Current version of input file synced to upstream.'
                    else:
                        self.noteworthy = True
                        status = status + 'Current input is using ' + self.wffiletrack.connection.Rev + ' ' \
                                'and upstream input file was last updated in ' + self.uffiletrack.lastupdated
                    self.description=  status
                elif self.inputscenariono==7:
                    self.description=  INPUT_NEWFRAME_SCENARIO7.format(self.fileheader) + self.SyncInputFiletrack()
                elif self.inputscenariono==6:
                    self.conflict = True
                    self.description=  INPUT_NEWFRAME_SCENARIO6.format(self.fileheader)
                elif self.inputscenariono==5:
                    self.conflict = True
                    self.description=  INPUT_NEWFRAME_SCENARIO5.format(self.fileheader) + self.SyncInputFiletrack()
                elif self.inputscenariono==4:
                    self.noteworthy = True
                    self.description=  INPUT_NEWFRAME_SCENARIO4.format(self.fileheader)
                elif self.inputscenariono==3:
                    self.conflict = True
                    self.description=   self.SyncInputFiletrack() + INPUT_NEWFRAME_SCENARIO3
                elif self.inputscenariono==2:
                    self.noteworthy = True
                    self.description=  INPUT_NEWFRAME_SCENARIO2.format(self.fileheader)
                elif self.inputscenariono==1:
                    self.noteworthy = True
                    self.description=  self.SyncInputFiletrack() + INPUT_NEWFRAME_SCENARIO1
                else:
                    self.description = 'Upstream is missing an output for this fileheader.  Requires techincial assistance.'

        else:
            if self.reqoutscenariono==10:
                if self.md5changed:
                    self.noteworthy = True
                    self.description=  self.fileheader + ' edited locally.'
                else:
                    self.description=  self.fileheader + ' unchanged'
            elif self.reqoutscenariono==9:
                self.noteworthy = True
                self.description=  regoutscen[self.reqoutscenariono].format(self.fileheader)
            elif self.reqoutscenariono==8:
                self.noteworthy = True
                self.description= regoutscen[self.reqoutscenariono]
            elif self.reqoutscenariono==7:#### nf, lf, wf all exist.
                self.description=  self.md5comparison_LF_WF_NF()
            elif self.reqoutscenariono==6:
                self.conflict = True
                self.description=  'Local {} has been removed but Newest Frame still exist.  Need to Resolve Conflict'
            elif self.reqoutscenariono==5:
                if self.wffiletrack.md5 == self.nffiletrack.md5:  ## local frame
                    self.description=  'This Local frame and the newest frame both added identical {} since ##RefFrameName.'
                    self.noteworthy = True
                else:
                    self.conflict = True
                    self.description=  'This Local frame and the newest frame both added fileheader {} since ##RefFrameName but with different files. Need to Resolve Conflict.'
            elif self.reqoutscenariono==4:
                self.noteworthy= True
                self.description=  'Newest Frame added fileheader {} .  Need to resolve.'
            elif self.reqoutscenariono==3:
                self.conflict = True
                self.description=  'Newest Frame deleted fileheader {}. Need to resolve.'
            elif self.reqoutscenariono==2:
                self.noteworthy = True
                self.description=  'Both this working Frame and Newest Frame deleted fileheader {}.'
            elif self.reqoutscenariono==1:
                self.noteworthy = True
                self.description=  'This Working Frame added this fileheader {}'



    def worthNoting(self):
        # worthNoting=False
        if self.conflict or self.noteworthy or self.md5changed:
            return True
        return False

    def writeHTMLStatus(self):

        color = 'white'
        if self.conflict:
            color = 'red'
        elif self.noteworthy or self.md5changed:
            color = 'Yellow'
        elif self.noteworthy:
            color = 'cyan'

        text = '<span style = "color:' +  color + '"> <b>'+self.fileheader + '</b>   :   '+ self.description + '</span> '

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

