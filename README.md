![Banner](https://github.com/user-attachments/assets/0a2bc0a7-a5bf-4314-b383-7ce0ed6bb054)

# Dynatrace Custom Monitoring

This automation script is designed to integrate the custom tool with Dynatrace using the REST API (out-of-the-box integration).

## Overview

This automation script is specifically designed to facilitate seamless integration between a custom Application and Dynatrace using the Dynatrace REST API. By leveraging out-of-the-box integration, the script enables efficient data exchange between the monitoring tool and Dynatrace, ensuring real-time insights and enhanced observability.

The script automates the process of fetching relevant monitoring data from a custom-built tool and transmitting it to the Dynatrace dashboard for centralized visibility. It interacts with Dynatrace’s REST API endpoints to push and retrieve monitoring metrics, logs, and system health data, enabling IT and DevOps teams to gain deeper insights into system performance, anomalies, and potential issues.

By implementing this script, organizations can enhance their monitoring strategy, improve incident detection and resolution times, and maximize operational efficiency.
<!--
## Usage

1. **Download the Script:**

   Download the script to the target Unix-based system where UDAgent is installed.
      ```bash
   git clone https://github.com/Prajwal-PS7/chRegistry.git
   ```

2. **Go to directory path**

   Download the script to the target Unix-based system where UDAgent is installed.
      ```bash
   cd chRegistry/
   ```
### (Linux/AIX)

3. **Grant Execution Permissions:**

   Ensure the script has execution permissions:

   ```bash
   chmod +x chRegistry.sh
   ```

4. **Execute the Script:**

   Run the script with elevated privileges:

   ```bash
   sudo ./chRegistry.sh
   ```

5. **Follow On-Screen Instructions:**

   The script will guide you through the process of regenerating the UDAgent registry entries. You do not need to put anything during execution of script.

6. **Verification:**

   After running the script, verify that the UDAgent registry entries have been successfully regenerated. You can check the "**aioptionrc**" file located in **/root/.discagnt/** or **/.discagnt/** for confirmation.

### (Windows)

3. **Execute the Script:**
<br>
Double Click on chRegistry.bat file.
<br><br >OR <br><br>
Right click on chRegistry.bat file and select Run.
<br><br>OR <br><br>
Open a command prompt and type below command :

   ```bash
   chRegistry.bat
   ```
   

5. **Follow On-Screen Instructions:**

   The script will not guide you through the process of regenerating the UDAgent registry entries. You do not need to put anything during execution of script.

6. **Verification:**

   After running the script, verify that the UDAgent registry entries have been successfully regenerated. You can check the "**UD_UNIQUE_ID**" and "**UD_UNIQUE_ID_HostName**" key value  located in **HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Hewlett-Packard\Universal Discovery\V1\Options** of windows registry editor.
   
## Important Notes

- **Backup:**
  Before running the script, it is recommended to create a backup of the existing UDAgent registry entries or any critical system configurations.

- **Dependencies:**
  Ensure that any dependencies required by UDAgent are installed on the system before running the script.

- **Logging:**
  As of now there is no logs creating for the script for troubleshooting. You can review the On-Screen Instructions to identify issue occurs during the regeneration process.
-->
## Contributing

Feel free to contribute to the improvement of this script by submitting pull requests or reporting issues.

## License

This script is released under the [MIT License](LICENSE). @Copyleft 

## Disclaimer

This script is provided as-is without any warranty. Use it at your own risk and ensure that you understand its impact on your system before execution.

For detailed information about the 3rd party integration and its configuration, refer to the official documentation provided by the OEM (Dynatrace).

