import os, shlex, csv, sys, datetime, subprocess, re, operator
from distutils import dir_util
from functools import reduce

'''
WEPPpy v0.1 - Initial
This script allow for 'pseudo binding' to the WEPP program through its command line interface 
    and necessary WEPP input files for watershed and hillslope simulations
    
    
Class objects are described for:
    Hill
    Channel
    Watershed
    Run
    SoilHorizon
    SoilDB
    PlantDB
    InitialDB
    Management
    Path
    
Functions include:
    readSoil
    writeSoil
    readOFEs
    makeHillRunFile
    makeWSRunFile
    readPRW
    runWEPP
    
Author: Dylan S. Quinn - quinnd@uidaho.edu - dylansquinn@gmail.com
'''
'''
read databases
    ofe assignments h,m,l,u for all ofes
    plant and initial db
    soils
    
'''

'''Custom classes for WEPP input file management'''

class Hill:
    '''Custom Hillslope object containing delineated OFEs and soil/management strings'''
    def __init__(self,hid,ofes):
        self.hid = hid
        self.ofes = ofes #[(ofe,bs),(1,4),(2,4),...]
        self.ofe_count = len(ofes)
        
    def __str__(self):
        return 'Hillslope {hid} with {ofe_count} OFEs'.format(**vars(self))


class Channel:
    def __init__(self, head, tail, direction, length, width, definition, soil, profile):
        self.head = head
        self.tail = tail
        self.direction = direction
        self.length = length
        self.width = width
        self.definition = definition
        self.soil = soil
        self.profile = profile #Slope object

'''     
head = (5610,1510)
Tail = (5690,1690)
Direction = 113.928993
Length = 213.137085
Width = 1.000000
Definition = "OnRock"
Soil = "willow\willow.sol"
Profile
'''
class Watershed:
    '''
    hills - a list of Hill objects
     '''
    def __init__(self,hills,channels):
        pass
       
       
class Slope:
    
    def __init__(self, length, width, aspect):
        self.length = length
        self.width = width
        self.aspect = aspect


class Run:
    '''
    
    '''
    def __init__(self,hills):
        self.hills = hills #list of Hill objects
        
        
        
    def __str__(self):
        return
    
     
    def makeHillRunFile(self,hid,files):
        
        files = ['soil_loss_file','water_file','plot_file','graph_file']
        
        soil_loss_file = '..\output\loss_{}.txt'.format(hid)#no bool
        
        folder = '..\\output\\'
        man = 'p{}_.man'.format(hid)
        cli = 'p{}_.cli'.format(hid)
        slp = 'p{}_.slp'.format(hid)
        sol = 'p{}_.sol'.format(hid)
        years = 5
        
        file_dic = {'water_file':'Y\n{}water_{}.txt'.format(folder,hid),'pass_file':'Y\n{}pass_{}.txt'.format(folder,hid),'init_file':'Y\n{}init_{}.txt'.format(folder,hid),'crop_file':'Y\n{}init_{}.txt'.format(folder,hid),'soil_file':'Y\n{}soil_{}.txt'.format(folder,hid),'sed_file':'Y\n{}sed_{}.txt'.format(folder,hid),'graph_file':'Y\n{}graph_{}.txt'.format(folder,hid),'event_file':'Y\n{}event_{}.txt'.format(folder,hid),'ofe_file':'Y\n{}ofe_{}.txt'.format(folder,hid),'sum_file':'Y\n{}sum_{}.txt'.format(folder,hid),'winter_file':'Y\n{}winter_{}.txt'.format(folder,hid),'plant_file':'Y\n{}plant_{}.txt'.format(folder,hid)}
        
        for k in file_dic.keys():
            if k not in files:
                file_dic[k] = 'N'
        
        default_dic = {'units':'M','overwrite':'Y','cli_type':'1','version':'1','pass_file':file_dic['pass_file'],'loss_type':'3','init_file':file_dic['init_file'],'soil_loss_file':soil_loss_file,'water_file':file_dic['water_file'],'crop_file':file_dic['crop_file'],'soil_file':file_dic['soil_file'],'sed_file':file_dic['sed_file'],'graph_file':file_dic['graph_file'],'event_file':file_dic['event_file'],'ofe_file':file_dic['ofe_file'],'sum_file':file_dic['sum_file'],'winter_file':file_dic['winter_file'],'plant_file':file_dic['plant_file'],'man':man,'cli':cli,'slp':slp,'sol':sol,'ir':'0','years':years,'bypass':'0'}
        return '{units}\n{overwrite}\n{cli_type}\n{version}\n{pass_file}\n{loss_type}\n{init_file}\n{soil_loss_file}\n{water_file}\n{crop_file}\n{soil_file}\n{sed_file}\n{graph_file}\n{event_file}\n{ofe_file}\n{sum_file}\n{winter_file}\n{plant_file}\n{man}\n{slp}\n{cli}\n{sol}\n{ir}\n{years}\n{bypass}'.format(**default_dic)

    
    '''    ./man/M{h}.man
    ./slope/H{h}.slp
    ./cli/C{h}.cli
    ./soil/S{h}.sol'''


class Path:
    '''Simple class to hold output path variables
            Instantalize with:
                workspace - path to master workspace
                file_db - database folder with generic WEPP files
                input - input WEPP file folder
                output - output WEPP file folder
                '''
    def __init__(self,workspace,file_db,input,output,exe_path):
        '''
        workspace - ws: working folder containing all related WEPP files
        file_db - fdb:  folder with generic, single OFE inputs ('.sol', '.rot', '.db',...)
        
        '''
        self.ws = workspace
        self.db = file_db
        self.foutput = output
        self.finput = input
        self.exe = exe_path
        self.slope = './input/'
        self.cli = './input/'
        self.man = './input/'
        self.soil = './input/'
        self.output = './output/'

    def fileo(self,file):
        '''Returns write path for a file to the WEPP output directory'''
        return os.path.join(self.ws,self.foutput,file)
    
    def filei(self,file):
        '''Returns write path for a file to the WEPP input directory'''
        return os.path.join(self.ws,self.finput,file)
    
    def filedb(self,file):
        '''Returns the read path for a file in the generic database directory'''
        return os.path.join(self.ws,self.db,file)
    
    def file(self,folder,file):
        '''Returns the generipc path for a read or write file from a specified directory'''
        return os.path.join(self.ws,folder,file)
    
    def all(self):
        return '\n'.join([self.ws,self.db,self.foutput,self.finput,self.exe])
    
    def __str__(self):
        return 'Path object workspace "{}"'.format(self.ws)
    
    '''
    necessary file structure:
        Master
            Database - All input files (*.sol,*.cli,*.slp....), Generic format
            Inputs - OFE formatted inputs to the WEPP model
            Output - 

'''


class Inp:
    
    def __init__(self):
        self.baseflow = '1e-9'
        self.timesetep = '600' #seconds
        self.ofes = '1'
        self.ofe = '67'
        
    
    def write(self,fout):
        fout = Path.fileo('',fout)
        with open(fout,'w') as o:
            o.write('2 {}\n{}\n{}\n'.format(self.timestep,self.baseflow,self.ofes,self.ofe))
 
        
class SoilHorizon:
    '''Stores attributes of a single soil horizon
            Initialize attributes based on horizon dictionary
            '''
    def __init__(self,h):        
        for k, v in h.items():
            setattr(self, k, v)
    
    def __str__(self):
        return 'Horizon at {} mm'.format(self.depth)


class SoilDB:
    '''Stores soil attributes and horizon objects for a single soil file
            Instantalized with:
                desc - a short description
                s - "soil" dictionary containing general soil properties
                h - "horizons" list containing dictionaries of each horizon's properties in order of horizon depth
                b - "bedrock" dictionary containing bedrock properties   
    '''
    def __init__(self,desc,s,h,b):
        self.version = 7778
        
        self.s = s
        self.h = h
        self.b = b
        
        
        #soil parameters
        self.name = s['name']
        self.version = s['version']
        self.texture = s['texture']
        self.horizons_count = s['horizons']
        self.albedo = s['albedo']
        self.sat = s['sat']
        self.kinter = s['kinter']
        self.krill = s['krill']
        self.keff = s['keff']
        self.tauc = s['tauc']
        
        self.horizons = []
        self.depth = 0
        for hi in h:
            ha = SoilHorizon(hi)
            self.horizons.append(ha)
            self.depth = ha.depth if ha.depth > self.depth else self.depth
            
        
        
        
        #bedrock parameters#
        self.bed = b['bed']
        self.bed_id = b['bed_id']
        self.bed_thickness = b['bed_thickness']
        self.bed_ksat = b['bed_ksat']
        
        
        
        
        self.desc = desc
        self.soil = self.update()
        
    
    
    def update(self):
        if self.version == '7778':
            soil_str ="'{name}'    '{texture}'    {horizons_count}    {albedo}    {sat}    {kinter:.2f}    {krill:.6f}    {tauc:.2f}    {keff:.2f}\n".format(**vars(self))
            for horizon in self.horizons:
                soil_str += "    {depth:.0f}    {bd}    {ksat}    {anis}    {fc}    {wp}    {sand}    {clay}    {om}    {cec}    {rocks}\n".format(**vars(horizon))                                       
            
            soil_str +="{bed}    {bed_id}    {bed_thickness}    {bed_ksat}\n".format(**vars(self))
            self.soil = soil_str
            return soil_str
        
        if self.version == '2006.2':
            soil_str ="'{name}'    '{texture}'    {horizons_count}    {albedo}    {sat}    {kinter:.2f}    {krill:.6f}    {tauc:.2f}    {keff:.2f}\n".format(**vars(self))
            for horizon in self.horizons:
                soil_str += "    {depth:.0f}    {sand}    {clay}    {om}    {cec}    {rocks}\n".format(**vars(horizon))                                       
            
            soil_str +="{bed}    {bed_id}    {bed_thickness}    {bed_ksat}\n".format(**vars(self))
            self.soil = soil_str
            return soil_str
        
    def __str__(self):
        return self.update()


class PlantDB:
    '''
    Stores plant attributes from the WEPP plant database file
    '''
    def __init__(self,r):
        for k, v in r.items():
            setattr(self, k, v)

        
        self.plant = self.update()
 
        
    
    def update(self):
        plant_str = ("test_{id:0>3}\n" #internal ID
                "{desc}\n" #description
                "{datasource}\n"
                "{comment}\n"
                "{lu:.0f}    #landuse\n{h_units}\n"
                "{canopy_cover} {canopy_param} {e_ratio} {temp} {resid_par} {gdd_em} {grazing_bio} {p_cut} {pct_canopy_sen} {p_diameter}\n"
                "{pct_to_max_lai} {pct_biomass_sen} {rad_coeff} {resid_adj} {dw_frict_fact} {gdd_season} {harvest} {canopy_max}\n"
                "{mfo_value:.0f}\n"
                "{decomp_above} {decomp_below} {temp_opt} {drought_tol} {p_space} {root_depth_max} {root_shoot} {root_mass_max} {sen_length} {temp_max_crit}\n"
                "{temp_min_crit} {lai_max} {yield_opt}").format(**vars(self))
                
        return plant_str


class InitialDB:
    '''
    Initial database for WEPP '.man' file use
    '''
    def __init__(self,r):
        for k, v in r.items():
            setattr(self, k, v)
        
        self.initial = self.update()
        
    def update(self):
        initial_str = ("test_{id:0>3}\n" #internal ID
                "{desc}\n" #description
                "{datasource}\n"
                "{comment}\n"
                "{lu:.0f}\n"
                "{bd} {cc_init} {days_harv} {days_till} {frost_init} {ir_cover_init}\n"
                ""#referenced plant - internal plant
                "{mgmt:.0f}\n"
                "{rain_till} {ridge_init} {r_cover_init} {rough_init} {rill_space}\n"
                "{r_type:.0f}  # rtyp - temporary\n"
                "{snow_d} {thaw_d} {sec_till_d} {pri_till_d} {ir_width}\n"
                "{root_init} {res_sub}").format(**vars(self))
        
        return initial_str

        
class Management:
    def __init__(self):
        
        pass
    
    def populate(self,r):
        ()




    

class Climate:
    def __init__(self,fin):
        self.file = ''
        with open(fin,'r') as c:
            for line in c.readlines():
                self.file += line
        
        self.name = fin.split('\\')[-1]
    
    def duplicate(self,dir,hid,pref_out='p'):
        '''Writes a duplicate climate file in the specified directory for 
            each hill id in the hid list'''
        cprint('Duplicating climate files for {} hillslope(s)'.format(len(hid)),True)
        for h in hid:
            with open(Path.file(dir,'{}{}.cli'.format(pref_out,h)),'w') as o:
                
                o.write(self.file)
  
'''Soil functions'''
def readSoil(fin):
    '''Reads in a 7778 or 2006.2 version WEPP soil file and returns a Soil object
        Support for other files can be added by by adding soil, horizon, and bed key lists as noted below
    
    
        Input:  A 7778 or 2006.2 version WEPP soil file ('.sol') with one OFE
        Return: Soil Object'''
    
    
    def floatDict(d):
        for k in d.keys():
            try:
                d[k] = float(d[k])
            except:
                pass
        return d    
    
    fin = Path.filedb(fin)
    with open(fin,'r') as f:
        i = 0
        file = [l for l in f.readlines() if not l.startswith("#")] #remove comments
        version = file[0].strip()
        
        #default format
        soil_key = ['name','texture','horizons','albedo','sat','kinter','krill','tauc','keff']
        horizon_key = ['depth','bd','ksat','anis','fc','wp','sand','clay','om','cec','rocks']
        bed_key = ['bed','bed_id','bed_thickness','bed_ksat']
        
        
        if version == '7778':
            soil_key = ['name','texture','horizons','albedo','sat','kinter','krill','tauc','keff']
            horizon_key = ['depth','bd','ksat','anis','fc','wp','sand','clay','om','cec','rocks']
            bed_key = ['bed','bed_id','bed_thickness','bed_ksat']
            
        if version == '2006.2':
            soil_key = ['name','texture','horizons','albedo','sat','kinter','krill','tauc','keff']
            horizon_key = ['depth','sand','clay','om','cec','rocks']
            bed_key = ['bed','bed_id','bed_thickness','bed_ksat']   
           
        # add file format for other versions here   
         
        comments = file[1]
        s = floatDict(dict(zip(soil_key, shlex.split(file[3]))))
        h = []
        for i in range(int(s['horizons'])):
            h.append(floatDict(dict(zip(horizon_key, file[4+i].split()))))
            file[4+i].split()
        b = floatDict(dict(zip(bed_key,file[5+i].split())))
        s['version'] = version  
    desc = fin.strip('.sol').split('/')[-1]
    
    
    return SoilDB(desc,s,h,b)
                
def writeSoil(fout,ofes):
    '''Writes a soil file (.sol) for each OFE in a list of Soil Objects
        Input: 
            ofes - [soil_object_1,soil_object_2,soil_object_3,...]
    '''
    with open(fout,'w') as o:
        #cprint('Writing {} with {} OFE(s)'.format(fout,len(ofes),True))
        o.write("7778\ncomments: soil file\n{} 1\n".format(len(ofes)))
        for s in ofes:
            o.write(s.soil)

        
        
def makeSol(prefix,year=None,prefix_out='p'):
    '''Makes a '.sol' file containing referenced soil parameters for each specified OFE
        reads in '.sol' files containing a single ofe and writes files for each specific hillslope
        containing the correct number of OFEs'''
    soils = []
    for sev in ['unb','low','mod','high']:
        #Custom loop for described file structure (eg. willow_high.sol')
        if year:
            file = Path.filedb(r'{}\{}_{}.sol'.format(year,prefix,sev))
        else:
            file = Path.filedb('{}_{}.sol'.format(prefix,sev))
        soil = readSoil(file)
        soils.append(soil)
        
    hills = readOFEs(Path.filedb('hills.csv'))
    
        
    for hid in hills.keys():
        soil_ofe = []
        for i in hills[hid]:
            soil_ofe.append(soils[i[1]-1])
            
        writeSoil(Path.filei('{}{}.sol'.format(prefix_out,hid)),soil_ofe)  
        
        if year:
            cprint('Writing sol file for hill id {} with {} ofe(s) for year {}'.format(hid,len(hills[hid]),year),True)
        else:
            cprint('Writing sol file for hill id {} with {} ofe(s)'.format(hid,len(hills[hid])),True) 
        
    return  


def readOFEs(fin):
    '''Reads a database file (.csv) with OFE breaks for each hillslope '''
    f = open(fin,'r')
    reader = csv.DictReader(f)
    hill_dic = {}
    
    cprint('Reading OFE database...: {}'.format(f.name),True)
    for row in reader:
        try:
            hill_dic[row['hid']].append((int(row['ofe']),int(row['bs_num'])))
        except:
            hill_dic[row['hid']] = [(int(row['ofe']),int(row['bs_num']))]
            
    for hid in hill_dic.keys():
        hill_dic[hid] = sorted(hill_dic[hid], key=lambda x: x[0])    #sort dictionary by ofe
    
    return hill_dic
    #21:[(1,4),(2,3)...]
        
def makeMan(hill_ofes,years,pfin,ifin):
     #hill_ofes = [(1,4),(2,3),(3,3),(4,1)] produced by readOFEs
    ofes = [x[1] for x in hill_ofes]
    years = str(years)
    mans = []
    plants = {}
    initials = {}
    id_index = {} #{'input id':'file index'} same for plant and initial
    for r in readCSVDB(pfin):
        plants[r['id']] = PlantDB(r)
        
    for r in readCSVDB(ifin):
        initials[r['id']] = InitialDB(r)
        
    def section(str):
        return '\n\n#######################\n# {str: <20}#\n#######################\n\n'.format(str=str)        
    
    '''for n in set(ofes):
        id_index[str(n)] = index()'''
            
    [initials[str(x)].initial for x in set(ofes)]
            
    id_index['3'] = 2
            
    version = '98.4'
    ofesl = len(ofes)
    
    
    #Prepare string inputs
    
    a = dict((str(y),str(x)) for x,y in hill_ofes) #{'1': '4', '3': '3', '2': '3', '4': '1'} {ofe:bs...}
    
    
    #Start writing string
    
    ms = '' #management string
    
    head = ('{version}\n'
           '#\n'
           '#\n'
           '#\n'
           '#\n\n'
           '{ofesl} # number of OFEs\n'
           '{years} # years in simulation\n\n').format(version=version,ofesl=ofesl,years=years)
    
    ms += head
    
    ms += section('Plant Section') + '{} # Number of plant scenarios\n\n\n'.format(len(set(ofes))) + '\n\n'.join([plants[str(x)].plant for x in set(ofes)])
    ms += section('Operation Section') + '{} # Number of operation scenarios\n'.format('0')
    ms += section('Initial Conditions Section') + '{} # Number of initial scenarios\n\n\n'.format(len(set(ofes))) + '\n\n'.join([initials[str(x)].initial for x in set(ofes)])
    ms += section('Surface Effects Section')+ '{} # Number of surface effect scenarios\n'.format('0')
    ms += section('Contouring Section')+ '{} # Number of contouring scenarios\n'.format('0')
    ms += section('Drainage Section')+ '{} # Number of drainage scenarios\n'.format('0')
    
    
    
    #plant growing scenarios
    yr = []
    im = 1
    
    for i in set(ofes):
        yr.append((i,im))
        im += 1
        
    yt = len(set(ofes))
    ys = '{yt} # looper; number of Yearly Scenarios\n'.format(yt = yt)
    for y in range(len(set(ofes))):
        ys += ('#\n# Yearly scenario {y} of {yt}\n#\n'
               'Year {y}\n\n\n\n'
                '1  # landuse <cropland>\n'
                '{y}  # plant growth scenario\n'
                '0  # surface effect scenario\n'
                '0  # contour scenario\n'
                '0  # drainage scenario\n'
                '2 # management <perennial>\n'
                '{sene_doy} # senescence date\n'
                '0 # perennial plant date --- 0 /0\n'
                '0 # perennial stop growth date --- 0/0\n'
                '0.0000  # row width\n'
                '3  # neither cut or grazed\n').format(y = y+1,yt=yt,sene_doy = plants[str(y+1)].sene_doy)
    
    ms += section('Yearly Section') + ys
    
    ms += section('Management Section')
    
    mgts = 'Manage\dnescription 1\ndescription2\ndescription3\n{ofes}   # number of OFEs\n'.format(ofes = len(ofes))
    for o in range(len(ofes)):    
        mgts += '    {ini_index}   # initial condition index\n'.format(ini_index = zip(*yr)[0].index(ofes[o])+1)
        
    mgts += '{}  # rotation repeats\n1  # years in rotation\n'.format(years)  
    
    for y in range(int(years)):
        mgts += '#\n# Rotation 1: year {y} to {y}\n#\n\n'.format(y=y+1)
        for o in range(len(ofes)):
            mgts += '   1    #  <plants/yr 1> - OFE: {ofe}>\n      {ind}    # year index\n'.format(ofe = o+1,ind = zip(*yr)[0].index(ofes[o])+1)
    
    ms += mgts
    return ms 


def readPRW(fin):
    '''Reads in a WEPP '.prw' watershed file and returns a dictionary of described parameters
        * no support for OFEs in prw file*
    '''
    def getFromDict(dataDict, mapList):
        return reduce(operator.getitem, mapList, dataDict)
    
    def setInDict(dataDict, mapList, value):
        getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value
        
    with open(fin,'r') as f:
        tags = {'Other':{}}
        temp = []
        tag_list = []
        
        bc = 0
        pt = None
        
        for line in f.readlines():
            #bracket counter
            bc0 = bc #previous itter
            if '{' in line:
                bc += 1
                tag = re.findall('([A-Za-z0-9.,_ ]+)',line)[0].strip()
                cprint('{} {}{}'.format(bc,(bc-1)*'    ', tag))
                tag_list.append(tag)            
                setInDict(tags, tag_list, {})
                continue
                
            if '}' in line:
                bc -= 1
                if len(temp)>0:
                    cprint('{} {}{}'.format(bc,bc*'    ','\n    '.join(temp)))
                    setInDict(tags, tag_list, '\n'.join(temp))
                    temp = []
                    
                tag_list.pop()
                continue
                
            if '=' in line:
                k,v = line.strip().split(' = ')
                temp_tag_list = list(tag_list)
                try:
                    setInDict(tags, temp_tag_list.append(k), v)
                except:
                    tags['Other'][k] = v
                
                cprint('{} {}{}'.format(bc,bc*'    ',[k,v]))
                continue
            
            if bc0 == bc:
                temp.append(line.strip())
                continue   
    
    return tags

def readDB(fin):
    '''Reads in a plant or initial '.db' file'''
    with open(Path.filedb(fin),'r') as o:
        pass

def readCSVDB(fin):
    '''Reads in a '.csv' database describing plant and initial plant conditions and returns a dictionary of key-value pairs
        * no support for OFEs in prw file*
        '''
    default_dic = {}
    with open(fin) as csvfile:
        rs = []
        reader = csv.DictReader(csvfile)
        for r in reader:  
            for k in r.keys():
                if r['id'] == '0' and k != "id":
                    #set defaults to first row, id 0
                    try:
                        default_dic[k] = float(r[k])
                    except:   
                        default_dic = r
                        
                
                elif  k != "id":
                #try to convert all other values to float        
                    try:
                        r[k] = float(r[k])
                    except:
                        pass
                    if r[k] == '':
                        r[k] = default_dic[k]
            rs.append(r)
        return rs


def cprint(message,log=False):
    '''Prints a message to console with optional support for writing to a log file    '''
    #os.chdir('C:\\GeoWEPP\\WEPP\\testruns\\wil\\script\\database')
    
    message = str(message)
    print(message)
    if log:
        with open(Path.file('','log.txt'),'a') as log_file:
            log_file.write(message)
            log_file.write('\n')
    return
    
     

def makeHillRunFile(hid,files):
    
    files = ['soil_loss_file','water_file','plot_file','graph_file']
    
    soil_loss_file = '..\output\loss_{}.txt'.format(hid)#no bool
    
    folder = '..\\output\\'
    man = 'p{}_.man'.format(hid)
    cli = 'p{}_.cli'.format(hid)
    slp = 'p{}_.slp'.format(hid)
    sol = 'p{}_.sol'.format(hid)
    years = 6
    
    file_dic = {'water_file':'Y\n{}water_{}.txt'.format(folder,hid),'pass_file':'Y\n{}pass_{}.txt'.format(folder,hid),'init_file':'Y\n{}init_{}.txt'.format(folder,hid),'crop_file':'Y\n{}init_{}.txt'.format(folder,hid),'soil_file':'Y\n{}soil_{}.txt'.format(folder,hid),'sed_file':'Y\n{}sed_{}.txt'.format(folder,hid),'graph_file':'Y\n{}graph_{}.txt'.format(folder,hid),'event_file':'Y\n{}event_{}.txt'.format(folder,hid),'ofe_file':'Y\n{}ofe_{}.txt'.format(folder,hid),'sum_file':'Y\n{}sum_{}.txt'.format(folder,hid),'winter_file':'Y\n{}winter_{}.txt'.format(folder,hid),'plant_file':'Y\n{}plant_{}.txt'.format(folder,hid)}
    
    for k in file_dic.keys():
        if k not in files:
            file_dic[k] = 'N'
    
    default_dic = {'units':'M','overwrite':'Y','cli_type':'1','version':'1','pass_file':file_dic['pass_file'],'loss_type':'3','init_file':file_dic['init_file'],'soil_loss_file':soil_loss_file,'water_file':file_dic['water_file'],'crop_file':file_dic['crop_file'],'soil_file':file_dic['soil_file'],'sed_file':file_dic['sed_file'],'graph_file':file_dic['graph_file'],'event_file':file_dic['event_file'],'ofe_file':file_dic['ofe_file'],'sum_file':file_dic['sum_file'],'winter_file':file_dic['winter_file'],'plant_file':file_dic['plant_file'],'man':man,'cli':cli,'slp':slp,'sol':sol,'ir':'0','years':years,'bypass':'0'}
    return '{units}\n{overwrite}\n{cli_type}\n{version}\n{pass_file}\n{loss_type}\n{init_file}\n{soil_loss_file}\n{water_file}\n{crop_file}\n{soil_file}\n{sed_file}\n{graph_file}\n{event_file}\n{ofe_file}\n{sum_file}\n{winter_file}\n{plant_file}\n{man}\n{slp}\n{cli}\n{sol}\n{ir}\n{years}\n{bypass}'.format(**default_dic)


def runWEPP(exe_path , run_file, error_file):
    '''Runs WEPP using a given run file
        Inputs:
            exe_path - path to wepp executable file
            run_file - path to any wepp run file
            error_file - output error file
            
        Example: 
            Path.exe = 'C:\GeoWEPP\WEPP\testruns\wil\thomas\WEPP2014_ph.exe'
            runWEPP(Path.exe,Path.file('','pw0.run'),Path.file('','pw0err.txt'))
    '''
    def checkError(fin):
        #read second to last line of error file
        l = ''
        with open(fin,'r') as e:
            l = e.readlines()[-1]
        if l.find('SUCCESSFULLY'):
            cprint('foundsuccess',True)
            return (True,l)
        else:
            return (False,l)
    
    #p18_.run
    #p18.err
    cmd = '{exe_path} < {run_file} > {error_file}'.format(exe_path=exe_path,run_file=run_file, error_file=error_file)
    cprint('Running WEPP with run file: {}'.format(run_file),True)
    dts = datetime.datetime.now()
    subprocess.call(cmd,shell=True)
    dte = datetime.datetime.now()
    dt = dte - dts
    e = checkError(error_file)
    if e[0]:
        cprint('WEPP simulation completed Successfully in {}'.format(str(dt)),True)
    else:
        cprint('Error in WEPP simulation:',True)
        cprint('    {}'.format(e[1]),True)
    return
    

def makeWSRunFile(hid, years='6',units = 'M',prf = 'p'):
    
    '''Creates a WEPP watershed run file
        
        Defaults:
            units:             Metric
            output paths:     /slope, /cli, /man, /soil, /output
    '''  
    
    file_out = Path.file('','pw0.run')
    
    try:
        years = str(years)
        units = str(units)
        map(str,hid)
        
    except:
        cprint('ERROR in Run File Input types',True)
    
    
    
    output_dic = {
        'water':True,
        'crop':True,
        'soil':True,
        'sed_loss':True,
        'graph':False,
        'event':True,
        'ofe':True,
        'summary':True,
        'winter':False,
        'plant':True}
            
    hill_output_order = ['water','crop','soil','sed_loss','graph','event','ofe','summary','winter','plant']
      
    #===HEADDER SECTION===
    ws_head = '\n'.join([
        '{units}',
        'Y',
        '1',
        '2',
        'pass_pw0.txt',
        '{hills}']).format(hills=len(hid),units=units)
    
    #===END HEADDER SECTION===
    
    #===HILLSLOPE SECTION===    
    '''
    Inputs:
        hid        - list of hill ids
        units      - 'M' or 'E' units
        years      - number of years to run
        output_dic - dictionary of bools to choose which output files to select
        
    '''
    ws_hill = ''
    for h in hid:
        #---create hillslope 'output file' string block
        
        #hillslope output/input directories
        hill_path = {'man_path':Path.man,
                     'slope_path':Path.slope,
                     'cli_path':Path.cli,
                     'soil_path':Path.soil,
                     'output_path':Path.output}
        
        hill_output_string = ''
        for re in hill_output_order:
            if output_dic[re]:
                hill_output_string += 'Yes\n{output_path}{h}_{re}.txt\n'.format(h=h,re=re,**hill_path)
            else:
                hill_output_string += 'No\n'
                
        hill_output_string =  hill_output_string.rstrip('\n')
        
        
        
        #---create hillslope string block including 'output file' block and 'input file' block
        
        
        
        hill_str = '\n'.join([
            'M',
            'No',
            '{output_path}{h}_pass.txt',
            '1',
            'No',
            './output/{h}_loss.txt',
            hill_output_string,
            '{man_path}{prf}{h}.man',
            '{slope_path}{prf}{h}.slp',
            '{cli_path}{prf}{h}.cli',
            '{soil_path}{prf}{h}.sol',
            '0',
            '{years}'
            ]).format(h=h,prf = prf,years=years,**hill_path)
        ws_hill += hill_str + '\n'
    
    #===END HILLSLOPE SECTION===  
     
    #=== WATERSHED SECTION===  
    ws_end = '\n'.join([
        'N',
        'N',
        '5',
        '.\{output}\loss_pw{ws}.txt',
        'Yes',
        '.\{output}\wat_pw{ws}.txt',
        'Yes',
        '.\{output}\plant_pw{ws}.txt',
        'Yes',
        '.\{output}\soil_pw{ws}.txt',
        'Yes',
        '.\{output}\plot_pw{ws}.txt',
        'Yes',
        '.\{output}\grph_pw{ws}.txt',
        'Yes',
        '.\{output}\ebe_pw{ws}.txt',
        'Yes',
        '.\{output}\summary_pw{ws}.txt',
        'No',
        'Yes',
        '.\{output}\yeild_pw{ws}.txt',
        './{ws_folder}/pw{ws}.str',
        './{ws_folder}/pw{ws}.chn',
        './{ws_folder}/pw{ws}.man',
        './{ws_folder}/pw{ws}.slp',
        './{ws_folder}/pw{ws}.cli',
        './{ws_folder}/pw{ws}.sol',
        '0',
        '{years}']).format(output='results',years=years,ws=0,ws_folder='ws')
        
    
    #'./{ws_folder}/pw{ws}.imp',    
    #===END WATERSHED SECTION===     
    
    
    with open(file_out,'w') as o:
        cprint('Writing watershed run file - {}'.format(file_out))
        o.write('\n'.join([ws_head,  ws_hill, ws_end]))
        
      
    return '\n'.join([ws_head,  ws_hill, ws_end])   


#print makeWSRunFile(['10','11'],years='5')
      
def initDB():
    '''Read in all relevant database (soil, plant, initial) databases and create object instances'''
    
    return

'''Unused Functions'''
    
def mergeGraph():
    
    dir = 'C:\GeoWEPP\WEPP\output\grph\grph'
    idir = 'C:\GeoWEPP\WEPP\output\grph'
    files = os.listdir(dir)
    w = open(os.path.join(idir,'all.csv'),'w')
    
    head = ['id','Days In Simulation', 'Hillslope: Precipitation (mm)', 'Hillslope: Average detachment (kg/m**2)', 'Hillslope: Maximum detachment (kg/m**2)', 'Hillslope: Point of maximum detachment (m)', 'Hillslope: Average deposition (kg/m**2)', 'Hillslope: Maximum deposition (kg/m**2)', 'Hillslope: Point of maximum deposition (m)', 'Hillslope: Sediment Leaving Profile (kg/m)', 'Hillslope: 5 day average mimimum temp. (C)', 'Hillslope: 5 day average maximum temp. (C)', 'Hillslope: daily minimum temp. (C)', 'Hillslope: daily maximum temp. (C)', 'Irrigation depth (mm)', 'Irrigation_volume_supplied/unit_area (mm)', 'Runoff (mm)', 'Interrill net soil loss (kg/m**2)', 'Canopy height (m)', 'Canopy cover (0-1)', 'Leaf area index', 'Interrill cover (0-1)', 'Rill cover (0-1)', 'Above ground live biomass (kg/m**2)', 'Live root mass for OFE (kg/m**2)', 'Live root mass 0-15 cm depth (kg/m**2)', 'Live root mass 15-30 cm depth (kg/m**2)', 'Live root mass 30-60 cm depth (kg/m**2)', 'Root depth (m)', 'Standing dead biomass (kg/m**2)', 'Current residue mass on ground (kg/m**2)', 'Previous residue mass on ground (kg/m**2)', 'Old residue mass on the ground (kg/m**2)', 'Current submerged residue mass (kg/m**2)', 'Previous submerged residue mass (kg/m**2)', 'Old submerged residue mass (kg/m**2)', 'Current dead root mass (kg/m**2)', 'Previous dead root mass (kg/m**2)', 'Old dead root mass (kg/m**2)', 'Porosity (%)', 'Bulk density (g/cc)', 'Effective hydraulic conductivity (mm/hr)', 'Suction across wetting front (mm)', 'Evapotranspiration (mm)', 'Drainage flux (m/day)', 'Depth to drainable zone (m)', 'Effective intensity (mm/h)', 'Peak runoff (mm/h)', 'Effective runoff duration (h)', 'Enrichment ratio', 'Adjusted Ki (millions kg-s/m**4)', 'Adjusted Kr (x 1000 s/m)', 'Adjusted Tauc (Pascals)', 'Rill width (m)', 'Plant Transpiration (mm)', 'Soil Evaporation (mm)', 'Seepage (mm)', 'Water stress', 'Temperature stress', 'Total soil water (mm)', 'Soil water in layer 1 (mm)', 'Soil water in layer 2 (mm)', 'Soil water in layer 3 (mm)', 'Soil water in layer 4 (mm)', 'Soil water in layer 5 (mm)', 'Soil water in layer 6 (mm)', 'Soil water in layer 7 (mm)', 'Soil water in layer 8 (mm)', 'Soil water in layer 9 (mm)', 'Soil water in layer 10 (mm)', 'Random roughness (mm)', 'Ridge height (mm)', 'Frost depth (mm)', 'Thaw depth (mm)', 'Snow depth (mm)', 'Water from snow melt (mm)', 'Snow density (kg/m**3)', 'Rill cover fric fac (crop)', 'Fric. fac. due to live plant', 'Rill total fric fac (crop)', 'Composite area total friction factor', 'Rill cov fric fac (range)', 'Live basal area fric fac (range)', 'Live plant canopy fric fac (range)', 'Days since last disturbance', 'Current crop type', 'Current residue on ground type', 'Previous residue on ground type', 'Old residue on ground type', 'Current dead root type', 'Previous dead root type', 'Old dead root type', 'Sediment leaving OFE (kg/m)', 'Evaporation from residue (mm)', 'Total frozen soil water (mm)', 'Frozen soil water in layer 1 (mm)', 'Frozen soil water in layer 2 (mm)', 'Frozen soil water in layer 3 (mm)', 'Frozen soil water in layer 4 (mm)', 'Frozen soil water in layer 5 (mm)', 'Frozen soil water in layer 6 (mm)', 'Frozen soil water in layer 7 (mm)', 'Frozen soil water in layer 8 (mm)', 'Frozen soil water in layer 9 (mm)', 'Frozen soil water in layer 10 (mm)']
    w.write(','.join(head))
    w.write('\n')
    
    for f in files:
        o = open(os.path.join(dir,f),'r')
        lines = o.readlines()
        for l in lines[121:]:
            ln = l.split()
            if '#' in ln[0]:
                break
            w.write('{},{}\n'.format(f.split('_')[-1],','.join(ln)))


def importDefaults(fin):
    #find a way to import from file
    with open(fin,'r') as d:
        pass


def runYears():
    years = ['2011','2012','2013','2014','2015','2016']
    dest = 'all'
    for y in years:
        makeSol('willow',y)
        runWEPP(Path.exe,Path.file('','pw0.run'),Path.file('','pw0err.txt'))
        #copy output
        dir_util.copy_tree(Path.file('output',''), Path.file(dest,y))
        dir_util.copy_tree(Path.file('results',''), Path.file(dest,y))

'''Default Variables'''
   
  #thomas 
#exe_path = r'C:\GeoWEPP\wepp\wepp.exe'    
exe_path = r'C:\GeoWEPP\WEPP\testruns\wil\script\WEPP2014_ph.exe'
ws = r'C:\GeoWEPP\WEPP\testruns\wil\script'
dbf = 'database'
inf = 'input' #inputs folder
outf =  'output' #outputs folder
'''
   

exe_path = r'C:\GeoWEPP\wepp\wepp.exe'    
exe_path = r'C:\\GeoWEPP\\WEPP\\wepp\\wepp.exe'
ws = r'C:\\GeoWEPP\\WEPP\\testruns\\wil\\script'
in_path = 'database'
out_path =  'input'

#exe_path = r'C:\GeoWEPP\wepp\wepp.exe'
ws = r'C:\Users\quinnd\OneDrive\UI\MS\Research\WEPPpy\workspace' #master workspace
dbf = 'database' #database folder
inf = 'inputs' #inputs folder
outf =  'outputs' #outputs folder
'''
#set working directory as specified
os.chdir(ws)

#initialize log file
with open('log.txt','w') as o:
    o.write('WEPPpy initialized at {}\n'.format(datetime.datetime.now()))

#create path instance
Path = Path(ws,dbf,inf,outf,exe_path)



if __name__ == '__main__':
        
         
    soils = []
    for sev in ['unb','low','mod','high']:
        soils.append(readSoil(Path.filedb('willow_{}.sol'.format(sev))))
    
    
    hills = readOFEs(Path.filedb('hills.csv'))
    
    for hid in hills.keys():
        soil_ofe = []
        for i in hills[hid]:
            soil_ofe.append(soils[i[1]-1])
        writeSoil(Path.file(inf,'','hill_{}'.format(hid)),soil_ofe)