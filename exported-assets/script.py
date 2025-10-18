
# Create Replit configuration for one-click deployment
replit_config = '''{
  "run": "uvicorn solana_discovery.web_server:app --host 0.0.0.0 --port 8000",
  "language": "python3",
  "onBoot": "pip install -r requirements.txt"
}
'''

with open('.replit', 'w') as f:
    f.write(replit_config)

print("✅ Created .replit configuration")

# Create replit.nix for environment setup
replit_nix = '''{ pkgs }: {
  deps = [
    pkgs.python310
    pkgs.python310Packages.pip
    pkgs.python310Packages.setuptools
  ];
}
'''

with open('replit.nix', 'w') as f:
    f.write(replit_nix)

print("✅ Created replit.nix")

# Create Procfile for Railway/Render
procfile = '''web: uvicorn solana_discovery.web_server:app --host 0.0.0.0 --port $PORT
'''

with open('Procfile', 'w') as f:
    f.write(procfile)

print("✅ Created Procfile for Railway/Render")

# Create railway.json
railway_config = '''{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn solana_discovery.web_server:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
'''

with open('railway.json', 'w') as f:
    f.write(railway_config)

print("✅ Created railway.json")
