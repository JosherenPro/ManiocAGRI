import sys
import os
import json

# Add backend/app to path so imports within main.py work (e.g. 'from api...')
sys.path.append(os.path.join(os.getcwd(), "app"))

try:
    from main import app
    
    print("Generating OpenAPI schema...")
    schema = app.openapi()
    
    output_path = "openapi.json"
    with open(output_path, "w") as f:
        json.dump(schema, f, indent=2)
    
    print(f"Success! OpenAPI schema exported to {os.path.abspath(output_path)}")

except ImportError as e:
    print(f"Import Error: {e}")
    print("Ensure dependencies are installed and you are running from 'backend' directory.")
except Exception as e:
    print(f"Error: {e}")
