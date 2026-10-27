#!/usr/bin/env bash
# Instala Postiz en un servidor Ubuntu 24.04 limpio (x86 o ARM, incluido Oracle Cloud Always Free).
# Correr con sudo, desde esta carpeta:
#   sudo bash instalar.sh redes.estudioierlip.com tu-mail@ejemplo.com
set -euo pipefail

DOMINIO="${1:?Uso: sudo bash instalar.sh <dominio> <mail>}"
EMAIL="${2:?Uso: sudo bash instalar.sh <dominio> <mail>}"
AQUI="$(cd "$(dirname "$0")" && pwd)"
DESTINO=/opt/postiz

# Oracle Cloud trae su propio firewall con iptables (rules.v4 con REJECT al final).
# Ahí no se usa ufw: se abren 80 y 443 en iptables y en la Security List de OCI (ver README).
ORACLE=0
if [ -f /etc/iptables/rules.v4 ] && grep -q "icmp-host-prohibited" /etc/iptables/rules.v4; then ORACLE=1; fi

echo "== 1/5 Paquetes (Docker desde los repositorios de Ubuntu)"
apt-get update -y
apt-get install -y docker.io docker-compose-v2 git openssl
systemctl enable --now docker
# Elasticsearch (lo usa Temporal) necesita este límite del kernel.
echo "vm.max_map_count=262144" > /etc/sysctl.d/99-postiz.conf
sysctl --system >/dev/null

echo "== 2/5 Firewall: solo SSH, HTTP y HTTPS"
if [ "$ORACLE" = 1 ]; then
  echo "   Oracle Cloud detectado: abro 80 y 443 en iptables."
  apt-get install -y iptables-persistent
  for PORT in 80 443; do
    iptables -C INPUT -p tcp -m state --state NEW --dport "$PORT" -j ACCEPT 2>/dev/null       || iptables -I INPUT 6 -p tcp -m state --state NEW --dport "$PORT" -j ACCEPT
  done
  netfilter-persistent save
else
  apt-get install -y ufw
  ufw allow OpenSSH
  ufw allow 80/tcp
  ufw allow 443/tcp
  ufw --force enable
fi

echo "== 3/5 Compose oficial de Postiz"
if [ ! -d "$DESTINO/.git" ]; then
  git clone https://github.com/gitroomhq/postiz-docker-compose "$DESTINO"
fi
cp "$AQUI/docker-compose.override.yaml" "$AQUI/Caddyfile" "$DESTINO/"
mkdir -p "$DESTINO/legal" && cp "$AQUI"/legal/*.html "$DESTINO/legal/"

echo "== 4/5 Configuración (.env)"
if [ ! -f "$DESTINO/.env" ]; then
  cp "$AQUI/.env.example" "$DESTINO/.env"
  sed -i "s|^DOMINIO=.*|DOMINIO=$DOMINIO|; s|^EMAIL_ACME=.*|EMAIL_ACME=$EMAIL|" "$DESTINO/.env"
  sed -i "s|^JWT_SECRET=.*|JWT_SECRET=$(openssl rand -hex 48)|" "$DESTINO/.env"
  sed -i "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$(openssl rand -hex 24)|" "$DESTINO/.env"
  chmod 600 "$DESTINO/.env"
else
  echo "   .env ya existe: no lo toco."
fi

echo "== 5/5 Levantando (la primera vez tarda unos minutos)"
cd "$DESTINO"
docker compose pull
docker compose up -d
echo
echo "Listo. Entrá a https://$DOMINIO y creá tu usuario."
echo "Después: DISABLE_REGISTRATION=true en $DESTINO/.env y 'docker compose up -d'."
