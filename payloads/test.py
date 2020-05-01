RETURNS = True # flag for if the program should wait for execute to return value

def execute(caller): # caller is refernce to execution thread if RETURNS==False
    print(caller.data) # argument passed as one string
    print("Execute payload")
    return "This is returned if RETURNS flag is set"
