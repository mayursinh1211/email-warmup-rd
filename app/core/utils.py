import re
from typing import List
import dns.resolver
from email_validator import validate_email, EmailNotValidError

def validate_email_format(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def validate_smtp_settings(smtp_server: str, smtp_port: int) -> bool:
    common_smtp_ports = [25, 465, 587, 2525]
    if smtp_port not in common_smtp_ports:
        return False
    
    try:
        dns.resolver.resolve(smtp_server, 'MX')
        return True
    except:
        return False

def get_email_domain(email: str) -> str:
    return email.split('@')[1]

def generate_warmup_schedule(
    start_volume: int,
    target_volume: int,
    days: int
) -> List[int]:
    if days <= 0:
        return []
    
    if start_volume >= target_volume:
        return [target_volume] * days
    
    daily_increment = (target_volume - start_volume) / days
    schedule = []
    
    current_volume = start_volume
    for _ in range(days):
        schedule.append(round(current_volume))
        current_volume += daily_increment
    
    return schedule
