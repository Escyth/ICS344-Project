## Setup
Following the guide set by the project instructions, we installed [Splunk Server](https://download.splunk.com/products/splunk/releases/9.3.2/linux/splunk-9.3.2-d8bb32809498-linux-2.6-amd64.deb) on Kali Linux to receive data from the victim machine, Metasploitable3. The web interface can be accessed at http://vbox-kali:8000.

![Web Interface](https://i.imgur.com/HSgjeiY.png)\
We also installed [Splunk Forwarder](https://download.splunk.com/products/universalforwarder/releases/9.4.1/linux/splunkforwarder-9.4.1-e3bdab203ac8-linux-arm64.deb) on Metasploitable3 to send data to the attacker machine, Kali Linux. The auth.log file is now being monitored by the Forwarder which has been connected to the Splunk Server on port 9997 and set active.

![Active Forwards](https://i.imgur.com/369YWLM.png)\
In order to monitor the attacker environment,  we have added logging functionality to the custom script created earlier in Phase 1. The log file is monitored under the index attacker on Splunk.

## Task 2.1 - Integrating Logs Into SIEM tool (Splunk)
1- Conduct the attack by following the steps shown in Phase 1.

2- Go to Splunk -> Search & Reporting.

![Log Integration](https://i.imgur.com/xgTRgXm.png)\
As seen, both the victim and attacker have been integrated into Splunk, the SIEM tool. For reference, both log files are also included in this phase's folder.

## Task 2.2 - Log Visualization and Comparison

3- Generate the attacker's environment log visualization:
```bash
index=attacker
| rex "=> (?<status>True|False)"
| timechart span=30s count by status
```
This command filters based on the index, which is attacker, then uses rex which is basically regular expression to extract the status of the entry. Finally, it creates a timechart of the data based on blocks of 30 seconds with the data being the count of each status.
![Attacker Logs](https://i.imgur.com/vAN3nBI.png)

4- Generate the victim's environment log visualization:
```bash
host=metasploitable3-ub1404
| eval status=if(Searchmatch("Accepted password"), "Success", "Fail")
| timechart span=30s count by status
```
This command filters based on the host, which is metaspoitable3-ub1404, then uses eval to create the variable status with an if-condition; if the entry has "Accepted password", it's a success, otherwise, it's a failure (incorrect credentials or invalid user). Finally, it creates a timechart of the data based on blocks of 30 seconds with the data being the count of each status.
![Victim Logs](https://i.imgur.com/kJE2Usk.png)\
As seen in the two graphs above, there was no activity prior to the attack on the victim machine. However, as soon as the attack started, it started flooding with SSH login attempts. This explains what a brute-force method is, it is basically trying the possible credentials until it forces its way in with a successful attempt. On 7:44:30 PM approximately, we can see that our script detected a <span style="color:deeppink">True</span> indicating it found correct credentials, and at the same timestamp in the auth.log file of the victim, we can see a <span style="color:deeppink">Success</span> indicating there has been a successful authorization attempt.