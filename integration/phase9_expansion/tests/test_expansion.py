from elm369.expansion import *

p=ExpansionPlanner()
r=ExpansionRequest('JMR0824197846902',Domain.INDUSTRIAL,'Full Industrial build',(DEFAULT_CAPABILITIES[Domain.INDUSTRIAL],))
plan=p.plan(r)
assert plan['execution_status']=='NOT_EXECUTED'
assert plan['steps']==['inventory','design','validate','authorize','execute','verify','audit']
assert plan['authorization_required'] is True
assert p.plan(ExpansionRequest('JMR0824197846902',Domain.AI,'AI integration'))['domain']=='AI'
print('ELM369 Phase 9 expansion tests: PASS')
