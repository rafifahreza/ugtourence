import requests
import pandas as pd
import pulp as plp


def generateData(city_id):
	web_url_attr = "http://103.56.206.198/api/attractions"
	#city_price dataset

	param = {"city_id":str(city_id)}
	try:
		r = requests.post(url=web_url_attr, params = param)
		response_attr = r.json()
	except Exception as e:
		print(e)

	all_data = (response_attr["attractions"])

	attraction_id = []
	attraction_name = []
	attraction_price = []

	for item in all_data:
		attraction_id.append(item["id"])
		attraction_name.append(item["attraction_name"])
		attraction_price.append(item["price"])

	dataset_price = {"no":attraction_id, "name":attraction_name, "attraction(ribu)":attraction_price}
	dataset_price = pd.DataFrame.from_dict(dataset_price, orient='columns')



	#city_priority dataset
	priority = []
	destination = []
	value = [0] * len(attraction_id)**2
	for ix in range(1, len(attraction_id)+1):
		for jx in range(1, len(attraction_id)+1):
			priority.append(ix)
			destination.append(jx)
	dataset_prior = {"priority":priority, "destination":destination, "value":value}
	dataset_prior = pd.DataFrame.from_dict(dataset_prior, orient='columns')

	#city travel dataset
	param_req = {"city_id":str(city_id)}
	r_travel = requests.post(url=web_url_attr, params = param_req)
	response_travel= r_travel.json()

	no = [nox for nox in range(1, len(attraction_id)**2+1)]
	departure_cost = []
	destination_cost = []
	travel_cost = []
	for attrs in response_travel["attractions"]:
		for cost in attrs["travel_cost"]:
			departure_cost.append(cost["attraction_id"])
			destination_cost.append(cost["attraction_destination"])
			travel_cost.append(cost["price"])
	for additional in range(1, len(attraction_id)+1):
		for add_jx in range(1, len(attraction_id)+1):
			if additional == add_jx:
				departure_cost.append(additional)
				destination_cost.append(add_jx)
				travel_cost.append(0)
	dataset_travel = {"no":no, "departure":departure_cost, "destination":destination_cost, "travel_cost":travel_cost}
	dataset_travel = pd.DataFrame.from_dict(dataset_travel, orient='columns')
	return dataset_travel, dataset_price, dataset_prior

def generateItenerary(city_id):
	df, df_pi, df_pki = generateData(city_id)
	i= df['departure'].to_numpy()
	j = df['destination'].to_numpy()
	c = df['travel_cost'].to_numpy()
	cij = {}
	for index in range(len(i)):
		cij[(i[index], j[index])] = c[index]

	k = df_pki['priority'].to_numpy()
	i = df_pki['destination'].to_numpy()
	p = df_pki['value'].to_numpy()

	pki = {}
	for index in range(len(k)):
		pki[(k[index], i[index])] = p[index]
	
	nama = df_pi['name']

	nama = nama.to_numpy()

	i = df_pi['no'].to_numpy()
	p = df_pi['attraction(ribu)'].to_numpy()

	pi = {}
	for index in range(len(i)):
		pi[i[index]] = p[index]

	n = len(i)
	model = plp.LpProblem('MIP')
	x_var = {}
	for i in range(1, n+1):
		for j in range(1, n+1):
			if i == j:
				pass
			else:
				x_var[(i,j)] = plp.LpVariable(cat=plp.LpBinary, name='X_{}_{}'.format(i, j))
	y_var = {(k,i) : plp.LpVariable(cat=plp.LpBinary, name='Y_{}_{}'.format(k,i)) for k in range(1, n+1) for i in range(1, n+1) }
	model += plp.lpSum(x_var[(i,1)] for i in range(1, n+1) if i != 1) == 1
	model += plp.lpSum(x_var[(i,j)] for i in range(1, n+1) for j in range(1, n+1) if i != j) == (plp.lpSum(y_var[(k, j)] for k in range(1, n+1)) for j in range(1, n+1))
	model += plp.lpSum(x_var[(1,j)] for j in range(1, n+1) if j != 1) == 1
	model += plp.lpSum(x_var[(1,j)] for j in range(1, n+1) if j != 1) == 1
	z_var = {i : plp.LpVariable(cat=plp.LpContinuous, name= 'Z_{}'.format(i)) for i in range(1, n+1)}
	for i in range(1, n+1):
		for j in range(1, n+1):
			if i == j:
				pass
			else:
				if i != 1 :
					model += z_var[i] - z_var[j] + (n * x_var[(i,j)]) <= n-1
	for j in range(1, n+1):
		if j != 1:
			model += x_var[(1, j)] == y_var[(1, j)]
	for k in range(1, n+1):
		if k > 1:
			for i in range(1, n+1):
				for j in range(1, n+1):
					if i != j:
						model += x_var[(i, j)] >= y_var[((k-1), i)] + y_var[k, j] - 1
	for k in range(1, n+1):
		if k >= 1 and k < n:
			model += plp.lpSum(y_var[(k,i)] for i in range(1, n+1)) >= plp.lpSum(y_var[(k+1), j] for j in range(1, n+1))
	for i in range(1, n+1):
		model += plp.lpSum(y_var[(k, i)] for k in range(1, n+1)) <= 1
	for k in range(1, n+1):
		model += plp.lpSum(y_var[(k,i)] for i in range(1, n+1)) <= 1
	obj = (plp.lpSum((pki[(k,i)] + pi[i]) * y_var[(k,i)] for k in range(1, n+1) for i in range(1, n+1)) - 
				plp.lpSum(x_var[(i,j)] * cij[(i,j)] for i in range(1, n+1) for j in range(1, n+1) if i != j))

	model.sense = plp.LpMaximize

	model.setObjective(obj)

	model.solve()

	opt_df = pd.DataFrame.from_dict(x_var, orient='index', columns=["variable_object"])
	opt_df.reset_index(inplace=True)
	opt_df['solution_val'] = opt_df['variable_object'].apply(lambda item : item.varValue)
	opt_df.drop(columns=['variable_object'], inplace=True)
	opt_df.to_excel("./optimized_fix.xls")

	df = pd.read_excel('optimized_fix.xls')

	def make_tuples(rows):
		x=int(rows.replace('(','').replace(')','').split(',')[0])
		y=int(rows.replace('(','').replace(')','').split(',')[1])
		return x,y

	def change_to_name(rows):
		x = int(rows.replace(",", '').replace('(', '').replace(')','').split(' ')[0])
		y = int(rows.replace(",", '').replace('(', '').replace(')','').split(' ')[1])
		y = nama[y-1]
		x = nama[x-1]
		rout =[]
		rout.append(x)
		rout.append(y)
		return rout

	df['fix_index'] = df['index'].apply(make_tuples)
	df['route'] = df['index'].apply(change_to_name)

	c = list(df[df['solution_val'] == 1]['route'])

	route = []
	route.append(c[0])

	i = len(c) - 1

	while i > 0:
		for j in range(1,len(c)):
			if c[j][0] == route[-1][1]:
				route.append(c[j])
				i = i -1
			else:
				pass

	fix_route = []
	for item in route:
		for obj in item:
			if obj in fix_route:
				pass
			else:
				fix_route.append(obj)
	return fix_route
