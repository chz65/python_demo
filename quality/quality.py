from dotenv import load_dotenv
import asyncio
import os
import sys
import json
from odsl import process
from odsl import sdk
from odsl import types
from datetime import date
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
   
			# Create the process message
			odsl_process = process.TASK(p, t)
			await odsl_process.startProcess()
			
			try:
				# Get the base curve
				await odsl_process.startPhase("INIT")
				input = t['input']
				dsid = input['dsid']    
				ondate = input['ondate']
				# Get the dataset delivery
				await odsl_process.logMessage("Getting dataset delivery " + dsid + ":" + ondate)
				dataset = odsl.get('dataset_delivery', 'private', dsid + ":" + ondate)
				od = date.fromisoformat(ondate)
				odt = od + datetime.timedelta(days=1)
				range={'$gte':od.isoformat(), '$lt':odt.isoformat()}    
				filter="{'_dsid':'" + dsid + "','eventstart':" + json.dumps(range) + "}"
				await odsl_process.logMessage("Getting events " + dsid + " for " + json.dumps(range))
				events = odsl.list('event', 'private', {'_filter':filter,'_limit':-1})
				await odsl_process.logMessage("Got " + repr(len(events)) + " events")
				await odsl_process.endPhase("success", "Initialised Successfully")

				# Check the events
				await odsl_process.startPhase("CHECK")
				valid = True
				for event in events:
					if event['price'] < 10:
						valid = False
				await odsl_process.logMessage("Check complete, valid=" + repr(valid))
				await odsl_process.logMessage("Updating dataset delivery")
				if valid:
					dataset['qualityStatus'] = 'valid'
				else:
					dataset['qualityStatus'] = 'failed'
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
