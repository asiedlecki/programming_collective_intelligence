import svmc
from svmc import C_SVC, NU_SVC, ONE_CLASS, EPSILON_SVR, NU_SVR
from svmc import LINEAR, POLY, RBF, SIGMOID
from math import exp, fabs

def _int_array(seq):
	size = len(seq)
	array = svmc.new_int(size)
	i = 0
	for item in seq:
		svmc.int_setitem(array,i,item)
		i = i + 1
	return array

def _double_array(seq):
	size = len(seq)
	array = svmc.new_double(size)
	i = 0
	for item in seq:
		svmc.double_setitem(array,i,item)
		i = i + 1
	return array

def _free_int_array(x):
	if x != 'NULL' and x != None:
		svmc.delete_int(x)

def _free_double_array(x):
	if x != 'NULL' and x != None:
		svmc.delete_double(x)

def _int_array_to_list(x,n):
	return map(svmc.int_getitem,[x]*n,range(n))

def _double_array_to_list(x,n):
	return map(svmc.double_getitem,[x]*n,range(n))

class svm_parameter:
	
	# wartości domyślne
	default_parameters = {
	'svm_type' : C_SVC,
	'kernel_type' : RBF,
	'degree' : 3,
	'gamma' : 0,		# 1/k
	'coef0' : 0,
	'nu' : 0.5,
	'cache_size' : 40,
	'C' : 1,
	'eps' : 1e-3,
	'p' : 0.1,
	'shrinking' : 1,
	'nr_weight' : 0,
	'weight_label' : [],
	'weight' : [],
	'probability' : 0
	}

	def __init__(self,**kw):
		self.__dict__['param'] = svmc.new_svm_parameter()
		for attr,val in self.default_parameters.items():
			setattr(self,attr,val)
		for attr,val in kw.items():
			setattr(self,attr,val)

	def __getattr__(self,attr):
		get_func = getattr(svmc,'svm_parameter_%s_get' % (attr))
		return get_func(self.param)

	def __setattr__(self,attr,val):

		if attr == 'weight_label':
			self.__dict__['weight_label_len'] = len(val)
			val = _int_array(val)
			_free_int_array(self.weight_label)
		elif attr == 'weight':
			self.__dict__['weight_len'] = len(val)
			val = _double_array(val)
			_free_double_array(self.weight)

		set_func = getattr(svmc,'svm_parameter_%s_set' % (attr))
		set_func(self.param,val)

	def __repr__(self):
		ret = '<svm_parameter:'
		for name in dir(svmc):
			if name[:len('svm_parameter_')] == 'svm_parameter_' and name[-len('_set'):] == '_set':
				attr = name[len('svm_parameter_'):-len('_set')]
				if attr == 'weight_label':
					ret = ret+' weight_label = %s,' % _int_array_to_list(self.weight_label,self.weight_label_len)
				elif attr == 'weight':
					ret = ret+' weight = %s,' % _double_array_to_list(self.weight,self.weight_len)
				else:
					ret = ret+' %s = %s,' % (attr,getattr(self,attr))
		return ret+'>'

	def __del__(self):
		_free_int_array(self.weight_label)
		_free_double_array(self.weight)
		svmc.delete_svm_parameter(self.param)

def _convert_to_svm_node_array(x):
	""" przekształcenie sekwencji lub odwzorowania w tablicę svm_node """
	import operator

	# Znajdowanie elementów niezerowych
	iter_range = []
	if type(x) == dict:
		for k, v in x.iteritems():
# wszystkie zera są zachowywane z powodu wstępnie obliczonego jądra; brak jeszcze dobrego rozwiązania
#			if v != 0:
				iter_range.append( k )
	elif operator.isSequenceType(x):
		for j in range(len(x)):
#			if x[j] != 0:
				iter_range.append( j )
	else:
		raise TypeError,"dane muszą być odwzorowaniem lub sekwencją"

	iter_range.sort()
	data = svmc.svm_node_array(len(iter_range)+1)
	svmc.svm_node_array_set(data,len(iter_range),-1,0)

	j = 0
	for k in iter_range:
		svmc.svm_node_array_set(data,j,k,x[k])
		j = j + 1
	return data

class svm_problem:
	def __init__(self,y,x):
		assert len(y) == len(x)
		self.prob = prob = svmc.new_svm_problem()
		self.size = size = len(y)

		self.y_array = y_array = svmc.new_double(size)
		for i in range(size):
			svmc.double_setitem(y_array,i,y[i])

		self.x_matrix = x_matrix = svmc.svm_node_matrix(size)
		self.data = []
		self.maxlen = 0;
		for i in range(size):
			data = _convert_to_svm_node_array(x[i])
			self.data.append(data);
			svmc.svm_node_matrix_set(x_matrix,i,data)
			if type(x[i]) == dict:
				if (len(x[i]) > 0):
					self.maxlen = max(self.maxlen,max(x[i].keys()))
			else:
				self.maxlen = max(self.maxlen,len(x[i]))

		svmc.svm_problem_l_set(prob,size)
		svmc.svm_problem_y_set(prob,y_array)
		svmc.svm_problem_x_set(prob,x_matrix)

	def __repr__(self):
		return "<svm_problem: size = %s>" % (self.size)

	def __del__(self):
		svmc.delete_svm_problem(self.prob)
		svmc.delete_double(self.y_array)
		for i in range(self.size):
			svmc.svm_node_array_destroy(self.data[i])
		svmc.svm_node_matrix_destroy(self.x_matrix)

class svm_model:
	def __init__(self,arg1,arg2=None):
		if arg2 == None:
			# tworzenie modelu przy użyciu pliku
			filename = arg1
			self.model = svmc.svm_load_model(filename)
		else:
			# tworzenie modelu przy użyciu problemu i parametru
			prob,param = arg1,arg2
			self.prob = prob
			if param.gamma == 0:
				param.gamma = 1.0/prob.maxlen
			msg = svmc.svm_check_parameter(prob.prob,param.param)
			if msg: raise ValueError, msg
			self.model = svmc.svm_train(prob.prob,param.param)

		#konfigurowanie zmiennych dotyczących całej klasy
		self.nr_class = svmc.svm_get_nr_class(self.model)
		self.svm_type = svmc.svm_get_svm_type(self.model)
		#tworzenie etykiet (klas)
		intarr = svmc.new_int(self.nr_class)
		svmc.svm_get_labels(self.model,intarr)
		self.labels = _int_array_to_list(intarr, self.nr_class)
		svmc.delete_int(intarr)
		#sprawdzanie poprawności modelu prawdopodobieństwa
		self.probability = svmc.svm_check_probability_model(self.model)

	def predict(self,x):
		data = _convert_to_svm_node_array(x)
		ret = svmc.svm_predict(self.model,data)
		svmc.svm_node_array_destroy(data)
		return ret


	def get_nr_class(self):
		return self.nr_class

	def get_labels(self):
		if self.svm_type == NU_SVR or self.svm_type == EPSILON_SVR or self.svm_type == ONE_CLASS:
			raise TypeError, "Nie można uzyskać etykiety z modelu SVR/ONE_CLASS"
		return self.labels
		
	def predict_values_raw(self,x):
		#przekształcenie x w svm_node; przydzielenie podwójnej tablicy dla danych zwracanych
		n = self.nr_class*(self.nr_class-1)//2
		data = _convert_to_svm_node_array(x)
		dblarr = svmc.new_double(n)
		svmc.svm_predict_values(self.model, data, dblarr)
		ret = _double_array_to_list(dblarr, n)
		svmc.delete_double(dblarr)
		svmc.svm_node_array_destroy(data)
		return ret

	def predict_values(self,x):
		v=self.predict_values_raw(x)
		if self.svm_type == NU_SVR or self.svm_type == EPSILON_SVR or self.svm_type == ONE_CLASS:
			return v[0]
		else: #self.svm_type == C_SVC or self.svm_type == NU_SVC
			count = 0
			d = {}
			for i in range(len(self.labels)):
				for j in range(i+1, len(self.labels)):
					d[self.labels[i],self.labels[j]] = v[count]
					d[self.labels[j],self.labels[i]] = -v[count]
					count += 1
			return  d

	def predict_probability(self,x):
		#kod języka C nie wykona żadnego działania dla niewłaściwego typu, dlatego wymagane będzie sprawdzenie we własnym zakresie
		if self.svm_type == NU_SVR or self.svm_type == EPSILON_SVR:
			raise TypeError, "Wywołanie get_svr_probability lub get_svr_pdf w celu uzyskania danych wyjściowych prawdopodobieństwa regresji"
		elif self.svm_type == ONE_CLASS:
			raise TypeError, "Prawdopodobieństwo nie jest jeszcze obsługiwane dla problemu jednej klasy"
		#tylko C_SVC,NU_SVC są w
		if not self.probability:
			raise TypeError, "Model nie obsługuje oszacowań prawdopodobieństwa"

		#przekształcenie x w svm_node i przydzielenie podwójnej tablicy w celu odebrania prawdopodobieństw
		data = _convert_to_svm_node_array(x)
		dblarr = svmc.new_double(self.nr_class)
		pred = svmc.svm_predict_probability(self.model, data, dblarr)
		pv = _double_array_to_list(dblarr, self.nr_class)
		svmc.delete_double(dblarr)
		svmc.svm_node_array_destroy(data)
		p = {}
		for i in range(len(self.labels)):
			p[self.labels[i]] = pv[i]
		return pred, p
	
	def get_svr_probability(self):
		#pozostawienie sprawdzanie błędów kodowi svm.cpp
		ret = svmc.svm_get_svr_probability(self.model)
		if ret == 0:
			raise TypeError, "Nie jest to model regresji lub niedostępne są informacje o prawdopodobieństwie"
		return ret

	def get_svr_pdf(self):
		#get_svr_probability będzie obsługiwać sprawdzanie błędów
		sigma = self.get_svr_probability()
		return lambda z: exp(-fabs(z)/sigma)/(2*sigma)


	def save(self,filename):
		svmc.svm_save_model(filename,self.model)

	def __del__(self):
		svmc.svm_destroy_model(self.model)


def cross_validation(prob, param, fold):
	if param.gamma == 0:
		param.gamma = 1.0/prob.maxlen
	dblarr = svmc.new_double(prob.size)
	svmc.svm_cross_validation(prob.prob, param.param, fold, dblarr)
	ret = _double_array_to_list(dblarr, prob.size)
	svmc.delete_double(dblarr)
	return ret
