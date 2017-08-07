import json
import datetime
from datetime import datetime as dt
import mintapi
import calendar
import unicodedata
from twilio.rest import Client
from time import strftime as stt
from apscheduler.schedulers.blocking import BlockingScheduler


email = raw_input("Enter Mint email: ")
password = raw_input("Enter Mint Password: ")
ius_session = raw_input("Enter IUS: ")
thx_guid = raw_input("Enter THX: ")
account_sid= raw_input("Enter Twilio SID: ")
auth_token = raw_input("Enter Twilio Auth Token: ")
budget = raw_input("Enter your monthly budget: ")
textTo = raw_input("Enter your phone number you'd like to text: ")
textFrom = raw_input("Enter the phone number you were given by Twilio: ")



timeChange = -3

listToAppendTo = []

#print "This past", calendar.day_name[(datetime.datetime.today() + datetime.timedelta(days=timeChange)).weekday()]
k = 0
limit = 10
totalAmountBought = 0
totalAmountEarnt = 0

x = True

if x == False:

	budget = 985
	with open('test.json') as data_file:    
    		transactions = json.load(data_file)
	
	for i in transactions:
		t = datetime.datetime.today()
		t = (t + datetime.timedelta(days=timeChange)).date()
		
		


		date = datetime.datetime.fromtimestamp(transactions[k]['date'] / 1e3)
		date = (date + datetime.timedelta(days=1)).date()

		thisDate = date
		merchant = transactions[k]['category']
		description = transactions[k]['description']
		if merchant == None:
			merchant = u'pharmacy'
		stringAmount = str(transactions[k]['amount'])

		stringDate = date.strftime("%Y-%m-%d")
		stringCategory = unicodedata.normalize('NFKD', merchant).encode('ascii','ignore')
		stringDescription = unicodedata.normalize('NFKD', description).encode('ascii','ignore')
		fullString = stringDate + " " + stringCategory + " " + stringDescription + " " + stringAmount + "\n"

		if (transactions[k]['category'] != 'income'):
			examinedMonth = int(stringDate[5] + stringDate[6])
			currentMonth = int(t.month)
			if currentMonth == examinedMonth:
				budget = budget - float(stringAmount)

		if(thisDate.strftime("%Y-%m-%d") == str(t)):
			if k<limit:
				listToAppendTo.append(fullString)
				if (transactions[k]['category'] == 'income'):
					totalAmountEarnt = totalAmountEarnt + float(stringAmount)
				else:
					totalAmountBought = totalAmountBought + float(stringAmount)
		k+=1

else:
	budget = 985
	mint = mintapi.Mint(email, password, ius_session, thx_guid)

	transactions = mint.get_transactions_json()

	for i in transactions:
		i = json.dumps(i)
		t = datetime.datetime.today()
		t = (t + datetime.timedelta(days=timeChange)).date()
		thisDate = dt.strptime(transactions[k]['date'], '%b %d').date()
		thisDate = thisDate.replace(year=datetime.datetime.today().year)
		stringDate = thisDate.strftime("%Y-%m-%d")
		stringCategory = unicodedata.normalize('NFKD', transactions[k]['mmerchant']).encode('ascii','ignore')
		stringAmount = unicodedata.normalize('NFKD', transactions[k]['amount']).encode('ascii','ignore')

		if (transactions[k]['category'] != 'Income'):
			examinedMonth = int(thisDate.month)
			currentMonth = int(t.month)
			if currentMonth == examinedMonth:
				budget = budget - float(stringAmount.strip('$'))

		if(thisDate == t):
			fullString = stringDate + " " + stringCategory + " " + stringAmount
			listToAppendTo.append(fullString)
			amountDiff = (transactions[k]['amount'])

			if (transactions[k]['category'] == 'Income'):
		 			totalAmountEarnt = totalAmountEarnt + float(amountDiff.strip("$").replace(',', ''))
	 		else:
	 			totalAmountBought = totalAmountBought + float(amountDiff.strip("$").replace(',', ''))
		k += 1

listToAppendTo.append("Purchasing Summary:" + " " + str(totalAmountBought))
listToAppendTo.append("Earnings Summary:" + " " + str(totalAmountEarnt))
listToAppendTo.append("Remaining Budget:" + " " + str(budget))

textMessage = '\n'.join(str(p) for p in listToAppendTo)
textMessage = "This past " +  calendar.day_name[(datetime.datetime.today() + datetime.timedelta(days=timeChange)).weekday()] + "\n\n" + textMessage


client = Client(account_sid, auth_token)

#print textMessage



def some_job():
	client.messages.create(
    to=textTo,
    from_=textFrom,
    body=textMessage)

scheduler = BlockingScheduler()
scheduler.add_job(some_job, 'interval', days=1)
scheduler.start()




