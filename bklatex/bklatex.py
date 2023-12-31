import os
import pandas as pd
import subprocess


class account:
    def __init__(self, file_name: str, company_name: str = "", year: str = ""):
        self.file_name = file_name
        self.company_name = company_name
        self.year = year
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        self.database = {}
        self.credit_natures = []

    def make_pdf(self, journals: bool = True, ledgers: bool = True, keep_tex: bool = False):
        tex_name = self.file_name + ".tex"
        com = compiler(tex_name, self.cwd, self.database, self.company_name, self.year, self.credit_natures)
        com.open_tex()
        if journals == True:
            com.write_journals()
        if ledgers == True:
            com.write_ledgers()
        com.close_tex()
        
        com.fabricate(keep_tex)

    def set_credit(self, accounts: list):
        self.credit_natures = accounts
        

class month:
    def __init__(self, acc, month, year):
        assert isinstance(acc, account), f"{account} is not an account class object"
        acc.database[(month, year)] = []
        self.entries = acc.database[(month, year)]
        self.month = month
        self.year = year

    def clean(self, string):
        cleaned = ""
        for i in string:
            if i in r"&%$#_{}~\\^": cleaned += fr"\{i}"
            else: cleaned += i
        return cleaned
        
    def entry(
        self,
        date: str = "1",
        debit_accounts: list = ["cash"],
        credit_accounts: list = ["capital"],
        debit_amounts: list = [100000],
        credit_amounts: list = [100000],
        debit_folios: list = [],
        credit_folios: list = [],
        narration: str = "being capital introduced"
    ):
        if not len(debit_folios): debit_folios = [""]*len(debit_accounts)
        if not len(credit_folios): credit_folios = [""]*len(credit_accounts)
        constituted = [
            self.clean(date), 
            [self.clean(name) for name in debit_accounts],
            [self.clean(name) for name in credit_accounts],
            debit_amounts,
            credit_amounts,
            debit_folios,
            credit_folios,
            self.clean(narration)
        ]
        bool1 = (len(constituted[1]) == len(constituted[3]) and (len(constituted[5]) == len(constituted[3]) or not len(constituted[5]))) and (len(constituted[2]) == len(constituted[4]) and (len(constituted[6]) == len(constituted[4]) or not len(constituted[6])))
        bool2 = all(constituted[i][j] > 0 for i in [3, 4] for j in range(len(constituted[i])))
        assert bool2, "Debit or credit amounts were not integer values."
        assert all(isinstance(constituted[i], list) for i in [1, 2, 3, 4]) and bool1, "Ensure debit (credit) accounts, amounts and folios are in lists and have equal lengths."
        
        self.entries.append(constituted)

class compiler:
    def __init__(self, file_name, cwd, database, company_name, year, credit_natures):
        self.file_name = file_name
        self.cwd = cwd
        self.database = database
        self.company_name = company_name
        self.year = year
        self.credit_natures = credit_natures
        
    def open_tex(self):
        cwd = self.cwd.replace("\\", "/")
        opening_commands = f"% This is {self.file_name}.tex printed using https://github.com/zplus11/Bookkeeping-LaTeX.git\n\n"
        opening_commands += f"\\input{{{cwd}/preamble.tex}}\n\\title{{Bookkeeping with \\LaTeX}}\n\\date{{\\today}}\n\n"
        opening_commands += f"\\begin{{document}}\n\t\\maketitle\n\n"

        with open(self.file_name, "w") as file:
            file.write(opening_commands)

        print("[1]", end = " ")
        
    def write_journals(self):
        journal_commands = f"\t%%%%%%%%%%%%%%%%%%%%%%\n\t% JOURNAL ENTRIES\n\t%%%%%%%%%%%%%%%%%%%%%%\n\n\t\\journal{{{self.company_name}}}{{{self.year}}}{{\n\n"
        current_year = ""
        
        for month in self.database:
            if month[1] != current_year:
                journal_commands += f"\t\t\\jyear{{{month[1]}}}\n\n"
            for entry in self.database[month]:
                journal_commands += f"\t\t\\jdr{{{entry[0].title() + " " + month[0][0:3]}}}{{{entry[1][0].title()}}}{{{entry[5][0]}}}{{{entry[3][0]}}}\n"
                if len(entry[1]) > 1:
                    for i in range(1, len(entry[1])):
                        journal_commands += f"\t\t\\jdr{{}}{{{entry[1][i].title()}}}{{{entry[5][i]}}}{{{entry[3][i]}}}\n"
                journal_commands += f"\t\t\\jcr{{{entry[2][0].title()}}}{{{entry[6][0]}}}{{{entry[4][0]}}}\n"
                if len(entry[2]) > 1:
                    for i in range(1, len(entry[2])):
                        journal_commands += f"\t\t\\jcr{{{entry[2][i].title()}}}{{{entry[6][i]}}}{{{entry[4][i]}}}\n"
                journal_commands += f"\t\t\\jnar{{{entry[7]}}}\n\n"
        journal_commands += "\t}\n\n"

        with open(self.file_name, "a") as file:
            file.write(journal_commands)
    
        print("[2]", end = " ")
        
    def write_ledgers(self):
        global unique_accounts, accounts
        
        ledger_commands = f"\t%%%%%%%%%%%%%%%%%%%%%%\n\t% LEDGER POSTING\n\t%%%%%%%%%%%%%%%%%%%%%%\n\n\tLedger posting: W.I.P.\n\n"
        
        unique_accounts = set()
        for monthlog in self.database.values():
            for entry in monthlog:
                for dacc in entry[1]:
                    unique_accounts.add(dacc)
                for cacc in entry[2]:
                    unique_accounts.add(cacc)
        
        accounts = {monthlog[0]: {account: {"nature": "d", "opening": 0, "debit": [], "credit": [], "closing": 0} for account in unique_accounts} for monthlog in self.database}

        for account in self.credit_natures:
            if account in unique_accounts:
                for monthlog in self.database:
                    accounts[monthlog[0]][account]["nature"] = "c"
                    
        '''
        --- self.database ---
        {
            ('December', '2023'): [
                ['29', ['Cash'], ['Capital'], [500000], [500000], ['1'], ['2'], 'being capital introduced'],
                ['29', ['Bank'], ['Cash'], [200000], [200000], ['3'], ['4'], 'being cash deposited into bank'],
                ['30', ['Furniture', 'Computers', 'Purchases'], ['Bank'], [20000, 10000, 20000], [50000], ['', '', ''], [''], 'being furniture, computers and stock purchased']
            ], ('January', '2024'): [
                ['1', ['Cash', 'Bank'], ['Sales'], [30000, 120000], [150000], ['9', '10'], ['11'], 'being sales made to bank and cash']
            ]
        }
        '''
        
        for account in unique_accounts:
            for monthlog in self.database:
                index = list(self.database).index(monthlog)
                accounts[monthlog[0]][account]["closing"] = accounts[monthlog[0]][account]["opening"]
                for entry in self.database[monthlog]:
                    for i in range(len(entry[1])):
                        if account == entry[1][i]:
                            accounts[monthlog[0]][account]["debit"].append([entry[0], entry[2], entry[3][i], entry[5]])
                            accounts[monthlog[0]][account]["closing"] += entry[3][i]
                    
                    for i in range(len(entry[2])):
                        if account == entry[2][i]:
                            accounts[monthlog[0]][account]["credit"].append([entry[0], entry[1], entry[4][i], entry[6]])
                            accounts[monthlog[0]][account]["closing"] -= entry[4][i]
                if index < len(self.database) - 1:
                    accounts[list(self.database)[index + 1][0]][account]["opening"] = accounts[monthlog[0]][account]["closing"]

        print(accounts)
                            
        for account in unique_accounts:
            ledger_commands += f"\t% {account.upper()} ACCOUNT \n"
            ledger_commands += f"\t\\ledger{{{account.title()} a/c}}{{\n"

            for month in accounts:
                ld = len(accounts[month][account]["debit"])
                lc = len(accounts[month][account]["credit"])
                nature = accounts[month][account]["nature"]

                opening_balance = accounts[month][account]["opening"]
                closing_balance = accounts[month][account]["closing"]
                
                if nature == "d":
                    ledger_commands += f"\t\t\\tobalbd{{1 {month[0:3]}}}{{{opening_balance}}}\n"

                for entry in accounts[month][account]["debit"]:
                    ledger_commands += f"\t\t\\ldr{{{entry[0] + " " + month[0:3].title()}}}{{{entry[1][0].title()}}}{{{entry[2]}}}{{{entry[3][0]}}}\n"

                if nature == "c":
                    ledger_commands += f"\t\t\\tobalcd{{30 {month[0:3]}}}{{{closing_balance}}}\n"

                ledger_commands += "\\mt\n\t\t"
                if ld < lc:
                    for i in range(lc - ld):
                        ledger_commands += "\\mt"
                        
                total_amt = opening_balance + sum([accounts[month][account]["debit"][i][2] for i in range(ld)])
                ledger_commands += f"\t\t\\total{{{total_amt}}}\n\t\t\\mt\n"
                        
            ledger_commands += "\n\t}{\n"
            
            for month in accounts:
                ld = len(accounts[month][account]["debit"])
                lc = len(accounts[month][account]["credit"])
                nature = accounts[month][account]["nature"]

                opening_balance = accounts[month][account]["opening"]
                closing_balance = accounts[month][account]["closing"]
                
                if nature == "c":
                    ledger_commands += f"\t\t\\bybalbd{{1 {month[0:3]}}}{{{opening_balance}}}\n"
                    
                for entry in accounts[month][account]["credit"]:
                    ledger_commands += f"\t\t\\lcr{{{entry[0] + " " + month[0:3].title()}}}{{{entry[1][0].title()}}}{{{entry[2]}}}{{{entry[3][0]}}}\n"

                if nature == "d":
                    ledger_commands += f"\t\t\\bybalcd{{30 {month[0:3]}}}{{{closing_balance}}}\n"

                ledger_commands += "\\mt\n\t\t"
                if lc < ld:
                    for i in range(ld - lc):
                        ledger_commands += "\\mt"
                        
                total_amt = closing_balance + sum([accounts[month][account]["credit"][i][2] for i in range(lc)])
                ledger_commands += f"\t\t\\total{{{total_amt}}}\n\t\t\\mt\n"
            
            ledger_commands += "\t\t\n\t}\n\n"

        print(accounts)

        with open(self.file_name, "a") as file:
            file.write(ledger_commands)
            
        print("[3]", end = " ")
        
    def close_tex(self):
        compiler_commands = f"\\end{{document}}\n% End of file."

        with open(self.file_name, "a") as file:
            file.write(compiler_commands)

        print("[4]")

    def fabricate(self, keep_tex):
        try:
            compiler_response = subprocess.run(
                ["pdflatex", self.file_name],
                stdout = subprocess.PIPE,
                text = True,
                check = True,
                creationflags = subprocess.CREATE_NO_WINDOW
            )
            compiler_response = f"{compiler_response.stdout}"
            
        except subprocess.CalledProcessError as e:
            compiler_response = f"{e.output}"

        print(compiler_response)

        if keep_tex == False:
            os.remove(self.file_name)
        os.remove(self.file_name[:-4] + ".aux")
        os.remove(self.file_name[:-4] + ".log")
        os.remove(self.file_name[:-4] + ".out")
