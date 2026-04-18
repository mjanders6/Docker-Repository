
# Fixing 53 Port Issues
🛠️ Step-by-Step Fix
Follow these steps to stop systemd-resolved from occupying port 53:
1. Disable the Stub Listener 
Edit the configuration file to stop the service from listening on port 53. 
Open the file: sudo nano /etc/systemd/resolved.conf
Find the line #DNSStubListener=yes.
Uncomment it (remove the #) and change it to DNSStubListener=no.
Save and exit (Ctrl+O, Enter, Ctrl+X). 

2. Update symbolic links
Disabling the stub listener can break local DNS resolution on the host machine. You must point the system to the correct resolv.conf file. 
Remove the existing link: sudo rm /etc/resolv.conf
Create a new link to the runtime version:
sudo ln -s /run/systemd/resolve/resolv.conf /etc/resolv.conf 

3. Restart the service
Apply the changes by restarting systemd-resolved. 
Run: sudo systemctl restart systemd-resolved 

✅ Verify the Port is Free 
Run the following command to confirm nothing is listening on port 53:
sudo lsof -i :53 or sudo ss -tulpn | grep :53 

If the output is empty, you can now start your Pi-hole container or service without a port conflict. 
