# NEM DateRange Search

[![Archer|Impact](https://cldup.com/dTxpPi9lDf.thumb.png)](https://www.archerimpact.com/)

Search the transactions of many NEM Wallet Address's within a given date range
View summary statistics of all transactions by NEM Wallet Address

# Usage

`python NEMDateRange.py -i input.csv -o output.csv -s 01/30/2018 -e 02/02/2018`
Arguements:
  - Input File: `-i inputfile.csv` (each address on own line)
  - Output File Name: `-o outputfile.csv`
  - Start Date: `-s mm/dd/yyyy` (inclusive)
  - End Date: `-e mm/dd/yyyy` (inclusive)


Notes:
  - Python2.7
  - Duplicate transactions are not repeated in transaction log (output file)
  - .csv can be opened/viewed in excel 


