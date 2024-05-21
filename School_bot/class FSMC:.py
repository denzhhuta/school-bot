# class FSMC:
#     def __init__(self):
#         self.state = "locked"
#         self.transitions = {
#             "locked": {"lock": "locked", "unlock": "unlocked"},
#             "unlocked":{"lock": "locked", "unlock": "unlocked"}
#         }
        
#     def process_input(self, action):
#         next_state = self.transitions[self.state].get(action)
#         if next_state:
#             self.state = next_state
#             return f"Door is {self.state}"
#         else:
#             return "Invalid action"
        
# fsm = FSMC()

# fsm.process_input("unlock")

# print(fsm.state)

# fsm.process_input("lock")

# print(fsm.state)

# print(fsm.state)
######################################################################
######################################################################
# from flask import Flask, render_template_string, request
# import requests

# app = Flask(__name__)

# class FSM:
#     def __init__(self):
#         self.state = "Off"

#     def toggle_state(self):
#         if self.state == "Off":
#             self.state = "On"
#         else:
#             self.state = "Off"

# # Initialize the FSM
# fsm = FSM()

# # HTML template for the web page
# html_template = '''
# <!DOCTYPE html>
# <html>
# <head>
#     <title>FSM Example</title>
# </head>
# <body>
#     <h1>Finite State Machine Example</h1>
#     <p>Current State: {{ state }}</p>
#     <form method="post">
#         <button type="submit" name="action" value="toggle">Toggle</button>
#     </form>
# </body>
# </html>
# '''

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         action = request.form.get('action')
#         if action == 'toggle':
#             fsm.toggle_state()

#     return render_template_string(html_template, state=fsm.state)

# if __name__ == '__main__':
#     app.run(debug=True)

######################################################################
######################################################################
x
from flask import Flask, request, jsonify

app = Flask(__name__)

# Finite State Machine for task states
class TaskFSM:
    def __init__(self):
        self.state = "To Do"
        self.transitions = {
            "To Do": {"start": "In Progress"},
            "In Progress": {"complete": "Completed", "reject": "To Do"},
            "Completed": {}
        }

    def process_input(self, action):
        next_state = self.transitions[self.state].get(action)
        if next_state:
            self.state = next_state

# Create an instance of the FSM
task_fsm = TaskFSM()

# Routes
@app.route("/task", methods=["POST"])
def create_task():
    data = request.get_json()
    task_name = data.get("task_name")
    task_id = data.get("task_id")
    # Save the task to the database with initial state "To Do"

    return jsonify({"message": "Task created successfully.", "task_id": task_id})

@app.route("/task/<task_id>/start", methods=["PUT"])
def start_task(task_id):
    # Update the state of the task to "In Progress" in the database
    task_fsm.process_input("start")
    return jsonify({"message": "Task started successfully."})

@app.route("/task/<task_id>/complete", methods=["PUT"])
def complete_task(task_id):
    # Update the state of the task to "Completed" in the database
    task_fsm.process_input("complete")
    return jsonify({"message": "Task completed successfully."})

@app.route("/task/<task_id>/reject", methods=["PUT"])
def reject_task(task_id):
    # Update the state of the task to "To Do" in the database
    task_fsm.process_input("reject")
    return jsonify({"message": "Task rejected."})

if __name__ == "__main__":
    app.run(debug=True)
