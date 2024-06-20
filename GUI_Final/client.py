import socket
import sys

def send_command(client_socket, command):
    client_socket.sendall(command.encode())
    print(f"Sent: {command}")

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 65432))

    while True:
        print("Menu:")
        print("1. Set Speed")
        print("2. Set RPM")
        print("3. Toggle Left Indicator")
        print("4. Toggle Right Indicator")
        print("5. Exit")
        
        choice = input("Enter your choice: ")

        if choice == '1':
            speed = input("Enter speed (0-180): ")
            try:
                speed = int(speed)
                if 0 <= speed <= 180:
                    send_command(client_socket, f"speed,{speed}")
                else:
                    print("Invalid speed! Enter a number between 0 and 180.")
            except ValueError:
                print("Invalid input! Enter a valid number.")
        
        elif choice == '2':
            rpm = input("Enter RPM (0-8000): ")
            try:
                rpm = int(rpm)
                if 0 <= rpm <= 8000:
                    send_command(client_socket, f"rpm,{rpm}")
                else:
                    print("Invalid RPM! Enter a number between 0 and 8000.")
            except ValueError:
                print("Invalid input! Enter a valid number.")
        
        elif choice == '4':
            send_command(client_socket, "right_indicator,toggle")
        
        elif choice == '3':
            send_command(client_socket, "left_indicator,toggle")
        
        elif choice == '5':
            print("Exiting...")
            send_command(client_socket, "exit")
            break
        
        else:
            print("Invalid choice! Enter 1, 2, 3, 4, or 5.")
    
    client_socket.close()

if __name__ == '__main__':
    main()
