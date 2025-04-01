import os
import requests
import oci
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_public_ip():
    try:
        return requests.get("https://api.ipify.org?format=text").text
    except requests.RequestException as e:
        print(f"Error fetching public IP: {e}")
        return None

def update_ingress_rule(vcn_id, security_list_id, public_ip):
    # Load OCI config
    config_path = os.getenv("OCI_CONFIG_PATH", "~/.oci/config")
    config = oci.config.from_file(config_path)
    network_client = oci.core.VirtualNetworkClient(config)
    
    # Fetch the security list
    security_list = network_client.get_security_list(security_list_id).data
    
    # New rule to be applied (you can modify this based on your needs)
    updated_rules = []
    rule_found = False
    for rule in security_list.ingress_security_rules:
        # Check if the rule has the description "d4rkcyber"
        if rule.description == "d4rkcyber":
            print(f"Updating rule with description: {rule.description}")
            updated_rule = oci.core.models.IngressSecurityRule(
                protocol="all",  # Modify as needed
                source=f"{public_ip}/32",  # New public IP
                source_type="CIDR_BLOCK",
                description="d4rkcyber"  # Keep the description as "d4rkcyber"
            )
            updated_rules.append(updated_rule)
            rule_found = True
        else:
            updated_rules.append(rule)

    # If no rule was found that matches, add the new rule
    if not rule_found:
        print(f"No matching rule found with description 'd4rkcyber'. Adding new rule.")
        updated_rules.append(
            oci.core.models.IngressSecurityRule(
                protocol="all", 
                source=f"{public_ip}/32", 
                source_type="CIDR_BLOCK",
                description="d4rkcyber"  # Add description if adding a new rule
            )
        )
    
    # Update the security list with the modified rules
    update_details = oci.core.models.UpdateSecurityListDetails(ingress_security_rules=updated_rules)
    network_client.update_security_list(security_list_id, update_details)
    print("Ingress rule updated successfully.")

if __name__ == "__main__":
    VCN_ID = os.getenv("VCN_ID")
    SECURITY_LIST_ID = os.getenv("SECURITY_LIST_ID")
    public_ip = get_public_ip()
    if public_ip:
        update_ingress_rule(VCN_ID, SECURITY_LIST_ID, public_ip)
