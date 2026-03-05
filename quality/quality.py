import asyncio
import os
import sys
import json
from odsl import process
from odsl import sdk
from odsl import types
from datetime import date
from dotenv import load_dotenv
import datetime

load_dotenv()

async def run(task):
	odsl = sdk.ODSL()
	odsl.setStage(os.getenv('ODSL_STAGE'))
	user=os.getenv('user')
	apikey=os.getenv('apikey')
	odsl.loginWithAPIKey(user, apikey)
    # Get the task details
	t = odsl.get('process-task', None, task)
	print(t)
	if t is not None:		
  		# Get the process details		
		p = odsl.get('process', None, t['name'])
		if p is not None:
			print(p)
   
			# Create the process message and start the process
			odsl_process = process.TASK(p, t)
			await odsl_process.startProcess()
			
			try:
				# Initialise Phase
				await odsl_process.startPhase("INIT")
    
				# Get the inputs
				input = t['input']
				dsid = input['dsid']
				name = input['name']
				ondate = input['ondate']
				events = input['events']
    
				# Get the dataset delivery
				await odsl_process.logMessage(datetime.datetime.now().isoformat() + " info Getting dataset delivery " + dsid + ":" + ondate)
				dataset = odsl.get('dataset_delivery', 'private', dsid + ":" + ondate)
				await odsl_process.logMessage(datetime.datetime.now().isoformat() + " info Got " + repr(len(events)) + " events")
				await odsl_process.endPhase("success", "Initialised Successfully")

				# Check the events phase
				await odsl_process.startPhase("CHECK")
				valid = len(events) > 0
				qmessage = "No events to check"
				for event in events:
					if float(event['price']) < 10:
						valid = False
						qmessage = "Some values are below the threshold"
				await odsl_process.logMessage(datetime.datetime.now().isoformat() + " info Check complete, valid=" + repr(valid))
				await odsl_process.logMessage(datetime.datetime.now().isoformat() + " info Updating dataset delivery")
				timestamp = datetime.datetime.now().isoformat() + 'Z[UTC]'
				timeline = dataset['timeline']
				qc = dataset['qualityChecks']
				if valid:
					dataset['qualityStatus'] = 'valid'
					timeline.append("{0} {1} {2} {3} {4}".format(timestamp, 'info', t['name'], 'quality', 'Quality Valid'))
					qc[name] = 'valid'
				else:
					dataset['qualityStatus'] = 'failed'
					timeline.append("{0} {1} {2} {3} {4}".format(timestamp, 'fatal', t['name'], 'quality', qmessage))
					qc[name] = 'failed'
				dataset['timeline'] = timeline
				odsl.update('dataset_delivery', 'private', dataset)

				await odsl_process.endPhase("success", "Checked Successfully")

				await odsl_process.endProcess("success", "Completed Successfully")
			except Exception as e:
				await odsl_process.endProcess("failed", repr(e))


task = sys.argv[1]
print("Running Process Task: " + task)
asyncio.run(run(task))
print("Finished Process Task")
print("-----------------------")
