#!/usr/bin/python3
import os
import shutil
import tempfile
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import filedialog
from tkinter import Toplevel, Label
from PIL import Image, ImageTk
from datetime import datetime
from fpdf import FPDF
from pandas import DataFrame, to_numeric
#mock to avoid crash while testing
try:
    import jaamPyFunctions as jpf
except ImportError:
    class MockJPF:
        workspace = ""
        def showMachines(self): return []
    jpf = MockJPF()

factoriesShowing = None
cfg_files = []
cfg_esit = []
resString = ''
OEEdict = {}
buttons_r = []

class Main:
    def __init__(self, master):
        #initialization
        self.master = master
        self.master.title("Factory Executor")
        self.master.config(bg="#001c8b")
        self.master.geometry("700x345")
        self.master.minsize(650, 320)
        self.master.rowconfigure(1, weight=1) #settinglabel and right buttons expands in height
        self.master.rowconfigure(2, weight=0) #downlabel stay fixed in height
        self.master.columnconfigure(0, weight=1) #left label expand in width
        self.master.columnconfigure(1, weight=0) #rightlabel stay fixed in width
        
        self.style = ttk.Style(self.master)
        self.style.theme_use("clam")

        #menu
        self.menu = tk.Menu(self.master)
        self.master.config(menu=self.menu)
        
        self.menu_0 = tk.Menu(self.menu, tearoff=0)
        self.menu_0.add_cascade(label="Load a simulations set", command=lambda: self.loadSetButton())
        self.menu_0.add_command(label="Show simulations in the selected set", command=lambda: self.showFactories())
        self.menu_0.add_cascade(label="OEE Analysis", command=lambda: self.oeeAnalysis())
        self.menu.add_cascade(label="Start", menu=self.menu_0)
        
        self.menu_1 = tk.Menu(self.menu, tearoff=0)
        self.menu_1.add_command(label="Help", command=lambda: self.helpMe())
        self.menu_1.add_command(label="Documentation", command=lambda: self.documentation())
        self.menu_1.add_command(label="About", command=lambda: messagebox.showinfo('About','version: 2.0 - alpha'))
        self.menu.add_cascade(label="Help", menu=self.menu_1)        

        #workspace label
        self.style.configure("workspacelabel.TLabel", background="#001c8b", foreground="#ffffff", anchor="nw")
        self.workspacelabel = ttk.Label(master=self.master, text="current workspace", style="workspacelabel.TLabel")
        self.workspacelabel.grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(4, 0))

        #factory setting label (frame)
        self.text_frame = tk.Frame(master=self.master, bg="#084999")
        self.text_frame.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=(5, 5))
        
        #scrollbar for setting label
        self.scrollbar = ttk.Scrollbar(master=self.text_frame, orient="vertical")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        #down label
        self.style.configure("downlabel.TLabel", background="#084999", foreground="#ffffff")
        self.downlabel = ttk.Label(master=self.master, style="downlabel.TLabel")
        self.downlabel.grid(row=2, column=0, sticky="ew", padx=(20, 10), pady=(5, 15))

        #config grid for down buttons
        for i in range(5):
            self.downlabel.columnconfigure(i, weight=1)
        self.downlabel.rowconfigure(0, weight=1)

        #down buttons
        self.runbutton = ttk.Button(master=self.downlabel, text="Run", style="runbutton.TButton", command=lambda: self.run())
        self.runbutton.grid(row=0, column=0, padx=5, pady=8, sticky="ew")

        self.pdfbutton = ttk.Button(master=self.downlabel, text="Save as PDF", style="pdfbutton.TButton", command=lambda: self.plotPDF())
        self.pdfbutton.grid(row=0, column=2, padx=5, pady=8, sticky="ew")

        self.listdatbutton = ttk.Button(master=self.downlabel, text="Clear Screen", style="listdatbutton.TButton", command=lambda: self.clearScreen())
        self.listdatbutton.grid(row=0, column=4, padx=5, pady=8, sticky="ew")
        
    def loadSetButton(self, *args):
        print("Load a set of simulations to execute")
        self.clearScreen()
        folder_path = filedialog.askdirectory(
            title="Select the simulations set",
            initialdir=getattr(jpf, 'src', None)
        )
        if folder_path:
            jpf.workspace = folder_path
            print(folder_path)
            self.updateFactorySettings()

    def showFactories(self, *args):
        global factoriesShowing
        if factoriesShowing is not None and factoriesShowing.winfo_exists():
            return
        print("Show simulations set")
        try:
            workspace_path = jpf.workspace
            factories = os.listdir(workspace_path)
        except Exception as e:
            print(f"Errore nella lettura del percorso: {e}")
            factories = []
        factoriesShowing = tk.Toplevel(root)
        factoriesShowing.title("Factories' list")
        factoriesShowing.geometry("300x250")
        label = tk.Label(factoriesShowing, text="Factories:", font=("Arial", 11, "bold"))
        label.pack(pady=10)
        frame_lista = tk.Frame(factoriesShowing)
        frame_lista.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set, font=("Arial", 10))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        for f in factories:
            if 'cfg' in f: #insert only jaamsim files
                listbox.insert(tk.END, f)

    def helpMe(self, *args):
        print("Help clicked")
        if os.name == 'nt': #windows
            os.startfile('README.md')
        else: #not windows
            os.system('README.md')
        
    def documentation(self, *args):
        print("Documentation clicked")
        if os.name == 'nt': #windows
            os.startfile('documentation.pdf')
        else: #not windows
            os.system('documentation.pdf')

    def updateFactorySettings(self,*args):
        #update name of the window
        self.master.title("Executor - "+jpf.workspace)
        #update workspace label
        self.workspacelabel['text'] = "current set: "+jpf.workspace
        #clear the screen from the previous simulations
        self.clearScreen()
        
    def run(self,*args):
        self.clearScreen()
        global cfg_files
        global cfg_esit
        global resString
        print("running: ")
        fol = jpf.workspace
        if fol != '':
            messagebox.showinfo('Ready!','In the moment you\'ll click \'okay\' the program will start to run. This operation may take a while')
            #ottieni le simulazioni (.cfg) del set (cartella)
            for file_name in os.listdir(fol):
                full_path = os.path.join(fol, file_name)
                if os.path.isfile(full_path) and file_name.endswith('.cfg'):
                    cfg_files.append(file_name)
            #esegui tutte le simulazioni, inserisci il pulsante e salva l'esito
            for sim in cfg_files:
                jpf.workspace = os.path.join(fol,sim)
                print("->"+str(jpf.workspace))
                cfg_esit.append(jpf.runSimulation(False))
                print(cfg_esit)
                self.addSimResults(sim,cfg_esit[-1])
            #rimuovi i .rep
            for file_name in os.listdir(fol):
                full_path = os.path.join(fol, file_name)
                if os.path.isfile(full_path) and file_name.endswith('.rep'):
                    os.remove(full_path)
            #crea la cartella con i risultati
            resString = 'results_'+str(datetime.now().day)+'-'+str(datetime.now().month)+'-'+str(datetime.now().year)+'_'+str(datetime.now().hour)+'-'+str(datetime.now().minute)+'-'+str(datetime.now().second)
            os.mkdir(os.path.join(fol, resString))
            #muovi i .dat nella cartella risultati
            for file_name in os.listdir(fol):
                full_path = os.path.join(fol, file_name)
                if os.path.isfile(full_path) and file_name.endswith('.dat'):
                    destination_file_path = os.path.join(resString, file_name)
                    shutil.move(full_path, os.path.join(fol, destination_file_path))
            messagebox.showinfo('Operation Completed!','The results are plotted on the screen')
        else:
            messagebox.showerror('Workspace Empty!','You need to select a sim set before run the simulations')
        jpf.workspace = fol

    def addSimResults(self, *args): #0=title, 1=work_or_not
        #insert the button into the setting frame
        buttonResult = tk.Button(master=self.text_frame, text=args[0], command=lambda: self.plotGraph(args[0],args[1]))
        #change colour based on works or not
        if args[1]:
            buttonResult.config(bg="green", fg="white")
        else:
            buttonResult.config(bg="red", fg="white")
        buttons_r.append([buttonResult.cget("bg"),buttonResult.cget("text")])
        #stacked vertically, take up horizontally
        buttonResult.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

    def plotGraph(self,*args):
        print("plotting graphs")
        if args[1]:
            jpf.plotGraph(os.path.join(jpf.workspace,resString,((args[0][:-4])+".dat")))

    def plotPDF(self, *args): #plot the pdf of the last simulation if available
        global resString
        global buttons_r
        global OEEdict
        print("plotpdf clicked")
        verdi = []
        rossi = []
        #get buttons OK/KO
        for widget in buttons_r:
            colore = widget[0]
            testo = widget[1]
            if colore in ["green", "#00ff00"]: 
                verdi.append(testo)
            elif colore in ["red", "#ff0000"]:
                rossi.append(testo)        
        #pdf initialization
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        #opening
        pdf.set_font("Arial", 'B', 24)
        pdf.cell(0, 20, "Simulations Set Report", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 150, 0)
        pdf.cell(0, 10, "Successfull Simulations:", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.set_text_color(0, 0, 0)
        for v in verdi:
            pdf.cell(0, 8, f"> {v}", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 10, "Failed Simulations:", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.set_text_color(0, 0, 0)
        for r in rossi:
            pdf.cell(0, 8, f"X {r}", ln=True)
        #OEE analysis graph
        if OEEdict:
            try:
                simulazioni = list(OEEdict.keys())
                qualita = [OEEdict[s][0] for s in simulazioni]
                oee_m1 = [OEEdict[s][1][2] for s in simulazioni]
                oee_m2 = [OEEdict[s][2][2] for s in simulazioni]
                oee_m3 = [OEEdict[s][3][2] for s in simulazioni]

                fig, ax = plt.subplots(figsize=(10, 5))
                x = range(len(simulazioni))
                width = 0.2

                ax.bar([i - 1.5*width for i in x], qualita, width, label='Quality (%)')
                ax.bar([i - 0.5*width for i in x], oee_m1, width, label='OEE M1 (%)')
                ax.bar([i + 0.5*width for i in x], oee_m2, width, label='OEE M2 (%)')
                ax.bar([i + 1.5*width for i in x], oee_m3, width, label='OEE M3 (%)')

                ax.set_xlabel('Simulations')
                ax.set_xticks(list(x))
                ax.set_xticklabels(simulazioni, rotation=10)
                ax.set_ylabel('Percentage (%)')
                ax.set_title('Comparison between Performance, Quality and OEE of the Simulations')
                ax.legend()
                plt.tight_layout()
                
                temp_grafico_path = os.path.join(tempfile.gettempdir(), "temp_global_chart.png")
                fig.savefig(temp_grafico_path, format="png")
                plt.close(fig)

                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(0, 10, "Global comparison(OEE and Quality)", ln=True)
                pdf.ln(5)
                pdf.image(temp_grafico_path, x=15, w=260)
                os.remove(temp_grafico_path)
            except Exception as e:
                print(f"Error during the generation of the OEE graph: {e}")
        #graphs and tables for the green files
        for v in verdi:
            nome_dat = v[:-4] + ".dat"
            file_path = os.path.join(jpf.workspace, resString, nome_dat)
            if not os.path.exists(file_path):
                continue
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            header = []
            data_rows = []
            for line in lines:
                parts = line.split()
                if not parts:
                    continue
                if not header:
                    parts[0] = parts[0].replace('\ufeff', '')
                    header = parts
                elif len(parts) == len(header):
                    data_rows.append(parts)
            if len(header) < 3:
                continue
            df = DataFrame(data_rows, columns=header)
            for col in df.columns:
                if col not in ['Scenario', 'Replication']:
                    df[col] = df[col].astype(str).str.replace(r'\[.*?\]', '', regex=True)
            for col in df.columns:
                df[col] = to_numeric(df[col], errors='coerce')
                
            pdf.add_page()
            pdf.set_font("Arial", 'B', 18)
            pdf.cell(0, 15, f"Risultati: {v}", ln=True, align='L')
            #inserting OEE table for each simulation
            if v in OEEdict:
                dati_sim = OEEdict[v]
                q_val = dati_sim[0]
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 8, f"System quality yield (Quality): {q_val}%", ln=True)
                pdf.ln(2)
                #
                pdf.set_font("Courier", 'B', 10)
                pdf.cell(50, 6, "Machine", 1)
                pdf.cell(40, 6, "Availability", 1)
                pdf.cell(40, 6, "Performance", 1)
                pdf.cell(40, 6, "OEE", 1, ln=True)
                pdf.set_font("Courier", '', 10)
                macchine_nomi = ["Machine1", "Machine2", "Machine3"]
                for i in range(3):
                    a, p, oee = dati_sim[i+1]
                    pdf.cell(50, 6, macchine_nomi[i], 1)
                    pdf.cell(40, 6, f"{a}%", 1)
                    pdf.cell(40, 6, f"{p}%", 1)
                    pdf.cell(40, 6, f"{oee}%", 1, ln=True)
                pdf.ln(8)
            target_columns = header[2:] 
            colours = {1: 'red', 2: 'teal', 3: 'green'}
            n_cols = len(colours)
            #graphs
            for col_name in target_columns:
                #create a figure
                fig, axes = plt.subplots(1, n_cols, figsize=(15, 4), sharey=True)
                if n_cols == 1: axes = [axes]
                for c, (scenario, colour) in enumerate(colours.items()):
                    ax = axes[c]
                    dt_scenario = df[df['Scenario'] == scenario]
                    if not dt_scenario.empty:
                        ax.bar(dt_scenario['Replication'], dt_scenario[col_name], color=colour)
                    ax.set_xlabel('Replication')
                    ax.set_title(f'Scenario {scenario}')            
                clean_title = col_name.split(']')[0] + ']' if ']' in col_name else col_name
                fig.suptitle(clean_title, fontsize=12, fontweight='bold')
                plt.tight_layout()
                tmp_path = os.path.join(tempfile.gettempdir(), "temp_plot.png")
                fig.savefig(tmp_path, format="png")
                plt.close(fig)
                #120mm in Y is max lenght, after 120 is \n
                if pdf.get_y() > 120:
                    pdf.add_page()
                pdf.image(tmp_path, x=10, w=270)
                pdf.ln(5) 
                os.remove(tmp_path)
            #print table
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, f"Data table: {nome_dat}", ln=True)
            chunk_size = 6 #max columns before \n
            for i in range(0, len(header), chunk_size):
                sub_header = header[i:i+chunk_size] 
                #print header of the block
                pdf.set_font("Courier", 'B', 8)
                header_str = " | ".join([str(h)[:20].ljust(20) for h in sub_header])
                pdf.cell(0, 5, header_str, ln=True)
                pdf.cell(0, 5, "-" * len(header_str), ln=True)
                #print rows of this block
                pdf.set_font("Courier", '', 8)
                for row in data_rows:
                    sub_row = row[i:i+chunk_size]
                    row_str = " | ".join([str(item)[:20].ljust(20) for item in sub_row])
                    pdf.cell(0, 5, row_str, ln=True)
                pdf.ln(10) #space before next columns block
        #save pdf
        pdf_output_path = os.path.join(jpf.workspace, resString, "Simulation_Report.pdf")
        pdf.output(pdf_output_path)
        print(f"Report PDF generated in: {pdf_output_path}")
        messagebox.showinfo('Operation Completed!', f'{pdf_output_path} has been successfully generated')
        
    def clearScreen(self,*args):
        print("clearing screen")
        global cfg_files
        global cfg_esit
        global resString
        global OEEdict
        OEEdict.clear()
        cfg_files.clear()
        cfg_esit.clear()
        buttons_r.clear()
        resString = ''
        for widget in self.text_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()

    def oeeAnalysis(self,*args):
        global resString
        dizionario_oee = {}
        print("OOE Analysis")
        #analyze each green
        for widget in self.text_frame.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("bg") == 'green':
                #file parsing
                file_path = os.path.join(jpf.workspace,resString,(widget.cget("text")[:-4])+'.dat')
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                header = []
                data_rows = []  
                for line in lines:
                    parts = line.split()
                    if not parts:
                        continue
                    if not header:
                        parts[0] = parts[0].replace('\ufeff', '')
                        header = parts
                    elif len(parts) == len(header):
                        data_rows.append(parts)
                if len(header) < 3:
                    print(f"File saltato: {widget.cget('text')} (Dati insufficienti)")
                    continue 
                df = DataFrame(data_rows, columns=header)
                #clean data
                for col in df.columns:
                    if col not in ['Scenario', 'Replication']:
                        df[col] = df[col].astype(str).str.replace(r'\[.*?\]', '', regex=True)
                    df[col] = to_numeric(df[col], errors='coerce')
                    
                df = df.dropna()
                #simulation variables
                simDuration_h = 1460.0  #run duration
                cap_performance = True
                #min value of time of machinery
                t_ideale_m1 = 30 / 3600
                t_ideale_m2 = 30 / 3600
                t_ideale_m3 = 50 / 3600 
                #columns .dat (global quality)
                colGoods = '[GearShipping].NumberAdded'
                colWasted1 = '[Waste-Conveyor].NumberAdded'
                colWasted2 = '[Remodel-Conveyor].NumberAdded'
                #columns .dat (input machinery)
                col_count_m1 = '[Workine1-Conveyor].NumberAdded'
                col_count_m2 = '[Workline2-Conveyor].NumberAdded'
                col_count_m3 = '[Workline3-Conveyor].NumberAdded' if '[Workline3-Conveyor].NumberAdded' in df.columns else col_count_m1
                if colGoods not in df.columns:
                    print(f"ignored file: {widget.cget('text')} (no shipping counter in the .dat)")
                    continue
                #calculation
                #quality
                df['TotalSystemCount'] = df[colGoods] + df[colWasted1] + df[colWasted2]
                df['Quality'] = df[colGoods] / df['TotalSystemCount'].replace(0, 1e-9)
                #machinery
                macchine_config = {
                    '[Machine1].WorkingTime': (col_count_m1, t_ideale_m1, 'Machine1'),
                    '[Machine2].WorkingTime': (col_count_m2, t_ideale_m2, 'Machine2'),
                    '[Machine3].WorkingTime': (col_count_m3, t_ideale_m3, 'Machine3')
                }
                for mac_col, (count_col, t_id, nome_m) in macchine_config.items():
                    if mac_col in df.columns:
                        work_time = df[mac_col]
                        #if counter doesn't exist, estimate it
                        effective_count_col = count_col if count_col in df.columns else 'TotalSystemCount'
                        #availability
                        df[f'A_{nome_m}'] = work_time / simDuration_h
                        #performance
                        df[f'P_{nome_m}'] = df.apply(
                            lambda row: 0.0 if row[mac_col] == 0 else (row[effective_count_col] * t_id) / row[mac_col], 
                            axis=1
                        )
                        if cap_performance:
                            df[f'P_{nome_m}'] = df[f'P_{nome_m}'].clip(upper=1.0)
                        #oee
                        df[f'OEE_{nome_m}'] = df[f'A_{nome_m}'] * df[f'P_{nome_m}'] * df['Quality']
                #order results for the printing
                media_simulazione = df.mean(numeric_only=True)
                nome_simulazione = widget.cget("text")
                #round the quality
                quality_val = round(media_simulazione['Quality'] * 100, 2)
                #initialize the list
                dati_simulazione = [quality_val]
                #print log
                print("\n" + "="*50)
                print(f"GLOBAL SIMULATION RESULTS: {nome_simulazione}")
                print("="*50)
                print(f"System Quality Yield (Quality): {quality_val}%")
                for mac_col, (_, _, nome_m) in macchine_config.items():
                    if f'OEE_{nome_m}' in media_simulazione:
                        a = media_simulazione[f'A_{nome_m}'] * 100
                        p = media_simulazione[f'P_{nome_m}'] * 100
                        oee = media_simulazione[f'OEE_{nome_m}'] * 100
                        #save data in the list for each machinery of each simulation
                        dati_simulazione.append([round(a, 2), round(p, 2), round(oee, 2)])
                        print(f"\n--- {nome_m} ---")
                        print(f"  Availability : {a:.2f}%")
                        print(f"  Performance  : {p:.2f}%")
                        print(f"  OEE          : {oee:.2f}%")
                #{"NomeSimulazione" : [quality, [a,p,oee], [a,p,oee], [a,p,oee]]}
                dizionario_oee[nome_simulazione] = dati_simulazione
        #show results in the GUI
        self.showOEE(dizionario_oee)

    def showOEE(self,*args):
        print("=====> SHOWING OEE RESULTS <=====")
        print(args[0])
        dizionario_oee = args[0]
        if not dizionario_oee:
            print("No data")
            return
        #OEE average of the three machinery to find the most efficient simulation
        def efficiencyMetric(item):
            dati = item[1]
            oee_m1 = dati[1][2]
            oee_m2 = dati[2][2]
            oee_m3 = dati[3][2]
            return (oee_m1 + oee_m2 + oee_m3) / 3.0
        simulazioni_ordinate = sorted(dizionario_oee.items(), key=efficiencyMetric, reverse=True)
        #clean the frame
        for widget in self.text_frame.winfo_children():
            widget.destroy()
        #when click the button it opens this new screen
        def openDetails(nome_sim, dati):
            det_win = Toplevel()
            det_win.title(f"Result details: {nome_sim}")
            det_win.geometry("320x320")
            q_val = dati[0]
            Label(det_win, text=f"SIMULATION: {nome_sim}", font=("Arial", 11, "bold")).pack(pady=8)
            Label(det_win, text=f"System Quality Yield (Quality): {q_val}%", fg="blue").pack(anchor="w", padx=15, pady=2)
            macchine_nomi = ["Machine1", "Machine2", "Machine3"]
            for i in range(3):
                a, p, oee = dati[i+1]
                machineryText = (
                    f"--- {macchine_nomi[i]} ---\n"
                    f"  Availability : {a}%\n"
                    f"  Performance  : {p}%\n"
                    f"  OEE          : {oee}%\n"
                )
                Label(det_win, text=machineryText, justify="left", font=("Consolas", 9)).pack(anchor="w", padx=15, pady=2)
        #order the list from most efficient to less efficient
        for nome_sim, dati in simulazioni_ordinate:
            buttonResult = tk.Button(
                master=self.text_frame, 
                text=nome_sim, 
                command=lambda s=nome_sim, d=dati: openDetails(s, d)
            )
            #change button to blue to show it changed
            buttonResult.config(bg="light blue", fg="black")
            buttonResult.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        #generate a comparative graph
        self.drawOEEgraphic(dizionario_oee)

    def drawOEEgraphic(self, dizionario_oee):
        global OEEdict
        simulazioni = list(dizionario_oee.keys())
        qualita = [dizionario_oee[s][0] for s in simulazioni]
        oee_m1 = [dizionario_oee[s][1][2] for s in simulazioni]
        oee_m2 = [dizionario_oee[s][2][2] for s in simulazioni]
        oee_m3 = [dizionario_oee[s][3][2] for s in simulazioni]
        fig, ax = plt.subplots(figsize=(9, 5))
        x = range(len(simulazioni))
        width = 0.2
        ax.bar([i - 1.5*width for i in x], qualita, width, label='Qualità (%)')
        ax.bar([i - 0.5*width for i in x], oee_m1, width, label='OEE M1 (%)')
        ax.bar([i + 0.5*width for i in x], oee_m2, width, label='OEE M2 (%)')
        ax.bar([i + 1.5*width for i in x], oee_m3, width, label='OEE M3 (%)')
        ax.set_xlabel('Simulations')
        ax.set_xticks(list(x))
        ax.set_xticklabels(simulazioni, rotation=10)
        ax.set_ylabel('Percentage (%)')
        ax.set_title('Comparation of Availability, Performance, OEE between all the Simulations')
        ax.legend()
        plt.tight_layout()
        plt.show()
        OEEdict = dizionario_oee

if __name__ == '__main__':
    root = tk.Tk()
    app = Main(root)
    root.mainloop()
