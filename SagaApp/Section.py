import yaml
import os
import requests
import uuid
from Config import BASE, ServerOrFront
import json

class Section:
    def __init__(self, sectionid, sectionname, description):
        self.sectionid = sectionid
        self.sectionname = sectionname
        self.description = description

    @classmethod
    def LoadSectionyaml(cls, sectionyamlfn):
        with open(sectionyamlfn, 'r') as yamlfn:
            sectionyaml = yaml.load(yamlfn, Loader=yaml.FullLoader)
        section = cls(sectionid=sectionyaml['sectionid'],
                     sectionname=sectionyaml['sectionname'],
                     description=sectionyaml['description'])
        return section

    @classmethod
    def CreateNewSection(cls, sectionname, description):
        # newsectionid = uuid.uuid4().__str__()
        # os.mkdir(os.path.join(basedir, CONTAINERFOLDER, newsectionid))
        # newsection = cls(sectionid= newsectionid,
        #                  sectionname=sectionname,
        #                  description=description)
        # newsection.saveSection()
        # return newsection
        return "function not available on front end"

    def saveSection(self,environ=ServerOrFront):
        if environ == 'FrontEnd':
            raise('Not ready for this yet')
        elif environ == 'Server':
            outyaml = open(os.path.join(basedir, CONTAINERFOLDER,self.sectionid,'sectionstate.yaml'), 'w')

        yaml.dump(self.dictify(), outyaml)
        outyaml.close()

    def dictify(self):
        dictout = {}
        keytosave = ['description', 'sectionname', 'sectionid']
        for key, value in vars(self).items():
            if key in keytosave:
                dictout[key] = value
        return dictout

    @staticmethod
    def list():
        response = requests.get(BASE + 'SECTION/List')
        sectiondict= yaml.load(response.content, Loader=yaml.FullLoader)
        return sectiondict



