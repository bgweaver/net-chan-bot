import random

def load_responses(file_name):
    with open(file_name, 'r') as file:
        responses = file.readlines()
    return [response.strip() for response in responses]

def get_response(event_type, message):
    
    if event_type == "updates":
        responses = load_responses('./responses/update_responses.txt')
    elif event_type == "backup":
        responses = load_responses('./responses/backup_responses.txt')
    elif event_type == "sync":
        responses = load_responses('./responses/sync_responses.txt')
    elif event_type =="unraid":
        responses = load_responses('./responses/unraid_responses.txt')
    elif event_type == "failed":
        responses = load_responses('./responses/failure_responses.txt')
    else:
        responses = ["🌸 **Net-chan Update!** 🌸\n" + message]

    response = random.choice(responses)
    if '{message}' in response:
        return response.format(message=message)
    else:
        return response