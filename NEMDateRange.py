#TO USE: python dateRange.py -i input.csv -o output.csv -s 01/30/2018 -e 02/02/2018
#to find open nodes: https://nodeexplorer.com/api_openapi_version

import urllib, json
import datetime
import sys
import csv
import argparse

def prettyPrint(transaction, adjustedTime, address):
	address = address
	recipient = "N/A"
	amount = -1
	time = str(adjustedTime)
	messagePayload = "N/A"
	outgoing = 0
	incoming = 0
	signer = ""
	sender = ""
	machineTime = str(int(adjustedTime.strftime("%s")) * 1000)
	if 'recipient' in transaction:
		recipient = transaction['recipient']
		if recipient == address:
			incoming = 1
		else:
			outgoing = 1

	if 'amount' in transaction:
		amount = (transaction['amount'] / 1000000.0)

	if 'message' in transaction:
		message = transaction['message']
		if 'payload' in message:
			messagePayload = str(message['payload'])

	if 'signer' in transaction:
		signer = transaction['signer']
		sender = getSender(baseUrl, signer)


	return (address, sender, recipient, time, amount, outgoing, incoming, messagePayload, machineTime)


def getTransactions(baseUrl, parameters, requestCount):
	request = "/account/transfers/all?"
	print "...search number #" + str(requestCount) + " ..."
	transferResponse = urllib.urlopen(baseUrl + request + parameters)
	transferRaw = json.loads(transferResponse.read())
	return transferRaw

def getSender(baseUrl, pubKey):
	request = "/account/get/from-public-key?publicKey="
	transferResponse = urllib.urlopen(baseUrl + request + pubKey)
	transferRaw = json.loads(transferResponse.read())
	return transferRaw["account"]["address"]

def getHistory(parameters, startDate, endDate, address):
	transactionsRecord = []
	requestCount = 0
	forceQuit = False
	while True:
		if forceQuit:
			break
		requestCount = requestCount + 1
		transferRaw = getTransactions(baseUrl, parameters, requestCount)
		
		if len(transferRaw['data']) == 0:
			return transactionsRecord

		transferData = transferRaw['data']
		for transfer in transferData:
			transaction = transfer['transaction']
			timeStamp = transaction['timeStamp']
			adjustedTime = nemBlockTimeStamp + datetime.timedelta(seconds = timeStamp)

			if startDate <= adjustedTime <= endDate:	
				transactionsRecord.append(prettyPrint(transaction, adjustedTime, address))
			elif adjustedTime < startDate:
				forceQuit = True

		#keep searching after the end? the api only returns the last 25 transactions - this might work?
		lastTransfer = transferData[-1]
		lastTransferHash = lastTransfer['meta']['hash']['data']
		lastTransferId = lastTransfer['meta']['id']
		parameters = "address=" + address + "&hash=" + str(lastTransferHash) + "&id=" + str(lastTransferId)
	return transactionsRecord

baseUrl = "http://66.228.48.37:7890/"#"http://202.5.19.142:7890"

nemBlockTimeStamp = datetime.datetime(2015, 3, 28, 16, 6, 25) #2015-03-28 16:06:25 - i think this is the nemisis block start time

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputFile", help="input file of addresses as .csv")
parser.add_argument("-o", "--outputFile", help="output file name as .csv")
parser.add_argument("-s", "--startDate", help="start date as mm/dd/yyyy")
parser.add_argument("-e", "--endDate", help="end date as mm/dd/yyyy")
flagArgs = parser.parse_args()

if len(sys.argv)<=1:
	print("\nSample Query: python dateRange.py -i input.csv -o output.csv -s 01/30/2018 -e 02/02/2018\n")
	parser.print_help()
	exit(0)

allTransactions = flagArgs.outputFile
inputFile = flagArgs.inputFile
startDate = datetime.datetime.strptime(flagArgs.startDate, '%m/%d/%Y')
endDate = datetime.datetime.strptime(flagArgs.endDate, '%m/%d/%Y')
summaryStatistics = []
summaryStatisticsFile = "summary.csv"

with open(inputFile, 'rb') as infile:
	addressReader = csv.reader(infile)
	with open(allTransactions, 'wb') as outfile:
		csv_outfile=csv.writer(outfile)
		csv_outfile.writerow(['address','sender','recipient','time','amount','outgoing', 'incoming','messagePayload', 'machineTime'])
		for address in addressReader:
			print "Fetching " + address[0]
			
			#summary statistics
			numTransactions = 0
			firstDate = datetime.datetime(3000, 1,1, 1, 1, 1)
			lastDate = datetime.datetime(1900, 1, 1, 1, 1, 1)  
			totalAmount = 0
			outgoingAmount = 0
			incomingAmount = 0
			totalRecieved = 0
			totalSent = 0

			parameters = "address=" + address[0]
			history = getHistory(parameters, startDate, endDate, address[0])
			for transaction in history:
				csv_outfile.writerow(transaction)

				#summary statistics
				numTransactions = numTransactions + 1
				firstDate = min(firstDate, datetime.datetime.strptime(transaction[3], "%Y-%m-%d %H:%M:%S"))
				lastDate = max(lastDate, datetime.datetime.strptime(transaction[3], "%Y-%m-%d %H:%M:%S"))
				
				outgoingAmount = outgoingAmount + transaction[5]
				incomingAmount = incomingAmount + transaction[6]

				if transaction[5] == 1:
					totalSent = totalSent + transaction[4]
					totalAmount = totalAmount - transaction[4]
				if transaction[6] == 1:
					totalRecieved = totalRecieved + transaction[4]
					totalAmount = totalAmount + transaction[4]

			summaryStatistics.append((address[0], numTransactions, incomingAmount, outgoingAmount, firstDate, lastDate, totalAmount, totalRecieved, totalSent))

with open(summaryStatisticsFile, 'wb') as summaryfile:
			csv_outfile=csv.writer(summaryfile)
			csv_outfile.writerow(['address','numTransactions','transactionsIncoming', 'transactionsOutgoing','firstDate','lastDate','netAmount', 'netRecieved', 'netSent'])
			for account in summaryStatistics:
				csv_outfile.writerow(account)




