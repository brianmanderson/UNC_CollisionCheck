from connect import *
import math


def run(case, beam_set, examination):
    couch_isocenters = {}
    for beam in beam_set.Beams:
        couch_angle = beam.CouchRotationAngle
        if couch_angle not in couch_isocenters:
            couch_isocenters[couch_angle] = []
        if hasattr(beam, 'Isocenter'):
            position = beam.Isocenter.Position
            x, y, z = position.x, position.y, position.z
            iso = (x, y, z)
            if iso not in couch_isocenters[couch_angle]:
                couch_isocenters[couch_angle].append(iso)
    print(couch_isocenters)
    poiList = case.PatientModel.StructureSets[examination.Name].PoiGeometries


if __name__ == '__main__':
    case = get_current("Case")
    examination = get_current("Examination")
    beam_set = get_current("BeamSet")
    run(case, beam_set, examination)