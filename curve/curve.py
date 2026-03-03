from odsl import sdk
import random

odsl = sdk.ODSL()
odsl.setStage("dev")
odsl.loginWithAPIKey('colin.hartley@opendatadsl.com', '6107d060fa02b20dbc442316')

obj = {
	'_id': 'AAA.PYTHON',
	'CURVE':{
			'_id': 'CURVE',
			'_type': 'VarCurve',
			'ondate': {'curveDate':'2026-03-02', 'expiryCalendar':'#REOMB'},
			'contracts': [
				{'tenor': 'M01', 'value': random.randrange(1, 100)},
				{'tenor': 'M02', 'value': random.randrange(1, 100)},
				{'tenor': 'M03', 'value': random.randrange(1, 100)},
				{'tenor': 'M04', 'value': random.randrange(1, 100)},
				{'tenor': 'M05', 'value': random.randrange(1, 100)},
				{'tenor': 'M06', 'value': random.randrange(1, 100)},
				{'tenor': 'M07', 'value': random.randrange(1, 100)},
				{'tenor': 'M08', 'value': random.randrange(1, 100)},
				{'tenor': 'M09', 'value': random.randrange(1, 100)},
				{'tenor': 'M10', 'value': random.randrange(1, 100)},
				{'tenor': 'M11', 'value': random.randrange(1, 100)},
				{'tenor': 'M12', 'value': random.randrange(1, 100)}
			]
		}
}

odsl.update('object', 'private', obj)

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
    spread = Curve(input_curve.ondate)
    
    # Get all contracts from the bootstrapped curve
    contracts = input_curve.contracts
    
    # Get the total number of contracts
    contract_size = len(contracts)
    
    # Iterate through contracts starting from the second one to calculate spreads
    for i in range(1, contract_size):
        # Get the current contract
        current = contracts[i]
        
        # Get the previous contract
        previous = contracts[i - 1]
        
        # Calculate the spread value as the difference between consecutive contracts
        spread_value = current.value - previous.value
        
        # Create the spread tenor label (e.g., "M01-M02")
        spread_tenor = f"{previous.tenor}-{current.tenor}"
        
        # Add the spread contract to the curve
        spread.add(spread_tenor, spread_value)
    
    # Return the spread curve
    return spread