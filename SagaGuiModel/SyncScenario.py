INPUT_NEWFRAME_SCENARIO15A = 'Fileheader Synced on Latest, workingframe and Upstream'
INPUT_NEWFRAME_SCENARIO15B = 'WorkingFrame is in Sync with Upstream but Newest frame has an older revnum.  ' \
              'Committing further will likely bring newest frame in conflict.'
INPUT_NEWFRAME_SCENARIO15C = 'WF and NF are at the same frame but not the same with upstream, no conflict.  Does WF want to update?'
INPUT_NEWFRAME_SCENARIO15D = 'Working Frame is out of date while newest is uptodate with upstream'
INPUT_NEWFRAME_SCENARIO15E = 'all 3 are not in sync, display all 3 possibility'

INPUT_NEWFRAME_SCENARIO15 = 'Comparing WF, UF, and NF'

INPUT_NEWFRAME_SCENARIO14 = 'WF removed the fileheader but newest Rev stil have it.' \
             ' Conflict arise'
INPUT_NEWFRAME_SCENARIO13 = 'newer frame added a fileheader but this work frame also added this fileheader too'

INPUT_NEWFRAME_SCENARIO12 = 'newer frame added a fileheader.'

INPUT_NEWFRAME_SCENARIO7 = 'FH Scenario7,  See if WF is out of sync with upstream. Newer Frame Exists but does not have this file header'
# INPUT_NEWFRAME_SCENARIO7A = 'newer frame exists, but doesnt have this fileheader'
# INPUT_NEWFRAME_SCENARIO7B = 'New Frame Exists, but doesnt have this fileheader,' \
#                             ' but Upstream latest rev is {} and and workingframe rev is refering to {}'

INPUT_NEWFRAME_SCENARIO6 = 'working Frame input has been removed, newer frame exists, but also doesnt have this fileheader'

INPUT_NEWFRAME_SCENARIO5 = 'FH Scenario5,  See if WF is out of sync with upstream.  Local File Added should be activated.'

UNSUPPORTED = 'UNSUPPORTED'

input_nf_scen = {
    15:INPUT_NEWFRAME_SCENARIO15,
    14:INPUT_NEWFRAME_SCENARIO14,
    13:INPUT_NEWFRAME_SCENARIO13,
    12:INPUT_NEWFRAME_SCENARIO12,
    11:UNSUPPORTED,
    10:UNSUPPORTED,
    9:UNSUPPORTED,
    8:UNSUPPORTED,
    7:INPUT_NEWFRAME_SCENARIO7,
    6:INPUT_NEWFRAME_SCENARIO6,
    5:INPUT_NEWFRAME_SCENARIO5,

}
# INPUT_NEWFRAME_SCENARIO5A = 'Working Frame added this Fileheader, and Synced to Upstream, File Handle also does not exist in newest Frame.'
# INPUT_NEWFRAME_SCENARIO5B = 'Working Frame added this Fileheader, and not Synced to Upstream, File Handle also does not exist in newest Frame.'
INPUT_LOCALFRAME_SCENARIO7 = 'Fileheader exists on local and working frame.  Just need to do altered file check.'
INPUT_LOCALFRAME_SCENARIO7A = 'Fileheader Synced on workingframe and Upstream'
INPUT_LOCALFRAME_SCENARIO7B = 'Fileheader not up to date.   Upstream latest rev is {} and and workingframe rev is refering to {}'

INPUT_LOCALFRAME_SCENARIO6 = '{}} removed from working frame'

INPUT_LOCALFRAME_SCENARIO5 = 'Input File added'
INPUT_LOCALFRAME_SCENARIO5A = 'Fileheader added and synced to upstream'
INPUT_LOCALFRAME_SCENARIO5B = 'Fileheader added and not synced to upstream'

input_local_scen = {

    7:INPUT_LOCALFRAME_SCENARIO7,
    6:INPUT_LOCALFRAME_SCENARIO6,
    5:INPUT_LOCALFRAME_SCENARIO5,

}

USERCREATEDALTEREDINPUT = 'Created Altered Input'


REQOUT_NEWFRAME_SCENARIO7 = 'Need to compare the 3 md5s to figure out what the situation is'
REQOUT_NEWFRAME_SCENARIO3 = 'Newest revision deleted this fileheader, user needs to decide whether to keep this file. Conflict'
REQOUT_NEWFRAME_SCENARIO6 = 'Working frame has deleted this fileheader but newest revision still have it.  Conflict'
REQOUT_NEWFRAME_SCENARIO2 = 'Both this working frame and the newest frame deleted this same file. No conflict.'
REQOUT_NEWFRAME_SCENARIO5 = 'This file header was added independently in your working frame and newer frame, ' \
                   'need to check md5 of wf and nw. Most likely cause conflict'
REQOUT_NEWFRAME_SCENARIO1 = 'File Header added in this local container.'
REQOUT_NEWFRAME_SCENARIO4 = 'Newest Revision added this fileheader.'

regoutnewframescen = {
    7:REQOUT_NEWFRAME_SCENARIO7,
    6:REQOUT_NEWFRAME_SCENARIO6,
    5:REQOUT_NEWFRAME_SCENARIO5,
4:REQOUT_NEWFRAME_SCENARIO4,
3:REQOUT_NEWFRAME_SCENARIO3,
2:REQOUT_NEWFRAME_SCENARIO2,
1:REQOUT_NEWFRAME_SCENARIO1,

}



REQOUT_LOCAL_SCENARIO3 = 'Exists on Ref and Local, Need to Check for MD5'
REQOUT_LOCAL_SCENARIO2 = '{} added in this local container.'
REQOUT_LOCAL_SCENARIO1 = 'Newest Revision added this fileheader.'

regoutlocalscren = {
3:REQOUT_LOCAL_SCENARIO3,
2:REQOUT_LOCAL_SCENARIO2,
1:REQOUT_LOCAL_SCENARIO1,
}