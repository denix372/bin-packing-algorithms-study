import platform
import psutil

def system_report():
    os_info = platform.platform()
    cpu_info = platform.processor()
    physical_cores = psutil.cpu_count(logical=False)
    logical_cores = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    memory = psutil.virtual_memory()

    print("=== System Information Report ===")
    print(f"Operating System: {os_info}")
    print(f"Processor: {cpu_info}")
    print(f"Physical Cores: {physical_cores}")
    print(f"Logical Cores: {logical_cores}")
    if cpu_freq:
        print(f"CPU Frequency: {cpu_freq.current:.2f} MHz")
    print(f"Available Memory: {memory.available / (1024 ** 3):.2f} GB")
    print(f"Total Memory: {memory.total / (1024 ** 3):.2f} GB")

if __name__ == "__main__":
    system_report()
