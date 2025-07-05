from ortools.sat.python import cp_model
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
from pocketbase import main

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, resources={
    r"/*": {
        "origins": ["*"],  # Allows all origins (replace with specific domains if needed)
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Setup log directory and file
LOG_DIR = "logs"
LOG_FILE = "api_activity.log"
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, LOG_FILE)

log_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=5)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)

logger = logging.getLogger("API_Logger")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

# New function to log detailed error messages for failed sections
def log_detailed_error(section, error_message, details=None):
    error_msg = f"[Failed Section: {section}] {error_message}"
    if details:
        error_msg += f" | Details: {details}"
    logger.error(error_msg)
    return error_msg



# Use a fixed schedule start for all time calculations
SCHEDULE_START = datetime(2025, 6, 12, 0, 0, 0)

# Define data structures for jobs, machines, and downtime
class Job:
    def __init__(self, job_id, operations, quantity, delivery_date, priority=0, schedule_direction='forward'):
        self.job_id = job_id
        self.operations = operations  # List of Operation objects
        self.quantity = quantity
        # Accept both string and datetime, store as datetime
        if isinstance(delivery_date, str):
            self.delivery_date = datetime.strptime(delivery_date, "%Y-%m-%dT%H:%M:%S")
        else:
            self.delivery_date = delivery_date
        self.priority = priority  # Lower value means higher priority (priority=1 is higher than priority=2) (default 0)
        self.schedule_direction = schedule_direction  # 'forward' or 'backward' or None

class Operation:
    def __init__(self, op_id, name, possible_machines):
        self.op_id = op_id
        self.name = name  # Name of the operation
        self.possible_machines = possible_machines  # List of (machine_id, duration) tuples

class Machine:
    def __init__(self, machine_id, name, machine_type=None, list_seq=None):
        self.machine_id = machine_id
        self.name = name  # Name of the machine
        self.machine_type = machine_type or "Unknown"  # Type of machine (e.g., "Finning")
        self.list_seq = list_seq or machine_id  # Sequence order for display (defaults to machine_id)

class Downtime:
    def __init__(self, machine_id, start, end, reason):
        self.machine_id = machine_id
        # Accept both string and datetime, store as datetime
        if isinstance(start, str):
            self.start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
        else:
            self.start = start
        if isinstance(end, str):
            self.end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
        else:
            self.end = end
        self.reason = reason  # Reason for downtime

class ScheduledJob:
    def __init__(self, job_id, op_id, machine_id, start, end):
        self.job_id = job_id
        self.op_id = op_id
        self.machine_id = machine_id
        if isinstance(start, str):
            self.start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
        else:
            self.start = start
        if isinstance(end, str):
            self.end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
        else:
            self.end = end

def prepare_intervals(machines, downtimes, scheduled_jobs, schedule_start):
    downtime_intervals = {m.machine_id: [] for m in machines}
    for dt in downtimes:
        start_minutes = int((dt.start - schedule_start).total_seconds() // 60)
        end_minutes = int((dt.end - schedule_start).total_seconds() // 60)
        downtime_intervals[dt.machine_id].append((start_minutes, end_minutes))

    scheduled_intervals = {m.machine_id: [] for m in machines}
    if scheduled_jobs:
        for sj in scheduled_jobs:
            start_minutes = int((sj.start - schedule_start).total_seconds() // 60)
            end_minutes = int((sj.end - schedule_start).total_seconds() // 60)
            scheduled_intervals[sj.machine_id].append((start_minutes, end_minutes))
    return downtime_intervals, scheduled_intervals

def add_operation_variables(model, jobs, machines, machine_dict, downtime_intervals, scheduled_intervals, horizon):
    all_tasks = {}
    machine_intervals = {m.machine_id: [] for m in machines}
    task_indices_by_machine = {m.machine_id: [] for m in machines}
    end_vars = []
    job_end_vars = {}
    selection_vars = {}

    for job in jobs:
        for op in job.operations:
            op_selection = []
            for machine_id, duration in op.possible_machines:
                suffix = f'j{job.job_id}_o{op.op_id}_m{machine_id}'
                select_var = model.NewBoolVar(f'select_{suffix}')
                selection_vars[(job.job_id, op.op_id, machine_id)] = select_var
                op_selection.append(select_var)

                start_var = model.NewIntVar(0, horizon, f'start_{suffix}')
                base_duration = duration

                # Downtime extension
                downtime_extension_vars = []
                for dt_idx, (dt_start, dt_end) in enumerate(downtime_intervals[machine_id]):
                    dt_length = dt_end - dt_start
                    overlaps = model.NewBoolVar(f'overlaps_{suffix}_dt{dt_idx}')
                    end_var_tmp = model.NewIntVar(0, horizon, f'end_{suffix}_tmp_{dt_idx}')
                    # Temporarily compute end without all extensions
                    if downtime_extension_vars:
                        model.Add(end_var_tmp == start_var + base_duration + sum(downtime_extension_vars))
                    else:
                        model.Add(end_var_tmp == start_var + base_duration)

                    not_before = model.NewBoolVar(f'not_before_{suffix}_dt{dt_idx}')
                    not_after = model.NewBoolVar(f'not_after_{suffix}_dt{dt_idx}')
                    model.Add(start_var < dt_end).OnlyEnforceIf(not_after)
                    model.Add(start_var >= dt_end).OnlyEnforceIf(not_after.Not())
                    model.Add(end_var_tmp > dt_start).OnlyEnforceIf(not_before)
                    model.Add(end_var_tmp <= dt_start).OnlyEnforceIf(not_before.Not())
                    model.AddBoolAnd([not_after, not_before]).OnlyEnforceIf(overlaps)
                    model.AddBoolOr([not_after.Not(), not_before.Not()]).OnlyEnforceIf(overlaps.Not())

                    ext = model.NewIntVar(0, dt_length, f'dt_ext_{suffix}_{dt_idx}')
                    model.Add(ext == dt_length).OnlyEnforceIf(overlaps)
                    model.Add(ext == 0).OnlyEnforceIf(overlaps.Not())
                    downtime_extension_vars.append(ext)

                # Compute total downtime extension as a single variable
                total_downtime_ext = model.NewIntVar(0, horizon, f'total_dt_ext_{suffix}')
                if downtime_extension_vars:
                    model.Add(total_downtime_ext == sum(downtime_extension_vars))
                else:
                    model.Add(total_downtime_ext == 0)

                end_var = model.NewIntVar(0, horizon, f'end_{suffix}')
                model.Add(end_var == start_var + base_duration + total_downtime_ext)

                # Use total_downtime_ext in the interval variable
                interval_var = model.NewOptionalIntervalVar(
                    start_var,
                    base_duration + total_downtime_ext,  # Use single variable for size
                    end_var,
                    select_var,
                    f'interval_{suffix}'
                )
                all_tasks[(job.job_id, op.op_id, machine_id)] = (start_var, end_var, interval_var, select_var)
                machine_intervals[machine_id].append(interval_var)
                task_indices_by_machine[machine_id].append((job.job_id, op.op_id, machine_id))
                end_vars.append(end_var)

                # Prevent overlap with scheduled jobs
                for sched_idx, (sched_start, sched_end) in enumerate(scheduled_intervals[machine_id]):
                    no_overlap = model.NewBoolVar(f'no_overlap_{suffix}_sched{sched_idx}')
                    model.Add(end_var <= sched_start).OnlyEnforceIf([no_overlap, select_var])
                    model.Add(start_var >= sched_end).OnlyEnforceIf([no_overlap.Not(), select_var])

                if job.job_id not in job_end_vars:
                    job_end_vars[job.job_id] = []
                job_end_vars[job.job_id].append(end_var)

            model.Add(sum(op_selection) == 1)
    return all_tasks, machine_intervals, task_indices_by_machine, end_vars, job_end_vars, selection_vars
def add_precedence_constraints(model, jobs, all_tasks):
    for job in jobs:
        if len(job.operations) > 1:
            for op_idx in range(1, len(job.operations)):
                prev_op = job.operations[op_idx - 1]
                curr_op = job.operations[op_idx]
                for prev_machine_id, _ in prev_op.possible_machines:
                    for curr_machine_id, _ in curr_op.possible_machines:
                        prev_start, prev_end, _, prev_sel = all_tasks[(job.job_id, prev_op.op_id, prev_machine_id)]
                        curr_start, _, _, curr_sel = all_tasks[(job.job_id, curr_op.op_id, curr_machine_id)]
                        both_selected = model.NewBoolVar(f'both_selected_j{job.job_id}_o{prev_op.op_id}_{prev_machine_id}_to_o{curr_op.op_id}_{curr_machine_id}')
                        model.AddBoolAnd([prev_sel, curr_sel]).OnlyEnforceIf(both_selected)
                        model.AddBoolOr([prev_sel.Not(), curr_sel.Not()]).OnlyEnforceIf(both_selected.Not())
                        model.Add(curr_start >= prev_end).OnlyEnforceIf(both_selected)

def add_no_overlap_constraints(model, machine_intervals):
    for machine_id, intervals in machine_intervals.items():
        if intervals:
            model.AddNoOverlap(intervals)

def add_pairwise_disjunctive_constraints(model, task_indices_by_machine, all_tasks):
    for machine_id, task_indices in task_indices_by_machine.items():
        n = len(task_indices)
        for i in range(n):
            for j in range(i + 1, n):
                (job_id1, op_id1, _), (job_id2, op_id2, _) = task_indices[i], task_indices[j]
                start1, end1, _, sel1 = all_tasks[(job_id1, op_id1, machine_id)]
                start2, end2, _, sel2 = all_tasks[(job_id2, op_id2, machine_id)]
                both_selected = model.NewBoolVar(f'both_selected_{job_id1}_{op_id1}_{job_id2}_{op_id2}_m{machine_id}')
                model.AddBoolAnd([sel1, sel2]).OnlyEnforceIf(both_selected)
                model.AddBoolOr([sel1.Not(), sel2.Not()]).OnlyEnforceIf(both_selected.Not())
                before = model.NewBoolVar(f'before_{job_id1}_{op_id1}_{job_id2}_{op_id2}_m{machine_id}')
                after = model.NewBoolVar(f'after_{job_id1}_{op_id1}_{job_id2}_{op_id2}_m{machine_id}')
                model.Add(end1 <= start2).OnlyEnforceIf([before, both_selected])
                model.Add(end2 <= start1).OnlyEnforceIf([after, both_selected])
                model.AddBoolOr([before, after, both_selected.Not()])

def add_priority_constraints(model, jobs, machine_dict, all_tasks):
    sorted_jobs = sorted(jobs, key=lambda j: j.priority)
    for machine_id in machine_dict:
        for i in range(len(sorted_jobs) - 1):
            high = sorted_jobs[i]
            for j in range(i + 1, len(sorted_jobs)):
                low = sorted_jobs[j]
                high_ops = [op for op in high.operations if machine_id in [m_id for m_id, _ in op.possible_machines]]
                low_ops = [op for op in low.operations if machine_id in [m_id for m_id, _ in op.possible_machines]]
                if high_ops and low_ops:
                    high_ends = []
                    low_starts = []
                    for op in high_ops:
                        _, end_var, _, sel_var = all_tasks[(high.job_id, op.op_id, machine_id)]
                        high_ends.append((end_var, sel_var))
                    for op in low_ops:
                        start_var, _, _, sel_var = all_tasks[(low.job_id, op.op_id, machine_id)]
                        low_starts.append((start_var, sel_var))
                    for (high_end, high_sel) in high_ends:
                        for (low_start, low_sel) in low_starts:
                            both_selected = model.NewBoolVar(f'prio_both_selected_{high.job_id}_{low.job_id}_m{machine_id}')
                            model.AddBoolAnd([high_sel, low_sel]).OnlyEnforceIf(both_selected)
                            model.AddBoolOr([high_sel.Not(), low_sel.Not()]).OnlyEnforceIf(both_selected.Not())
                            model.Add(high_end <= low_start).OnlyEnforceIf(both_selected)

def add_delivery_date_constraints(model, jobs, job_end_vars, schedule_start):
    """Add delivery date constraints based on each job's individual schedule_direction"""
    delivery_penalties = []
    backward_jobs = []
    forward_jobs = []
    unscheduled_jobs = []

    for job in jobs:
        if job.job_id in job_end_vars:
            # Convert delivery date to minutes from schedule start
            delivery_minutes = int((job.delivery_date - schedule_start).total_seconds() // 60)

            # Get the maximum end time for this job (when all operations complete)
            job_completion = model.NewIntVar(0, 200000, f'job_{job.job_id}_completion')
            model.AddMaxEquality(job_completion, job_end_vars[job.job_id])

            # Apply constraints based on individual job's schedule_direction
            if job.schedule_direction == 'backward':
                # For backward scheduling, jobs must finish by delivery date
                model.Add(job_completion <= delivery_minutes)
                backward_jobs.append(job.job_id)
            elif job.schedule_direction == 'forward':
                # For forward scheduling, add penalty for late deliveries
                lateness = model.NewIntVar(0, 200000, f'job_{job.job_id}_lateness')
                model.AddMaxEquality(lateness, [job_completion - delivery_minutes, 0])
                delivery_penalties.append(lateness * job.priority if job.priority > 0 else lateness)
                forward_jobs.append(job.job_id)
            elif job.schedule_direction is None or job.schedule_direction == 'none':
                # No specific scheduling constraints for this job
                unscheduled_jobs.append(job.job_id)
            else:
                # Default to forward scheduling for unknown directions
                lateness = model.NewIntVar(0, 200000, f'job_{job.job_id}_lateness')
                model.AddMaxEquality(lateness, [job_completion - delivery_minutes, 0])
                delivery_penalties.append(lateness * job.priority if job.priority > 0 else lateness)
                forward_jobs.append(job.job_id)

    return delivery_penalties, forward_jobs, backward_jobs, unscheduled_jobs

def model_basic_constraints(jobs, machines, downtimes, scheduled_jobs=None):
    """
    Create scheduling model with mixed scheduling directions based on individual job settings.
    Each job can have its own schedule_direction: 'forward', 'backward', or None.
    """
    model = cp_model.CpModel()
    horizon = 200000
    schedule_start = SCHEDULE_START
    machine_dict = {m.machine_id: m for m in machines}

    downtime_intervals, scheduled_intervals = prepare_intervals(machines, downtimes, scheduled_jobs, schedule_start)

    all_tasks, machine_intervals, task_indices_by_machine, end_vars, job_end_vars, selection_vars = add_operation_variables(
        model, jobs, machines, machine_dict, downtime_intervals, scheduled_intervals, horizon
    )

    add_precedence_constraints(model, jobs, all_tasks)
    add_no_overlap_constraints(model, machine_intervals)
    add_pairwise_disjunctive_constraints(model, task_indices_by_machine, all_tasks)
    add_priority_constraints(model, jobs, machine_dict, all_tasks)

    # Add delivery date constraints based on individual job scheduling directions
    delivery_penalties, forward_jobs, backward_jobs, unscheduled_jobs = add_delivery_date_constraints(
        model, jobs, job_end_vars, schedule_start
    )

    # Create mixed objective function based on job scheduling directions
    objective_components = []

    # For jobs with backward scheduling, we want to maximize their start times (minimize negative start times)
    if backward_jobs:
        backward_start_vars = []
        for (job_id, op_id, machine_id), (start_var, _, _, _) in all_tasks.items():
            if job_id in backward_jobs:
                backward_start_vars.append(start_var)

        if backward_start_vars:
            min_backward_start = model.NewIntVar(0, horizon, "min_backward_start")
            model.AddMinEquality(min_backward_start, backward_start_vars)
            # Add negative of min start time to minimize (which maximizes the actual start times)
            neg_min_start = model.NewIntVar(-horizon, 0, "neg_min_backward_start")
            model.Add(neg_min_start == -min_backward_start)
            objective_components.append(neg_min_start)

    # For jobs with forward scheduling and unscheduled jobs, minimize makespan and penalties
    forward_and_unscheduled_jobs = forward_jobs + unscheduled_jobs
    if forward_and_unscheduled_jobs:
        # Get end vars for forward and unscheduled jobs
        forward_end_vars = []
        for (job_id, op_id, machine_id), (_, end_var, _, _) in all_tasks.items():
            if job_id in forward_and_unscheduled_jobs:
                forward_end_vars.append(end_var)

        if forward_end_vars:
            forward_makespan = model.NewIntVar(0, horizon, "forward_makespan")
            model.AddMaxEquality(forward_makespan, forward_end_vars)
            objective_components.append(forward_makespan)

    # Add delivery penalties for forward scheduled jobs
    if delivery_penalties:
        total_penalty = model.NewIntVar(0, horizon * len(jobs), "total_penalty")
        model.Add(total_penalty == sum(delivery_penalties))
        objective_components.append(total_penalty)

    # Set the final objective
    if objective_components:
        if len(objective_components) == 1:
            model.Minimize(objective_components[0])
        else:
            # Combine multiple objectives with weights
            total_objective = model.NewIntVar(-horizon, horizon * 3, "total_objective")
            model.Add(total_objective == sum(objective_components))
            model.Minimize(total_objective)
    else:
        # Fallback: minimize overall makespan
        makespan = model.NewIntVar(0, horizon, "makespan")
        model.AddMaxEquality(makespan, end_vars)
        model.Minimize(makespan)

    return model, all_tasks, forward_jobs, backward_jobs, unscheduled_jobs

# Example: create a simple CP-SAT model instance
def create_cp_model():
    model = cp_model.CpModel()
    # Example variable: start time of job 0 operation 0 on machine 0
    start_var = model.NewIntVar(0, 100, 'start_j0o0m0')
    # ...add more variables and constraints in later steps...
    return model

def plot_schedule(jobs, machines, all_tasks, solver, schedule_start, downtimes=None, scheduled_jobs=None):
    """
    Create a compact Gantt chart showing job scheduling over time.

    Y-axis: Machines listed in ascending order of list_seq (most compact display)
    X-axis: Timestamps showing when jobs are scheduled

    Optimized for displaying many machines with detailed hover information.
    """
    import plotly.graph_objects as go
    from plotly.colors import qualitative

    # Sort machines by list_seq in ascending order for y-axis
    sorted_machines = sorted(machines, key=lambda m: m.list_seq, reverse=True)

    # Create machine info dictionaries
    machine_dict = {m.machine_id: m for m in machines}
    job_dict = {j.job_id: j for j in jobs}
    operation_dict = {}
    for job in jobs:
        for op in job.operations:
            operation_dict[op.op_id] = op

    # Create y-axis labels in ascending order of list_seq (compact format)
    y_labels = []
    y_positions = {}
    for i, machine in enumerate(sorted_machines):
        # Compact label format for many machines - truncate long names if needed
        machine_name = machine.name[:12] + "..." if len(machine.name) > 15 else machine.name
        machine_type = machine.machine_type[:10] + "..." if len(machine.machine_type) > 13 else machine.machine_type
        label = f"{machine_type}/{machine_name}"
        y_labels.append(label)
        y_positions[machine.machine_id] = i

    # Prepare data for plotting
    fig = go.Figure()

    # Color palette for jobs
    colors = qualitative.Plotly
    job_colors = {}
    job_index = 0

    # Add scheduled operations (newly scheduled)
    scheduled_ops = []
    for (job_id, op_id, machine_id), (start_var, end_var, _, sel_var) in all_tasks.items():
        if solver.Value(sel_var) == 1:
            start_minutes = solver.Value(start_var)
            end_minutes = solver.Value(end_var)
            start_dt = schedule_start + timedelta(minutes=start_minutes)
            end_dt = schedule_start + timedelta(minutes=end_minutes)

            # Get job, operation, and machine details
            job = job_dict.get(job_id)
            operation = operation_dict.get(op_id)
            machine = machine_dict.get(machine_id)

            # Assign color to job if not already assigned
            if job_id not in job_colors:
                job_colors[job_id] = colors[job_index % len(colors)]
                job_index += 1

            # Create detailed hover text
            duration_hours = (end_minutes - start_minutes) / 60
            hover_text = (
                f"<b>Job Details:</b><br>"
                f"Job ID: {job_id}<br>"
                f"Quantity: {job.quantity if job else 'N/A'}<br>"
                f"Priority: {job.priority if job else 'N/A'}<br>"
                f"Delivery Date: {job.delivery_date.strftime('%Y-%m-%d %H:%M') if job else 'N/A'}<br>"
                f"<br><b>Operation Details:</b><br>"
                f"Operation ID: {op_id}<br>"
                f"Operation Name: {operation.name if operation else 'N/A'}<br>"
                f"<br><b>Machine Details:</b><br>"
                f"Machine ID: {machine_id}<br>"
                f"Machine Name: {machine.name if machine else 'N/A'}<br>"
                f"Machine Type: {machine.machine_type if machine else 'N/A'}<br>"
                f"<br><b>Schedule Details:</b><br>"
                f"Start: {start_dt.strftime('%Y-%m-%d %H:%M:%S')}<br>"
                f"End: {end_dt.strftime('%Y-%m-%d %H:%M:%S')}<br>"
                f"Duration: {duration_hours:.1f} hours"
            )

            scheduled_ops.append({
                'job_id': job_id,
                'start_dt': start_dt,
                'end_dt': end_dt,
                'machine_id': machine_id,
                'hover_text': hover_text,
                'color': job_colors[job_id],
                'name': f"Job {job_id}"
            })

    # Sort scheduled operations by job_id for consistent legend ordering
    scheduled_ops.sort(key=lambda x: x['job_id'])

    # Add traces for each job - group all operations of same job together
    added_jobs = set()
    for op in scheduled_ops:
        show_legend = op['job_id'] not in added_jobs
        added_jobs.add(op['job_id'])

        # Calculate duration in milliseconds for Plotly
        duration_ms = (op['end_dt'] - op['start_dt']).total_seconds() * 1000

        fig.add_trace(go.Bar(
            x=[duration_ms],
            y=[y_positions[op['machine_id']]],
            base=[op['start_dt']],
            orientation='h',
            name=op['name'],  # This should be the same for all operations of the same job
            legendgroup=f"job_{op['job_id']}",  # Group all operations of same job
            marker_color=op['color'],
            hovertemplate=op['hover_text'] + "<extra></extra>",
            showlegend=show_legend,
            offsetgroup=op['job_id']
        ))

    # Add downtimes
    if downtimes:
        for dt in downtimes:
            machine = machine_dict.get(dt.machine_id)
            hover_text = (
                f"<b>Downtime Details:</b><br>"
                f"Machine ID: {dt.machine_id}<br>"
                f"Machine Name: {machine.name if machine else 'N/A'}<br>"
                f"Machine Type: {machine.machine_type if machine else 'N/A'}<br>"
                f"Reason: {dt.reason}<br>"
                f"Start: {dt.start.strftime('%Y-%m-%d %H:%M:%S')}<br>"
                f"End: {dt.end.strftime('%Y-%m-%d %H:%M:%S')}<br>"
                f"Duration: {((dt.end - dt.start).total_seconds() / 3600):.1f} hours"
            )

            # Calculate duration in milliseconds for Plotly
            downtime_duration_ms = (dt.end - dt.start).total_seconds() * 1000

            fig.add_trace(go.Bar(
                x=[downtime_duration_ms],
                y=[y_positions[dt.machine_id]],
                base=[dt.start],
                orientation='h',
                name="Downtime",
                legendgroup="downtime",  # Group all downtimes together
                marker_color='red',
                marker_pattern_shape="x",
                hovertemplate=hover_text + "<extra></extra>",
                showlegend='Downtime' not in [trace.name for trace in fig.data],
                offsetgroup='downtime'
            ))

    # Add scheduled jobs (fixed)
    if scheduled_jobs:
        for sj in scheduled_jobs:
            machine = machine_dict.get(sj.machine_id)
            hover_text = (
                f"<b>Pre-Scheduled Job:</b><br>"
                f"Job ID: {sj.job_id}<br>"
                f"Operation ID: {sj.op_id}<br>"
                f"Machine ID: {sj.machine_id}<br>"
                f"Machine Name: {machine.name if machine else 'N/A'}<br>"
                f"Machine Type: {machine.machine_type if machine else 'N/A'}<br>"
                f"Start: {sj.start.strftime('%Y-%m-%d %H:%M:%S')}<br>"
                f"End: {sj.end.strftime('%Y-%m-%d %H:%M:%S')}<br>"
                f"Duration: {((sj.end - sj.start).total_seconds() / 3600):.1f} hours"
            )

            # Calculate duration in milliseconds for Plotly
            scheduled_duration_ms = (sj.end - sj.start).total_seconds() * 1000

            fig.add_trace(go.Bar(
                x=[scheduled_duration_ms],
                y=[y_positions[sj.machine_id]],
                base=[sj.start],
                orientation='h',
                name="Pre-Scheduled",
                legendgroup="pre_scheduled",  # Group all pre-scheduled jobs together
                marker_color='gray',
                marker_pattern_shape="/",
                hovertemplate=hover_text + "<extra></extra>",
                showlegend='Pre-Scheduled' not in [trace.name for trace in fig.data],
                offsetgroup='scheduled'
            ))

    # Update layout for compact display with many machines
    fig.update_layout(
        title=dict(
            text="Job Schedule - Machines in List Sequence Order",
            font=dict(size=14)
        ),
        xaxis=dict(
            title="Time",
            type='date',
            tickformat='%Y-%m-%d %H:%M',
            tickangle=45
        ),
        yaxis=dict(
            title="Type/Machines",
            tickmode='array',
            tickvals=list(range(len(y_labels))),
            ticktext=y_labels,
            categoryorder='array',
            categoryarray=y_labels,
            tickfont=dict(size=8),  # Smaller font for compact display
            automargin=True
        ),
        # Dynamic compact height calculation based on number of machines
        height=max(400, min(len(sorted_machines) * 25 + 150, 1200)),  # Cap at 1200px for very many machines
        font=dict(size=9),  # Smaller overall font
        margin=dict(l=200, r=120, t=60, b=80),  # Adjusted margins
        barmode='overlay',
        hovermode='closest',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.01,
            font=dict(size=8),  # Smaller legend font
            itemsizing='constant',
            itemwidth=30,
            groupclick="toggleitem"  # Enable double-click to isolate groups
        ),
        # Additional compact settings
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True
    )

    fig.show()

def solve_schedule_mixed(jobs, machines, downtimes, scheduled_jobs=None):
    """
    Mixed schedule solver that handles individual job scheduling directions.
    Each job can specify its own schedule_direction: 'forward', 'backward', or None.
    """
    model, all_tasks, forward_jobs, backward_jobs, unscheduled_jobs = model_basic_constraints(
        jobs, machines, downtimes, scheduled_jobs
    )
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    schedule_start = SCHEDULE_START  # Use the fixed reference

    # Initialize result dictionary for API response
    result = {
        "scheduled_operations": [],
        "delivery_date_analysis": [],
        "downtimes": [
            {
                "machine_id": dt.machine_id,
                "start": dt.start.strftime("%Y-%m-%d %H:%M:%S"),
                "end": dt.end.strftime("%Y-%m-%d %H:%M:%S"),
                "reason": dt.reason
            } for dt in downtimes
        ]
    }

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("=== MIXED SCHEDULING SOLUTION FOUND ===")
        print(f"Forward scheduled jobs: {forward_jobs}")
        print(f"Backward scheduled jobs: {backward_jobs}")
        print(f"Unscheduled jobs (no direction): {unscheduled_jobs}")

        print("\nScheduled Operations:")
        for (job_id, op_id, machine_id), (start_var, end_var, _, sel_var) in all_tasks.items():
            if solver.Value(sel_var) == 1:
                start = solver.Value(start_var)
                end = solver.Value(end_var)
                start_dt = schedule_start + timedelta(minutes=start)
                end_dt = schedule_start + timedelta(minutes=end)

                # Get job direction for display
                job = next((j for j in jobs if j.job_id == job_id), None)
                direction = job.schedule_direction if job else 'unknown'
                print(f"Job {job_id} ({direction}), Operation {op_id}, Machine {machine_id}: Start at {start_dt}, End at {end_dt}")
                
                # Add to result dictionary
                result["scheduled_operations"].append({
                    "job_id": job_id,
                    "operation_id": op_id,
                    "machine_id": machine_id,
                    "start": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "end": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "direction": direction
                })

        # Show delivery date compliance with scheduling direction context
        print("\nDelivery Date Analysis by Scheduling Direction:")
        for job in jobs:
            job_ops = [(job_id, op_id, machine_id) for (job_id, op_id, machine_id) in all_tasks.keys() if job_id == job.job_id]
            if job_ops:
                job_end_times = []
                for (job_id, op_id, machine_id) in job_ops:
                    start_var, end_var, _, sel_var = all_tasks[(job_id, op_id, machine_id)]
                    if solver.Value(sel_var) == 1:
                        job_end_times.append(solver.Value(end_var))

                if job_end_times:
                    latest_end = max(job_end_times)
                    completion_dt = schedule_start + timedelta(minutes=latest_end)
                    direction_info = f"[{job.schedule_direction}]"

                    if completion_dt <= job.delivery_date:
                        print(f"Job {job.job_id} {direction_info}: ✓ Completes {completion_dt} (Due: {job.delivery_date})")
                        status = "✓ Completes"
                        delay = 0
                    else:
                        delay = (completion_dt - job.delivery_date).total_seconds() / 3600  # Delay in hours
                        print(f"Job {job.job_id} {direction_info}: ✗ Late by {delay} - Completes {completion_dt} (Due: {job.delivery_date})")
                        status = f"✗ Late by {delay} hours"
                    
                    # Add to result dictionary
                    result["delivery_date_analysis"].append({
                        "job_id": job.job_id,
                        "direction": job.schedule_direction,
                        "status": status,
                        "completion_time": completion_dt.strftime("%Y-%m-%d %H:%M:%S"),
                        "due_date": job.delivery_date.strftime("%Y-%m-%d %H:%M:%S")
                    })

        print("\nDowntimes:")
        for dt in downtimes:
            print(f"Machine {dt.machine_id}: Downtime from {dt.start} to {dt.end} ({dt.reason})")
        if scheduled_jobs:
            print("\nScheduled jobs (fixed):")
            for sj in scheduled_jobs:
                print(f"Machine {sj.machine_id}: Scheduled job {sj.job_id} op {sj.op_id} from {sj.start} to {sj.end}")

        return solver, all_tasks, forward_jobs, backward_jobs, unscheduled_jobs, result
    else:
        print("❌ No solution found using mixed scheduling.")
        print("\n🔍 DIAGNOSTIC ANALYSIS:")

        # Analyze potential issues
        schedule_start = SCHEDULE_START

        # Check delivery date feasibility
        tight_jobs = []
        impossible_jobs = []

        for job in jobs:
            # Estimate minimum processing time for this job
            min_processing_time = 0
            for op in job.operations:
                # Find fastest machine for this operation
                fastest_time = float('inf')
                for machine_id, duration in op.possible_machines:
                    machine = next((m for m in machines if m.machine_id == machine_id), None)
                    if machine:
                        op_time = duration
                        fastest_time = min(fastest_time, op_time)
                if fastest_time != float('inf'):
                    min_processing_time += fastest_time

            # Check if delivery date is feasible
            time_available = (job.delivery_date - schedule_start).total_seconds() / 60

            if min_processing_time > time_available:
                impossible_jobs.append((job.job_id, min_processing_time, time_available))
            elif min_processing_time > time_available * 0.8:  # Less than 20% buffer
                tight_jobs.append((job.job_id, min_processing_time, time_available))

        # Check machine capacity conflicts
        machine_utilization = {}
        total_demand = 0

        for job in jobs:
            for op in job.operations:
                for machine_id, duration in op.possible_machines:
                    if machine_id not in machine_utilization:
                        machine_utilization[machine_id] = 0
                    machine_utilization[machine_id] += duration
                    total_demand += duration

        # Calculate available time (assuming 24/7 operation for simplicity)
        max_delivery = max(job.delivery_date for job in jobs)
        total_available_time = (max_delivery - schedule_start).total_seconds() / 60

        print(f"\n📊 CAPACITY ANALYSIS:")
        print(f"   Total processing demand: {total_demand:.0f} minutes ({total_demand/60:.1f} hours)")
        print(f"   Time horizon: {total_available_time:.0f} minutes ({total_available_time/60:.1f} hours)")
        print(f"   Overall utilization: {(total_demand/total_available_time)*100:.1f}%")

        # Report issues and suggestions
        if impossible_jobs:
            print(f"\n❌ IMPOSSIBLE JOBS ({len(impossible_jobs)} jobs):")
            for job_id, min_time, available_time in impossible_jobs[:5]:  # Show first 5
                deficit = min_time - available_time
                print(f"   Job {job_id}: Needs {min_time:.0f} min, has {available_time:.0f} min (deficit: {deficit:.0f} min)")
            if len(impossible_jobs) > 5:
                print(f"   ... and {len(impossible_jobs) - 5} more jobs")

        if tight_jobs:
            print(f"\n⚠️  TIGHT SCHEDULE JOBS ({len(tight_jobs)} jobs):")
            for job_id, min_time, available_time in tight_jobs[:5]:  # Show first 5
                buffer = available_time - min_time
                print(f"   Job {job_id}: Needs {min_time:.0f} min, has {available_time:.0f} min (buffer: {buffer:.0f} min)")
            if len(tight_jobs) > 5:
                print(f"   ... and {len(tight_jobs) - 5} more jobs")

        # Check backward scheduling conflicts
        backward_jobs = [job for job in jobs if job.schedule_direction == 'backward']
        if backward_jobs:
            print(f"\n🔄 BACKWARD SCHEDULING ANALYSIS:")
            print(f"   {len(backward_jobs)} jobs require backward scheduling")
            early_delivery_jobs = [job for job in backward_jobs if job.delivery_date < schedule_start + timedelta(days=7)]
            if early_delivery_jobs:
                print(f"   {len(early_delivery_jobs)} jobs have very early delivery dates")

        print(f"\n💡 SUGGESTED SOLUTIONS:")

        if impossible_jobs:
            print(f"   1. 📅 EXTEND DELIVERY DATES:")
            print(f"      - Move delivery dates later for jobs: {[job_id for job_id, _, _ in impossible_jobs[:10]]}")
            print(f"      - Add at least {max(deficit for _, deficit, _ in [(j, mt-at, at) for j, mt, at in impossible_jobs]):.0f} minutes buffer")

        if tight_jobs or impossible_jobs:
            print(f"   2. 📉 REDUCE JOB QUANTITIES:")
            print(f"      - Consider splitting large jobs into smaller batches")
            print(f"      - Reduce quantities for jobs with tight schedules")

        if total_demand / total_available_time > 0.9:
            print(f"   3. 🏭 INCREASE CAPACITY:")
            print(f"      - Add more machines or increase working hours")
            print(f"      - Current utilization is {(total_demand/total_available_time)*100:.1f}% (>90% is very tight)")

        if len(backward_jobs) > len(jobs) * 0.5:
            print(f"   4. 🔄 ADJUST SCHEDULING DIRECTIONS:")
            print(f"      - Too many jobs ({len(backward_jobs)}) use backward scheduling")
            print(f"      - Consider changing some to 'forward' or None for more flexibility")

        print(f"   5. 🎯 REDUCE PROBLEM COMPLEXITY:")
        print(f"      - Try scheduling fewer jobs at once (e.g., 20-50 jobs)")
        print(f"      - Focus on high-priority jobs first")

        print(f"   6. ⚙️  ADJUST SOLVER SETTINGS:")
        print(f"      - Increase solver time limit")
        print(f"      - Relax some constraints if business allows")

        print(f"\n🔧 QUICK FIXES TO TRY:")
        if impossible_jobs:
            earliest_impossible = min(impossible_jobs, key=lambda x: x[0])
            job_id, min_time, available_time = earliest_impossible
            deficit_days = (min_time - available_time) / (24 * 60)
            print(f"   - Move Job {job_id} delivery date {deficit_days:.1f} days later")

        if len(jobs) > 50:
            print(f"   - Reduce to first 20 jobs: jobs = jobs[:20]")

        if len(backward_jobs) > 10:
            print(f"   - Change some backward jobs to forward: job.schedule_direction = 'forward'")

        return None, None, [], [], [], result
def solve_schedule(jobs, machines, downtimes, scheduled_jobs=None, direction='forward'):
    """
    Legacy function for backward compatibility.
    For new implementations, use solve_schedule_mixed() to leverage individual job directions.
    """
    print(f"Warning: Using legacy solve_schedule with global direction '{direction}'.")
    print("Consider using solve_schedule_mixed() for individual job scheduling directions.")

    # Temporarily override all job directions for legacy compatibility
    original_directions = {}
    for job in jobs:
        original_directions[job.job_id] = job.schedule_direction
        job.schedule_direction = direction

    try:
        result = solve_schedule_mixed(jobs, machines, downtimes, scheduled_jobs)
        return result[:2]  # Return only solver and all_tasks for backward compatibility
    finally:
        # Restore original directions
        for job in jobs:
            job.schedule_direction = original_directions[job.job_id]

def schedule_mixed(jobs, machines, downtimes, scheduled_jobs=None):
    """
    Mixed scheduling: Use individual job schedule_direction settings.
    Each job can specify 'forward', 'backward', or None for its scheduling approach.

    Args:
        jobs: List of Job objects (each with schedule_direction attribute)
        machines: List of Machine objects
        downtimes: List of Downtime objects
        scheduled_jobs: List of already scheduled jobs (optional)

    Returns:
        tuple: (solver, all_tasks, forward_jobs, backward_jobs, unscheduled_jobs) if solution found
    """
    print("=== MIXED SCHEDULING ===")
    print("Scheduling jobs based on individual job schedule_direction settings.")

    # Show job directions
    forward_count = sum(1 for job in jobs if job.schedule_direction == 'forward')
    backward_count = sum(1 for job in jobs if job.schedule_direction == 'backward')
    none_count = sum(1 for job in jobs if job.schedule_direction is None or job.schedule_direction == 'none')

    print(f"Jobs with forward scheduling: {forward_count}")
    print(f"Jobs with backward scheduling: {backward_count}")
    print(f"Jobs with no specific direction: {none_count}")

    return solve_schedule_mixed(jobs, machines, downtimes, scheduled_jobs)

def schedule_forward(jobs, machines, downtimes, scheduled_jobs=None):
    """
    Forward scheduling: Start from current time and schedule jobs as early as possible.
    Minimizes makespan while penalizing late deliveries.

    Args:
        jobs: List of Job objects
        machines: List of Machine objects
        downtimes: List of Downtime objects
        scheduled_jobs: List of already scheduled jobs (optional)

    Returns:
        tuple: (solver, all_tasks) if solution found, (None, None) otherwise
    """
    print("=== FORWARD SCHEDULING ===")
    print("Scheduling jobs from current time forward, minimizing total completion time.")
    return solve_schedule(jobs, machines, downtimes, scheduled_jobs, direction='forward')

def schedule_backward(jobs, machines, downtimes, scheduled_jobs=None):
    """
    Backward scheduling: Start from delivery dates and work backward.
    Maximizes start times while ensuring all jobs meet their delivery dates.

    Args:
        jobs: List of Job objects
        machines: List of Machine objects
        downtimes: List of Downtime objects
        scheduled_jobs: List of already scheduled jobs (optional)

    Returns:
        tuple: (solver, all_tasks) if solution found, (None, None) otherwise
    """
    print("=== BACKWARD SCHEDULING ===")
    print("Scheduling jobs backward from delivery dates, starting as late as possible.")
    return solve_schedule(jobs, machines, downtimes, scheduled_jobs, direction='backward')

def validate_scheduling_input(jobs, machines, downtimes=None, scheduled_jobs=None):
    """
    Validate scheduling input and provide recommendations before running the scheduler.

    Returns:
        tuple: (is_valid, warnings, recommendations)
    """
    print("🔍 VALIDATING SCHEDULING INPUT...")

    warnings = []
    recommendations = []
    is_valid = True
    schedule_start = SCHEDULE_START

    # Basic validation
    if not jobs:
        warnings.append("No jobs provided")
        is_valid = False

    if not machines:
        warnings.append("No machines provided")
        is_valid = False

    if not is_valid:
        return False, warnings, recommendations

    # Check delivery date feasibility
    impossible_count = 0
    tight_count = 0

    for job in jobs:
        min_processing_time = 0
        for op in job.operations:
            fastest_time = float('inf')
            for machine_id, duration in op.possible_machines:
                machine = next((m for m in machines if m.machine_id == machine_id), None)
                if machine:
                    op_time = duration
                    fastest_time = min(fastest_time, op_time)
            if fastest_time != float('inf'):
                min_processing_time += fastest_time

        time_available = (job.delivery_date - schedule_start).total_seconds() / 60

        if min_processing_time > time_available:
            impossible_count += 1
        elif min_processing_time > time_available * 0.8:
            tight_count += 1

    # Check overall capacity
    total_demand = sum(
        sum(duration for machine_id, duration in op.possible_machines)
        for job in jobs for op in job.operations
    ) / len(machines)  # Average across machines

    max_delivery = max(job.delivery_date for job in jobs)
    total_available_time = (max_delivery - schedule_start).total_seconds() / 60
    utilization = total_demand / total_available_time if total_available_time > 0 else float('inf')

    # Generate warnings and recommendations
    if impossible_count > 0:
        warnings.append(f"{impossible_count} jobs have impossible delivery dates")
        recommendations.append(f"Extend delivery dates for {impossible_count} jobs")
        is_valid = False

    if tight_count > 0:
        warnings.append(f"{tight_count} jobs have very tight schedules")
        recommendations.append("Consider adding buffer time to tight jobs")

    if utilization > 1.0:
        warnings.append(f"Overall utilization {utilization*100:.1f}% exceeds capacity")
        recommendations.append("Reduce job quantities or extend time horizon")
        is_valid = False
    elif utilization > 0.9:
        warnings.append(f"High utilization {utilization*100:.1f}% may cause scheduling difficulties")
        recommendations.append("Consider reducing load or adding capacity")

    if len(jobs) > 50:
        warnings.append(f"Large number of jobs ({len(jobs)}) may increase solve time")
        recommendations.append("Consider scheduling in smaller batches")

    backward_jobs = sum(1 for job in jobs if job.schedule_direction == 'backward')
    if backward_jobs > len(jobs) * 0.6:
        warnings.append(f"High proportion of backward jobs ({backward_jobs}/{len(jobs)})")
        recommendations.append("Consider using more forward scheduling for flexibility")

    # Print results
    if is_valid:
        print("✅ Input validation PASSED")
    else:
        print("❌ Input validation FAILED")

    if warnings:
        print(f"\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   - {warning}")

    if recommendations:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"   - {rec}")

    print(f"\n📊 SUMMARY:")
    print(f"   Jobs: {len(jobs)}")
    print(f"   Machines: {len(machines)}")
    print(f"   Estimated utilization: {utilization*100:.1f}%")
    print(f"   Impossible jobs: {impossible_count}")
    print(f"   Tight jobs: {tight_count}")

    return is_valid, warnings, recommendations

def choose_scheduling_approach(jobs, machines, downtimes, scheduled_jobs=None, approach='mixed'):
    """
    Convenience function to choose between different scheduling approaches.

    Args:
        jobs: List of Job objects (with schedule_direction attributes for mixed approach)
        machines: List of Machine objects
        downtimes: List of Downtime objects
        scheduled_jobs: List of already scheduled jobs (optional)
        approach: 'mixed', 'forward', 'backward', or 'all' for comparison

    Returns:
        dict: Results containing solver(s) and task(s) information
    """
    results = {}

    if approach.lower() == 'mixed':
        result = schedule_mixed(jobs, machines, downtimes, scheduled_jobs)
        if len(result) == 5:  # Full mixed result
            solver, tasks, forward_jobs, backward_jobs, unscheduled_jobs = result
            results['mixed'] = {
                'solver': solver,
                'tasks': tasks,
                'forward_jobs': forward_jobs,
                'backward_jobs': backward_jobs,
                'unscheduled_jobs': unscheduled_jobs
            }
        else:
            results['mixed'] = {'solver': None, 'tasks': None}

    elif approach.lower() == 'forward':
        solver, tasks = schedule_forward(jobs, machines, downtimes, scheduled_jobs)
        results['forward'] = {'solver': solver, 'tasks': tasks}

    elif approach.lower() == 'backward':
        solver, tasks = schedule_backward(jobs, machines, downtimes, scheduled_jobs)
        results['backward'] = {'solver': solver, 'tasks': tasks}

    elif approach.lower() == 'all':
        print("\n" + "="*60)
        print("COMPARISON: Running all scheduling approaches")
        print("="*60)

        # Run mixed scheduling
        result_mixed = schedule_mixed(jobs, machines, downtimes, scheduled_jobs)
        if len(result_mixed) == 5:
            solver_m, tasks_m, forward_jobs, backward_jobs, unscheduled_jobs = result_mixed
            results['mixed'] = {
                'solver': solver_m,
                'tasks': tasks_m,
                'forward_jobs': forward_jobs,
                'backward_jobs': backward_jobs,
                'unscheduled_jobs': unscheduled_jobs
            }
        else:
            results['mixed'] = {'solver': None, 'tasks': None}

        print("\n" + "-"*60)

        # Run forward scheduling
        solver_f, tasks_f = schedule_forward(jobs, machines, downtimes, scheduled_jobs)
        results['forward'] = {'solver': solver_f, 'tasks': tasks_f}

        print("\n" + "-"*60)

        # Run backward scheduling
        solver_b, tasks_b = schedule_backward(jobs, machines, downtimes, scheduled_jobs)
        results['backward'] = {'solver': solver_b, 'tasks': tasks_b}

        # Print comparison summary
        print("\n" + "="*60)
        print("SUMMARY COMPARISON")
        print("="*60)

        solvers = [('Mixed', solver_m), ('Forward', solver_f), ('Backward', solver_b)]
        tasks_dict = [('Mixed', tasks_m), ('Forward', tasks_f), ('Backward', tasks_b)]

        for name, solver in solvers:
            if solver:
                tasks = next(tasks for task_name, tasks in tasks_dict if task_name == name)
                makespan = max([solver.Value(end_var) for (_, end_var, _, sel_var) in tasks.values() if solver.Value(sel_var) == 1])
                print(f"{name} Scheduling Makespan: {makespan} minutes")
            else:
                print(f"{name} Scheduling: No solution found")

    else:
        raise ValueError("approach must be 'mixed', 'forward', 'backward', or 'all'")

    return results

@app.route('/api/jobs', methods=['POST'])
def create_job():
    # Log the request
    logger.info("Received POST request for /api/jobs")

    # Get JSON data from request
    data = request.get_json()
    if not data:
        logger.error("No JSON data provided")
        return jsonify({
            'status': 'error',
            'message': 'No JSON data provided'
        }), 400

    # Parse machines from API
    machines = []
    for m in data.get('machines', []):
        machines.append(Machine(
            machine_id=m['machine_id'],
            name=m.get('name', m['machine_id']),
            machine_type=m.get('machine_type', ''),
            list_seq=m.get('list_seq', 0)
        ))

    # Parse downtimes from API
    downtimes = []
    for dt in data.get('downtimes', []):
        downtimes.append(Downtime(
            machine_id=dt['machine_id'],
            start=dt['start'],
            end=dt['end'],
            reason=dt.get('reason', '')
        ))

    # Parse scheduled_jobs from API
    scheduled_jobs = []
    for sj in data.get('scheduled_jobs', []):
        scheduled_jobs.append(ScheduledJob(
            job_id=sj['job_id'],
            op_id=sj['op_id'],
            machine_id=sj['machine_id'],
            start=sj['start'],
            end=sj['end']
        ))

    jobs = []
    for input_job in data.get('jobs', []):
        job_id = input_job.get('job_id')
        quantity = input_job.get('quantity')
        delivery_date_str = input_job.get('delivery_date')
        priority = input_job.get('priority', 0)
        schedule_direction = input_job.get('schedule_direction', 'forward')
        operations_data = input_job.get('operations', [])

        operations = [Operation(op['op_id'], op['name'], op['possible_machines']) for op in operations_data]

        job = Job(
            job_id=job_id,
            operations=operations,
            schedule_direction=schedule_direction,
            quantity=quantity,
            delivery_date=delivery_date_str,
            priority=priority,
        )
        jobs.append(job)

    is_valid, warnings, recommendations = validate_scheduling_input(jobs, machines, downtimes, scheduled_jobs)

    if not is_valid:
        # ...existing error handling code...
        return jsonify({
            'status': 'error',
            'message': 'Input validation failed',
            'warnings': warnings,
            'recommendations': recommendations
        }), 400

    print("\n" + "="*60)
    print("STARTING MIXED SCHEDULING")
    print("="*60)

    print("✅ Input validation passed. Starting mixed scheduling (using individual job directions)...")
    _, _, _, _, _, result = solve_schedule_mixed(jobs, machines, downtimes, scheduled_jobs)
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=6000)

