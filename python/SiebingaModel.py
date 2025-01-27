"""
based on the model in https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4938879/
"""
from functools import cache

import PBPKModel
import XCATPhantom

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

class SiebingaModel(PBPKModel.PBPKModel):
    '''
    initialize the parameters, as in Table 2  of 
    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10431047/pdf/PSP4-12-1060.pdf
    '''
        
    def __init__(self, subject: XCATPhantom, name="SiebingaModel"):
        params = PBPKModel.PBPKModelParams(
            initial_activity_blood=3000,  # MBq
            k10=0.288,  # 1/hr
            k12=0.0238,  # 1/hr
            k21=0.0307,  # 1/hr
            k13=0.0086,  # 1/hr
            k31=0.0141,  # 1/hr
            k14=0.0238,  # 1/hr
            k41=0.0283,  # 1/hr
            k15=0.000248,  # 1/hr
            k51=0.00902,  # 1/hr
            k16=1.05,  # 1/hr
            k61=0.744,  # 1/hr
            V1=10.3,  # L (apparently only applied to the tumor?)
            Bmax_salivary=40.4,  # MBq
            Bmax_kidney=1e7,  # MBq, assumed
            Bmax_liver=1e7,  # MBq, assumed
            Bmax_tumor=1e7,  # MBq, assumed
            Bmax_rest=1e7  # MBq, assumed
        )

        # loosely based of volumes from XCAT log file
        compartments = PBPKModel.PBPKModelCompartments(
            blood=10.3,  # L
            salivary=0.094,  # L
            kidney=0.326,  # L
            liver=1.764,  # L
            tumor=0.00214,  # L
            rest=60  # L
        )

        super().__init__(params, compartments, name)
        self.scale_params("female")



    def update_compartments(self, subject: XCATPhantom):
        self.compartments['lung'] = self.subject.organ_volumes['rlung'] + self.subject.organ_volumes['llung']
        self.compartments['liver'] = self.subject.organ_volumes['liver']
        self.compartments['brain'] = self.subject.organ_volumes['brain']
        self.compartments['kidney'] = self.subject.organ_volumes['rightkidney'] + self.subject.organ_volumes['leftkidney']
        self.compartments['salivary'] = self.subject.organ_volumes['salivaryglands']

        self.scale_params(subject.sex)
        
    def scale_params(self, sex):
        scaling = {'male_liver': 1.2303, 'male_kidney': 0.202,
               'female_liver': 0.9953, 'female_kidney': 0.154,
               'male_salivary_gland': .04166 * 2, 'female_salivary_gland': .03324 * 2}  # units are L

        scale_liver = scaling[f'{self.subject.sex}_liver'] / self.compartments['liver']
        scale_kidney = scaling[f'{self.subject.sex}_kidney'] / self.compartments['kidney']
        scale_salivary = scaling[f'{self.subject.sex}_salivary_gland'] / self.compartments['salivary']

        self.scaled_params = self.params.copy()

        self.scaled_params.k12 *= scale_salivary  # 1/hr
        self.scaled_params.k21 *= scale_salivary  # 1/hr
        self.scaled_params.k13 *= scale_liver  # 1/hr
        self.scaled_params.k31 *= scale_liver  # 1/hr
        self.scaled_params.k14 *= scale_kidney  # 1/hr
        self.scaled_params.k41 *= scale_kidney  # 1/hr

    def simulate(self, time: float, dt:float):
        f = lambda t,y: odes_siebinga(t,y,self.scaled_params)
        y0 = np.zeros(6)
        t_eval = np.range(0, time, dt)
        out = solve_ivp(f, (0,time), self.params.initial_activity_blood, method='BDF', t_eval=t_eval)
        
        return results_to_df(out)

def compartment(Ablood, Atarget, kin, kout):
    '''
     
    from: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10431047/pdf/PSP4-12-1060.pdf
    '''
    return kin*Ablood - kout*Atarget
    
def compartment_PSMA(Ablood, Atarget, kin, kout, Bmax):
    '''
     
    from: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10431047/pdf/PSP4-12-1060.pdf
    '''
    return kin*Ablood*(1-Atarget/Bmax) - kout*Atarget

def odes_siebinga(t,y,par):
    '''
    from: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10431047/pdf/PSP4-12-1060.pdf
    '''
    Ablood, Asalivary, Akidney, Aliver, Atumor, Arest = y
    rin = par.k21*Asalivary+par.k31*Akidney+par.k41*Aliver+par.k51*Atumor+par.k61*Arest
    # dblood = rin*(1-Ablood/par.Bmax_blood) - par.k10*Ablood + par.kin
    # dblood = rin - par.k10*Ablood + par.kin(t)
    dblood = rin - (par.k10+par.k21+par.k13+par.k14+par.k15+par.k16)*Ablood 
    dsalivary = compartment_PSMA(Ablood, Asalivary, par.k12, par.k21,par.Bmax_salivary)
    dkidney = compartment(Ablood, Akidney, par.k13, par.k31)
    dliver = compartment(Ablood, Aliver, par.k14, par.k41)
    dtumor = compartment(Ablood, Atumor, par.k15, par.k51)
    drest = compartment(Ablood, Arest, par.k16, par.k61)
    return np.array([dblood, dsalivary, dkidney, dliver, dtumor, drest])
    
def results_to_df(out):
    columns = ('time [hr]', 'activity blood [MBq]', 'activity salivary [MBq]', 'activity kidney [MBq]', 'activity liver [MBq]', 'activity tumor [MBq]', 'activity rest [MBq]')
    data = np.vstack((out.t, out.y)).T
    df = pd.DataFrame(data, columns=columns)
    return df