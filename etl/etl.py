import asyncio
import os
import sys
import json
from odsl import process
from odsl import sdk
import random
import datetime
from datetime import date

async def run(task):
	odsl = sdk.ODSL()
	user='alex.lynch@glencore.co.uk'
	apikey='69a813b0d6152d543360a8ed'
	odsl.loginWithAPIKey(user, apikey)
    # Get the task details
	t = odsl.get('process-task', None, task)
	print(t)
	if t is not None:
		# Get the process details		
		p = odsl.get('process', None, t['name'])
		if p is not None:
			print(p)
   
			# Create the process message
			odsl_process = process.TASK(p, t)
			await odsl_process.startProcess()
			try:
				# Create the object to update
				print("starting phase LOAD")
				await odsl_process.startPhase("LOAD")
				dnow = date.today() - datetime.timedelta(days=1)
				ondate = dnow.isoformat()
				input = t['input']
				if 'ondate' in input and input['ondate']:
					ondate = input['ondate']
				await odsl_process.logMessage(datetime.datetime.now().isoformat() + " info Running ETL for " + ondate)
				obj = {
					'_id': 'AAA.PYTHON',
					'EVENTS': [
						{
							'_id': 'DEMO-'+ondate+'-M01',
							'_type': 'VarEvent',
							'_dsid':'ODSL.PYTHON.TRADER',
							'eventtype': 'TraderPrices',
							'eventtime': ondate,
							'relative': 'M01',
							'price': random.randrange(1, 100)
						},
						{
							'_id': 'DEMO-'+ondate+'-M02',
							'_type': 'VarEvent',
							'_dsid':'ODSL.PYTHON.TRADER',
							'eventtype': 'TraderPrices',
							'eventtime': ondate,
							'relative': 'M02',
							'price': random.randrange(1, 100)
						},
						{
							'_id': 'DEMO-'+ondate+'-M03',
							'_type': 'VarEvent',
							'_dsid':'ODSL.PYTHON.TRADER',
							'eventtype': 'TraderPrices',
							'eventtime': ondate,
							'relative': 'M03',
							'price': random.randrange(1, 100)
						}
					]
				}
				print("Logging message")
				await odsl_process.logMessage(datetime.datetime.now().isoformat() + " info Updating " + obj['_id'])
				print("Updating object")
				print(json.JSONEncoder().encode(o=obj))
				odsl.update('object', 'private', obj, {'_origin':t['name']})
				print("Ending phase LOAD")
				await odsl_process.endPhase("success", "Updating Successfully")
				await odsl_process.endProcess("success", "Completed Successfully")
			except Exception as e:
				await odsl_process.endProcess("failed", repr(e))

task = sys.argv[1]
print("Running Process Task: " + task)
asyncio.run(run(task))
print("Finished Process Task")
print("-----------------------")
