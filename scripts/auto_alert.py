import json
import sys
import time
from pathlib import Path

LOG_FILE = Path("data/logs.jsonl")

def main():
    if not LOG_FILE.exists():
        print(f"File {LOG_FILE} không tồn tại.")
        return

    print(f"Monitoring {LOG_FILE} for anomalies...")
    
    total_req = 0
    total_err = 0
    
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                
                # Check for latency SLO
                if "latency_ms" in data and data["latency_ms"] > 3000:
                    print(f"[ALERT] High latency detected! {data['latency_ms']}ms - Correlation ID: {data.get('correlation_id')}")
                    
                # Track error rate
                if data.get("event") == "request_received":
                    total_req += 1
                elif data.get("event") == "request_failed":
                    total_err += 1
                    
                # Check for PII leaks (Redacted text means PII was processed, but if we want to find actual leaks we could use regex. Here we just log if a redaction happened)
                # Alternatively, check if raw unredacted data somehow slipped. We will just alert on REDACTED tags to show awareness.
                if "payload" in data:
                    payload_str = str(data["payload"])
                    if "[REDACTED_" in payload_str:
                        print(f"[WARNING] PII was detected and redacted in payload - Correlation ID: {data.get('correlation_id')}")
                        
            except Exception as e:
                pass
                
    # Calculate error rate
    if total_req > 0:
        err_rate = (total_err / total_req) * 100
        if err_rate > 2.0:
            print(f"[CRITICAL] Error rate is high! {err_rate:.2f}% (SLO is <= 2%)")
        else:
            print(f"[OK] Error rate is normal: {err_rate:.2f}%")

if __name__ == "__main__":
    main()
