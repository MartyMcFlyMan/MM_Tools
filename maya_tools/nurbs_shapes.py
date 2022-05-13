import maya.mel as mel


def four_side_cross():
    mel.eval("curve -d 1 -p -1 0 -1 -p -1 0 -3 -p 1 0 -3 "
             "-p 1 0 -1 -p 3 0 -1 -p 3 0 1 -p 1 0 1 -p 1 "
             "0 3 -p -1 0 3 -p -1 0 1 -p -3 0 1 -p -3 0 -1"
             " -p -1 0 -1 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 "
             "-k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 ;")
    mel.eval("select -d ;")


def arrow():
    mel.eval("curve -d 1 -p 1 0 4 -p -1 0 4 -p -1 0 0 -p -2 0 0 "
             "-p 0 0 -3 -p 2 0 0 -p 1 0 0 -p 1 0 4 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 ;")
    mel.eval("select -d ;")


def segmented_circle():
    mel.eval("circle -c 0 0 0 -nr 0 1 0 -sw 360 -r 5 -d 1 -ut 0 -tol 0 -s 45 -ch 1; objectMoveCommand;")
    mel.eval("select -r nurbsCircle1.cv[11:12] ;")
    mel.eval("select -tgl nurbsCircle1.cv[6:7] ;")
    mel.eval("select -tgl nurbsCircle1.cv[1:2] ;")
    mel.eval("select -tgl nurbsCircle1.cv[41:42] ;")
    mel.eval("select -tgl nurbsCircle1.cv[36:37] ;")
    mel.eval("select -tgl nurbsCircle1.cv[31:32] ;")
    mel.eval("select -tgl nurbsCircle1.cv[26:27] ;")
    mel.eval("select -tgl nurbsCircle1.cv[21:22] ;")
    mel.eval("select -tgl nurbsCircle1.cv[16:17] ;")
    mel.eval("scale -cs -ls -r 1 1.829562 1 ;")
    mel.eval("move -r -os -wd 0 0.583789 0 ;")
    mel.eval("select -d ;")

