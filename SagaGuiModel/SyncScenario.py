

THREEINPUT_SCENA = 'Input Fileheader {} Synced on this frame, newer Frame and Upstream'
THREEINPUT_SCENB = 'WorkingFrame is in Sync with Upstream but Newest frame has an older revnum. Need to Resolve'
THREEINPUT_SCENC = 'WF and NF are at the same frame but not the same with upstream. Need to Resolve'
THREEINPUT_SCEND = 'Working Frame is out of date while newest is uptodate with upstream. Need to Resolve Conflict'
THREEINPUT_SCENE = 'all 3 are not in sync, display all 3 possibility. Need to Resolve Conflict.'

INPUT_NEWFRAME_SCENARIO7 = 'Comparing WF, UF, and NF.  '

INPUT_NEWFRAME_SCENARIO6 = 'WF removed {} but newest frame still have it.  Need to resolve conflict.'
INPUT_NEWFRAME_SCENARIO5 = 'Newer frame added {} but this work frame added this seperately. Need to resolve conflict'

INPUT_NEWFRAME_SCENARIO4 = 'newer frame added fileheader {}.  Requires user attention'

INPUT_NEWFRAME_SCENARIO3 = 'Newer Frame Exists but does not have this file header. Need to Resolve Conflict'






# INPUT_NEWFRAME_SCENARIO7A = 'newer frame exists, but doesnt have this fileheader'
# INPUT_NEWFRAME_SCENARIO7B = 'New Frame Exists, but doesnt have this fileheader,' \
#                             ' but Upstream latest rev is {} and and workingframe rev is refering to {}'

INPUT_NEWFRAME_SCENARIO2 = '{} removed on this frame. Seperately Newest Frame also had this fileheader removed. No conflict.'

INPUT_NEWFRAME_SCENARIO1 = '{} added as input in this working frame'

UNSUPPORTED = 'UNSUPPORTED'
INPUT_LOCALFRAME_SCENARIO3 = 'Fileheader exists on local and working frame.  Just need to do altered file check.'
# INPUT_LOCALFRAME_SCENARIO7A = 'Fileheader Synced on workingframe and Upstream'
# INPUT_LOCALFRAME_SCENARIO7B = 'Fileheader not up to date.   Upstream latest rev is {} and and workingframe rev is refering to {}'

INPUT_LOCALFRAME_SCENARIO2 = '{} removed from working frame'

INPUT_LOCALFRAME_SCENARIO1 = 'Input File added'
# INPUT_LOCALFRAME_SCENARIO5A = 'Fileheader added and synced to upstream'
# INPUT_LOCALFRAME_SCENARIO5B = 'Fileheader added and not synced to upstream'


input_scen = {
    10: INPUT_LOCALFRAME_SCENARIO3,
    9: INPUT_LOCALFRAME_SCENARIO2,
    8: INPUT_LOCALFRAME_SCENARIO1,
    7:INPUT_NEWFRAME_SCENARIO7,
    6:INPUT_NEWFRAME_SCENARIO6,
    5:INPUT_NEWFRAME_SCENARIO5,
    4:INPUT_NEWFRAME_SCENARIO4,
    # 11:UNSUPPORTED,
    # 10:UNSUPPORTED,
    # 9:UNSUPPORTED,
    # 8:UNSUPPORTED,
    3:INPUT_NEWFRAME_SCENARIO3,
    2:INPUT_NEWFRAME_SCENARIO2,
    1:INPUT_NEWFRAME_SCENARIO1,

}
# INPUT_NEWFRAME_SCENARIO5A = 'Working Frame added this Fileheader, and Synced to Upstream, File Handle also does not exist in newest Frame.'
# INPUT_NEWFRAME_SCENARIO5B = 'Working Frame added this Fileheader, and not Synced to Upstream, File Handle also does not exist in newest Frame.'


USERCREATEDALTEREDINPUT = 'Created Altered Input'


REQOUT_NEWFRAME_SCENARIO7 = 'Need to compare the 3 md5s to figure out what the situation is'
REQOUT_NEWFRAME_SCENARIO3 = 'Newest revision deleted this fileheader, user needs to decide whether to keep this file. Conflict'
REQOUT_NEWFRAME_SCENARIO6 = 'Working frame has deleted this fileheader but newest revision still have it.  Conflict'
REQOUT_NEWFRAME_SCENARIO2 = 'Both this working frame and the newest frame deleted this same file. No conflict.'
REQOUT_NEWFRAME_SCENARIO5 = 'This file header was added independently in your working frame and newer frame, ' \
                   'need to check md5 of wf and nw. Most likely cause conflict'
REQOUT_NEWFRAME_SCENARIO1 = 'File Header added in this local container.'
REQOUT_NEWFRAME_SCENARIO4 = 'Newest Revision added this fileheader.'
REQOUT_LOCAL_SCENARIO3 = 'Exists on Ref and Local, Need to Check for MD5'
REQOUT_LOCAL_SCENARIO2 = '{} added in this local container.'
REQOUT_LOCAL_SCENARIO1 = 'Newest Revision added this fileheader.'

regoutscen = {
10:REQOUT_LOCAL_SCENARIO3,
9:REQOUT_LOCAL_SCENARIO2,
8:REQOUT_LOCAL_SCENARIO1,
    7:REQOUT_NEWFRAME_SCENARIO7,
    6:REQOUT_NEWFRAME_SCENARIO6,
    5:REQOUT_NEWFRAME_SCENARIO5,
4:REQOUT_NEWFRAME_SCENARIO4,
3:REQOUT_NEWFRAME_SCENARIO3,
2:REQOUT_NEWFRAME_SCENARIO2,
1:REQOUT_NEWFRAME_SCENARIO1,

}


