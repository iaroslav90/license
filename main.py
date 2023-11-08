from datetime import datetime
import json
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from ftplib import FTP
from io import BytesIO, StringIO



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return "connection is okay."

with open('accounts.json', 'r') as f:
    accounts = json.load(f)

class LicenseItem(BaseModel):
    mail: str
    account: str


@app.post("/license")
async def root(item: LicenseItem):
    ftp = FTP('ftp.theauroraai.com') 
    ftp.login(user='license@theauroraai.com', passwd = 'J,MAR&_welCm')
    r = BytesIO()
    ftp.retrbinary('RETR clients.csv', r.write)
    data = StringIO(r.getvalue().decode('utf-8'))
    license = pd.read_csv(data)
    ftp.close()

    if len(license.index[license['Payment Email'] == item.mail].tolist()) == 0:
        return "false,not registered email,,"

    idx = license.index[license['Payment Email'] == item.mail].tolist()[0]
    # date = license['Date of Expiry'].loc[idx]
    acc_num = license['Allowed Accounts'].loc[idx]

    # if datetime.now().strftime("%Y.%m.%d") > date:
    #     return "false,license expired at %s,," % date

    if item.mail not in accounts:
        accounts[item.mail] = []
    if item.account not in accounts[item.mail] and len(accounts[item.mail]) >= acc_num:
        return "false,your license can be used for only %d accounts,," % acc_num
    if item.account not in accounts[item.mail]:
        accounts[item.mail].append(item.account)
        try:
            with open('accounts.json', 'w') as f:
                json.dump(accounts, f, indent=4)
        except:
            pass
    
    # return "ok,%s,%s,%s" % (date, len(accounts[item.mail]), acc_num)
    return "ok,,%s,%s" % (len(accounts[item.mail]), acc_num)