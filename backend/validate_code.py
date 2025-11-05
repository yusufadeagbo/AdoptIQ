#!/usr/bin/env python
import os
import sys
import ast

def validate_python_files(directory):
    errors = []
    valid_files = 0

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', 'env']]

        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        code = f.read()
                    ast.parse(code)
                    valid_files += 1
                except SyntaxError as e:
                    errors.append(f"{filepath}: {e}")
                except Exception as e:
                    errors.append(f"{filepath}: {e}")

    return valid_files, errors

print("🔍 Validating Backend Python Code...")
valid, errors = validate_python_files('/home/user/AdoptIQ/backend')

if errors:
    print(f"❌ Found {len(errors)} errors:")
    for error in errors[:10]:
        print(f"  - {error}")
else:
    print(f"✅ All {valid} Python files are syntactically valid!")

print("\n🔍 Checking Configuration Files...")
config_files = [
    'adoptiq/settings.py',
    'adoptiq/urls.py',
    'adoptiq/wsgi.py',
    'adoptiq/asgi.py',
    'adoptiq/celery.py'
]

for config in config_files:
    path = os.path.join('/home/user/AdoptIQ/backend', config)
    if os.path.exists(path):
        print(f"  ✓ {config}")
    else:
        print(f"  ✗ {config} MISSING")

print("\n🔍 Checking Django Apps...")
apps = ['core', 'users', 'missions', 'audits', 'billing', 'analytics']
for app in apps:
    app_path = os.path.join('/home/user/AdoptIQ/backend/apps', app)
    required_files = ['__init__.py', 'models.py', 'views.py', 'urls.py']

    missing = []
    for req_file in required_files:
        if not os.path.exists(os.path.join(app_path, req_file)):
            missing.append(req_file)

    if missing:
        print(f"  ⚠ {app}: Missing {', '.join(missing)}")
    else:
        print(f"  ✓ {app}: Complete")

print("\n✅ Backend validation complete!")
sys.exit(0 if not errors else 1)
