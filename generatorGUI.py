#!/usr/bin/python3
import os
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from PIL import Image, ImageTk
#mock to avoid crash while testing
try:
    import jaamPyFunctions as jpf
except ImportError:
    class MockJPF:
        workspace = ""
        def showMachines(self): return []
    jpf = MockJPF()

factoriesShowing = None

class Main:
    def __init__(self, master):
        #initialization
        self.master = master
        self.master.title("Generator")
        self.master.config(bg="#001c8b")
        self.master.geometry("700x500")
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
        self.menu_0_0 = tk.Menu(self.menu_0, tearoff=0)
        self.menu_0_0.add_command(label="Load default factory", command=lambda: self.defaultFactoryButton())
        self.menu_0_0.add_command(label="Load factory with custom options", command=lambda: self.customFactoryButton())
        self.menu_0.add_cascade(label="Load a factory", menu=self.menu_0_0)
        self.menu_0.add_command(label="Show factories", command=lambda: self.showFactories())
        self.menu_0.add_command(label="Save as", command=lambda: self.saveAs())
        self.menu_0.add_command(label="Delete a factory", command=lambda: self.delFactory())
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

        #setting label (label)
        self.settinglabel = tk.Text(master=self.text_frame,font=("Helvetica", 12), bg="#084999", fg="#ffffff", bd=0, highlightthickness=0, wrap="word", yscrollcommand=self.scrollbar.set)
        self.settinglabel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.settinglabel.yview)

        # Inserimento testo iniziale in sola lettura
        self.settinglabel.insert("1.0", "no factory selected")
        self.settinglabel.config(state="disabled")

        
        #right label (Pannello laterale destro)
        self.style.configure("rightlabel.TLabel", background="#084999", foreground="#ffffff", anchor="n")
        self.rightlabel = ttk.Label(master=self.master, text="Edit the Factory", style="rightlabel.TLabel", anchor="n")
        self.rightlabel.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=(0, 20), pady=(5, 15))

        #configurazione griglia interna per i pulsanti di destra
        for i in range(6):
            self.rightlabel.rowconfigure(i, weight=1)
        self.rightlabel.columnconfigure(0, weight=1)

        #buttons on right
        self.style.configure("rundurbutton.TButton", background="#E4E2E2", foreground="#000")
        self.style.map("rundurbutton.TButton", background=[("active", "#E4E2E2")], foreground=[("active", "#000")])
        
        self.rundurbutton = ttk.Button(master=self.rightlabel, text="run duration", style="rundurbutton.TButton", command=lambda: self.runEdit())
        self.rundurbutton.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.pphbutton = ttk.Button(master=self.rightlabel, text="production per hour", style="pphbutton.TButton", command=lambda: self.productionEdit())
        self.pphbutton.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.branchbutton = ttk.Button(master=self.rightlabel, text="branch condition", style="branchbutton.TButton", command=lambda: self.branchCond())
        self.branchbutton.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        self.m1button = ttk.Button(master=self.rightlabel, text="edit the Machinery 1", style="m1button.TButton", command=lambda: self.editM1())
        self.m1button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

        self.m2button = ttk.Button(master=self.rightlabel, text="edit the Machinery 2", style="m2button.TButton", command=lambda: self.editM2())
        self.m2button.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

        self.m3button = ttk.Button(master=self.rightlabel, text="edit the Machinery 3", style="m3button.TButton", command=lambda: self.editM3())
        self.m3button.grid(row=5, column=0, padx=5, pady=5, sticky="ew")

    def saveAs(self, *args):
        print("Save as clicked")
        if jpf.workspace == '':
            return
        nameChosen = self.askForInput()
        if nameChosen != '':
            if nameChosen+'.cfg' in os.listdir(jpf.src):
                n = messagebox.askyesno('file already exists','do you want to override it?')
                if not n:
                    return
            jpf.saveWorkspace(nameChosen,False)
            self.updateFactorySettings()
            #messagebox.showinfo('Saved','Operation completed')
            
    def defaultFactoryButton(self, *args):
        print("Load default factory clicked")
        if 'FactoryEdited' not in os.listdir(jpf.src):
            jpf.newWorkspace('FactoryEdited')
        jpf.workspace = 'FactoryEdited'
        self.updateFactorySettings()
        
    def customFactoryButton(self, *args):
        print("Load factory with custom options clicked")
        self.showFactories()
        selection = self.askForInput()
        if selection != '':
            if selection+'.cfg' in os.listdir(jpf.src):
                jpf.workspace = selection
                self.updateFactorySettings()
        
    def delFactory(self,*args):
        global factoriesShowing
        print("Delete factory clicked")
        self.showFactories()
        selection = self.askForInput()
        self.showFactories()
        factoriesShowing.destroy()
        if selection != '':
            jpf.deleteFactoryEdited(selection)
            
    def showFactories(self,*args):
        #if window is opened by another function
        global factoriesShowing
        if factoriesShowing is not None and factoriesShowing.winfo_exists():
            return
        #body of the function
        print("Show factories clicked")
        factories = jpf.showWorkspaces()
        #open the window factoriesShowing
        factoriesShowing = tk.Toplevel(root)
        factoriesShowing.title("Factories' list")
        factoriesShowing.geometry("300x250")
        #title
        label = tk.Label(factoriesShowing, text="Factories:", font=("Arial", 11, "bold"))
        label.pack(pady=10)
        #window (frame, scrollbar, listbox)
        frame_lista = tk.Frame(factoriesShowing)
        frame_lista.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set, font=("Arial", 10))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        #insert names in the listbox
        for f in factories:
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
        self.master.title("Generator - "+jpf.workspace)
        #update workspace label
        self.workspacelabel['text'] = "current workspace: "+jpf.workspace
        #update settinglabel
        string = ""
        par = jpf.showMachines()
        parC = ["production per hour", "simulation duration", "branch condition",
                ["Minimum time between failures of m1 (exponential)","Maximum time between failures of m1 (exponential)","Mean time between failures of m1 (exponential)"],
                ["Shape of the TBF weibull dist of m2","Scale of the TBF weibull dist of m2"],
                ["Shape of the TBF weibull dist of m3","Scale of the TBF weibull dist of m3"],["Minimum time to repair m1","Maximum time to repair m1"],
                ["Minimum time to repair m2","Maximum time to repair m2"],["Minimum time to repair m3","Maximum time to repair m3"],
                ["Maintenance 1 interval","Maintenance 1 duration"],
                ["Maintenance 2 interval","Maintenance 2 duration"],
                ["Maintenance 3 interval","Maintenance 3 duration"],
                ["Minimum processing time of machinery 1","Maximum processing time of machinery 1"],
                ["Minimum processing time of machinery 2","Maximum processing time of machinery 2"],
                ["Minimum processing time of machinery 3","Maximum processing time of machinery 3"],
                ["Probability of error by machinery 1", "Probability of success by machinery 1"],
                ["Probability of error by machinery 2", "Probability of success by machinery 2"],
                ["Probability of error by machinery 3", "Probability of success by machinery 3"]]
        self.settinglabel.config(state="normal")
        self.settinglabel.delete("1.0", tk.END)
        for p in range(len(par)):
            if isinstance(par[p],str):
                string += "-> "+parC[p]+": "+par[p]+"\n"
            else:
                string+='\n'
                for a in range(len(par[p])):
                    string +="-> "+parC[p][a]+": "+par[p][a]+'\n'
        self.settinglabel.insert("1.0", string)
        self.settinglabel.config(state="disabled")

    def askForInput(self,*args) -> str:
        stringPopup = tk.Tk()
        stringPopup.withdraw() 
        result = simpledialog.askstring("Input", "insert:")
        if not result:
            messagebox.showerror("Error", "the string cannot be empty")
        return result
        
    def run(self,*args):
        print("running")
        if jpf.workspace != '':
            messagebox.showinfo('Running...','This operation may take a while')
            jpf.runSimulation(True)
            messagebox.showinfo('Operation Completed!','The results are plotted on the screen')

    def plotRunPDF(self,*args): #plot the pdf of the last simulation if available
        print("plotpdf clicked")
        if jpf.last != '':
            jpf.plotPdf('lastrun')
        else:
            messagebox.showwarning('Warning','You must run at least a simulation before print the PDF file')
        
    def plotRun(self,*args): #select the simulation from which plot the graph
        print("plotrun clicked")
        if jpf.workspace != '':
            #load .dat files
            files = []
            for file in os.listdir('reports'):
                if file[-4:] == '.dat' and jpf.workspace in file: #select only .dat files with the name of the current factory
                    files.append(file)
            #window
            popup = tk.Toplevel(root)
            popup.title("Report files")
            popup.geometry("700x500")

            tk.Label(popup, text="Select the runned simulation:", font=("Arial", 11, "bold")).pack(pady=10)

            canvas = tk.Canvas(popup, highlightthickness=0)
            scrollbar = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
            frameBtn = tk.Frame(canvas)
            frameBtn.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

            canvas.create_window((0, 0), window=frameBtn, anchor="nw", width=680)
            canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True, padx=10, pady=5)
            #mouse movement of the window
            def mouseWheel(event):
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            canvas.bind_all("<MouseWheel>", mouseWheel)
            #insert a button for each .dat file
            for f in files:
                btn = tk.Button(frameBtn, text=f, command=lambda fname=f: jpf.plotGraph(fname),width=80,anchor="w",padx=10)
                btn.pack(pady=3, fill="x", expand=True)
        else:
            messagebox.showwarning('Warning','You must select a factory before plot the results')

    def openDatFile(self,*args): #open the list of the .dat file to view them in calc format
        print("opendat clicked")
        if jpf.workspace != '':
            #load .dat files
            files = []
            for file in os.listdir('reports'):
                if file[-4:] == '.dat' and jpf.workspace in file: #select only .dat files with the name of the current factory
                    files.append(file)
            #window
            popup = tk.Toplevel(root)
            popup.title("Report files")
            popup.geometry("700x500")

            tk.Label(popup, text="Select the runned simulation:", font=("Arial", 11, "bold")).pack(pady=10)

            canvas = tk.Canvas(popup, highlightthickness=0)
            scrollbar = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
            frameBtn = tk.Frame(canvas)
            frameBtn.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

            canvas.create_window((0, 0), window=frameBtn, anchor="nw", width=680)
            canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True, padx=10, pady=5)
            #mouse movement of the window
            def mouseWheel(event):
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            canvas.bind_all("<MouseWheel>", mouseWheel)
            #insert a button for each .dat file
            for f in files:
                btn = tk.Button(frameBtn, text=f, command=lambda fname=f: jpf.openDat(fname),width=80,anchor="w",padx=10)
                btn.pack(pady=3, fill="x", expand=True)
        else:
            messagebox.showwarning('Warning','You must select a factory before open the results')

    def showReports(self,*args):
        print("showreports clicked")
        if jpf.workspace != '':
            #load .dat files
            files = []
            for file in os.listdir('reports'):
                if file[-4:] == '.dat' and jpf.workspace in file: #select only .dat files with the name of the current factory
                    files.append(file)
            #window
            popup = tk.Toplevel(root)
            popup.title("Report files")
            popup.geometry("700x500")

            tk.Label(popup, text="Select the runned simulation:", font=("Arial", 11, "bold")).pack(pady=10)

            canvas = tk.Canvas(popup, highlightthickness=0)
            scrollbar = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
            frameBtn = tk.Frame(canvas)
            frameBtn.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

            canvas.create_window((0, 0), window=frameBtn, anchor="nw", width=680)
            canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True, padx=10, pady=5)
            #mouse movement of the window
            def mouseWheel(event):
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            canvas.bind_all("<MouseWheel>", mouseWheel)
            #insert a button for each .dat file to generate the relative PDF
            for f in files:
                btn = tk.Button(frameBtn, text=f, command=lambda fname=f: jpf.plotPdf(fname),width=80,anchor="w",padx=10)
                btn.pack(pady=3, fill="x", expand=True)
        else:
            messagebox.showwarning('Warning','You must select a factory before select the reports')

    def runEdit(self,*args): #edit the duration of the simulation
        print("edit rundur clicked")
        if jpf.workspace != '':
            stringPopup = tk.Tk()
            stringPopup.withdraw()
            try:
                result = int(simpledialog.askstring("Run Duration", "insert the new run duration (the value is in hours):\nExample: 5"))
            except (TypeError, ValueError):
                messagebox.showerror("Error!","The input must be an integer")
            jpf.editRD(str(result))
            messagebox.showinfo('Updated!', "the run duration is updated to "+str(result))
            self.updateFactorySettings()
        else:
            messagebox.showwarning('Warning','You must select a factory before edit its parameters')

    def productionEdit(self,*args): #edit the arrival of the components for each hour of the simulation
        print("edit production per hour clicked")
        if jpf.workspace != '':
            stringPopup = tk.Tk()
            stringPopup.withdraw()
            result = simpledialog.askstring("Production per Hour", "insert the new production per hour:\nExample: { 0 h 0 } { 13 h 90 } { 14 h 90 } { 24 h 270 }")
            print(result)
            if jpf.editFpph(str(result)):
                messagebox.showinfo('Updated!', "the production per hour is updated to "+str(result))
                self.updateFactorySettings()
            else:
                messagebox.showerror("Error!","The input must increase monotonically and start with { 0 h 0 } and following with { n h n }, respecting the spacing { n h n } { n1 h n1 } { n2 h n2 } ...")
        else:
            messagebox.showwarning('Warning','You must select a factory before edit its parameters')

    def branchCond(self, *args): #edit the branch condition bewteen machinery 1,2,3
        print("branch clicked")
        if jpf.workspace != '':
            stringPopup = tk.Tk()
            stringPopup.withdraw()
            result = simpledialog.askstring("Branch Condition", "insert the new branch condition:\nExample: [Machine1].Working == 0 && [Machine1].Maintenance == 0 && [Machine1].Breakdown == 0 ? 1 : 2")
            messagebox.showinfo('Testing the condition!', "This operation may take a while...")
            if jpf.editBR(str(result)):
                messagebox.showinfo('Updated!', "the branch condition is updated to "+str(result))
                self.updateFactorySettings()
            else:
                messagebox.showerror("Error!","The condition contains a syntax error")
        else:
            messagebox.showwarning('Warning','You must select a factory before edit its parameters')

    def editM1(self, *args): #open the control window of the Machinery 1
        print("m1 clicked")
        self.updateMachineryPopup("1")
        
    def editM2(self, *args): #open the control window of the Machinery 2
        print("m2 clicked")
        self.updateMachineryPopup("2")

    def editMe(self, *args): #open the control window of the Machinery 3
        print("m3 clicked")
        self.updateMachineryPopup("3")

    #MANAGEMENT OF THE MACHINERY ONE, TWO, THREE
    def updateMachineryPopup(self,func,*args):
        if jpf.workspace != '':
            insertedWidget = {}
            popup = tk.Toplevel(root)
            popup.title("Update Machinery "+func)
            popup.geometry("500x500")
            popup.configure(padx=20, pady=20)
            #title
            lbl_titolo = tk.Label(popup, text="Update the Machinery One Parameters", font=("Arial", 14, "bold"), fg="#333333")
            lbl_titolo.pack(pady=(0, 10))
            #placeholders for textlines
            configFields = [
                ("Error Probability [error,pass]:", "Ex: [0.10,0.90]"),
                ("Time of elaboration [min,max]:", "Ex: [30 s,50 s]"),
                ("Maintenance [interval,duration]:", "Ex: [1 w, 1 h]"),
                ("(TTR) Time to Repair [min,max]:", "Ex: [2 h, 5 h]")
                ]
            if func == '1':
                configFields.append(("(TBF) Time Between Failures\nExponential Distibution [min,max,mean]:", "Ex: [2 s,20 h,5 h]"))
            else:
                configFields.append(("(TBF) Time Between Failures\nWeibull Distribution [min,max]:", "Ex: [113 h,2]"))
            for textLabel, placeholder in configFields:
                lbl = tk.Label(popup, text=textLabel, font=("Arial", 10, "bold"), anchor="w")
                lbl.pack(fill="x", pady=(5, 2))

                entry = tk.Entry(popup, font=("Arial", 10), fg="gray", bd=1, relief="solid")
                entry.insert(0, placeholder)
                entry.pack(fill="x", ipady=4, pady=(0, 10))
                insertedWidget[textLabel] = (entry, placeholder)
                #placeholders' beheavior
                def on_focus_in(event, ent=entry, ph=placeholder):
                    if ent.get() == ph:
                        ent.delete(0, tk.END)
                        ent.configure(fg="black")
                def on_focus_out(event, ent=entry, ph=placeholder):
                    if ent.get() == "":
                        ent.insert(0, ph)
                        ent.configure(fg="gray")
                entry.bind("<FocusIn>", on_focus_in)
                entry.bind("<FocusOut>", on_focus_out)

            def updateMachinery(): #update the machinery fields
                messagebox.showinfo('Testing','we\'re testing the inserted data. This operation may take a while...')
                #get datas from the text lines
                updateResults = []
                for fieldName, (ent, ph) in insertedWidget.items():
                    value = ent.get()
                    if not value == ph: #if placeholder, ignore the field
                        if str(func)=='1':
                            if fieldName == configFields[0][0]: #update the probability error
                                if not jpf.editAssignM1(value.strip(' ').strip(']').strip('[')):
                                    messagebox.showerror('Error in the Probability Error!',"Syntax error. Remember to respect the format in the example")
                            elif fieldName == configFields[1][0]: #update the time of elaboration
                                if not jpf.editProcM1(value.strip(' ').strip(']').strip('[')):
                                    messagebox.showerror('Error in the Elaboration Time!',"Syntax error. Remember to respect the format in the example")
                            elif fieldName == configFields[2][0]: #update the maintenance
                                if not jpf.editMainM1(value.strip(' ').strip(']').strip('[')):
                                    messagebox.showerror('Error in the Maintenance!',"Syntax error. Remember to respect the format in the example")
                            elif fieldName == configFields[3][0]: #update the TTR
                                if not jpf.editTtrM1(value.strip(' ').strip(']').strip('[')):
                                    messagebox.showerror('Error in the TTR!',"Syntax error. Remember to respect the format in the example")
                            elif fieldName == configFields[4][0]: #update the TBF
                                if not jpf.editTbfM1(value.strip(' ').strip(']').strip('[')):
                                    messagebox.showerror('Error in the TBF!',"Syntax error. Remember to respect the format in the example")
                        elif str(func) == '2':
                            if fieldName == configFields[0][0]: #update the probability error
                                if not jpf.editAssignM2(value.strip(' ').strip(']').strip('[')):
                                    messagebox.showerror('Error in the Probability Error!',"Syntax error. Remember to respect the format in the example")
                            elif fieldName == configFields[1][0]: #update the time of elaboration
                                if not jpf.editProcM2(value.strip(' ').strip(']').strip('[')):
                                    messagebox.showerror('Error in the Elaboration Time!',"Syntax error. Remember to respect the format in the example")
                            elif fieldName == configFields[2][0]: #update the maintenance
                                if not jpf.editMainM2(value.strip(' ').strip(']').strip('[')):
                                    messagebox.showerror('Error in the Maintenance!',"Syntax error. Remember to respect the format in the example")
                            elif fieldName == configFields[3][0]: #update the TTR
                                if not jpf.editTtrM2(value.strip(' ').strip(']').strip('[')):
                                    messagebox.showerror('Error in the TTR!',"Syntax error. Remember to respect the format in the example")
                            elif fieldName == configFields[4][0]: #update the TBF
                                if not jpf.editTbfM2(value.strip(' ').strip(']').strip('[')):
                                    messagebox.showerror('Error in the TBF!',"Syntax error. Remember to respect the format in the example")
                        else: #func==3
                            if fieldName == configFields[0][0]: #update the probability error
                                if not jpf.editAssignM3(value.strip(' ').strip(']').strip('[')):
                                    messagebox.showerror('Error in the Probability Error!',"Syntax error. Remember to respect the format in the example")
                            elif fieldName == configFields[1][0]: #update the time of elaboration
                                if not jpf.editProcM3(value.strip(' ').strip(']').strip('[')):
                                    messagebox.showerror('Error in the Elaboration Time!',"Syntax error. Remember to respect the format in the example")
                            elif fieldName == configFields[2][0]: #update the maintenance
                                if not jpf.editMainM3(value.strip(' ').strip(']').strip('[')):
                                    messagebox.showerror('Error in the Maintenance!',"Syntax error. Remember to respect the format in the example")
                            elif fieldName == configFields[3][0]: #update the TTR
                                if not jpf.editTtrM3(value.strip(' ').strip(']').strip('[')):
                                    messagebox.showerror('Error in the TTR!',"Syntax error. Remember to respect the format in the example")
                            elif fieldName == configFields[4][0]: #update the TBF
                                if not jpf.editTbfM3(value.strip(' ').strip(']').strip('[')):
                                    messagebox.showerror('Error in the TBF!',"Syntax error. Remember to respect the format in the example")
                messagebox.showinfo('Updated!','The Machinery has been successfully updated')
                #update the settings label of the factory
                self.updateFactorySettings()
                #close the window
                popup.destroy()

            #button to send the update of the machinery
            btn = tk.Button(popup, text="UPDATE!", font=("Arial", 11, "bold"), bg="#001c8b", fg="white", command=updateMachinery, cursor="hand2")
            btn.pack(fill="x", pady=(15, 0), ipady=6)
        else:
            messagebox.showwarning('Warning','You must select a factory before edit its machinery')



if __name__ == '__main__':
    root = tk.Tk()
    app = Main(root)
    root.mainloop()
