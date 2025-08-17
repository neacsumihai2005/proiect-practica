# Proiect Honeypot - Stagiu de Practică

Acest proiect este un experiment de tip honeypot, rulând **3 mașinării virtuale Ubuntu** pe același host:  

1. `malware` – mașină virtuală care simulează atacul.  
2. `honeypotproxy` – mașină virtuală care monitorizează și loghează traficul SSH.  
3. `c2_server` – server C2 care primește fișierele exfiltrate.  

---

## Network adapters

- Fiecare VM are **două interfețe de rețea**:  
  1. **NAT** – folosită pentru acces la Internet din VM.  
  2. **Bridged** – folosită pentru comunicare directă între VM-uri (malware ↔ honeypotproxy).  

