# What-If Analysis suite to Manage Anomalies in Critical Industrial Services

## Table of Contents

* [Overview](#overview)

* [Architecture & Workflow](#architecture--workflow)

  * [1. The Generator](#1-the-generator-generatorguipy)

  * [2. The Executor](#2-the-executor-executorguipy)

* [Key Features](#key-features)

* [Prerequisites & Installation](#prerequisites--installation)

* [Usage](#usage)

* [Built With](#built-with)

* [Author](#author)

## Overview

This software is a Python-based suite integrated with **JaamSim** designed for comprehensive industrial "what-if" simulation analysis.

The software enables the users to generate multiple configurations of a baseline industrial complex, execute them in automated batches, and scientifically classify the outcomes. By evaluating system variations through **OEE (Overall Equipment Effectiveness)**, focusing on machine availability, performance, and overall quality yield. The tool provides robust, data-driven decision support for industrial optimization

## Architecture & Workflow

The suite is based on two separate part to support multi-simulation scenario generation and analysis:

### 1. The Generator \[Example\] (`generatorGUI.py`)

The generation of the configurations can be executed by humans, AI or any other software. Here stands an example tool used to build varying scenarios (N configurations) of the same industrial complex. The baseline system architecture remains constant to ensure valid comparative analysis, while specific parameters are altered:

* **Global Conditions:** Adjust production per hour (PPH), and workload branching/routing between parallel machines.

* **Machinery Parameters:** For each machine (M1, M2, M3), users can modify failure distributions (TBF - Exponential/Weibull), repair times (TTR), fixed maintenance schedules, processing times, and error/success probabilities.

By systematically varying these parameters and saving them as new workspace configurations, the user builds a complete "what-if" dataset.

### 2. The Executor (`executorGUI.py`)

The Executor is the core of the what-if analysis and it’s the real star of this software. It consumes the directory of configurations created by the Generator and automates the testing process.

* **Batch Execution:** Runs all simulation scenarios sequentially without requiring manual intervention.

* **Binary Classification:** Once completed, simulations are visually classified on the GUI:

  * 🔴 **Red (Error):** The simulation failed to execute (e.g., due to contradictory generation parameters).

  * 🟢 **Green (OK):** The simulation ran successfully and generated valid data.

* **OEE Analysis & Ranking:** Clicking the OEE Analysis button filters out unexecutable scenarios and evaluates the successful ones. It ranks the simulations from *best to worst* based on the OEE performance of individual machines and the global quality yield of the system.

## Key Features

* **Automated Batch Processing:** Run dozens of JaamSim `.cfg` setups with a single click.

* **OEE Analytical Engine:** Automatically calculates Availability, Performance, and OEE for each machine, alongside the Global System Quality Yield.

* **Interactive Results:** Click on any successful simulation to view deep-dive metrics for specific machinery.

* **Automated PDF Reporting:** Generates comprehensive, academic-grade `.pdf` reports containing data tables and comparative Matplotlib bar charts for off-line analysis, storage, or publication.

## Prerequisites & Installation

**System Requirements:**

* **Python 3.12+**

* **JaamSim** (ensure `JaamSim.jar` is located in the root directory or adjust the path in `jaamPyFunctions.py`)

* Supported OS: Windows 11, Linux (Ubuntu tested)

**Installation:**
Clone the repository and install the required dependencies:

```
git clone https://github.com/yourusername/factory-zero.git
cd factory-zero
pip install -r requirements.txt

```

## Usage

The workflow requires running the two interfaces sequentially.

**Step 1: Generate Scenarios** 

Generate many different configurations of the simulation

**Step 2: Execute & Analyze**
Launch the Executor GUI, load the folder containing your generated `.cfg` files, and run the analysis.

```
python executorGUI.py

```

*Use "Start > Load a simulations set" to select your folder, click "Run" at the bottom, and finally use "OEE Analysis" to rank your results and "Save as PDF" to export.*

## Built With

* [Tkinter](https://docs.python.org/3/library/tkinter.html) - Graphical User Interface

* [Pandas](https://pydata.org) - Data extraction and statistical manipulation

* [Matplotlib](https://matplotlib.org) - Data visualization and plotting

* [FPDF](https://pyfpdf.readthedocs.io/en/latest/) - PDF report generation

* [JaamSim](https://jaamsim.com/) - Discrete-event simulation engine

## Author

**Alessandro Esposito**
