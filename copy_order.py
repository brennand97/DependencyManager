
def list_contains(l, e):
	for i in l:
		if e == i:
			return True
	return False


def list_leave_distinct(l):
	nl = []
	for i in l:
		if not list_contains(nl, i):
			nl.append(i)
	return nl


def D2_list_contains(l, e):
	for g in l:
		for i in g:
			if e == i:
				return True
	return False


def D2_list_length(l):
	size = 0
	for g in l:
		for i in g:
			size = size + 1
	return size


def D2_list_if_contains_remove(l, e):
	for g_i in range(0, len(l)):
		for i in range(len(l[g_i]) - 1, -1, -1):
			i_e = l[g_i][i]
			if i_e == e:
				del l[g_i][i]


def count_empty_arrays(l):
	size = 0
	for g in l:
		if len(g) == 0:
			size = size + 1
	return size


def remove_empty_arrays(l):
	for g_i in range(len(l) - 1, -1, -1):
		if len(l[g_i]) == 0:
			del l[g_i]


def to_copy_order_v2(table_names, tables):
	groups = []
	#Create most dependent group
	groups.append([])
	for t in sorted(table_names):
		table = tables[t]
		if len(table.dependents) == 0:
			groups[0].append(t)

	#Loop through the most recent level in the groups multi-dim array,
	#until an excess of empty lists are observed, this means that the
	#order has relaxed into its final state.
	group_i = 0
	#while group_i < 3 or len(groups[group_i - 3]) > 0:
	while group_i == 0 or count_empty_arrays(groups) < 20:
		#Add the new dependency level to the group
		groups.append([])
		#Increase the current dependency level
		group_i = group_i + 1
		#Loop through every table in the previous group level
		for t in sorted(table_names):
			if list_contains(groups[group_i - 1], t):
				table = tables[t]
				for t_d in sorted(table.dependiences) :
					if not list_contains(groups[group_i], t_d):
						D2_list_if_contains_remove(groups[:-1], t_d)
						groups[group_i].append(t_d)
	#Remove the empty list from groups
	remove_empty_arrays(groups)
	return groups
