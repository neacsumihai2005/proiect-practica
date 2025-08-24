# SSH Monitor Setup

Aceasta este configurarea pentru SSH Monitor pe **HoneypotProxy**.

---

## 1. Copiere scripturi

1. Pune script-ul `ssh_monitor.py` în:
```bash
/usr/local/bin/
````

2. Pune fișierul `ssh-monitor.service` în:

```bash
/etc/systemd/system/ssh-monitor.service
```

---

## 2. Activare serviciu

Execută comenzile:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ssh-monitor.service
sudo systemctl start ssh-monitor.service
sudo systemctl status ssh-monitor.service
```

* Verifică că status-ul arată `active (running)`.

---

## 3. Instalare dependențe

### Scapy

```bash
sudo python3 -m pip install scapy
```

### SSH server

```bash
sudo apt update
sudo apt install openssh-server -y
sudo systemctl enable ssh
sudo systemctl start ssh
sudo systemctl status ssh
```

* Asigură-te că serverul SSH e activ și rulează la boot.
* Deschide portul 22 dacă folosești firewall:

```bash
sudo ufw allow 22/tcp
sudo ufw reload
```

---

## 4. Verificare IP

* Rulează în VM:

```bash
ip a
```

---

Acest setup asigură că:

* Rulează scriptul `ssh_monitor.py` automat la boot
* Poate fi accesat prin SSH de pe VM-ul malware
* Detectează SYN-uri și logări SSH

