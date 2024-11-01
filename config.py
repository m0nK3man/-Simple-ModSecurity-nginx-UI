# config.py
MODSECURITY_CONF_PATH = '/etc/nginx/modsec/modsecurity.conf'
MODSECURITY_RULES_DIR = '/etc/nginx/modsec/crs/rules'
NGINX_RELOAD_CMD = 'nginx -s reload'

# Paths to log files
ACCESS_LOG_PATH = "/var/log/nginx/access.log"
ERROR_LOG_PATH = "/var/log/nginx/error.log"
AUDIT_LOG_PATH = "/var/log/modsec_audit.log"
