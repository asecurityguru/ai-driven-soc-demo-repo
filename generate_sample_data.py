#!/usr/bin/env python3
"""
Generate realistic sample security events for Splunk demo
Creates various security scenarios: brute force, data exfiltration, malware, etc.
"""

import json
import random
from datetime import datetime, timedelta

# Sample data pools
INTERNAL_IPS = [f"192.168.1.{i}" for i in range(10, 50)]
EXTERNAL_IPS = [
    "185.220.101.45",  # Known TOR exit node
    "103.224.182.251",  # Suspicious IP
    "142.250.185.46",  # Google (legitimate)
    "104.16.132.229",  # Cloudflare (legitimate)
    "198.51.100.42",   # Suspicious IP
    "45.141.215.103",  # Known malicious
]

USERS = ["jsmith", "admin", "bwilson", "mjones", "rkumar", "slee", "tdavis"]
DOMAINS = [
    "google.com", "microsoft.com", "github.com",  # Legitimate
    "malicious-domain.xyz", "c2-server.net", "evil-phishing.com"  # Malicious
]

MALWARE_SIGNATURES = [
    "ET TROJAN Suspicious SSL Cert",
    "ET MALWARE Generic Backdoor Communication",
    "Ransomware File Encryption Activity",
    "Cryptominer Connection Detected",
    "ET EXPLOIT Remote Code Execution Attempt"
]

CATEGORIES = ["malware", "data_exfiltration", "brute_force", "scanning", 
              "privilege_escalation", "phishing", "normal", "authentication"]

ACTIONS = ["blocked", "allowed", "alerted", "quarantined"]

def generate_timestamp(hours_ago=0, minutes_ago=0):
    """Generate timestamp"""
    now = datetime.now() - timedelta(hours=hours_ago, minutes=minutes_ago)
    return now.strftime("%Y-%m-%dT%H:%M:%S")

def generate_brute_force_attack():
    """Generate brute force attack events"""
    events = []
    attacker_ip = random.choice(EXTERNAL_IPS[:3])
    target_user = random.choice(USERS)
    
    for i in range(12):  # 12 failed attempts
        events.append({
            "time": generate_timestamp(hours_ago=2, minutes_ago=i*2),
            "event_type": "authentication",
            "user": target_user,
            "src_ip": attacker_ip,
            "dest_ip": random.choice(INTERNAL_IPS),
            "action": "failed_login",
            "reason": "invalid_password",
            "severity": "high" if i > 5 else "medium",
            "category": "brute_force",
            "session_id": f"sess_{random.randint(10000, 99999)}"
        })
    
    return events

def generate_data_exfiltration():
    """Generate data exfiltration events"""
    events = []
    insider_ip = random.choice(INTERNAL_IPS)
    external_ip = random.choice(EXTERNAL_IPS[:2])
    
    # Large data transfer
    events.append({
        "time": generate_timestamp(hours_ago=1),
        "event_type": "data_transfer",
        "src_ip": insider_ip,
        "dest_ip": external_ip,
        "user": random.choice(USERS),
        "bytes": random.randint(150000000, 500000000),  # 150-500 MB
        "protocol": "HTTPS",
        "action": "allowed",
        "severity": "critical",
        "category": "data_exfiltration",
        "signature": "Unusual Data Volume to External Host"
    })
    
    return events

def generate_malware_traffic():
    """Generate malware C2 traffic"""
    events = []
    infected_ip = random.choice(INTERNAL_IPS)
    c2_server = EXTERNAL_IPS[0]  # Known bad IP
    
    # Multiple C2 beacons
    for i in range(5):
        events.append({
            "time": generate_timestamp(hours_ago=0, minutes_ago=i*10),
            "event_type": "network_traffic",
            "src_ip": infected_ip,
            "dest_ip": c2_server,
            "dest_port": 443,
            "protocol": "SSL",
            "action": "blocked" if i > 2 else "allowed",
            "severity": "critical",
            "category": "malware",
            "signature": random.choice(MALWARE_SIGNATURES),
            "bytes_sent": random.randint(1024, 8192),
            "bytes_received": random.randint(512, 4096)
        })
    
    return events

def generate_port_scanning():
    """Generate port scanning activity"""
    events = []
    scanner_ip = random.choice(EXTERNAL_IPS[:2])
    target_ip = random.choice(INTERNAL_IPS)
    
    # Scan multiple ports
    ports = [21, 22, 23, 25, 80, 443, 3389, 8080, 8443]
    for port in ports:
        events.append({
            "time": generate_timestamp(hours_ago=3, minutes_ago=random.randint(0, 30)),
            "event_type": "network_scan",
            "src_ip": scanner_ip,
            "dest_ip": target_ip,
            "dest_port": port,
            "action": "blocked",
            "severity": "high",
            "category": "scanning",
            "signature": "Multiple Port Connection Attempts",
            "protocol": "TCP"
        })
    
    return events

def generate_privilege_escalation():
    """Generate privilege escalation attempt"""
    events = []
    user = random.choice(USERS[1:4])  # Non-admin user
    
    events.append({
        "time": generate_timestamp(hours_ago=0, minutes_ago=30),
        "event_type": "privilege_change",
        "user": user,
        "src_ip": random.choice(INTERNAL_IPS),
        "action": "privilege_escalation",
        "target_group": "domain_admins",
        "method": "token_manipulation",
        "severity": "critical",
        "category": "privilege_escalation",
        "status": "detected_and_blocked"
    })
    
    return events

def generate_normal_traffic():
    """Generate normal traffic for baseline"""
    events = []
    
    for i in range(20):
        events.append({
            "time": generate_timestamp(hours_ago=random.randint(0, 4), 
                                     minutes_ago=random.randint(0, 59)),
            "event_type": random.choice(["web_browsing", "email", "file_access"]),
            "user": random.choice(USERS),
            "src_ip": random.choice(INTERNAL_IPS),
            "dest_ip": random.choice(EXTERNAL_IPS[2:]),  # Legitimate IPs
            "action": "allowed",
            "severity": "low",
            "category": "normal",
            "bytes": random.randint(1024, 102400)
        })
    
    return events

def generate_phishing_attempt():
    """Generate phishing email events"""
    events = []
    
    events.append({
        "time": generate_timestamp(hours_ago=4),
        "event_type": "email",
        "sender": "noreply@evil-phishing.com",
        "recipient": random.choice(USERS) + "@company.com",
        "subject": "URGENT: Verify Your Account",
        "action": "quarantined",
        "severity": "high",
        "category": "phishing",
        "signature": "Phishing Email with Malicious Link",
        "attachment_count": 1,
        "links": ["hxxp://evil-phishing.com/verify"]
    })
    
    return events

def main():
    """Generate and save sample security events"""
    all_events = []
    
    # Generate different attack scenarios
    all_events.extend(generate_brute_force_attack())
    all_events.extend(generate_data_exfiltration())
    all_events.extend(generate_malware_traffic())
    all_events.extend(generate_port_scanning())
    all_events.extend(generate_privilege_escalation())
    all_events.extend(generate_phishing_attempt())
    all_events.extend(generate_normal_traffic())
    
    # Sort by time
    all_events.sort(key=lambda x: x['time'])
    
    # Save to JSON file
    output_file = "sample_security_events.json"
    with open(output_file, 'w') as f:
        for event in all_events:
            f.write(json.dumps(event) + '\n')
    
    print(f"✅ Generated {len(all_events)} security events")
    print(f"📁 Saved to: {output_file}")
    print("\nEvent breakdown:")
    print(f"  - Brute Force Attacks: 12 events")
    print(f"  - Data Exfiltration: 1 event")
    print(f"  - Malware C2 Traffic: 5 events")
    print(f"  - Port Scanning: 9 events")
    print(f"  - Privilege Escalation: 1 event")
    print(f"  - Phishing: 1 event")
    print(f"  - Normal Traffic: 20 events")
    print(f"\n📊 Total: {len(all_events)} events")
    
    # Print sample events
    print("\n📋 Sample Events:")
    for event in all_events[:3]:
        print(json.dumps(event, indent=2))

if __name__ == "__main__":
    main()
