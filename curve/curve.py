from dotenv import load_dotenv
import asyncio
import os
import sys
from odsl import process
from odsl import sdk
from odsl import types

load_dotenv()

def timespread(input_curve):
    """
    Function to calculate the spread between consecutive contracts on a bootstrapped curve.
    Creates a calendar spread curve showing the price difference between adjacent months.
    
    Args:
        input_curve: The input curve to bootstrap and calculate spreads for
        
    Returns:
        A curve containing spreads between consecutive contracts
    """
    # Create a new curve to store the spread values
    ondate = input_curve['ondate']
    spread = types.Curve(ondate['curveDate'], ondate['expiryCalendar'])
    
    # Get all contracts from the bootstrapped curve
    contracts = input_curve['contracts']
    
    # Get the total number of contracts
    contract_size = len(contracts)
    
    # Iterate through contracts starting from the second one to calculate spreads
    for i in range(1, contract_size):
        # Get the current contract
        current = contracts[i]
        
        # Get the previous contract
        previous = contracts[i - 1]
        
        # Calculate the spread value as the difference between consecutive contracts
        spread_value = current['value'] - previous['value']
        
        # Create the spread tenor label (e.g., "M01-M02")
        spread_tenor = f"{previous['tenor']}-{current['tenor']}"
        
        # Add the spread contract to the curve
        spread.add(spread_tenor, spread_value)
    
    # Return the spread curve
    return spread

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
		input = t['input']
		id = input['id']
		name = input['name']
		base = input['BASE']
		expression = input['expression']
		ondate = input['ondate']
		
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
				await odsl_process.logMessage("Getting base curve " + base + ":" + ondate)
				base_curve = odsl.get('data', 'private', base + ":" + ondate)
				print(base_curve)
				await odsl_process.endPhase("success", "Initialised Successfully")

				# Create the object to update
				await odsl_process.startPhase("BUILD")
				await odsl_process.logMessage("Building " + id + ":" + name)
				obj = {'_id': id}
				obj['name'] = timespread(base_curve).data
				print("Updating Object: " + repr(obj))
				odsl.update('object', 'private', obj)
				await odsl_process.endPhase("success", "Updating Successfully")
				await odsl_process.endProcess("success", "Completed Successfully")
			except Exception as e:
				await odsl_process.endProcess("failed", repr(e))


task = sys.argv[1]
print("Running Process Task: " + task)
asyncio.run(run(task))
print("Finished Process Task")
print("-----------------------")


