import pandas as pd
import json
import os
import subprocess
from time import sleep

def read_journals(project_name):
    while not os.path.exists(project_name):
        path = input("That file does not exist. Try again: ")
    with open(f"{project_name}\{project_name}_entries.json", "r") as file:
        entries_file = json.load(file)
    return entries_file["entries"]
    print(entries_file)

def write_journals(project_name, entries):
    with open(f"{project_name}\{project_name}_entries.json", "w") as file:
        json.dump({"entries": entries}, file)

def create_project(name):
    if not os.path.exists(name):
        empty = {"entries": []}
        os.mkdir(name)
        with open(f"{name}\{name}_entries.json", "w") as file:
            json.dump(empty, file)
        print(f"Made project with {name} name. An entries file was made in that folder with {name}_entries.json name.")
    else:
        print("Project with that name exists. Supply unique name or delete that project.")

def start_year(project_name):
    year = input("Enter the year to start: ")
    journals_data = read_journals(project_name)
    journals_data.append([f"{year}"])
    write_journals(project_name, journals_data)
    
def add_entry(project_name):
    add_date = input("Enter date of transaction: ")
    add_debit = input("Enter debited account names. Separate with comma if more than one: ").lower()
    add_credit = input("Enter credited account names. Separate with comma if more than one: ").lower()
    add_debit_amt = input("Add debited amounts in same order of accounts. Separate with comma: ")
    add_credit_amt = input("Add credited amounts in same order of accounts. Separate with comma: ")
    add_debit_folio = input("Add folio numbers for debit accounts. Enter none if NA. Separate with comma: ")
    add_credit_folio = input("Add folio numbers for credit accounts. Enter none if NA. Separate with comma: ")
    add_narration = input("Add narration: ")
    add_narration = "being " + add_narration
    debit_accounts = [element.strip() for element in add_debit.split(",")]
    credit_accounts = [element.strip() for element in add_credit.split(",")]
    debit_amounts = [element.strip() for element in add_debit_amt.split(",")]
    credit_amounts = [element.strip() for element in add_credit_amt.split(",")]
    debit_folios = [element.strip() for element in add_debit_folio.split(",")]
    credit_folios = [element.strip() for element in add_credit_folio.split(",")]
    journals_data = read_journals(project_name)
    entry = [add_date, debit_accounts, credit_accounts, debit_amounts, credit_amounts, debit_folios, credit_folios, add_narration]
    journals_data.append(entry)
    print("The following entry was added:")
    print(f"{add_date}\t{debit_accounts}\t\t\t{debit_folios}\t{debit_amounts}\n\t\t\t{credit_accounts}\t\t\t{credit_folios}\t{credit_amounts}\n{add_narration}")
    write_journals(project_name, journals_data)

def print_journals(project_name):
    journals_data = read_journals(project_name)
    print(journals_data)
    journal_commands = "%%%%%%%%%%%%%%%%%%%%%%\n% JOURNAL ENTRIES\n%%%%%%%%%%%%%%%%%%%%%%\n\n\journal{\n\n"
    for entry in journals_data:
        print(entry)
        if len(entry) == 1:
            journal_commands = journal_commands + f"\t\jyear{{{entry[0]}}}\n\n"
        else:
            journal_commands = journal_commands + f"\t\jdr{{{entry[0].title()}}}{{{entry[1][0].title()}}}{{{entry[5][0]}}}{{{entry[3][0]}}}\n"
            if len(entry[1]) > 1:
                for i in range(1, len(entry[1])):
                    journal_commands = journal_commands + f"\t\jdr{{}}{{{entry[1][i].title()}}}{{{entry[5][i]}}}{{{entry[3][i]}}}\n"
            journal_commands = journal_commands + f"\t\jcr{{{entry[2][0].title()}}}{{{entry[6][0]}}}{{{entry[4][0]}}}\n"
            if len(entry[2]) > 1:
                for i in range(1, len(entry[2])):
                    journal_commands = journal_commands + f"\t\jcr{{{entry[2][i].title()}}}{{{entry[6][i]}}}{{{entry[4][i]}}}\n"
            journal_commands = journal_commands + f"\t\jnar{{{entry[7]}}}\n\n"
    journal_commands = journal_commands + "}"
    with open(f"{project_name}\{project_name}_journal.tex", "w") as file:
        file.write(journal_commands)

def print_ledgers(project_name):
    journals_data = read_journals(project_name)
    journals = pd.DataFrame(journals_data, columns = ["date", "dr acc", "cr acc", "dr", "cr", "djf", "cjf", "narrations"])
    accounts_temp = set()
    for entry in journals_data:
        if len(entry) > 1:
            for i in range(len(entry[1])):
                dr_account = entry[1][i]
                accounts_temp.add(dr_account)
            for i in range(len(entry[2])):  
                cr_account = entry[2][i]
                accounts_temp.add(cr_account)
    
    unique_accounts = list(accounts_temp)
    
    accounts = {}
    for account in unique_accounts:
        accounts[account] = {"debit": [], "credit": []}
        
    for account in list(accounts.keys()):
        for entry in journals_data:
            if len(entry) == 1:
                accounts[account]["debit"].append(entry)
                accounts[account]["credit"].append(entry)
            else:
                for i in range(len(entry[1])):
                    if account == entry[1][i]:
                        accounts[account]["debit"].append([entry[0], entry[2], entry[3][i], entry[5]])
                for i in range(len(entry[2])):
                    if account == entry[2][i]:
                        accounts[account]["credit"].append([entry[0], entry[1], entry[4][i], entry[6]])
                        
    ledger_commands = "%%%%%%%%%%%%%%%%%%%%%%\n% LEDGER ENTRIES\n%%%%%%%%%%%%%%%%%%%%%%\n\n"
    for account in accounts.keys():
        ld = len(accounts[account]["debit"])
        lc = len(accounts[account]["credit"])
        ledger_commands = ledger_commands + f"% {account.upper()} ACCOUNT \n"
        ledger_commands = ledger_commands + f"\ledger{{{account.title()} a/c}}{{\n"
        for entry in accounts[account]["debit"]:
            if len(entry) == 1:
                ledger_commands = ledger_commands + f"\t\lyear{{{entry[0]}}}\n"
            else:
                ledger_commands = ledger_commands + f"\t\ldr{{{entry[0].title()}}}{{{entry[1][0].title()}}}{{{entry[2]}}}{{{entry[3][0]}}}\n"
        if ld < lc:
            ledger_commands = ledger_commands + "\t"
            for i in range(lc - ld):
                ledger_commands = ledger_commands + "\mt"
            ledger_commands = ledger_commands + "\n"
        ledger_commands = ledger_commands + "\t\mt\n}{\n"
        for entry in accounts[account]["credit"]:
            if len(entry) == 1:
                ledger_commands = ledger_commands + f"\t\lyear{{{entry[0]}}}\n"
            else:
                ledger_commands = ledger_commands + f"\t\lcr{{{entry[0].title()}}}{{{entry[1][0].title()}}}{{{entry[2]}}}{{{entry[3][0]}}}\n"
        if lc < ld:
            ledger_commands = ledger_commands + "\t"
            for i in range(ld - lc):
                ledger_commands = ledger_commands + "\mt"
            ledger_commands = ledger_commands + "\n"
        ledger_commands = ledger_commands + "\t\mt\n}\n\n"
        with open(f"{project_name}\{project_name}_ledger.tex", "w") as file:
            file.write(ledger_commands)
        
def fabricate(project_name):
    cwd = os.getcwd().replace("\\", "/")
    main_commands = f"% This is {project_name}_main.tex fabricated using https://github.com/zplus11/Bookkeeping-LaTeX.git\n"
    main_commands += f"\input{{{cwd}/preamble.tex}}\n\n"
    main_commands += f"\\begin{{document}}\n\t\\begin{{center}}\n\t\t{{\Huge Bookkeeping with \LaTeX}}\\\\[5pt]{{\LARGE Automation with Python}}\n\t\end{{center}}\n"
    main_commands += f"\t\section{{Journal}}\n\t\input{{{cwd}/{project_name}/{project_name}_journal.tex}}\n"
    main_commands += f"\t\section{{Ledger Posting}}\n\t\input{{{cwd}/{project_name}/{project_name}_ledger.tex}}\n"
    main_commands += f"\end{{document}}"
    with open(f"{project_name}\{project_name}_main.tex", "w") as file:
        file.write(main_commands)
    cwd = os.getcwd()
    os.chdir(cwd + f"\{project_name}")
    subprocess.run(['pdflatex', f"{project_name}_main.tex"])
    os.chdir(cwd)
