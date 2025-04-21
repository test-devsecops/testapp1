import os

def createGroups(tenant_name):
  print(f"Creating Groups on Checkmarx tenant {tenant_name}...")

if __name__ == "__main__":
  tenant_name = os.environ['CX_TENANT_NAME']
  
  createGroups(teanant_name)
