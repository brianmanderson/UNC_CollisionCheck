from connect import *
import math


def make_cylinder(case, examination, couch_angle, iso, name, color='red', radius=42, length=80):
    px, py, pz = iso
    cosCouch = math.cos(math.pi * couch_angle / 180)
    sinCouch = math.sin(math.pi * couch_angle / 180)
    try:
        retval_0 = case.PatientModel.CreateRoi(Name=name, Color=color, Type="Undefined")
    except:
        case.PatientModel.RegionsOfInterest[name].DeleteRoi()
        retval_0 = case.PatientModel.CreateRoi(Name=name, Color=color, Type="Undefined")

    retval_0.CreateCylinderGeometry(Radius=radius, Axis={'x': 0, 'y': 0, 'z': 1}, Length=length,
                                    Examination=examination, Center={'x': px, 'y': py, 'z': pz},
                                    Representation="Voxels", VoxelSize=None)

    # rotate the cylinder
    transmat = {'M11': cosCouch, 'M12': 0, 'M13': sinCouch, 'M14': 1 + px - px * cosCouch - pz * sinCouch,
                'M21': 0, 'M22': 1, 'M23': 0, 'M24': 1, 'M31': -1 * sinCouch, 'M32': 0, 'M33': cosCouch,
                'M34': 1 + pz - pz * cosCouch + px * sinCouch, 'M41': 0, 'M42': 0, 'M43': 0, 'M44': 1}
    retval_0.TransformROI3D(Examination=examination, TransformationMatrix=transmat)


def run(case, beam_set, examination):
    couch_isocenters = {}
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
            make_cylinder(case, examination, couch_angle, iso, "GantryHead_42cm", color='red', radius=42,
                          length=80)
            overlap_name = beam_name + '_' + 'GantryHead'
            try:
                retval_0 = case.PatientModel.CreateRoi(Name=overlap_name, Color='blue', Type="Undefined")
            except:
                case.PatientModel.RegionsOfInterest[overlap_name].DeleteRoi()
                retval_0 = case.PatientModel.CreateRoi(Name=overlap_name, Color='blue', Type="Undefined")

            make_cylinder(case, examination, couch_angle, iso, "kVpanel_51cm", color='yellow', radius=51,
                          length=80)


    poiList = case.PatientModel.StructureSets[examination.Name].PoiGeometries


def main():
    case = get_current("Case")
    examination = get_current("Examination")
    beam_set = get_current("BeamSet")
    run(case, beam_set, examination)


if __name__ == '__main__':
    main()
