# Honeypot Mitmproxy Daemon

Acest repository conține configurarea și scriptul pentru rularea unui **mitmproxy daemon** (`mitmdump`) cu log rotativ pe un honeypot. Scriptul este gândit să ruleze continuu, să se auto-repornească dacă mitmdump pică și să logheze activitatea HTTP/HTTPS într-un fișier cu **RotatingFileHandler**.

---

## **Fișiere**

* `mitm_daemon.py` – script Python care pornește mitmdump în **transparent mode**, loghează stdout/stderr în fișier rotativ și face restart automat.
* `mitm-daemon.service` – unitate systemd pentru a porni scriptul la boot și a-l menține activ.

---

## **Prerechizite**

Instalare mitmproxy:

```bash
sudo apt update
sudo apt install mitmproxy python3-pip -y
```

Verifică versiunea:

```bash
mitmdump --version
```

---

## **Configurare mitm\_daemon.py**

* **Port de ascultare:** 8080
* **Mode:** transparent
* **Log rotativ:** `/var/log/mitmproxy_activity.log`, MAX_BYTES dimensiune maxima
* **Restart automat:** RESTART_DELAY secunde între încercări

**Exemplu de configurare:**

```python
LOG_PATH = "/var/log/mitmproxy_activity.log"
MAX_BYTES = 10 * 1024 * 1024
BACKUP_COUNT = 7
RESTART_DELAY = 5
```

---

## **Systemd service**

In fisierul `/etc/systemd/system/mitm-daemon.service`:

```ini
[Unit]
Description=Mitmproxy daemon (mitmdump) with rotating file logs
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/local/bin/mitm_daemon.py
Restart=always
User=root
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=mitm-daemon

[Install]
WantedBy=multi-user.target
```

* `ExecStart` trebuie să fie calea completă către scriptul tău `mitm_daemon.py`.
* Se recomandă rularea ca **root** pentru modul transparent.

---

## **Pornire și rulare la boot**

1. Copiază scriptul în `/usr/local/bin/mitm_daemon.py`:

```bash
sudo cp mitm_daemon.py /usr/local/bin/
sudo chmod +x /usr/local/bin/mitm_daemon.py
```

2. Copiază unitatea systemd:

```bash
sudo cp mitm-daemon.service /etc/systemd/system/
```

3. Reîncarcă systemd:

```bash
sudo systemctl daemon-reload
```

4. Activează serviciul la boot:

```bash
sudo systemctl enable mitm-daemon.service
```

5. Pornește serviciul:

```bash
sudo systemctl start mitm-daemon.service
```

6. Verifică status:

```bash
sudo systemctl status mitm-daemon.service
```

* Logurile mitmproxy vor fi în `/var/log/mitmproxy_activity.log` cu rotire automată.

---

## **Configurarea certificatului Mitmproxy pentru HTTPS**
Când rulezi mitmproxy sau mitmdump pentru prima dată, acesta generează un CA auto-semnat pe care îl folosește pentru a semna certificatele serverelor interceptate:

Implicit, CA-ul se află în home-ul utilizatorului care rulează mitmproxy:
```text
~/.mitmproxy/mitmproxy-ca-cert.pem
```
De exemplu, dacă rulezi ca root:
```text
/root/.mitmproxy/mitmproxy-ca-cert.pem
```
Acest fișier .pem conține cheia publică a CA-ului mitmproxy. El se copiaza în /usr/local/share/ca-certificates/.

/usr/local/share/ca-certificates/ este directorul standard pe Debian/Ubuntu pentru certificate CA suplimentare care pot fi trustate sistem-wide.

După ce copiezi fișierul acolo și rulezi:
```bash
sudo update-ca-certificates
```
CA-ul mitmproxy va fi adăugat la lista de CA-uri recunoscute de sistemul tău.

---

## **Test**

* Folosește de pe VM-ul Malware curl pentru a testa HTTPS prin mitmproxy cu certificatul CA instalat:

```bash
curl -v --cacert /usr/local/share/ca-certificates/mitmproxy-ca.crt https://<honeypot-ip>
```

* Verifică logul `/var/log/mitmproxy_activity.log` pentru trafic interceptat și mesaje de restart.

---

## **Avantaje**

* Rulare continuă și restart automat.
* Log rotativ pentru a nu umple discul.
* Transparență totală a traficului HTTP/HTTPS interceptat.

---





