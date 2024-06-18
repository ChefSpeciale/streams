import os
import time, sys
import urllib
import json
import urllib2
import ssl
import random
import string
import base64

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def update_progress(progress):
    barLength = 40
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength * progress))
    text = "\rPercent: [{0}] {1}% {2}".format("#" * block + "-" * (barLength - block), progress * 100, status)
    sys.stdout.write(text)
    sys.stdout.flush()

def representsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def getText(prompt, default=""):
    value = raw_input(prompt)

    if value == "" and default != "":
        return default

    if value == "" and default == "":
        while value == "":
            value = raw_input(prompt)

            if value != "":
                return value

    return value

def getInt(prompt, default):
    value = raw_input(prompt)

    if value == "":
        return default

    while not representsInt(value):
        value = raw_input(prompt)

        if value == "":
            return default

    return int(value)

def rand_str(length):
    result = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
    return result

def log_request_response(url, response):
    log_entry = {
        'url': url,
        'response': response
    }
    with open('requests_log.json', 'a') as log_file:
        log_file.write(json.dumps(log_entry) + '\n')

print("\n")

license_key = getText('Insert key: ')

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req_url = "https://download.mdstreamer.com/msser6z3/install/verify_key/" + license_key
req = urllib2.Request(req_url, headers=hdr)

try:
    result = urllib2.urlopen(req, context=ctx).read()
    log_request_response(req_url, result)
except urllib2.HTTPError as e:
    error_response = e.fp.read()
    log_request_response(req_url, error_response)
    print error_response
    quit()

if result != 'ok':
    print(bcolors.FAIL + '\n' + result + '\n' + bcolors.ENDC)
    quit()

http_port = getInt('Insert HTTP port or press ENTER for 8000: ', 8000)
https_port = getInt('Insert HTTPS port or press ENTER for 8001: ', 8001)
rtmp_port = getInt('Insert RTMP port or press ENTER for 8002: ', 8002)
admin_password = getText('Insert panel admin password: ')

print(bcolors.WARNING + "\nIf you have already installed MySQL/Mariadb, insert the EXISTING MySQL root password otherwise the installation will fail with a \"No database connection\" error!\n" + bcolors.ENDC)
print(bcolors.WARNING + "If you DON'T have already installed MySQL/Mariadb, insert a NEW MySQL root password.\n" + bcolors.ENDC)

mysql_password = getText('Insert MySQL root password: ')
panel_version = getText('Insert panel version, e.g. 5.2.0 or press ENTER for newest: ', 'Newest')

admin_path = rand_str(10)

data = {
    "license_key": license_key,
    "http_port": http_port,
    "https_port": https_port,
    "rtmp_port": rtmp_port,
    "admin_password": base64.b64encode(admin_password),
    "mysql_password": base64.b64encode(mysql_password),
    "admin_path": admin_path,
    "panel_version": panel_version
}

summary = ["HTTP port: " + str(http_port), "HTTPS port: " + str(https_port), "RTMP port: " + str(rtmp_port), "Panel admin password: " + admin_password, "MySQL root password: " + mysql_password, "Panel version: " + panel_version]

if raw_input('\nIs this correct?\n\n' + bcolors.OKCYAN + '\n'.join(summary) + bcolors.ENDC + '\n\nPress any key to continue or type exit to quit:\n\n') == 'exit':
    exit()

data = urllib.quote(json.dumps(data))

with open('/tmp/ms_progress', 'w') as file:
    file.write("0")
    file.close()

install_script_url = 'https://download.mdstreamer.com/msser6z3/install/download/script/' + data + '/$p/main'
os.system('cd /root;apt-get -h > /dev/null 2>&1;if [ $? -eq 0 ]; then apt-get update;p=apt-get; else p=yum; fi; $p install wget -y; wget -O ms_install_standalone.sh --no-check-certificate ' + install_script_url + ' >/dev/null 2>&1; $p install screen -y; pkill -15 screen; screen -dmS ms_install bash ms_install_standalone.sh >/dev/null 2>&1 &')
log_request_response(install_script_url, 'Installation script initiated')

print(bcolors.WARNING + "\nThe installation will now run in the background!\nPlease wait few minutes for the installation to complete.\n" + bcolors.ENDC)

while True:
    with open('/tmp/ms_progress', 'r') as file:
        progress = float(file.read().replace('\n', ''))

    update_progress(progress)

    time.sleep(1)

    if progress > 1:
        break

print(bcolors.OKCYAN + "\n\nInstallation complete!\n\nYou can access your panel visiting:\nhttp://your_server_ip:" + str(http_port) + "/" + admin_path + "\n" + bcolors.ENDC)
print(bcolors.OKCYAN + "You can retrieve your access code or reset the admin password by running:\n/home/midnightstreamer/iptv_midnight_streamer/toolbox\n" + bcolors.ENDC)
