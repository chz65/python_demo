from dotenv import load_dotenv
import asyncio
import os
import sys
from odsl import process
from odsl import sdk
import random

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

			# Create the object to update
			await odsl_process.startPhase("LOAD")
			obj = {
				'_id': 'AAA.PYTHON',
				'EVENTS': [
					{
						'_id': 'DEMO-2026-03-02-M01',
						'_type': 'VarEvent',
						'_dataset':'ODSL.PYTHON.TRADER',
						'eventtype': 'TraderPrices',
						'eventtime': '2026-03-02',
						'tenor': 'M01',
						'price': random.randrange(1, 100)
					},
					{
						'_id': 'DEMO-2026-03-02-M02',
						'_type': 'VarEvent',
						'_dataset':'ODSL.PYTHON.TRADER',
						'eventtype': 'TraderPrices',
						'eventtime': '2026-03-02',
						'tenor': 'M02',
						'price': random.randrange(1, 100)
					},
					{
						'_id': 'DEMO-2026-03-02-M03',
						'_type': 'VarEvent',
						'_dataset':'ODSL.PYTHON.TRADER',
						'eventtype': 'TraderPrices',
						'eventtime': '2026-03-02',
						'tenor': 'M03',
						'price': random.randrange(1, 100)
					}
				]
			}
			await odsl_process.logMessage("Updating " + obj['_id'])
			odsl.update('object', 'private', obj)
			await odsl_process.endPhase("success", "Updating Successfully")
			await odsl_process.endProcess("success", "Completed Successfully")

task = sys.argv[1]
print("Running Process Task: " + task)
asyncio.run(run(task))
print("Finished Process Task")
print("-----------------------")
