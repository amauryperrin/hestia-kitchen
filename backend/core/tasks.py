import subprocess
import os
from datetime import datetime
from celery import shared_task

@shared_task
def backup_database():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = 'app/backups'
    os.makedirs(backup_dir, exist_ok=True)
    filename = f'{backup_dir}/backup_{timestamp}.sql'

    result = subprocess.run([
        'pg_dump',
        '-h', os.getenv('POSTGRES_HOST', 'db'),
        '-U', os.getenv('POSTGRES_USER', 'hestia'),
        '-d', os.getenv('POSTGRES_DB', 'hestia'),
        '-f', filename,
    ], env={
        **os.environ,
        'PGPASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
    }, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f'Backup échoué : {result.stderr}')
    
    return f'Backup créé : {filename}'