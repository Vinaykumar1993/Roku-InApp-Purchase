import time
import sys
import re
import telnetlib
import os
from zipfile import ZipFile
import requests
from requests.auth import HTTPDigestAuth
from requests.auth import HTTPBasicAuth
from os.path import basename
import sys
import re
# HOST = input("enter your host IP:")
# username = input("enter your Roku UserName:")
# password = input("enter your Roku Password:")
HOST="192.168.0.116"
username="rokudev"
password="ventuno"
auth_d=HTTPDigestAuth(username, password)
user_options=["1.generate New DevID and password:2.check DevID on roku build system:","3.Install Zip:","4.Delete Zip:","5.Generate Package:","6:Rekey the package"];
#genkey generation start
roku_url = 'http://'+HOST+'/'
roku_url1 = 'http://'+HOST+':8060/'
try:
    tn=telnetlib.Telnet(HOST,"8080")
except:
    print("error while connecting Device......")
    sys.exit(2)





def generateNewDevIdAndPassword():
    try:
        print("generating new devid and password please wait.....")
        tn.write(b"genkey\n")
        tn.write(b"quit \n")
        x = tn.read_all()
        splittext=(re.split("\s",((x.decode("utf-8")))))
        pass_index=splittext.index('Password:')
        devid_index=splittext.index('DevID:')
        genPassword=splittext[pass_index+1].strip()
        genDevId=splittext[devid_index+1].strip()
        package_generation = dict()
        package_generation['devId']=genDevId
        package_generation['genPassword']=genPassword
        return package_generation
    except:
        return "Error Generating New DevId and Password"




def zipit(folders, zip_filename,extrafiles):
    # create a ZipFile object
    zfName = zip_filename
    foo = ZipFile(zfName, 'w')
    for files in extrafiles:
        foo.write(files)
    for x in folders:
        # print(x)
        for root, dirs, files in os.walk(x):
            for f in files:
                foo.write(os.path.join(root, f))
    foo.close()


def install_zip(zip_file):
    try:
        url = roku_url+"plugin_install"
        files = {'archive': open(zip_file, 'rb')}
        payload = {'mysubmit' : 'Install'}
        getdata = requests.post(url, files = files, auth=auth_d, data=payload, timeout=60, verify=False,  stream=True)
        return "successfull installed "+zip_file+" in roku build system"
    except:
        return "file not avilable to install....."

def delete_zip(zip_file):
    try: 
        url = roku_url+"plugin_install"
        files = {'archive': open(zip_file, 'rb')}
        payload = {'mysubmit' : 'Delete'}
        getdata = requests.post(url, files = files, auth=auth_d, data=payload, timeout=60, verify=False,  stream=True)
        return "successfull Deleted "+zip_file+" in roku build system"
    except:
        return "file not avilable to delete....."

def rekey_package(pkg_file,passwd):
    print(pkg_file,passwd)
    try: 
        url = roku_url+"plugin_inspect"
        files = {'archive': open(pkg_file, 'rb')}
        payload = {'mysubmit' : 'Rekey','passwd': passwd}
        r = requests.post(url, auth=auth_d, data=payload, timeout=60, verify=False,  stream=True ,files=files)
        # print(r.content);
        public_key_error = re.search('Invalid public key', r.text)
        password_error = re.search('Please enter a password', r.text)
        if(public_key_error):
            return "Invalid public key.: iostream error"
        elif(password_error):
            return "Password Not Given While Rekeying"
        else:
            return "successfull Rekeyed "+pkg_file+" in roku build system"
    except:
        return "Problem With Rekeying......."



def get_current_devid():
    try:
        print("getting current Dev ID please wait.....")
        r = requests.get(roku_url1+"query/device-info", auth=auth_d)
        pattern = "<keyed-developer-id\>(.*?)\</keyed-developer-id>"
        splittext=(re.search(pattern,((r.content.decode("utf-8"))))).group(1)
        current_dev_id = dict()
        current_dev_id['devId']=splittext
        return current_dev_id
    except:
        return "Error Getting current devId"
    
    # return ""
def current_package():
    url = roku_url+"plugin_package"
    r= requests.get(url, auth=auth_d)
    getcurrentpackage=re.search('"pkgs(.*)pkg"', r.text)
    if(getcurrentpackage):
        currentpackage_name=getcurrentpackage.group(0).strip('"')
        get_package(currentpackage_name,currentpackage_name.split('//')[1])
        return currentpackage_name.split('//')[1]
    else:
        return "No Package were added yet"

def get_package(package_name,app_name):
    print('Downloading...')
    url = roku_url+str(package_name)
    filename = app_name
    # print(len(filename))
    r = requests.get(url, auth=auth_d)
    with open(filename, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)

def generate_package(app_name,passwd):
    # print('Generating...',app_name,passwd)
    #payload = {'pkg_time': '1617687686495', 'mysubmit': 'Package', 'app_name': 'test/1.0.8', 'passwd': 'yz15gM+0WzTzCSIGza+PVw=='} 
    try:
        payload = {'pkg_time': time.time(), 'mysubmit': 'Package', 'app_name': app_name, 'passwd': passwd}
        # print(payload)
        url = roku_url+"plugin_package"
        # print(auth_d)
        files = {'archive': ""}
        r = requests.post(url, auth=auth_d, data=payload, timeout=60, verify=False,  stream=True ,files=files)
        # print(r.text)
        # Grep package name
        package_name = re.search('"pkgs(.*)pkg"', r.text)
        # print(package_name.group(0))
        pkg = package_name.group(0).strip('"')
        app_pkg_name="app_"+app_name+""
        replace_pkg_name=str(app_pkg_name.replace("/","_")+".pkg")
        get_package(pkg,replace_pkg_name);
        return replace_pkg_name
    except:
        # print("Problem")
        return "Problem Generating Package"


def CallCommand(currentOption):
    if(currentOption == "NEW_GEN_KEY_PASSWORD"):
       return generateNewDevIdAndPassword()
    elif(currentOption == "CURRENT_GEN_KEY"):
        return get_current_devid()
    elif(currentOption == "INSTALL_ZIP"):
        if(arg_count==2):
            zipfileName_install=sys.argv[2]
            delete_zip(zipfileName_install);
            return install_zip(zipfileName_install)
        else:
            print("Arguments not matched\nArguments like -  python youfile.py command yourfilename.zip")
            return ""
    elif(currentOption == "DELETE_ZIP"):
        if(arg_count==2):
            zipfileName_delete=sys.argv[2]
            return delete_zip(zipfileName_delete);
        else:
            print("Arguments not matched\nArguments like -  python youfile.py command yourfilename.zip")
            return ""
    elif(currentOption == "GENERATE_PACKAGE"):
        if(arg_count==3):
            app_gen_name=sys.argv[2]
            app_gen_pass=sys.argv[3]
            return generate_package(app_gen_name,app_gen_pass)
        else:
            print("Arguments not matched\nArguments like -  python yourfile.py command appname/1.0.8 genkeypassword")
            return ""
    elif(currentOption == "REKEY_PACKAGE"):
        if(arg_count==3):
            app_rekey_pkg=sys.argv[2]
            app_rekey_pass=sys.argv[3]
            pattern = re.compile(r'\s+')
            return rekey_package(re.sub(pattern, '', app_rekey_pkg),re.sub(pattern, '', app_rekey_pass))
        else:
            print("Arguments not matched\nArguments like -  python yourfile.py command filename.pkg genkeypassword")
            return ""
    elif(currentOption == "CURRENT_PACKAGE"):
        if(arg_count==1):
            return current_package()
    else:
        print("Wrong Options......")
folders = [
"components",
"images",
"fonts",
"source"
]
extrafiles = [
"manifest"
]
zipit(folders, "roku_ait_alpha_001.zip",extrafiles)
arg_count = len(sys.argv) - 1
print('arg_count',arg_count)
if(arg_count>0):
    try:
        val = sys.argv[1]
        resultoption = CallCommand(val)
        print(resultoption)
    except ValueError:
        print("not an valid option")
else:
    print("Arguments not matched....")
# print(arg_count)
# if arg_count == 2:
  
#     print(str(sys.argv))
#     zip_file = sys.argv[1]
#     app_name = sys.argv[2]
#     # passwd = sys.argv[3]
#     delete_zip(zip_file)
#     install_zip(zip_file)
#     #delete_package()
#     package_name = generate_package(app_name, genPassword)
#     get_package(package_name)
# else:
#     file_name =  os.path.basename(sys.argv[0])
#     print("Required 3 arguments")
#     print("Pass zip file path, app_name and genkey passwd")
#     print("python "+file_name+" roku_simply_south_beta001.zip 'test/1.0.8' 'uHcLhcEuKsAPYViou/ibAQ=='")
def exitForm():
    exitinput=input('continue or exit ?')
    if(exitinput=="continue"):
        userOptionsPopup()
    elif(exitinput=='exit'):
        sys.exit(1)
    else:
        print("invalid input...")

def processOption(user_input):
    if user_input<=len(user_options):
        if(user_input==1):
                retundata = generateNewDevIdAndPassword()
                print(retundata)
                exitForm()
        elif(user_input==2):
                devIdRetrunData = get_current_devid()
                print(devIdRetrunData)
                exitForm()
        elif(user_input==3):
         
                install_zip_file_name = input("enter the file name of zip and proceed\n")
                deletresponse=delete_zip(install_zip_file_name);
                print(deletresponse +" continuing to install.......")
                intallreturndata = install_zip(install_zip_file_name)
                print(intallreturndata)
                exitForm()

        elif(user_input==4):
                delete_zip_file_name = input("enter the file name of zip and proceed\n")
                deletereturndata = delete_zip(delete_zip_file_name)
                print(deletereturndata)
                exitForm()
        elif(user_input==5):
                input_app_name = input("enter the app name\n")
                input_app_version = input("enter the version eg:(1.0.8)\n")
                input_app_password = input("enter the app password\n")

                generatepkgreturndata = generate_package(input_app_name+"/"+input_app_version,input_app_password)
                print(generatepkgreturndata)
                exitForm()
        elif(user_input==6):
                input_rekey_pkg_name = input("enter the file name of your package eg(filename.pkg)\n")
                input_rekey_pkg_pwd = input("enter your genkey password\n")
                rekeyreturndata = rekey_package(input_rekey_pkg_name,input_rekey_pkg_pwd)
                print(rekeyreturndata)
                exitForm()
        else:
            print("processing....");
    else:
        print("invalid options")
        userOptionsPopup(1)

def userOptionsPopup(val=""):
    if val!=1:
        for x in range(0,len(user_options)):
            print(user_options[x])

    options = input("Select your options to process")
    try:
        val = int(options)
        processOption(val)
    except ValueError:
        print("not an valid option")
        userOptionsPopup(1);

# if (username=='rokudev' and password=='ventuno'):
#     userOptionsPopup();
# else :
#     print("invalid username or password")