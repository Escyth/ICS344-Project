## Task 3.1 - Implementing a Defense Mechanism
As discussed earler, the vulnerability that makes the SSH brute-force attack possible is the lack of some prevention mechanism on the victim machine, Metasploitable3. In other words, there is no service or daemon that prevents authorization attempts after multiple unsuccessful requests. 

After researching possible security patches and tools, we found [Fail2Ban](https://github.com/fail2ban/fail2ban) to be suitable in detecting and preventing brute-force SSH attacks. The way this software works is by monitoring the auth.log file and based on failed attempts, it will automatically ban that IP address from sending login requests. It is also quite simple to configure as will be demonstrated.

1- Install Fail2Ban on Metasploitable3:
```bash
sudo apt install fail2ban
```

2- Configure Fail2Ban if needed:
```bash
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
```
When using Fail2Ban, the best practice is to copy the configuration file to another called jail.local and keep the default settings as they are. Fail2Ban will prioritize jail.local over jail.conf if it exists.
```bash
sudo nano /etc/fail2ban/jail.local
```
Going to the [ssh] section, we will change the maxretry value from 6 to 2 for testing purposes.
![Fail2Ban Config](https://i.imgur.com/OXLPQEL.png)\
3- Restart Fail2Ban service for the changes to take effect:
```bash
sudo service fail2ban restart
```

## Task 3.2 - Validate Defense Mechanism and Compare
4- Clear auth.log to prevent an immediate ban:
```bash
sudo truncate -s 0 /var/log/auth.log
```

5- Restart Fail2Ban service to remove a ban if it happened:
```bash
sudo service fail2ban restart
```

6- Conduct the attack:
```bash
use auxiliary/scanner/ssh/ssh_login
set RHOSTS 192.168.56.102
set USER_FILE ~/usernames.txt
set PASS_FILE ~/passwords.txt
set VERBOSE true
run
```
Before (taken from Phase 1):

![Attack Result 1](https://i.imgur.com/l5T8jUE.png)\
After:

![After](https://i.imgur.com/BKrwZFP.png)\
Before allowed countless attempts. This clearly shows that the implementation of the Fail2Ban service can prevent SSH brute-force attacks. According to our configuration, we would allow 2 failed attempts and then block the IP address which is exactly what happened on the attacker's side; it tried `leah_organa:help_me_obiw@n` and `leah_organa:use_the_f0rce` then could not attempt to login anymore as the victim would now refuse its connection due to Fail2Ban.