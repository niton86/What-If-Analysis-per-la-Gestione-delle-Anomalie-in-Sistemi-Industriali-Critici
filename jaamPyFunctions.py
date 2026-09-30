#!/usr/bin/python3
from os import path, remove, system, name, listdir, mkdir
from subprocess import call as subcall
from datetime import datetime
from pandas import DataFrame, read_csv, to_numeric
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import shutil
from colorama import Fore
import re
if name == 'nt':
    from os import startfile

src = "jaamfiles/" #folder where is located the FactoryZero.cfg
installFolder = "./" #folder where is located the JaamSim.jar
workspace = ""
plt.ion() #matplotlib interactive mode (allows to plot graph and keep running
last = "" #save the name of the report of the last simulation runned

def newWorkspace(name):
    #create a new factory file to edit
    shutil.copyfile(src+"FactoryZero.cfg", src+name+".cfg")

def showWorkspaces():
    factories = []
    #list all the factory files created
    print(Fore.GREEN+"WORKSPACES")
    for ws in listdir(src):
        if ws != "factoryZero.cfg" and ws.split(".")[1] == "cfg":
            factories.append(ws.split(".")[0])
            print(Fore.CYAN+ws.split(".")[0])
    return factories

def saveWorkspace(newName,shell):
    global workspace
    if newName+'.cfg' in listdir(src):
        if shell == True:
            n = input(Fore.YELLOW+"[*] workspace already exists; override it [Y/n]? ")
            if n == 'n':
                print(Fore.RED+"[!] operation aborted")
                return
    print(Fore.BLUE+"[+] copying file in the new workspace")
    shutil.copyfile(src+workspace+".cfg", src+newName+".cfg") #copy workspace
    print(Fore.LIGHTBLUE_EX+" └> file copied")
    #deleteFactoryEdited(workspace) #delete current workspace
    workspace = newName #update the variable

def saveReport() -> str:
    if 'reports' not in listdir(): #create the reports folder if not exist
        mkdir('reports')
    #create the destination path for the report
    today = datetime.now()
    dst = workspace+'_'+str(today.day)+"-"+str(today.month)+"-"+str(today.year)
    dst += '_'+str(today.hour)+'-'+str(today.minute)+'-'+str(today.second)+'.dat'
    #save the report
    shutil.copyfile(src+workspace+'.dat','reports/'+dst)
    print(Fore.BLUE+"[+] report saved in the ./reports/ folder")
    print(Fore.BLUE+" └> report name: "+Fore.WHITE+dst)
    return dst

def printDat(name):
    if fname == 'lastrun':
        global last
        fname = last
    if '.dat' not in name:
        name = name.strip(' ') + '.dat'
    with open('reports/'+name, 'r') as file:
        for line in file:
            print(line.strip())

def openDat(fname):
    if fname == 'lastrun':
        global last
        fname = last
    if '.dat' not in fname:
        fname = fname.strip(' ') + '.dat'
    file_dat = path.join('reports',fname)
    if name == 'nt': #windows
        startfile(file_dat)
    else: #not windows
        subcall(["mimeopen", "-a", file_dat])

def plotGraph(fname):
    with open(fname, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    header = []
    data_rows = []
    
    for line in lines:
        #split each space and tab
        parts = line.split()
        if not parts:
            continue  
        if not header:
            parts[0] = parts[0].replace('\ufeff', '')
            header = parts
        else:
            if len(parts) == len(header):
                data_rows.append(parts)
    #if the file is empty => exit
    if len(header) < 3:
        print(f"Error: no metric found in the file '{path.basename(fname)}'.")
        return
    #analyze
    df = DataFrame(data_rows, columns=header)
    for col in df.columns:
        if col not in ['Scenario', 'Replication']:
            df[col] = df[col].astype(str).str.replace(r'\[.*?\]', '', regex=True)      
    for col in df.columns:
        df[col] = to_numeric(df[col], errors='coerce')     
    target_columns = header[2:] 
    colours = {1: 'red', 2: 'teal', 3: 'green'}
    n_rows = len(target_columns)
    n_cols = len(colours)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 3 * n_rows), sharex=True)
    if n_rows == 1:
        axes = [axes]
    for r, col_name in enumerate(target_columns):
        for c, (scenario, colour) in enumerate(colours.items()):
            #select the cell
            if n_rows > 1:
                ax = axes[r][c]
            else:
                ax = axes[0][c]
            dt_scenario = df[df['Scenario'] == scenario]
            #if the file is different from the expectation => ignore the empty scenario
            if dt_scenario.empty:
                continue
            ax.bar(dt_scenario['Replication'], dt_scenario[col_name], color=colour)
            ax.set_xlabel('Replication')
            ax.set_ylabel('Value')
            clean_title = col_name.split(']')[0] + ']' if ']' in col_name else col_name
            ax.set_title(f'{clean_title} - Scenario {scenario}')
    plt.tight_layout()
    plt.show()

def showMachines() -> list[str]: #return a list with all parameters used in the simulation
    parameters = []
    #format of the list:
    #[productionPerHour, runDuration, branchCondition, tbf1, tbf2, tbf3, ttr1,
    #ttr2, ttr3, maintenance1, maintenance2, maintenance3, duration1, duration2,
    #duration3, assign1, assign2, assign3]
    #the ones with a number are lists as well
    #tbf1 = [min,max,mean], tbf2/3 = [scale,shape]
    #ttr = [min,max], maintenance = [interval,duration]
    #duration = [min,max], assign = [perror,ppass]
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    f.close()
    #read production per hour
    parameters.append(factory.split("FactoryProductionPerHour Value {")[1].split("FactoryProductionPerHour CycleTime {")[0])
    #read run duration
    parameters.append(factory.split("Simulation RunDuration {")[1].split("Simulation GlobalSubstreamSeed { ")[0])
    #read the branch condition
    parameters.append(factory.split("BranchWorkline Choice { ")[1].split("InspectionBranch NextComponentList { ")[0])
    #read the TBFdist1 parameters
    tbfString = factory.split("TBFdist1 MinValue { ")[1].split("# *** NonStatExponentialDist ***")[0]
    tbfMin = tbfString.split("TBFdist1 MinValue { ")[0].split('TBFdist1 Max')[0].strip('}\n')
    tbfMax = tbfString.split("TBFdist1 MaxValue { ")[1].split('TBFdist1 Mean')[0].strip('}\n')
    tbfMean = tbfString.split("TBFdist1 MeanValue { ")[0].split('Mean {')[1].strip('}\n')
    parameters.append([tbfMin,tbfMax,tbfMean])
    del tbfMin
    del tbfMax
    del tbfMean
    #read the TBFdist2 parameters
    tbfString = factory.split("TBFdist2 Scale { ")[1].split("TBFdist3 RandomSeed { ")[0]
    tbfScale = tbfString.split("}")[0]
    tbfShape = tbfString.split("{")[1]
    parameters.append([tbfScale,tbfShape])
    del tbfScale
    del tbfShape
    #read the TBFdist3 parameters
    tbfString = factory.split("TBFdist3 Scale { ")[1].split("# *** Assign ***")[0]
    tbfScale = tbfString.split("}")[0]
    tbfShape = tbfString.split("{")[1]
    parameters.append([tbfScale,tbfShape])
    del tbfScale
    del tbfShape
    del tbfString
    #read the ttr1 parameters
    ttrString = factory.split("TTRdist1 MinValue { ")[1].split("TTRdist2 RandomSeed { ")[0]
    ttrMin = ttrString.split("}")[0]
    ttrMax = ttrString.split("{")[1]
    parameters.append([ttrMin,ttrMax])
    #read the ttr2 parameters
    ttrString = factory.split("TTRdist2 MinValue { ")[1].split("TTRdist3 RandomSeed { ")[0]
    ttrMin = ttrString.split("}")[0]
    ttrMax = ttrString.split("{")[1]
    parameters.append([ttrMin,ttrMax])
    #read the ttr3 parameters
    ttrString = factory.split("TTRdist3 MinValue { ")[1].split("# *** WeibullDistribution ***")[0]
    ttrMin = ttrString.split("}")[0]
    ttrMax = ttrString.split("{")[1]
    parameters.append([ttrMin,ttrMax])
    del ttrMin
    del ttrMax
    del ttrString
    #read the maintenance1 parameters
    mainString = factory.split("Machine1Maintenance Interval { ")[1].split("Machine2Breakdown Interval {")[0]
    mainInt = mainString.split("}")[0]
    mainDur = mainString.split("{")[1]
    parameters.append([mainInt,mainDur])
    #read the maintenance2 parameters
    mainString = factory.split("Machine2Maintenance Interval { ")[1].split("Machine3Breakdown Interval {")[0]
    mainInt = mainString.split("}")[0]
    mainDur = mainString.split("{")[1]
    parameters.append([mainInt,mainDur])
    #read the maintenance3 parameters
    mainString = factory.split("Machine3Maintenance Interval { ")[1].split("# *** ExpressionEntity ***")[0]
    mainInt = mainString.split("}")[0]
    mainDur = mainString.split("{")[1]
    parameters.append([mainInt,mainDur])
    del mainInt
    del mainDur
    del mainString
    #read the duration1 parameters
    durString = factory.split("Machine1Distribution MinValue { ")[1].split("Machine2Distribution RandomSeed { ")[0]
    durMin = durString.split("}")[0]
    durMax = durString.split("{")[1]
    parameters.append([durMin,durMax])
    #read the duration2 parameters
    durString = factory.split("Machine2Distribution MinValue { ")[1].split("Machine3Distribution RandomSeed { ")[0]
    durMin = durString.split("}")[0]
    durMax = durString.split("{")[1]
    parameters.append([durMin,durMax])
    #read the duration1 parameters
    durString = factory.split("Machine3Distribution MinValue { ")[1].split("TTRdist1 RandomSeed {")[0]
    durMin = durString.split("}")[0]
    durMax = durString.split("{")[1]
    parameters.append([durMin,durMax])
    del durMin
    del durMax
    del durString
    #read the assign1 parameters
    asString = factory.split("A1distribution ProbabilityList { ")[1].split("A2distribution RandomSeed {")[0]
    asMin = asString.replace("  "," ").split(" ")[0]
    asMax = asString.replace("  "," ").split(" ")[1]
    parameters.append([asMin,asMax])
    #read the assign2 parameters
    asString = factory.split("A2distribution ProbabilityList { ")[1].split("A3distribution RandomSeed {")[0]
    asMin = asString.replace("  "," ").split(" ")[0]
    asMax = asString.replace("  "," ").split(" ")[1]
    parameters.append([asMin,asMax])
    #read the assign3 parameters
    asString = factory.split("A1distribution ProbabilityList { ")[1].split("PassedDistribution RandomSeed {")[0]
    asMin = asString.replace("  "," ").split(" ")[0]
    asMax = asString.replace("  "," ").split(" ")[1]
    parameters.append([asMin,asMax])
    del asMin
    del asMax
    del asString
    #polish the list
    for p in range(len(parameters)):
        if isinstance(parameters[p],str):
            parameters[p]=parameters[p].strip('\n').strip('}').strip(' ').strip("'")
        else:
            for a in range(len(parameters[p])):
                parameters[p][a]=parameters[p][a].strip('\n').strip('}').strip(' ').strip("'")
    return parameters

def plotPdf(fname): #transform the matplotlib graphs into a pdf file
    if fname == 'lastrun':
        global last
        fname = last
    if '.dat' not in fname:
        fname = fname.strip(' ') + '.dat'
    file_pdf = path.abspath(path.join('reports', fname[:-4]+'.pdf')) #path for the file report.pdf
    #if the file already exist open it
    if fname[:-4]+'.pdf' in listdir('reports'):
        if name == 'nt': #windows
            startfile(file_pdf)
        else: #not windows
            system(file_pdf)
        return
    #load the file
    df = read_csv(path.join('reports',fname), sep='\t', header=0)
    #delete the units of measure
    for col in df.columns:
        df[col] = df[col].astype(str).str.replace(r'\[.*\]', '', regex=True)
    #convert anything to float (string become NaN)
    df = df.apply(to_numeric, errors='coerce')
    #delete empty rows
    df = df.dropna(subset=['Replication'])
    #identify the columns and the colour for each scenario
    target_columns = [i for i in range(2, len(df.columns), 2)]
    colours = {1: 'red', 2: 'teal', 3: 'green'}
    #print the PDF
    with PdfPages(('reports/'+fname)[:-4]+'.pdf') as pdf:
        for colnum in target_columns:
            fig, axes = plt.subplots(3, 1, figsize=(8, 11)) #one row for each page
            for i, (scenario, colour) in enumerate(colours.items()):
                ax = axes[i]
                dt_scenario = df[df['Scenario'] == scenario]
                ax.bar(dt_scenario['Replication'], dt_scenario.iloc[:, colnum], color=colour)
                ax.set_title(f'{df.columns[colnum]} - Scenario {scenario}')           
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)
    #open the pdf
    if name == 'nt': #windows
        startfile(file_pdf)
    else: #not windows
        system(file_pdf)

def editTbfM1(value):
    #check if the value is like 10 s, 10 h, 5 h
    #parse the value
    val = value.split(',')
    if len(val) != 3:
        print(Fore.RED+"[!] the list must contain 3 elements: [min,max,mean]")
        return False
    for v in range(len(val)):
        val[v] = val[v].strip(' ')
    #insert the values [min,max,mean]
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    first = factory.split("TBFdist1 MinValue { ")[0]
    last = factory.split("# *** NonStatExponentialDist ***")[1]
    last = "# *** NonStatExponentialDist ***\n" + last
    f.close()
    valueString = "TBFdist1 MinValue { "+val[0]+" }\n"
    valueString += "TBFdist1 MaxValue { "+val[1]+" }\n"
    valueString += "TBFdist1 Mean { "+val[2]+" }"
    try:
        f = open(src+workspace+".cfg",'w')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    f.write(first+valueString+'\n'+last)
    f.close()
    #run the simulation to test the value
    return testSim()

def editTbfM2(value):
    #check if the value is like 10 s, 2
    #parse the value
    val = value.split(',')
    if len(val) != 2:
        print(Fore.RED+"[!] the list must contain 2 elements: [shape,scale]")
        return False
    for v in range(len(val)):
        val[v] = val[v].strip(' ')
    #insert the values
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    first = factory.split("TBFdist2 Scale { ")[0]
    last = factory.split("TBFdist3 RandomSeed { ")[1]
    last = "TBFdist3 RandomSeed { " + last
    f.close()
    valueString = "TBFdist2 Scale { "+val[0]+" }\n"
    valueString += "TBFdist2 Shape { "+val[1]+" }"
    try:
        f = open(src+workspace+".cfg",'w')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    f.write(first+valueString+'\n'+last)
    f.close()
    #run the simulation to test the value
    return testSim()

def editTbfM3(value):
    #check if the value is like 10 s, 2
    #parse the value
    val = value.split(',')
    if len(val) != 2:
        print(Fore.RED+"[!] the list must contain 2 elements: [shape,scale]")
        return False
    for v in range(len(val)):
        val[v] = val[v].strip(' ')
    #insert the values
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    first = factory.split("TBFdist3 Scale { ")[0]
    last = factory.split("# *** Assign ***")[1]
    last = "\n# *** Assign ***" + last
    f.close()
    valueString = "TBFdist3 Scale { "+val[0]+" }\n"
    valueString += "TBFdist3 Shape { "+val[1]+" }"
    try:
        f = open(src+workspace+".cfg",'w')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    f.write(first+valueString+'\n'+last)
    f.close()        
    #run the simulation to test the value
    return testSim()

def editTtrM1(value):
    #check if the value is like 10 s, 20 s
    #parse the value
    val = value.split(',')
    if len(val) != 2:
        print(Fore.RED+"[!] the list must contain 2 elements: [min,max]")
        return False
    for v in range(len(val)):
        val[v] = val[v].strip(' ')
    #insert the values
        try:
            f = open(src+workspace+".cfg",'r')
        except Exception as e:
            print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
            exit(1)
        factory = f.read()
        first = factory.split("TTRdist1 MinValue { ")[0]
        last = factory.split("TTRdist2 RandomSeed { ")[1]
        last = "TTRdist2 RandomSeed { " + last
        f.close()
        valueString = "TTRdist1 MinValue { "+val[0]+" }\n"
        valueString += "TTRdist1 MaxValue { "+val[1]+" }"
        try:
            f = open(src+workspace+".cfg",'w')
        except Exception as e:
            print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
            exit(1)
        f.write(first+valueString+'\n'+last)
        f.close()  
    #run the simulation to test the value
    return testSim()

def editTtrM2(value):
    #check if the value is like 10 s, 20 s
    #parse the value
    val = value.split(',')
    if len(val) != 2:
        print(Fore.RED+"[!] the list must contain 2 elements: [min,max]")
        return False
    for v in range(len(val)):
        val[v] = val[v].strip(' ')
    #insert the values
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    first = factory.split("TTRdist2 MinValue { ")[0]
    last = factory.split("TTRdist3 RandomSeed { ")[1]
    last = "TTRdist3 RandomSeed { " + last
    f.close()
    valueString = "TTRdist2 MinValue { "+val[0]+" }\n"
    valueString += "TTRdist2 MaxValue { "+val[1]+" }"
    try:
        f = open(src+workspace+".cfg",'w')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    f.write(first+valueString+'\n'+last)
    f.close()
    #run the simulation to test the value
    return testSim()

def editTtrM3(value):
    #check if the value is like 10 s, 20 s
    #parse the value
    val = value.split(',')
    if len(val) != 2:
        print(Fore.RED+"[!] the list must contain 2 elements: [min,max]")
        return False
    for v in range(len(val)):
        val[v] = val[v].strip(' ')
    #insert the values
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    first = factory.split("TTRdist3 MinValue { ")[0]
    last = factory.split("# *** WeibullDistribution ***")[1]
    last = "\n# *** WeibullDistribution ***" + last
    f.close()
    valueString = "TTRdist3 MinValue { "+val[0]+" }\n"
    valueString += "TTRdist3 MaxValue { "+val[1]+" }"
    try:
        f = open(src+workspace+".cfg",'w')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    f.write(first+valueString+'\n'+last)
    f.close()
    #run the simulation to test the value
    return testSim()

def editMainM1(value):
    #check if the value is like 1 w, 2 h
    #parse the value
    val = value.split(',')
    if len(val) != 2:
        print(Fore.RED+"[!] the list must contain 2 elements: [interval,duration]")
        return False
    for v in range(len(val)):
        val[v] = val[v].strip(' ')
    #insert the values
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    first = factory.split("Machine1Maintenance Interval { ")[0]
    last = factory.split("Machine2Breakdown Interval {")[1]
    last = "\nMachine2Breakdown Interval {" + last
    f.close()
    valueString = "Machine1Maintenance Interval { "+val[0]+" }\n"
    valueString += "Machine1Maintenance Duration { "+val[1]+" }"
    try:
        f = open(src+workspace+".cfg",'w')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    f.write(first+valueString+'\n'+last)
    f.close()
    #run the simulation to test the value
    return testSim()

def editMainM2(value):
    #check if the value is like 1 w, 2 h
    #parse the value
    val = value.split(',')
    if len(val) != 2:
        print(Fore.RED+"[!] the list must contain 2 elements: [interval,duration]")
        return False
    for v in range(len(val)):
        val[v] = val[v].strip(' ')
    #insert the values
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    first = factory.split("Machine2Maintenance Interval { ")[0]
    last = factory.split("Machine3Breakdown Interval {")[1]
    last = "\nMachine3Breakdown Interval {" + last
    f.close()
    valueString = "Machine2Maintenance Interval { "+val[0]+" }\n"
    valueString += "Machine2Maintenance Duration { "+val[1]+" }"
    try:
        f = open(src+workspace+".cfg",'w')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    f.write(first+valueString+'\n'+last)
    f.close()
    #run the simulation to test the value
    return testSim()

def editMainM3(value):
    #check if the value is like 1 w, 2 h
    #parse the value
    val = value.split(',')
    if len(val) != 2:
        print(Fore.RED+"[!] the list must contain 2 elements: [interval,duration]")
        return False
    for v in range(len(val)):
        val[v] = val[v].strip(' ')
    #insert the values
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    first = factory.split("Machine3Maintenance Interval { ")[0]
    last = factory.split("# *** ExpressionEntity ***")[1]
    last = "\n# *** ExpressionEntity ***" + last
    f.close()
    valueString = "Machine3Maintenance Interval { "+val[0]+" }\n"
    valueString += "Machine3Maintenance Duration { "+val[1]+" }"
    try:
        f = open(src+workspace+".cfg",'w')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    f.write(first+valueString+'\n'+last)
    f.close()
    #run the simulation to test the value
    return testSim()

def editProcM1(value):
    #check if the value is like 50 s, 80 s
    #parse the value
    val = value.split(',')
    if len(val) != 2:
        print(Fore.RED+"[!] the list must contain 2 elements: [min,max]")
        return False
    for v in range(len(val)):
        val[v] = val[v].strip(' ')
    #insert the values
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    first = factory.split("Machine1Distribution MinValue { ")[0]
    last = factory.split("Machine2Distribution RandomSeed { ")[1]
    last = "Machine2Distribution RandomSeed { " + last
    f.close()
    valueString = "Machine1Distribution MinValue { "+val[0]+" }\n"
    valueString += "Machine1Distribution MaxValue { "+val[1]+" }"
    try:
        f = open(src+workspace+".cfg",'w')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    f.write(first+valueString+'\n'+last)
    f.close()
    #run the simulation to test the value
    return testSim()

def editProcM2(value):
    #check if the value is like 50 s, 80 s
    #parse the value
    val = value.split(',')
    if len(val) != 2:
        print(Fore.RED+"[!] the list must contain 2 elements: [min,max]")
        return False
    for v in range(len(val)):
        val[v] = val[v].strip(' ')
    #insert the values
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    first = factory.split("Machine2Distribution MinValue { ")[0]
    last = factory.split("Machine3Distribution RandomSeed { ")[1]
    last = "Machine3Distribution RandomSeed { " + last
    f.close()
    valueString = "Machine2Distribution MinValue { "+val[0]+" }\n"
    valueString += "Machine2Distribution MaxValue { "+val[1]+" }"
    try:
        f = open(src+workspace+".cfg",'w')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    f.write(first+valueString+'\n'+last)
    f.close()
    #run the simulation to test the value
    return testSim()

def editProcM3(value):
    #check if the value is like 50 s, 80 s
    #parse the value
    val = value.split(',')
    if len(val) != 2:
        print(Fore.RED+"[!] the list must contain 2 elements: [min,max]")
        return False
    for v in range(len(val)):
        val[v] = val[v].strip(' ')
    #insert the values
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    first = factory.split("Machine3Distribution MinValue { ")[0]
    last = factory.split("TTRdist1 RandomSeed {")[1]
    last = "\nTTRdist1 RandomSeed {" + last
    f.close()
    valueString = "Machine3Distribution MinValue { "+val[0]+" }\n"
    valueString += "Machine3Distribution MaxValue { "+val[1]+" }"
    try:
        f = open(src+workspace+".cfg",'w')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    f.write(first+valueString+'\n'+last)
    f.close()
    #run the simulation to test the value
    return testSim()

def editAssignM1(value):
    #check if the value is like 10 s, 10 h, 5 h
    #parse the value
    val = value.split(',')
    if len(val) != 2:
        print(Fore.RED+"[!] the list must contain 2 elements: [errorProbability,passProbability]")
        return False
    for v in range(len(val)):
        val[v] = val[v].strip(' ')
    #insert the values
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    first = factory.split("A1distribution ProbabilityList { ")[0]
    last = factory.split("A2distribution RandomSeed {")[1]
    last = "\nA2distribution RandomSeed {" + last
    f.close()
    valueString = "A1distribution ProbabilityList { "+val[0]+" "+val[1]+" }"
    try:
        f = open(src+workspace+".cfg",'w')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    f.write(first+valueString+'\n'+last)
    f.close()
    #run the simulation to test the value
    return testSim()

def editAssignM2(value):
    #check if the value is like 10 s, 10 h, 5 h
    #parse the value
    val = value.split(',')
    if len(val) != 2:
        print(Fore.RED+"[!] the list must contain 2 elements: [errorProbability,passProbability]")
        return False
    for v in range(len(val)):
        val[v] = val[v].strip(' ')
    #insert the values
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    first = factory.split("A2distribution ProbabilityList { ")[0]
    last = factory.split("A3distribution RandomSeed {")[1]
    last = "\nA3distribution RandomSeed {" + last
    f.close()
    valueString = "A2distribution ProbabilityList { "+val[0]+" "+val[1]+" }"
    try:
        f = open(src+workspace+".cfg",'w')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    f.write(first+valueString+'\n'+last)
    f.close()
    #run the simulation to test the value
    return testSim()

def editAssignM3(value):
    #check if the value is like 10 s, 10 h, 5 h
    #parse the value
    val = value.split(',')
    if len(val) != 2:
        print(Fore.RED+"[!] the list must contain 2 elements: [errorProbability,passProbability]")
        return False
    for v in range(len(val)):
        val[v] = val[v].strip(' ')
    #insert the values
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    first = factory.split("A3distribution ProbabilityList { ")[0]
    last = factory.split("PassedDistribution RandomSeed {")[1]
    last = "\nPassedDistribution RandomSeed {" + last
    f.close()
    valueString = "A3distribution ProbabilityList { "+val[0]+" "+val[1]+" }"
    try:
        f = open(src+workspace+".cfg",'w')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    f.write(first+valueString+'\n'+last)
    f.close()
    #run the simulation to test the value
    return testSim()

def editBR(value): #branch between machine1 machine2 machine3
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    first = factory.split("BranchWorkline Choice { ")[0]
    last = factory.split("InspectionBranch NextComponentList { ")[1]
    last = "InspectionBranch NextComponentList { " + last
    f.close()
    branchString = "BranchWorkline Choice { '"+value+"' }"
    try:
        f = open(src+workspace+".cfg",'w')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    f.write(first+branchString+'\n'+last)
    f.close()
    #run the simulation to test the condition
    return testSim()

def editRD(value): #run duration
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    first = factory.split("Simulation RunDuration {")[0]
    last = factory.split("Simulation GlobalSubstreamSeed { ")[1]
    last = "Simulation GlobalSubstreamSeed { " + last
    f.close()
    runDurationString = "Simulation RunDuration { "+value+" h }"
    try:
        f = open(src+workspace+".cfg",'w')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    f.write(first+runDurationString+'\n'+last)
    f.close()
    #run the simulation to test the condition
    return testSim()

def editFpph(value): #factory production per hour
    #check if the value is acceptable
    #check if it respect spaces { n h n }, starts with { 0 h 0 } and follow with { number h number )
    re_spaces = r"^\{ 0 h 0 \}( \{ \d+ h \d+ \})*$"
    re_values = r"^\s*\{\s*0\s+h\s+0\s*\}(\s*\{\s*\d+\s+h\s+\d+\s*\})*\s*$"
    if not re.match(re_values,value) or not re.match(re_spaces,value.strip(' ')):
        print(Fore.RED+"[!] Syntax error: The input must start with { 0 h 0 } and following with { n h n }, respecting the spacing { n h n } { n1 h n1 } { n2 h n2 } ...")
        return False
    #check if its monotonary (n2<n2+1) by checking all the n2 values
    n2_value = [int(v) for v in re.findall(r'\{\s*\d+\s+h\s+(\d+)\s*\}', value)]
    for i in range(len(n2_value) - 1):
        if n2_value[i] > n2_value[i+1]:
            print(Fore.RED+"[!] Syntax error: The input must be a TimeSeries that increases monotonically")
            return False
    #continue if passed all checks
    try:
        f = open(src+workspace+".cfg",'r')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    factory = f.read()
    first = factory.split("FactoryProductionPerHour Value {")[0]
    string = factory.split("# *** TimeSeries ***")[1]
    string = string.split("FactoryProductionPerHour CycleTime")[0]
    last = factory.split("FactoryProductionPerHour CycleTime { 24  h }")[1]
    last = "FactoryProductionPerHour CycleTime { 24  h }" + last
    f.close()
    productionPerHourString = newProductionPerHour(string,value)
    try:
        f = open(src+workspace+".cfg",'w')
    except Exception as e:
        print(Fore.RED+"[!] "+str(e)+Fore.WHITE)
        exit(1)
    f.write(first[:-2]+productionPerHourString+'\n'+last)
    f.close()
    #run the simulation to test the condition
    return testSim()

def testSim() -> bool: #run the simulation to test
    cfg_path = src + workspace + ".cfg"
    backup_path = cfg_path + ".bak"
    #create a backup before testing it
    try:
        shutil.copyfile(cfg_path, backup_path)
    except Exception as e:
        print(Fore.RED + "[!] Impossibile creare il backup: " + str(e) + Fore.WHITE)
        return False
    print(Fore.YELLOW + "[*] testing the values")
    print(" └> this operation may take a while...")
    system('java -jar ' + installFolder + 'JaamSim.jar ' + cfg_path + ' -b -h')
    
    #if it works, remove backup and dat
    if workspace + ".dat" in listdir(src):
        print(Fore.GREEN + "[+] condition correct")
        print(" ├> values updated")
        remove(src + workspace + ".dat")
        if path.exists(backup_path):
            remove(backup_path)
        print(" └> .dat testing case removed")
        return True
    else: #if not works, restore from backup
        print(Fore.RED + "[!] condition invalid")
        print(" ├> restoring file before branch condition")
        try:
            if path.exists(backup_path):
                shutil.move(backup_path, cfg_path)
        except Exception as e:
            print(Fore.RED + "[!] Errore nel ripristino del backup: " + str(e) + Fore.WHITE)
        print(" └> file restored")
        return False

def runSimulation(plot):
    #run the simulation (-b = immediately) and (-h = without GUI)
    esito = system('java -jar '+installFolder+'JaamSim.jar '+workspace+' -b -h')
    if esito==0:
        return True
    else: #error
        return False

def newProductionPerHour(string, value) -> str:
    newString = string.split("{")[0]    
    return (newString+"{ "+value+" }")

def deleteFactoryEdited(name):
    #delete the selected factory
    if name == 'factoryZero':
        name = '°'
    if name == 'default':
        name = 'FactoryEdited'
    print(Fore.GREEN+"[+] deleting "+name+Fore.LIGHTGREEN_EX)
    if path.exists(src+name+".cfg"):
        remove(src+name+".cfg")
        print(" ├> "+name+".cfg deleted")
    else:
        print(Fore.RED+"[!] "+name+" doesn't exists")
        return
    if path.exists(src+name+".rep"):
        remove(src+name+".rep")
        print(" ├> "+name+".rep deleted")
    if path.exists(src+name+".log"):
        remove(src+name+".log")
        print(" ├> "+workspace+".log deleted")
    if path.exists(src+name+".dat"):
        remove(src+name+".dat")
        print(" ├> "+name+".dat deleted")
    print(Fore.YELLOW+" └> "+name+" successfully deleted")
