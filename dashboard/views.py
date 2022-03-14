import string
from tokenize import Number
from django.shortcuts import render
import requests
import datetime
import json

# Create your views here.
def dashboard(req):
    current_datetime = datetime.datetime.now()
    found = False
    connected = False
    for x in range(0, 7):
        querydate = current_datetime - datetime.timedelta(days=x)
        print(querydate.day, querydate.month, querydate.year)
        day = f'{querydate.day:02d}'
        month = f'{querydate.month:02d}'
        url1 = "https://api.data.gov.hk/v2/filter?q=%7B%22resource%22%3A%22http%3A%2F%2Fwww.chp.gov.hk%2Ffiles%2Fmisc%2Fno_of_confines_by_types_in_quarantine_centres_eng.csv%22%2C%22section%22%3A1%2C%22format%22%3A%22json%22%2C%22filters%22%3A%5B%5B1%2C%22eq%22%2C%5B%22"+str(day)+"%2F"+str(month)+"%2F"+str(querydate.year)+"%22%5D%5D%5D%7D"  
        response1 = requests.get(url1)
        url2 = "https://api.data.gov.hk/v2/filter?q=%7B%22resource%22%3A%22http%3A%2F%2Fwww.chp.gov.hk%2Ffiles%2Fmisc%2Foccupancy_of_quarantine_centres_eng.csv%22%2C%22section%22%3A1%2C%22format%22%3A%22json%22%2C%22sorts%22%3A%5B%5B8%2C%22desc%22%5D%5D%2C%22filters%22%3A%5B%5B1%2C%22eq%22%2C%5B%22"+str(day)+"%2F"+str(month)+"%2F"+str(querydate.year)+"%22%5D%5D%5D%7D"
        response2 = requests.get(url2)
        if response1 and response2:
            connected = True
        result1 = response1.json()
        result2 = response2.json()
        #print(result1)
        #print(result2)
        if result1 and result2:
            if result1[0]["As of date"] == result2[0]["As of date"]:
                centres = []
                count = 0
                uunit = 0
                runit = 0
                qcount = 0
                for y in range(len(result2)):
                    if count < 3:
                        centre = {
                            "name": result2[y]["Quarantine centres"],
                            "units": result2[y]["Ready to be used (unit)"],
                        }
                        centres.append(centre)
                        count+=1
                    uunit += result2[y]["Current unit in use"]
                    runit += result2[y]["Ready to be used (unit)"]
                    qcount += result2[y]["Current person in use"]
                found = True    
                break
    
    if qcount == result1[0]["Current number of close contacts of confirmed cases"] + result1[0]["Current number of non-close contacts"]:
        countconsistent = True
    else:
        countconsistent = False
    return render(req, "index.html", {
        "date": result1[0]["As of date"],
        "persons_quarantined": result1[0]["Current number of close contacts of confirmed cases"] + result1[0]["Current number of non-close contacts"],
        "non_close_contacts": result1[0]["Current number of non-close contacts"],
        "connected": connected,
        "has_data": found,
        "count_consistent": countconsistent,
        "centres": centres,
        "units_in_use": uunit,
        "units_available": runit
    })