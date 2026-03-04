import asyncio
import os
import sys
import json
from odsl import process
from odsl import sdk
from odsl import types
from datetime import date
import datetime


async def run(task):
	odsl = sdk.ODSL()
	odsl.setStage(os.getenv('ODSL_STAGE'))
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
				# Get the base curve
				await odsl_process.startPhase("INIT")
				input = t['input']
				dsid = input['_dsid']    
				ondate = input['ondate']
				# Get the dataset delivery
				await odsl_process.logMessage(datetime.datetime.now().isoformat() + " info Getting dataset delivery " + dsid + ":" + ondate)
				dataset = odsl.get('dataset_delivery', 'private', dsid + ":" + ondate)
				od = date.fromisoformat(ondate)
				odt = od + datetime.timedelta(days=1)
				range={'$gte':od.isoformat(), '$lt':odt.isoformat()}    
				filter="{'_dsid':'" + dsid + "','eventstart':" + json.dumps(range) + "}"
				await odsl_process.logMessage(datetime.datetime.now().isoformat() + " info Getting events " + dsid + " for " + json.dumps(range))
				events = odsl.list('event', 'private', {'_filter':filter,'_limit':-1})
				await odsl_process.logMessage(datetime.datetime.now().isoformat() + " info Got " + repr(len(events)) + " events")
				await odsl_process.endPhase("success", "Initialised Successfully")

				# Check the events
				await odsl_process.startPhase("CHECK")
				valid = True
				for event in events:
					if event['price'] < 10:
						valid = False
				await odsl_process.logMessage(datetime.datetime.now().isoformat() + " info Check complete, valid=" + repr(valid))
				await odsl_process.logMessage(datetime.datetime.now().isoformat() + " info Updating dataset delivery")
				timestamp = datetime.datetime.now().isoformat()
				timeline = dataset['timeline']
				if valid:
					dataset['qualityStatus'] = 'valid'
					timeline.append("{0} {1} {2} {3} {4}".format(timestamp, 'info', t['name'], 'quality', 'Quality Valid'))
				else:
					dataset['qualityStatus'] = 'failed'
					timeline.append("{0} {1} {2} {3} {4}".format(timestamp, 'fatal', t['name'], 'quality', 'Quality Failed'))
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
