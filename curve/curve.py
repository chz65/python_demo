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