from abc import ABC, abstractmethod
import sys

import PBPKModel

class BiologicalSex:
    def __init__(self, sex):
        if isinstance(sex,str):
            sex = sex.lower()

            if sex[0] == 'm' or sex[0:1] == 'xy':
                self.value = True
            elif sex[0] == 'f' or sex[0:1] == 'xx':
                self.value = False
        elif isinstance(sex, int) or isinstance(sex, float) or isinstance(sex, bool):
            self.value = bool(sex)
        else:
            raise ValueError(f"{sex} cannot be implicitly converted to a BiologicalSex")
               
    def __str__(self):
        return "male" if self.value else "female"
    
    def __int__(self):
        return int(self.value)
    
    def __float__(self):
        return float(self.value)
    
    def __eq__(self, value):
        if isinstance(value, BiologicalSex):
            return self.value & value.value
        else:
            return self == BiologicalSex(value)
       
class XCATPhantom:
    def __init__(self, log_file, sex, tumor, name):
        self.name = name
        self.sex = BiologicalSex(sex)
        get_compartments_from_xcat(log_file, tumor)
    

def parse_compartments(file, tumor):
    recorder = False
    organ_volumes = PBPKModel.PBPKModelCompartments(tumor = tumor)
    for line in file: 
        if 'ORGAN VOLUMES:' in line:
            recorder = True     
            continue

        if recorder:
            if '----------------------------------------' in line:
                recorder = False
                continue
            line=line.replace(' ','').split('=')
            organ_volumes[line[0]] = float(line[-1][:-3])

    return organ_volumes

def get_compartments_from_xcat(file, tumor):
        if file is sys.stdin:
            f = sys.stdin
        else:
            f = open(file, 'r')

        return parse_compartments(f, tumor)