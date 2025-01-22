"""
script to run MongoDB and microservices simultaneously using multiprocessing.
"""
import subprocess
import sys
import time
import os
from multiprocessing import Process
import platform


def is_mongodb_running():
    """Check if MongoDB is already running"""
    if platform.system() == "Windows":
        output = subprocess.run(["tasklist"], capture_output=True, text=True)
        return "mongod.exe" in output.stdout
    else:
        try:
            output = subprocess.run(["pgrep", "mongod"], capture_output=True)
            return output.returncode == 0
        except FileNotFoundError:
            return False


def start_mongodb():
    """Start MongoDB server"""
    try:
        if not is_mongodb_running():
            # Create data directory if it doesn't exist
            data_dir = os.path.join(os.getcwd(), "mongodb_data")
            os.makedirs(data_dir, exist_ok=True)

            print("Starting MongoDB...")
            if platform.system() == "Windows":
                return subprocess.Popen(["mongod", "--dbpath", data_dir])
            else:
                return subprocess.Popen(["mongod", "--dbpath", data_dir])
        else:
            print("MongoDB is already running")
            return None
    except FileNotFoundError:
        print("MongoDB executable not found. Please ensure it is installed and in the PATH.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error starting MongoDB: {e}")
        sys.exit(1)


def run_service(command):
    """Run a service using the specified command"""
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Service failed to start: {e}")
    except KeyboardInterrupt:
        pass


def main():
    # Store process references
    processes = []

    try:
        # Start MongoDB first
        mongodb_process = start_mongodb()
        if mongodb_process:
            processes.append(mongodb_process)
            # Wait for MongoDB to start
            time.sleep(5)

        # Create virtual environment and install dependencies if needed
        if not os.path.exists("venv"):
            print("Creating virtual environment...")
            subprocess.run("python -m venv venv", shell=True, check=True)
            
            # Install requirements
            if platform.system() == "Windows":
                pip_cmd = ".\\venv\\Scripts\\pip"
            else:
                pip_cmd = "./venv/bin/pip"
                
            subprocess.run(f"{pip_cmd} install -r requirements.txt", shell=True, check=True)

        # Determine Python path based on platform
        if platform.system() == "Windows":
            python_path = ".\\venv\\Scripts\\python"
        else:
            python_path = "./venv/bin/python"

        # Commands to run services
        services = [
            f"{python_path} user_service/main.py",
            f"{python_path} order_service/main.py"
        ]

        # Start each service in a separate process
        for service in services:
            process = Process(target=run_service, args=(service,))
            process.start()
            processes.append(process)
            time.sleep(2)  # Give each service time to start

        print("\nAll services are running!")
        print("MongoDB: localhost:27017")
        print("User Service: http://localhost:8000")
        print("Order Service: http://localhost:8001")

        # Wait for all processes to complete
        for process in processes:
            process.join()

    except KeyboardInterrupt:
        print("\nStopping all services...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        # Cleanup processes
        for process in processes:
            if isinstance(process, subprocess.Popen):
                # For MongoDB process
                if platform.system() == "Windows":
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)])
                else:
                    process.terminate()
                    process.wait()
            else:
                # For service processes
                process.terminate()
                process.join()

        print("All services stopped")


if __name__ == "__main__":
    main()
