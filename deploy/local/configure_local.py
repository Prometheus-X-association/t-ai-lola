#!/usr/bin/env python3
import os
import re
import sys
import hashlib
import base64

def parse_yaml(file_path):
    vars_dict = {}
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        sys.exit(1)
    with open(file_path, 'r') as f:
        for line in f:
            # Remove comments and strip whitespace
            line = re.sub(r'#.*$', '', line).strip()
            if not line:
                continue
            if ':' in line:
                key, val = line.split(':', 1)
                key = key.strip()
                val = val.strip()
                # Remove quotes if present
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                vars_dict[key] = val
    return vars_dict

def update_env_file(sample_path, target_path, updates):
    if not os.path.exists(sample_path):
        print(f"Error: Sample file {sample_path} not found.")
        sys.exit(1)
    
    lines = []
    updated_keys = set()
    with open(sample_path, 'r') as f:
        for line in f:
            matched = False
            for key, val in updates.items():
                if line.startswith(f"{key}="):
                    val_str = str(val).replace('/home/lolauser', '/tmp/lolauser')
                    lines.append(f"{key}={val_str}\n")
                    updated_keys.add(key)
                    matched = True
                    break
            if not matched:
                line_str = line.replace('/home/lolauser', '/tmp/lolauser')
                lines.append(line_str)
                
    # Append any updates that weren't in the sample file
    for key, val in updates.items():
        if key not in updated_keys:
            val_str = str(val).replace('/home/lolauser', '/tmp/lolauser')
            lines.append(f"{key}={val_str}\n")
            
    with open(target_path, 'w') as f:
        f.writelines(lines)
    print(f"Generated {target_path}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    # 1. Generate app/lolapy/.env
    lolapy_sample = os.path.join(project_root, 'app', 'lolapy', '.env.sample')
    lolapy_target = os.path.join(project_root, 'app', 'lolapy', '.env')
    
    lolapy_updates = {
        'FRONTEND_API_IP': 'app',
        'FRONTEND_API_PORT': '80',
        'LOLAPY_HOST_IP': 'backend',
        'HARBOR_HOST': 'localhost:5001',
        'HARBOR_USER': 'backend',
        'HARBOR_PASSWORD': 'password',
        'CLUSTER_TYPE': 'local',
        'SFTP_USER': 'lola',
        'SFTP_PASSWORD': 'lola',
        'MYSQL_ROOT_PASSWORD': 'lolapassword',
        'DATABASE_NAME': 'loladb',
        'MYSQL_USER': 'lola',
        'MYSQL_PASSWORD': 'password',
    }
    update_env_file(lolapy_sample, lolapy_target, lolapy_updates)
    
    # 2. Generate app/frontend/.env
    frontend_sample = os.path.join(project_root, 'app', 'frontend', '.env.sample')
    frontend_target = os.path.join(project_root, 'app', 'frontend', '.env')
    frontend_root_dir = os.path.join(project_root, 'app', 'frontend')
    
    frontend_updates = {
        'ROOT_DIR': frontend_root_dir,
        'DATABASE_HOST': 'db',
        'MYSQL_HOST': 'db',
        'LOLAPY_API_ADRESS': 'backend',
        'ENABLE_API_ACCESS_CONTROL': 'true',
        'DATABASE_NAME': 'loladb',
        'MYSQL_ROOT_PASSWORD': 'lolapassword',
        'MYSQL_USER': 'lola',
        'MYSQL_PASSWORD': 'password',
        'SFTP_USER': 'lola',
        'SFTP_PASSWORD': 'lola',
        'SFTP_PORT': '2222',  # Non-conflicting local port for DMZ SFTP
    }
    update_env_file(frontend_sample, frontend_target, frontend_updates)
    
    # 3. Generate app/frontend/build/app/.env (copy of app/frontend/.env)
    frontend_build_dir = os.path.join(frontend_root_dir, 'build', 'app')
    os.makedirs(frontend_build_dir, exist_ok=True)
    frontend_build_env = os.path.join(frontend_build_dir, '.env')
    with open(frontend_target, 'r') as src, open(frontend_build_env, 'w') as dest:
        dest.write(src.read())
    print(f"Copied frontend .env to {frontend_build_env}")
    
    # 4. Generate deploy/local/.env for docker-compose substitutions
    compose_env = os.path.join(script_dir, '.env')
    compose_updates = {
        'MYSQL_ROOT_PASSWORD': lolapy_updates.get('MYSQL_ROOT_PASSWORD', ''),
        'DATABASE_NAME': lolapy_updates.get('DATABASE_NAME', ''),
        'MYSQL_USER': lolapy_updates.get('MYSQL_USER', ''),
        'MYSQL_PASSWORD': lolapy_updates.get('MYSQL_PASSWORD', ''),
        'SFTP_USER': lolapy_updates.get('SFTP_USER', ''),
        'SFTP_PASSWORD': lolapy_updates.get('SFTP_PASSWORD', ''),
        'PMA_HOST': 'db',
        'RESTART_SERVICES': 'no',
    }
    with open(compose_env, 'w') as f:
        for k, v in compose_updates.items():
            f.write(f"{k}={v}\n")
    print(f"Generated compose env: {compose_env}")

    # 5. Generate htpasswd file for the registry container
    auth_dir = os.path.join(script_dir, 'auth')
    os.makedirs(auth_dir, exist_ok=True)
    htpasswd_path = os.path.join(auth_dir, 'htpasswd')
    
    # Generate bcrypt hashed password (required by modern docker registries)
    password = lolapy_updates.get('HARBOR_PASSWORD', 'password')
    import subprocess
    try:
        bcrypt_line = subprocess.check_output(
            ['docker', 'run', '--rm', 'httpd:alpine', 'htpasswd', '-Bbn', 'backend', password],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        with open(htpasswd_path, 'w') as f:
            f.write(bcrypt_line + '\n')
        print(f"Generated bcrypt registry htpasswd file: {htpasswd_path}")
    except Exception as e:
        # Fallback to SHA-1 if Docker is not available
        sha1_hash = hashlib.sha1(password.encode('utf-8')).digest()
        sha1_b64 = base64.b64encode(sha1_hash).decode('utf-8')
        with open(htpasswd_path, 'w') as f:
            f.write(f"backend:{{SHA}}{sha1_b64}\n")
        print(f"Generated registry htpasswd file (fallback to SHA-1): {htpasswd_path}")
    
    # 6. Create directories
    home_dir = '/tmp/lolauser'
    datasets_dir = os.path.join(home_dir, 'nf-workdir', 'datasets')
    os.makedirs(datasets_dir, exist_ok=True)
    print(f"Ensured datasets directory exists: {datasets_dir}")

if __name__ == '__main__':
    main()
