import subprocess

# Run the pip show command for Flask
result = subprocess.run(['pip', 'show', 'requests'], capture_output=True, text=True) #Flask, Flask_PyMongo, pymongo, bcrypt, pytest, selenium, requests

# Print the output
print(result.stdout)
if result.stderr:
    print(result.stderr)  # Print any error messages

def vv():
    print("")