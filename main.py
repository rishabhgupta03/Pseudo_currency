import sqlite3
import random as rd
from datetime import datetime
import numpy as nd
import pandas as pd


class user:

    def open_account(self):                            #To open new account and to assigns the account_no to the customer
        print("-#-#-#-#-WELCOME TO PSUEDO CURRENCY BANK-#-#-#-#-\n")
        self.first_name= input("Enter your first name--\n")
        self.last_name= input("enter your last name--\n")
        while True:
            self.account_type= input("enter your account type---(SAVINGS,CURRENT)--\n").upper().strip()
            if self.account_type=='SAVINGS' or self.account_type=='CURRENT':
                break
            else:
                print("--Either write SAVINGS or CURRENT,no other option are available--\n\n")

        while True:                                         #confirmatiom password
            try:
                self.password=int(input("enter your new password(numeric)--\n").strip())
                confirm_password=int(input("re-enter your password for confirmation--\n").strip())
                if self.password==confirm_password:
                    break
                else:
                    print("---password did not match---")
            except ValueError:
                print("--only numeric values can be enter--\n\n")

        self.account_no=rd.randint(111,999999999)
        self.account_bal=0
        conn =sqlite3.connect("BANK_SYSTEM.db")
        crsr = conn.cursor()
        crsr.execute("select account_no from user")
        check=crsr.fetchall()
        conn.commit()

        while self.account_no in check:                       #to avoid the assignment of existing account no to new customer
            self.account_no=rd.randint(111,999999999)
        crsr.execute("insert into user values(?,?,?,?,?)",(self.account_no,self.first_name,self.last_name,self.account_bal,self.account_type))
        crsr.execute("insert into login values(?,?)",(self.account_no,self.password))
        conn.commit()
        conn.close()
        print("-x-x-x-x-x-x-x-ACCOUNT CREATED-x-x-x-x-x-x-x-\nYOUR ACCOUNT NO----->",self.account_no)
        print("\n\tNOTE:Use this account no. and your password for any query in future ")
    #--------------------------------------------------------------------------------------------------------------------
    def balance_enquiry(self,account_no):  #To return balance of the account
        self.account_no=account_no

        conn =sqlite3.connect("BANK_SYSTEM.db")
        crsr = conn.cursor()
        crsr.execute("select account_bal from user where account_no=?",(self.account_no ,))
        balance=crsr.fetchone()
        conn.commit()
        conn.close()
        return balance[0]
    #----------------------------------------------------------------------------------------------------------------------
    def update_passbook(self,account_no,amount,trans_type,account_bal): #To update passbook after every transaction
        self.account_no=account_no
        self.amount=amount
        self.trans_type=trans_type
        self.account_bal=account_bal
        now = datetime.now()
        dt_string = str(now.strftime("%B %d, %Y %H:%M:%S"))

        conn =sqlite3.connect("BANK_SYSTEM.db")
        crsr = conn.cursor()
        crsr.execute("INSERT INTO passbook VALUES(?,?,?,?,?)",(dt_string,self.account_no,self.amount,self.trans_type,self.account_bal))
        conn.commit()
        conn.close()
    #---------------------------------------------------------------------------------------------------------------------
    def deposit(self,account_no,amount,trans_type='CREDITED'):   #To deposit pusedo cash in account
        self.account_no=account_no
        self.amount=amount

        conn =sqlite3.connect("BANK_SYSTEM.db")
        crsr = conn.cursor()
        crsr.execute("""UPDATE USER
                        SET account_bal=account_bal + ?
                        where account_no=?""",(self.amount,self.account_no))
        conn.commit()
        conn.close()

        balance=self.balance_enquiry(account_no)
        self.update_passbook(account_no,amount,trans_type,balance)
        print("\n\n-+-+-+-CASH DEPOSITED-+-+-+-\n\n")
    #---------------------------------------------------------------------------------------------------------------------
    def withdraw(self,account_no,amount,trans_type='DEBITED'):   #To withdraw psuedo cash from account
        self.account_no=account_no
        self.amount=amount
        if(self.balance_enquiry(account_no) < amount):
            print("INSUFFICIENT BALANCE FOR WITHDRAW")
            return None
        else:
            conn =sqlite3.connect("BANK_SYSTEM.db")
            crsr = conn.cursor()
            crsr.execute("""UPDATE USER
                            SET account_bal=account_bal - ?
                            where account_no= ?""",(self.amount,self.account_no))
            conn.commit()
            conn.close()
        balance=self.balance_enquiry(account_no)
        self.update_passbook(account_no,amount,trans_type,balance)
        print("\n\n-+-+-+-CASH WITHDRAWN-+-+-+-\n\n")
    #----------------------------------------------------------------------------------------------------------------------
    def fund_transfer(self,p_account_no,r_account_no,amount):   #For tranfering funds from your own account to given recepient account


        if(self.balance_enquiry(p_account_no) < amount):       #Checking account balance before tranferring
            print("INSUFFICIENT BALANCE\n DEPOSIT SOME MONEY TO CONTINUE THE TRANFER")


        else:
            conn =sqlite3.connect("BANK_SYSTEM.db")
            crsr = conn.cursor()
            crsr.execute("select account_no from user where account_no=?",(r_account_no,))
            account=crsr.fetchone()
            conn.commit()
            conn.close()
            if(account is None):                                   #Checking wheather recepient account exist or not.
                print("\nMENTIONED RECIPIENT ACCOUNT DOES NOT EXIST")

            else:
                password=int(input("--enter your password for tranfering fund--\n").strip())
                if(password==self.login_check(p_account_no)):        #enter your login password for tranferring funds
                    self.withdraw(p_account_no,amount,'TRANSFERED')
                    self.deposit(r_account_no,amount,'CREDITED')
                    print("TRANFER HAS BEEN DONE")
                else:
                    print("TRANSFER OF FUNDS CANCELLED DUE TO WRONG CREDENTIALS")
    #---------------------------------------------------------------------------------------------------------------------

    def display_category(self,account_no,trans_type): #Display passbook according to transaction type

        conn =sqlite3.connect("BANK_SYSTEM.db")
        crsr = conn.cursor()
        crsr.execute("select * from passbook where account_no=? and trans like (?)",(account_no,trans_type))
        passbook=crsr.fetchall()
        if len(passbook)==0:
            print("no trasanction happened till now")
        else:
            passbook=nd.array(passbook)
            print("\n\n"+pd.DataFrame(passbook,columns='DATE-TIME ACCOUNT_NO AMOUNT TRANS_TYPE FINAL_ACC_BAL'.split())+"\n\n")
        conn.commit()
        conn.close()
    #--------------------------------------------------------------------------------------------------------------------

    def e_passbook_choice(self,account_no):  #Display passbook reading choice
        choice=int(input(("press\n(1)ALL TRANSACTION\n(2)CREDITED TRANSACTION\n(3)DEBITED TRANSACTION\n(4)TRANSFERED TRANSACTION\n---choice---")).strip())
        conn =sqlite3.connect("BANK_SYSTEM.db")
        crsr = conn.cursor()
        if choice==1 :
            crsr.execute("select * from passbook where account_no=?",(account_no,))
            m=crsr.fetchall()
            if len(m)==0:
                print("no trasanction happened till now")
            else:
                m=nd.array(m)
                print(pd.DataFrame(m,columns='DATE-TIME ACCOUNT_NO AMOUNT TRANS_TYPE FINAL_ACC_BAL'.split()))
                conn.commit()
                conn.close()
        elif choice==2:
            self.display_category(account_no,'CREDITED')
        elif choice==3:
            self.display_category(account_no,'DEBITED')
        elif choice==4:
            self.display_category(account_no,'TRANSFERED')
        else:
            print("-x-x-x-x-invalid choice-x-x-x-x-")
    #---------------------------------------------------------------------------------------------------------------------

    def login_check(self,account_no):  #Use to check the login credentials like password, account_no

        conn =sqlite3.connect("BANK_SYSTEM.db")
        crsr = conn.cursor()
        crsr.execute("select password from login where account_no=?",(account_no ,))
        password=crsr.fetchone()
        conn.commit()
        conn.close()
        return password[0]

#----------------------------------------------------------------------------------------------------------------------



s=user()
while True:
    print("\n\n\n*@*@*@*@*@*@*@*@*@*@*-PSUEDO CURRENCY BANK SYSTEM-*@*@*@*@*@*@*@*@*@*@*\n".center(180,' '))
    print("(1)Log in with account number and password")
    print("(2)Open new account")
    print("(3)Exit")


    ch=int(input("<------enter choice------>").strip())

    if ch==1:
        account_no=input("enter your account number--\n")
        password=int(input("enter your password--"))
        conn =sqlite3.connect("BANK_SYSTEM.db")
        crsr = conn.cursor()
        crsr.execute("select account_no from user where account_no=?",(account_no,))
        account=crsr.fetchone()
        conn.commit()
        conn.close()
        if(account is None):
            print("\nMENTIONED ACCOUNT DOES NOT EXIST")
            break
        elif(password==s.login_check(account_no)):

            conn =sqlite3.connect("BANK_SYSTEM.db")
            crsr = conn.cursor()
            crsr.execute("select customer_first,customer_last from user where account_no=?",(account_no,))
            m=crsr.fetchone()
            conn.commit()
            while True:
                print("-$-$-$-$-$-$-$-$-$-WELCOME TO YOUR PORTAL {name}-$-$-$-$-$-$-$-$-$-\n\n\n".format(name=m[0].upper()+" "+m[1].upper()))
                print("(B)BALANCE ENQUIRY\n")
                print("(D)CASH DEPOSIT\n")
                print("(W)CASH WITHDRAWN\n")
                print("(T)TRANSFER FUNDS\n")
                print("(E)E-PASSBOOK")
                print("(X)LOG-OUT")
                s1=user()
                ch2=input("---input your choice---\n").strip()
                if ch2=='b' or ch2=='B':
                    print("Your account balance is ",s1.balance_enquiry(account_no))
                elif ch2=='d' or ch2=='D':
                    try:
                        amount=int(input("-*-*-enter the amount for deposit-*-*-").strip())
                        s1.deposit(account_no,amount)
                    except ValueError:
                        print("---PLEASE ENTER AMOUNT CAREFULLY---")
                elif ch2=='w' or ch2=='W':
                    try:
                        amount=int(input("-*-*-enter the amount for withdraw-*-*-").strip())
                        s1.withdraw(account_no,amount)
                    except ValueError:
                        print("---PLEASE ENTER AMOUNT CAREFULLY---")
                elif ch2=='t' or ch2=='T':
                    try:
                        r_account=int(input("\n-*-*-enter the recipient account no:-*-*-").strip())
                        amount=int(input("-*-*-enter the amount for transfer-*-*-").strip())
                        s1.fund_transfer(account_no,r_account,amount)
                    except ValueError:
                        print("---PLEASE ENTER  ACCOUNT NO AND AMOUNT CAREFULLY---")
                elif ch2=='e' or ch2=='E':
                    s1.e_passbook_choice(account_no)
                elif ch2=='x' or ch2=='X':
                    break
                else:
                    print("invalid choice entered")

    elif ch==2:
        s.open_account()

    elif ch==3:
        break
    else:
        print("invalid choice")