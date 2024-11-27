# Script created 3/9/2020  -JMF

#   RayStation version: 8.0.1.10

from connect import *
import math
import json
import datetime
import wpf
import os
import sys
import clr
import glob
import shutil
from System.Windows import *

# specific to UNC CH, this needs to be configureable
auxDir = r'\\vscifs1\PhysicsQAdata\BMA\CollisionChecker'

# get current case and exam
case = get_current("Case")
examination = get_current("Examination")

# get current points
poiList = case.PatientModel.StructureSets[examination.Name].PoiGeometries

# make empty lists for POIs
poiNames = []

# find QA plans for current beamset
for eachPOI in poiList:
    poiNames.append(eachPOI.OfPoi.Name)


### GUI FOR SELECTING A POI ###

class choosePOI(Window):
    ''' Runs a drop-down list gui to select POI '''

    def __init__(self, poiList, poiNames):
        wpf.LoadComponent(self, auxDir + r'\poi_gui.xaml')  # loads gui file from auxDir
        self.Topmost = True  # so window does not get lost

        self.bestPOI.ItemsSource = poiNames

    def OKPressed(self, sender, event):

        selectedPOIName = self.bestPOI.SelectedItem  # get user selected POI

        numStr = self.CouchAngle.Text  # get angle from user
        cangle = int(numStr)  # attempt to convert to int

        cosCouch = math.cos(math.pi * cangle / 180)
        sinCouch = math.sin(math.pi * cangle / 180)

        for poi in poiList:
            if poi.OfPoi.Name == selectedPOIName:
                point = poi.Point
                px = point.x
                py = point.y
                pz = point.z

                # create the cylinders
                try:
                    retval_0 = case.PatientModel.CreateRoi(Name=r"GantryHead_42cm", Color="Red", Type="Undefined")
                except:
                    case.PatientModel.RegionsOfInterest["GantryHead_42cm"].DeleteRoi()
                    retval_0 = case.PatientModel.CreateRoi(Name=r"GantryHead_42cm", Color="Red", Type="Undefined")

                retval_0.CreateCylinderGeometry(Radius=25, Axis={'x': 0, 'y': 0, 'z': 1}, Length=80,
                                                Examination=examination, Center={'x': px, 'y': py, 'z': pz},
                                                Representation="Voxels", VoxelSize=None)

                try:
                    retval_1 = case.PatientModel.CreateRoi(Name=r"kVpanel_51cm", Color="Yellow", Type="Undefined")
                except:
                    case.PatientModel.RegionsOfInterest["kVpanel_51cm"].DeleteRoi()
                    retval_1 = case.PatientModel.CreateRoi(Name=r"kVpanel_51cm", Color="Yellow", Type="Undefined")

                retval_1.CreateCylinderGeometry(Radius=27, Axis={'x': 0, 'y': 0, 'z': 1}, Length=80,
                                                Examination=examination, Center={'x': px, 'y': py, 'z': pz},
                                                Representation="Voxels", VoxelSize=None)

                # rotate the cylinder
                transmat = {'M11': cosCouch, 'M12': 0, 'M13': sinCouch, 'M14': 1 + px - px * cosCouch - pz * sinCouch,
                            'M21': 0, 'M22': 1, 'M23': 0, 'M24': 1, 'M31': -1 * sinCouch, 'M32': 0, 'M33': cosCouch,
                            'M34': 1 + pz - pz * cosCouch + px * sinCouch, 'M41': 0, 'M42': 0, 'M43': 0, 'M44': 1}
                retval_0.TransformROI3D(Examination=examination, TransformationMatrix=transmat)
                retval_1.TransformROI3D(Examination=examination, TransformationMatrix=transmat)

                break

        self.DialogResult = True

    def CancelClicked(self, sender, event):
        ''' close the window '''
        self.DialogResult = False

    ### EXPORT QA HERE ###


# if there are multiple QA plans in the beamset, allow user to select appropriate one in gui
dialog = choosePOI(poiList, poiNames)  # create dialog
dialog.ShowDialog()  # display modal dialog
