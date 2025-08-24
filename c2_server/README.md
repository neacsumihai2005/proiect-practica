# C2 Server Setup

Acest README descrie setup-ul necesar pentru serverul C2 care primește fișiere exfiltrate de la VM-ul malware.

---

## 1. Dependențe Python

Serverul folosește **Flask**. Instalează Python 3 și Flask:

```bash
sudo apt update
sudo apt install python3-pip -y
pip3 install flask
````

---

## 2. Director de upload

Fișierele primite de la malware vor fi salvate în:

```python
UPLOAD_FOLDER = "/tmp/exfiltrated"
```

* Folderul se creează automat de script.
* Asigură-te că userul care rulează scriptul are permisiuni de scriere în `/tmp/exfiltrated`.

---

## 3. Certificat SSL

Serverul rulează pe HTTPS:

```python
ssl_context=("cert.pem", "key.pem")
```

* Trebuie să ai un certificat și o cheie valabile.
* Pentru test local, generează un certificat self-signed care include IP-ul serverului în Subject Alternative Name (SAN):

```bash
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout key.pem \
  -out cert.pem \
  -subj "/CN=<C2_IP>" \
  -addext "subjectAltName = IP:<C2_IP>"

```
* Înlocuiește <C2_IP> cu adresa IP a mașinii unde rulează serverul C2. Poate fi un IP intern (ex: 192.168.x.x).

* Pune `cert.pem` și `key.pem` în același folder cu scriptul C2.

---

## 4. Rulare

Rulează serverul manual:

```bash
python3 c2_server.py
```

* Serverul va asculta pe toate interfețele (`0.0.0.0`) la portul **5000** și va accepta conexiuni HTTPS.

---

## 5. Firewall / rețea

* Asigură-te că portul **5000** este deschis și accesibil din VM-ul malware:

```bash
sudo ufw allow 5000/tcp
sudo ufw reload
```

---

## 6. Fișiere primite

* Toate fișierele trimise de malware vor fi salvate în `/tmp/exfiltrated`.
* Numele fișierelor vor fi păstrate așa cum sunt trimise.
