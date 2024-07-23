import os    # for file handling  
import sys   # for writing/printing messages
import math

import re    # for splitting input

from file_utils import remove_file, rename_file, DISK_PATH

######### CONSTANTS (unlimited number allowed) #######################
PATH = os.path.join(DISK_PATH, "") # path to store files (DO NOT CHANGE)
SEP = "====" # used to separate messages when printing them out
ADMIN = os.path.join(PATH, "admin.txt") 
RECYLING = os.path.join(PATH, "recycling.txt") 

######### VARIABLES (at most 10 active at any time) ##################
counter_messages = 0
message_max_val = 200
message_per_file_val = 10
ids_to_be_recycled = ""
current_username = ""

######### EXCEPTIONS #################################################
class MessagesFullExn(Exception):
    print("Exception called")
    pass

######### SYSTEM SETUP, SHUTDOWN, AND RESET ##########################

def connect(username: str, restart: bool) -> None:
    """
    Starts a connection to the system by the named user

    Parameters:
    username -- the name of the user who is connecting (they will be the
                poster of messages added until they disconnect)
    restart -- if the program has just connected to the server
    """
    
    global current_username 
    current_username = username
    if restart:
        if not os.path.exists(PATH) and not os.path.isdir(PATH):
            os.mkdir(PATH)
        open(ADMIN, 'a').close()  
        open(RECYLING, 'a').close()

        with open(RECYLING, 'r') as file:
            recycled_ids = file.read().strip()
            if recycled_ids:
                global ids_to_be_recycled
                for id in recycled_ids.split():
                    if not ids_to_be_recycled:
                        ids_to_be_recycled += id
                    else:
                        ids_to_be_recycled += " "+id   
                ids_to_be_recycled += " "         

    with open(ADMIN, 'r') as file:
        global message_max_val
        global message_per_file_val
        global counter_messages
        first_line = file.readline()
        if first_line.strip():
            message_max_val = first_line.split(":")[1].strip()
            message_per_file_val = file.readline().split(":")[1].strip()
            counter_messages = file.readline().split(":")[1].strip()
          

def disconnect() -> None:
    """
    Disconnects the current user (this will depend on your design) and saves
    data as necessary so that the system can resume even if the Python program
    is restarted 
    """
    global counter_messages
    with open(ADMIN, 'a') as file:
        file.write(f"message_max_val: {message_max_val}\nmessage_per_file_val: {message_per_file_val}\ncounter_messages: {counter_messages}\n")   
    counter_messages = 0  
    with open(RECYLING, 'w') as file:
        file.write("")
    global ids_to_be_recycled 
    formatted_ids = "\n".join(ids_to_be_recycled.split())
    with open(RECYLING, 'a') as file:
        file.write(formatted_ids)



def soft_disconnect() -> None:
    """
    Disconnects the current user (this will depend on your design)
    """
    global current_username
    current_username = ""
    
    


def clean_reset(msg_max_val=200, msg_per_file_val=10) -> None:
    """
    Deletes all the disk files to start a clean run of the system.
    Supports setting different constant values.
    Useful for testing.

    Parameters:
    msg_max_val -- max number of messages system can hold
    msg_per_file_val -- max number of messages each file can hold

    """

    global message_max_val
    message_max_val = msg_max_val
    global message_per_file_val
    message_per_file_val = msg_per_file_val
    global counter_messages
    counter_messages = 0
    global ids_to_be_recycled
    ids_to_be_recycled = ""
    if os.path.exists(PATH) and os.path.isdir(PATH):
        for file_name in os.listdir(PATH):
            file_path = os.path.join(PATH, file_name)
            remove_file(file_path)
     

    # TODO: Fill in with what makes sense for your design.
    # It might relate to how you store your necessary info
    # between (dis)connections to the server!
    # Feel free to pass in different values when testing for clean_reset,
    # 200 and 10 are just the default. (You do not need to edit
    # the method header to do this. Just pass different values in when calling)


######## DESIGN HELPERS ##########################################
def write_msg(f, id: int, who: str, subj: str, msg: str, labeled=False) -> str:
    """
    Writes a message to the given file handle. e.g., If you want to print to a
    file, open the file and use fh from the following code as the first argument

           with open(FILENAME, mode) as fh

    If you want to print to the console/screen, you can pass the following as 
    the first argument

            sys.stdout

    msg can be passed as false to suppress printing the text/body of the message.

    Parameters:
    f -- file descriptor
    id -- message id
    who -- poster
    subj -- subject line
    msg -- body text
    labeled -- boolean deciding if labels should also be used
    """
    output = SEP + "\n"      
    f.write(SEP + "\n")
    f.write("ID: " + str(id) + "\n")
    output += "ID: " + str(id) + "\n"
    if labeled:
        output += who
        f.write(who)
        output += subj
        f.write(subj)
        if msg: 
            f.write(msg)
            output += msg
    else: # needs labels
        output += "Poster: " + who + "\n"
        f.write("Poster: " + who + "\n")
        output += "Subject: " + subj + "\n"
        f.write("Subject: " + subj + "\n")
        if msg: 
            f.write("Text: " + msg + "\n")
            output +="Text: " + msg + "\n"
    return output

def split_string_exclude_quotes(s) -> list[str]:
    """
    Splits a given string and splits it based on spaces, while also grouping
    words in double quotes together.

    Parameters:
    s -- string to be split
    Returns:
    A list of strings after splitting
    Example:
    'separate "these are together" separate` --> ["separate", "these are together", "separate"]
    """
    # This pattern matches a word outside quotes or captures a sequence of characters inside double quotes without including the quotes
    pattern = r'"([^"]*)"|(\S+)'
    matches = re.findall(pattern, s)
    # Each match is a tuple, so we join non-empty elements
    return [m[0] if m[0] else m[1] for m in matches]


####### CORE SYSTEM OPERATIONS ####################################


def show_menu(): 
    """
    Prints the menu of options.
    """
    print("Please select an option: ")
    print("  - type A <subj> <msg> to add a message")
    print("  - type D <msg-num> to delete a message")
    print("  - type S for a summary of all messages")
    print("  - type S <text> for a summary of messages with <text> in title or poster")
    print("  - type V <msg-num> to view the contents of a message")
    print("  - type X to exit (and terminate the Python program)")
    print("  - type softX to exit (and keep the Python program running)")


def post_msg(subj: str, msg: str) -> None:
    """
    Stores a new message (however it makes sense for your design). Your code
    should determine what ID to use for the message, and the poster of the
    message should be the user who is connected when this function is called

    Parameters:
    subj -- subject line
    msg -- message body
    """
    global counter_messages
    global id
    id = 0
    if int(counter_messages) >= int(message_max_val):
            raise MessagesFullExn("Messages limit reached")
    
    global ids_to_be_recycled
    if not ids_to_be_recycled:
        id = int(counter_messages)+1
        text_file = f"file{id%(int(int(message_max_val)/10)+1)}.txt"
        file_path = os.path.join(PATH, text_file)
        with open(file_path, 'a') as file:
            file.write(f"ID: {id}\nPoster: {current_username}\nSubject: {subj}\nText: {msg}\n") 
    else:
        id = ids_to_be_recycled.split(" ")[0].strip()
        ids_to_be_recycled = ids_to_be_recycled.replace(id+" ", "")
        text_file = f"file{str(int(id)%(int(int(message_max_val)/10)+1))}.txt"
        file_path = os.path.join(PATH, text_file)
        with open(file_path, 'a') as file:
            file.write(f"ID: {id}\nPoster: {current_username}\nSubject: {subj}\nText: {msg}\n")      

    counter_messages = int(counter_messages) + 1

def find_print_msg(id: int) -> str:
    """
    Prints contents of message for given ID. 

    Parameters:
    id -- message ID
    Returns:
    The string to be printed (for autograder).
    """
    message = ""
    for file_name in os.listdir(PATH):
        if file_name.startswith("file"):
            file_path = os.path.join(PATH, file_name)
            with open(file_path, 'r') as file:
                while True:
                    line = file.readline()
                    if not line:
                        break
                    if line.startswith("ID:"):
                        message_id = line.split(":")[1].strip()
                        if (message_id == str(id)):
                            poster = file.readline().split(":")[1].strip()
                            subject = file.readline().split(":")[1].strip()
                            text = file.readline().split(":")[1].strip()
                            message += f"ID: {message_id}\nPoster: {poster}\nSubject: {subject}\nText: {text}\n"
                            write_msg(sys.stdout, message_id, poster, subject, text)
                            return message
    return message 

def remove_msg(id: int) -> None:
    """
    Removes a message from however your design is storing it. A removed message
    should no longer appear in summaries, be available to print, etc.
    """
    text_file_1 = f"file{id%(int(int(message_max_val)/10)+1)}.txt"
    file_path_1 = os.path.join(PATH, text_file_1)
    text_file_2 = f"temp.txt"
    file_path_2 = os.path.join(PATH, text_file_2)

    with open(file_path_1, 'r') as input_file, open(file_path_2, 'a') as output_file:
        count = 4
        flag = False
        for line in input_file:
            if line.split(":")[1].strip() == str(id):
                flag = True
            if count == 4 and flag is False or count <1:
                output_file.write(line)
            if flag is True:
                count -= 1
    remove_file(file_path_1)
    rename_file(file_path_2, file_path_1)

    global ids_to_be_recycled
    global counter_messages
    if (flag == True):
        ids_to_be_recycled +=(str(id)+" ")
        counter_messages = int(counter_messages) - 1

    
    

def print_summary(term = "") -> str:
    """
    Prints summary of messages that have the search term in the who or subj fields.
    A search string of "" will match all messages.
    Summary does not need to present messages in order of IDs.

    Returns:
    A string to be printed (for autograder).
    """
    summary = ""
    for file_name in os.listdir(PATH):
        if file_name.startswith("file"):
            file_path = os.path.join(PATH, file_name)

            with open(file_path, 'r') as file:
                while True:
                    line = file.readline()
                    if not line:
                        break
                    if line.startswith("ID:"):
                        message_id = line.split(":")[1].strip()
                        poster = file.readline().split(":")[1].strip()
                        subject = file.readline().split(":")[1].strip()

                        if term.lower() in poster.lower() or term.lower() in subject.lower() or not term:
                            summary += write_msg(sys.stdout, message_id, poster, subject, False)
    return summary
    

############### SAMPLE FROM HANDOUT ######################

# Our test cases will look like this, with assertions intertwined

def sample():
    connect("kathi", True)
    post_msg("post homework?", "is the handout ready?")
    post_msg("vscode headache", "reinstall to fix the config error")
    soft_disconnect()  # keep the python programming running and connect another user
    connect("nick", False)
    print_summary("homework")
    find_print_msg(1)
    post_msg("handout followup", "yep, ready to go")
    remove_msg(1)
    print_summary()
    disconnect()

############### MAIN PROGRAM ############################

# If you want to run the code interactively instead, use the following:

def start_system():
    """
    Loop to run the system. It does not do error checking on the inputs that
    are entered (and you do not need to fix that problem)
    """
    
    print("Welcome to our BBS!")
    print("What is your username?")
    connect(input(), True)

    done = False
    while(not done):
        show_menu()
        whole_input = input() # read the user command
        choice = split_string_exclude_quotes(whole_input) #split into quotes
        match choice[0].upper():
            case "A": 
                post_msg(choice[1], choice[2]) # subject, text
            case "D": 
                remove_msg(int(choice[1]))
            case "S": 
                if len(choice) == 1:
                    print_summary("")
                else:
                    term = choice[1]
                    print_summary(term)
            case "V":
                find_print_msg(int(choice[1]))
            case "X": 
                disconnect()
                done = True
                exit()
            case "SOFTX":
                soft_disconnect()

                # restart menu 
                print("What's your username?")
                connect(input(), False)
            case _: 
                print("Unknown command")

# uncomment next line if want the system to start when the file is run
#clean_reset(5)
#start_system()
