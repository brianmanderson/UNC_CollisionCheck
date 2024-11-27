from connect import *
import math


def make_cylinder(case, examination, couch_angle, iso, roi_names, name, color='red', radius=42, length=80):
    px, py, pz = iso
    cosCouch = math.cos(math.pi * couch_angle / 180)
    sinCouch = math.sin(math.pi * couch_angle / 180)
    if name not in roi_names:
        retval_0 = case.PatientModel.CreateRoi(Name=name, Color=color, Type="Undefined")
    else:
        case.PatientModel.RegionsOfInterest[name].DeleteRoi()
        retval_0 = case.PatientModel.CreateRoi(Name=name, Color=color, Type="Undefined")

    retval_0.CreateCylinderGeometry(Radius=radius, Axis={'x': 0, 'y': 0, 'z': 1}, Length=length,
                                    Examination=examination, Center={'x': px, 'y': py, 'z': pz},
                                    Representation="Voxels", VoxelSize=None)

    retval_0.CreateAlgebraGeometry(Examination=examination, Algorithm="Auto",
                                  ExpressionA={'Operation': "Union", 'SourceRoiNames': [name],
                                               'MarginSettings': {'Type': "Expand", 'Superior': 0,
                                                                  'Inferior': 0, 'Anterior': 5, 'Posterior': 5,
                                                                  'Right': 5, 'Left': 5}},
                                  ExpressionB={'Operation': "Union", 'SourceRoiNames': [name],
                                               'MarginSettings': {'Type': "Expand", 'Superior': 1,
                                                                  'Inferior': 1, 'Anterior': 0, 'Posterior': 0,
                                                                  'Right': 0, 'Left': 0}},
                                  ResultOperation="Subtraction",
                                  ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                        'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
    # rotate the cylinder
    transmat = {'M11': cosCouch, 'M12': 0, 'M13': sinCouch, 'M14': 1 + px - px * cosCouch - pz * sinCouch,
                'M21': 0, 'M22': 1, 'M23': 0, 'M24': 1, 'M31': -1 * sinCouch, 'M32': 0, 'M33': cosCouch,
                'M34': 1 + pz - pz * cosCouch + px * sinCouch, 'M41': 0, 'M42': 0, 'M43': 0, 'M44': 1}
    retval_0.TransformROI3D(Examination=examination, TransformationMatrix=transmat)

def make_box(case, examination, iso, roi_names, name, color='red', lr=70, sup_inf=25, ap=50):
    px, py, pz = iso
    if name not in roi_names:
        retval_0 = case.PatientModel.CreateRoi(Name=name, Color=color, Type="Undefined")
        retval_0.CreateBoxGeometry(Size={'x': lr, 'y': ap, 'z': sup_inf},
                                   Examination=examination, Center={'x': px, 'y': py, 'z': pz},
                                   Representation="Voxels", VoxelSize=None)


def run(case, beam_set, examination):
    couch_isocenters = {}
    roi_names = [i.Name for i in case.PatientModel.RegionsOfInterest]
    external_roi = [i.Name for i in case.PatientModel.RegionsOfInterest if i.Type == 'External' and
                    case.PatientModel.StructureSets[examination.Name].RoiGeometries[i.Name].HasContours()]
    for beam in beam_set.Beams:
        beam_name = beam.Name
        couch_angle = beam.CouchRotationAngle
        if couch_angle not in couch_isocenters:
            couch_isocenters[couch_angle] = []
        if hasattr(beam, 'Isocenter'):
            position = beam.Isocenter.Position
            x, y, z = position.x, position.y, position.z
            iso = (x, y, z)
            run_check = False
            if iso not in couch_isocenters[couch_angle]:
                couch_isocenters[couch_angle].append(iso)
                run_check = True
            if not run_check:
                continue
            """
            If all the beams share the same iso and couch, only have to run once
            """
            for roi_name, radius in zip(["GantryHead", "kVPanel"], [42, 51]):
                make_cylinder(case, examination, couch_angle, iso, roi_names, roi_name, color='red',
                              radius=radius, length=25)
                overlap_name = "Potential_Collision" + '_' + beam_name
                if overlap_name not in roi_names:
                    ret_val = case.PatientModel.CreateRoi(Name=overlap_name, Color='blue', Type="Undefined")
                else:
                    case.PatientModel.RegionsOfInterest[overlap_name].DeleteRoi()
                    ret_val = case.PatientModel.CreateRoi(Name=overlap_name, Color='blue', Type="Undefined")
                ret_val.CreateAlgebraGeometry(Examination=examination, Algorithm="Auto",
                                              ExpressionA={'Operation': "Union", 'SourceRoiNames': external_roi,
                                                           'MarginSettings': {'Type': "Expand", 'Superior': 5,
                                                                              'Inferior': 5, 'Anterior': 5, 'Posterior': 0,
                                                                              'Right': 5, 'Left': 5}},
                                              ExpressionB={'Operation': "Union", 'SourceRoiNames': [roi_name],
                                                           'MarginSettings': {'Type': "Expand", 'Superior': 0,
                                                                              'Inferior': 0, 'Anterior': 0, 'Posterior': 0,
                                                                              'Right': 0, 'Left': 0}},
                                              ResultOperation="Intersection",
                                              ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                                    'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
                if case.PatientModel.StructureSets[examination.Name].RoiGeometries[overlap_name].HasContours():
                    print("Potential collision!" + ' ' + overlap_name)
                else:
                    case.PatientModel.RegionsOfInterest[overlap_name].DeleteRoi()
                case.PatientModel.RegionsOfInterest[roi_name].DeleteRoi()
                """
                Why check gantry and kv-panels? If the gantry passes, so will the kv-panels
                """
                break


def main():
    case = get_current("Case")
    examination = get_current("Examination")
    beam_set = get_current("BeamSet")
    run(case, beam_set, examination)


if __name__ == '__main__':
    main()
