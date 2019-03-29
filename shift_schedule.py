"""Shift schedule with pyomo abstract model"""

from pyomo.opt import SolverFactory
from pyomo.environ import *
import pandas as pd


# Some settings
min_shifts_per_worker = 21
max_shifts_per_worker = 23

max_shift_lenght = 7
min_shift_length = 2
min_free_length = 2

# Read input data
data = pd.read_csv('input/dem_month.csv', index_col=0)
vacation_planinng = pd.read_csv('input/vacation_planning.csv', index_col=0)
request_list = pd.read_excel('input/request_list.xlsx', index_col=0)

# Select solver
opt = SolverFactory('cbc')

# Create model
m = AbstractModel()

# Define number of workers and shifts
num_workers = len(request_list.index)
num_shifts = len(data.columns)

# Define indices
m.all_workers = Set(initialize=range(num_workers))
m.all_shifts = Set(initialize=range(num_shifts))
m.all_days = Set(initialize=data.index, ordered=True)

# Create bool variables
m.shifts = Var(m.all_workers, m.all_days, m.all_shifts, within=Binary)
m.start_work = Var(m.all_workers, m.all_days, m.all_shifts, within=Binary)
m.start_free = Var(m.all_workers, m.all_days, m.all_shifts, within=Binary)

# Translate request_list to shift_request
shift_request = [[[0 for s in range(num_shifts)]
                 for d in range(len(request_list.columns)+1)]
                 for w in range(num_workers)]

for worker in request_list.index:
    for day in request_list.columns:
        day_id = int(day.split('_')[1])-1
        if(request_list.loc[worker, day] == 0):
            shift_request[worker][day_id][0] = 1
        if(request_list.loc[worker, day] == 1):
            shift_request[worker][day_id][1] = 1
        if(request_list.loc[worker, day] == 2):
            shift_request[worker][day_id][2] = 1


# Each shift is assigned to a necessary number of workers in
# the schedule period
def define_early_shift(m, d):
    return (sum(m.shifts[w, d, 0] for w in m.all_workers) ==
            data.loc[d, 'early_shift'])
m.define_early_shift = Constraint(m.all_days, rule=define_early_shift)


def define_middle_shift(m, d):
    return (sum(m.shifts[w, d, 1] for w in m.all_workers) ==
            data.loc[d, 'middle_shift'])
m.define_middle_shift = Constraint(m.all_days, rule=define_middle_shift)


def define_late_shift(m, d):
    return (sum(m.shifts[w, d, 2] for w in m.all_workers) ==
            data.loc[d, 'late_shift'])
m.define_late_shift = Constraint(m.all_days, rule=define_late_shift)


# Each worker works at most one shift per day
def only_one_shift_per_day(m, w, d):
    return sum(m.shifts[w, d, s] for s in m.all_shifts) <= 1
m.only_one_shift_per_day = Constraint(m.all_workers, m.all_days,
                                      rule=only_one_shift_per_day)


# Each worker has a min and max number of shifts per schedule period
def min_shifts(m, w):
    num_shifts_worked = sum(m.shifts[w, d, s] for s in m.all_shifts
                            for d in m.all_days)
    return min_shifts_per_worker <= num_shifts_worked
m.min_shifts = Constraint(m.all_workers, rule=min_shifts)


def max_shifts(m, w):
    num_shifts_worked = sum(m.shifts[w, d, s] for s in m.all_shifts
                            for d in m.all_days)
    return num_shifts_worked <= max_shifts_per_worker
m.max_shifts = Constraint(m.all_workers, rule=max_shifts)


# Relations between shift, start to work and start freetime
def relation_between_binaries(m, w, d, s):
    if d < m.all_days.next(m.all_days.first()):
        return Constraint.Skip
    else:
        return (m.shifts[w, d, s] - m.shifts[w, d-1, s] ==
                m.start_work[w, d, s]-m.start_free[w, d, s])
m.relation_between_binaries = Constraint(m.all_workers, m.all_days,
                                         m.all_shifts,
                                         rule=relation_between_binaries)


# Minimal sequence of shifts
def min_seq_shifts(m, w, d, s):
    if d < min_shift_length+1:
        return Constraint.Skip
    else:
        return (sum(m.start_work[w, i, s]
                    for i in range(d-min_shift_length+1, d+1)) <=
                m.shifts[w, d, s])
m.min_seq_shifts = Constraint(m.all_workers, m.all_days,
                              m.all_shifts, rule=min_seq_shifts)


# Maximal sequence of shifts
def max_seq_shifts(m, w, d, s):
    if d < max_shift_lenght+1:
        return Constraint.Skip
    else:
        return (sum(m.start_work[w, i, s]
                    for i in range(d-max_shift_lenght+1, d+1)) >=
                m.shifts[w, d, s])
m.max_seq_shifts = Constraint(m.all_workers, m.all_days, m.all_shifts,
                              rule=max_seq_shifts)


# Minimal sequence of free time
def min_seq_free(m, w, d, s):
    if d < min_free_length+1:
        return Constraint.Skip
    else:
        return (sum(m.start_free[w, i, s]
                    for i in range(d-min_free_length+1, d+1)) <=
                1-m.shifts[w, d, s])
m.min_seq_free = Constraint(m.all_workers, m.all_days, m.all_shifts,
                            rule=min_seq_free)


# No early shift after a late shift
def no_early_after_late(m, w, d):
    if d == m.all_days.last():
        return Constraint.Skip
    else:
        return m.shifts[w, d, 2]+m.shifts[w, d+1, 0] <= 1
m.no_early_after_late = Constraint(m.all_workers, m.all_days,
                                   rule=no_early_after_late)


# Respect the vacation planning
def vacation_planning(m, w, d):
    return (sum(m.shifts[w, d, s] for s in m.all_shifts) <=
            vacation_planinng.loc[d, str(w)])
m.vacation_planning = Constraint(m.all_workers, m.all_days,
                                 rule=vacation_planning)


# Objective function to maximize the requests
def obj_expression(m):
    return sum(shift_request[w][d][s]*m.shifts[w, d, s]
               for w in m.all_workers
               for d in m.all_days
               for s in m.all_shifts)
m.obj = Objective(rule=obj_expression, sense=maximize)


# Create instanz
instance = m.create_instance()

# Solve the optimization problem
results = opt.solve(instance, symbolic_solver_labels=True,
                    tee=True, load_solutions=True)

# Write Results
df_shift_schedule = pd.DataFrame(index=range(num_workers))
df_statistic = pd.DataFrame(index=range(num_workers))
df_shift_schedule.index.name = 'worker'
df_statistic.index.name = 'worker'

for d in instance.all_days.value:
    col_name = 'day_'+str(d)
    for w in instance.all_workers.value:
        is_working = False
        for s in instance.all_shifts.value:
            if instance.shifts[w, d, s].value:
                is_working = True
                df_shift_schedule.loc[w, col_name] = s
        if not is_working:
                df_shift_schedule.loc[w, col_name] = -1

df_statistic['early'] = df_shift_schedule[df_shift_schedule == 0].count(axis=1)
df_statistic['middle'] = df_shift_schedule[df_shift_schedule == 1].count(axis=1)
df_statistic['late'] = df_shift_schedule[df_shift_schedule == 2].count(axis=1)
df_statistic['free'] = df_shift_schedule[df_shift_schedule == -1].count(axis=1)

# Export the shift schedule and statistic in one file
export = pd.ExcelWriter('shift_schedule.xlsx', engine='xlsxwriter')
df_shift_schedule.to_excel(export, 'shift_schedule', startrow=0,
                           startcol=0)
df_statistic.to_excel(export, 'statistic', startrow=0,
                      startcol=0)
export.save()
