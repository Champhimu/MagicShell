# import subprocess
import subprocess

while True:
    command = input("PyShell> ")
    if command.lower() in ["exit", "quit"]:
        print("Exiting shell...")
        break
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Error:", result.stderr)
    except Exception as e:
        print("Exception:", e)
