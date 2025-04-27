import xmlrpc.client
import time

def main():
    proxy = xmlrpc.client.ServerProxy("http://localhost:10001")
    
    if proxy.acquire_lock("client1"):
        print("🔒 LOCK ACQUIRED - Other clients will be blocked")
        print("Press Ctrl+C to release the lock")
        try:
            while True:  # Hold lock indefinitely
                time.sleep(1)
        except KeyboardInterrupt:
            proxy.release_lock("client1")
            print("🔓 Lock released")
    else:
        print("Server is already locked by another client")

if __name__ == "__main__":
    main()