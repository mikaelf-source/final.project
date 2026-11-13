
from dataclasses import dataclass
from drafter import *
from bakery import assert_equal


SUBJECTS = ["Math", "Computer Science", "Chemistry", "English", "Civics"]


@dataclass
class Assignment:
    """Represents an individual school assignment."""
    name: str
    subject: str
    due_date: str
    is_urgent: bool
    is_completed: bool


@dataclass
class State:
    """Stores the application information."""
    assignments: list[Assignment]
    current_filter: str
    selected_subject: str
    status_message: str


def index(state: State) -> Page:
    """Displays the main dashboard."""

    if len(state.assignments) == 0:
        summary = "No assignments added yet. Get started by adding a task!"
    else:
        completed_count = sum(1 for a in state.assignments if a.is_completed)
        summary = f"Total: {len(state.assignments)} | Completed: {completed_count}"

    assignment_text = []
    assignment_buttons = []

    for i, a in enumerate(state.assignments):

        if state.current_filter == "Pending" and a.is_completed:
            continue

        if state.current_filter == "Completed" and not a.is_completed:
            continue

        if state.selected_subject != "All" and a.subject != state.selected_subject:
            continue

        urgency = " [URGENT]" if a.is_urgent else ""
        status = "Done" if a.is_completed else "Pending"

        assignment_text.append(
            f"{a.name}{urgency} ({a.subject}) - Due: {a.due_date} - [{status}]"
        )

        assignment_buttons.append(
            Button("Toggle Status", toggle_completion, Argument("item_index", i))
        )

        assignment_buttons.append(
            Button("Delete", delete_assignment, Argument("item_index", i))
        )

    if len(assignment_text) == 0:
        assignment_text.append("No assignments match your filters.")

    navigation = Row(
        Button("Add Assignment", add_assignment_page),
        Button("Filter Options", filter_page),
        Button("View Completed", completed_tasks_page),
        Button("View Pending", pending_tasks_page)
    )

    tasks = BulletedList(assignment_text)

    action_buttons = Row(*assignment_buttons)

    dashboard = Row(
        navigation,
        tasks,
        action_buttons
    )

    return Page(
        "Student Assignment Tracker",
        state.status_message,
        summary,
        dashboard
    )


def add_assignment_page(state: State) -> Page:
    """Displays the form for adding an assignment."""

    form = Row(
        TextBox("name", label="Assignment Name"),
        SelectBox("subject", SUBJECTS, label="Subject"),
        TextBox("due_date", label="Due Date (e.g. Nov 20)"),
        CheckBox("is_urgent", label="High Priority / Urgent")
    )

    buttons = Row(
        Button("Save Assignment", create_assignment),
        Button("Back to Home", index)
    )

    return Page(
        "Add New Assignment",
        "Enter your assignment information below.",
        form,
        buttons
    )


def create_assignment(state: State, name: str, subject: str,
                      due_date: str, is_urgent: bool) -> Page:
    """Creates and saves a new assignment."""

    if name.strip() == "":
        state.status_message = "Error: Assignment name cannot be empty."

    else:
        new_assignment = Assignment(
            name,
            subject,
            due_date,
            is_urgent,
            False
        )

        state.assignments.append(new_assignment)
        state.status_message = f"Successfully added '{name}'!"

    return index(state)


def toggle_completion(state: State, item_index: int) -> Page:
    """Changes an assignment between completed and pending."""

    if 0 <= item_index < len(state.assignments):
        assignment = state.assignments[item_index]
        assignment.is_completed = not assignment.is_completed
        state.status_message = "Updated assignment completion status."

    return index(state)


def delete_assignment(state: State, item_index: int) -> Page:
    """Deletes an assignment."""

    if 0 <= item_index < len(state.assignments):
        removed = state.assignments.pop(item_index)
        state.status_message = f"Deleted '{removed.name}'."

    return index(state)


def filter_page(state: State) -> Page:
    """Displays filtering options."""

    filters = Row(
        SelectBox(
            "current_filter",
            ["All", "Pending", "Completed"],
            label="Status Filter"
        ),
        SelectBox(
            "selected_subject",
            ["All"] + SUBJECTS,
            label="Subject Filter"
        )
    )

    buttons = Row(
        Button("Apply Filter", apply_filter),
        Button("Back to Home", index)
    )

    return Page(
        "Filter Assignments",
        "Choose which assignments you want to see.",
        filters,
        buttons
    )


def apply_filter(state: State, current_filter: str,
                 selected_subject: str) -> Page:
    """Applies the selected filters."""

    state.current_filter = current_filter
    state.selected_subject = selected_subject
    state.status_message = "Filters updated."

    return index(state)


def completed_tasks_page(state: State) -> Page:
    """Displays completed assignments."""

    completed = [a for a in state.assignments if a.is_completed]

    task_text = []

    for a in completed:
        task_text.append(
            f"{a.name} ({a.subject}), Due: {a.due_date}"
        )

    if len(task_text) == 0:
        task_text.append("No completed assignments.")

    return Page(
        "Completed Tasks",
        f"Total completed: {len(completed)}",
        BulletedList(task_text),
        Button("Back to Home", index)
    )


def pending_tasks_page(state: State) -> Page:
    """Displays pending assignments."""

    pending = [a for a in state.assignments if not a.is_completed]

    task_text = []

    for a in pending:
        task_text.append(
            f"{a.name} ({a.subject}), Due: {a.due_date}"
        )

    if len(task_text) == 0:
        task_text.append("No pending assignments.")

    return Page(
        "Pending Tasks",
        f"Total pending: {len(pending)}",
        BulletedList(task_text),
        Button("Back to Home", index)
    )


# UNIT TESTS

st_index = State([], "All", "All", "Welcome")
assert_equal(index(st_index), index(st_index))

st_add = State([], "All", "All", "")
assert_equal(add_assignment_page(st_add), add_assignment_page(st_add))

st_create = State([], "All", "All", "")
create_assignment(st_create, "Physics Lab", "Chemistry", "Nov 20", False)
assert_equal(len(st_create.assignments), 1)
assert_equal(st_create.assignments[0].name, "Physics Lab")

st_error = State([], "All", "All", "")
create_assignment(st_error, "   ", "Math", "Nov 22", True)
assert_equal(len(st_error.assignments), 0)
assert_equal(
    st_error.status_message,
    "Error: Assignment name cannot be empty."
)

st_toggle = State(
    [Assignment("Essay", "English", "Nov 12", False, False)],
    "All", "All", ""
)
toggle_completion(st_toggle, 0)
assert_equal(st_toggle.assignments[0].is_completed, True)

st_delete = State(
    [Assignment("Quiz", "Math", "Nov 14", True, False)],
    "All", "All", ""
)
delete_assignment(st_delete, 0)
assert_equal(len(st_delete.assignments), 0)

st_filter = State([], "All", "All", "")
apply_filter(st_filter, "Pending", "Math")
assert_equal(st_filter.current_filter, "Pending")
assert_equal(st_filter.selected_subject, "Math")

st_completed = State(
    [Assignment("Done Task", "Civics", "Nov 1", False, True)],
    "All", "All", ""
)
assert_equal(
    completed_tasks_page(st_completed),
    completed_tasks_page(st_completed)
)

st_pending = State(
    [Assignment("Pending Task", "Civics", "Nov 5", False, False)],
    "All", "All", ""
)
assert_equal(
    pending_tasks_page(st_pending),
    pending_tasks_page(st_pending)
)


# START APPLICATION

if __name__ == "__main__":
    start_server(
        State([], "All", "All", "Welcome to your Assignment Tracker!"),
        title="Student Assignment Tracker",
        port=8080
    )

