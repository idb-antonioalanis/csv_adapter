from adapter import Adapter

if __name__ == "__main__":
    valid_files = Adapter().adapt()

    print(f"Valid files - {valid_files}.")
