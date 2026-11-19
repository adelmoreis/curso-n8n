#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor do curso N8N Academia Agente3d, com BANCO DE DADOS PROTEGIDO.

 - Serve o curso (index.html, apostila.html, ...) e guarda TODOS os dados em  dados/banco.json
   (alunos, progresso, pagamentos, metas, duvidas, configuracoes).
 - A pasta  dados/  NUNCA e tocada quando voce atualiza o curso: atualizar = trocar os .html/.js.
 - Copias automaticas em  dados/backups/  (ao ligar, a cada 15 min se algo mudou, e antes de restaurar).
 - Alunos so enxergam os proprios dados. Tudo do gestor exige login de gestor.
Precisa apenas de Python 3 (sem instalar nada).
"""
import os, sys, json, time, hmac, hashlib, base64, secrets, threading, re, shutil, mimetypes
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, 'dados')
BK = os.path.join(DATA, 'backups')
DB_FILE = os.path.join(DATA, 'banco.json')
KEY_FILE = os.path.join(DATA, 'segredo.key')
PORT = int(os.environ.get('PORT') or (sys.argv[1] if len(sys.argv) > 1 else 8080))
DEF_EMAIL, DEF_PASS, DEF_SALT = '3digitos2023@gmail.com', 'admin1234', 'ZGVmYXVsdC1hZG1pbjEy'
STATIC_OK = {'.html', '.js', '.css', '.png', '.jpg', '.jpeg', '.svg', '.ico', '.webp', '.gif', '.woff', '.woff2', '.mp3', '.mp4', '.txt'}
LOCK = threading.RLock()
DOCS = {}
DIRTY = {'v': False}
FAILS = {}

def b64(b): return base64.b64encode(b).decode()
def pw_hash(pw, salt_b64): return b64(hashlib.pbkdf2_hmac('sha256', pw.encode('utf-8'), base64.b64decode(salt_b64), 100000, 32))
def now(): return int(time.time() * 1000)

os.makedirs(BK, exist_ok=True)

def valid_docs(d):
    return isinstance(d, dict) and all(isinstance(k, str) and re.match(r'^[a-z]+/[^/]+$', k) and isinstance(v, dict) for k, v in d.items())

def read_file(p):
    with open(p, 'r', encoding='utf-8') as f:
        j = json.load(f)
    d = j.get('docs') if isinstance(j, dict) and 'docs' in j else j
    if not valid_docs(d): raise ValueError('formato invalido')
    return d

def backups_list():
    out = []
    for n in sorted(os.listdir(BK), reverse=True):
        if n.endswith('.json'):
            p = os.path.join(BK, n)
            out.append({'name': n, 'size': os.path.getsize(p), 'at': int(os.path.getmtime(p) * 1000)})
    return out

def write_db():
    tmp = DB_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump({'v': 1, 'docs': DOCS}, f, ensure_ascii=False)
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp, DB_FILE)
    DIRTY['v'] = True

def snapshot(tag='auto'):
    if not os.path.exists(DB_FILE): return None
    name = 'banco-%s-%s.json' % (time.strftime('%Y%m%d-%H%M%S'), tag)
    shutil.copy2(DB_FILE, os.path.join(BK, name))
    for old in backups_list()[300:]:
        try: os.remove(os.path.join(BK, old['name']))
        except OSError: pass
    return name

def load_db():
    global DOCS
    if os.path.exists(DB_FILE):
        try:
            DOCS = read_file(DB_FILE)
        except Exception:
            bad = os.path.join(DATA, 'banco.corrompido-%s.json' % time.strftime('%Y%m%d-%H%M%S'))
            os.replace(DB_FILE, bad)
            print('ATENCAO: banco.json estava danificado. Guardei em', bad)
            DOCS = {}
            for b in backups_list():
                try:
                    DOCS = read_file(os.path.join(BK, b['name'])); print('Restaurado da copia', b['name']); break
                except Exception: continue
    if 'config/admin' not in DOCS:
        DOCS['config/admin'] = {'email': DEF_EMAIL, 'salt': DEF_SALT, 'hash': pw_hash(DEF_PASS, DEF_SALT), 'def': True, 'v': 1, 'at': now()}
    # Limpa automaticamente registros fantasmas de visitantes sem cadastro nem progresso
    before_len = len(DOCS)
    DOCS = {k: v for k, v in DOCS.items() if not (k.startswith('progress/') and not v.get('sid') and not v.get('name'))}
    if len(DOCS) != before_len:
        print('Limpeza: removidos %d registros fantasmas de visitantes sem cadastro.' % (before_len - len(DOCS)))
    write_db()
    snapshot('inicio')

def secret():
    if not os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'w') as f: f.write(secrets.token_hex(32))
    return open(KEY_FILE).read().strip().encode()
SECRET = None

def sign(p):
    body = base64.urlsafe_b64encode(json.dumps(p, separators=(',', ':')).encode()).decode().rstrip('=')
    return body + '.' + hmac.new(SECRET, body.encode(), hashlib.sha256).hexdigest()

def verify(tok):
    try:
        body, sig = tok.rsplit('.', 1)
        if not hmac.compare_digest(sig, hmac.new(SECRET, body.encode(), hashlib.sha256).hexdigest()): return None
        p = json.loads(base64.urlsafe_b64decode(body + '=' * (-len(body) % 4)))
        if p.get('exp', 0) < time.time(): return None
        if p.get('r') == 'a':
            ad = DOCS.get('config/admin') or {}
            if p.get('pv') != (ad.get('hash') or '')[:10]: return None
        return p
    except Exception:
        return None

def merge_update(old, upd):
    new = dict(old)
    new.update(upd)
    if isinstance(upd.get('perms'), dict):
        p = dict(old.get('perms') or {}); p.update(upd['perms']); new['perms'] = p
    return new

class H(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    server_version = 'Curso/1'
    def log_message(self, *a): pass

    def send_json(self, code, obj, extra=None):
        b = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(b)))
        self.send_header('Cache-Control', 'no-store')
        for k, v in (extra or {}).items(): self.send_header(k, v)
        self.end_headers(); self.wfile.write(b)

    def body(self):
        n = int(self.headers.get('Content-Length') or 0)
        if n > 8 * 1024 * 1024: raise ValueError('grande')
        raw = self.rfile.read(n) if n else b''
        return json.loads(raw.decode('utf-8')) if raw else {}

    def who(self):
        tok = self.headers.get('X-Token') or ''
        p = verify(tok) if tok else None
        uid = self.headers.get('X-Uid') or ''
        if not re.match(r'^[A-Za-z0-9_-]{8,48}$', uid): uid = ''
        return p, uid

    def limited(self):
        ip = self.client_address[0]
        t = [x for x in FAILS.get(ip, []) if x > time.time() - 300]
        FAILS[ip] = t
        return len(t) >= 10
    def fail(self):
        FAILS.setdefault(self.client_address[0], []).append(time.time())

    def allowed(self, method, path, p, uid):
        if p and p.get('r') == 'a': return True
        if '/' not in path: return False
        col, did = path.split('/', 1)
        sid = (p or {}).get('sid') if p and p.get('r') == 's' else ''
        if method == 'GET':
            if path == 'config/app': return True
            if col == 'students' and did in (sid, uid) and did: return True
            if col == 'saves' and sid and did == sid: return True
            return False
        if method == 'PUT':
            if col == 'progress': return bool(sid and did == sid)
            if col == 'duvidas' and did and did in (uid, sid): return True
            if col == 'saves' and sid and did == sid: return True
        return False

    def do_GET(self): self.route('GET')
    def do_POST(self): self.route('POST')
    def do_PUT(self): self.route('PUT')
    def do_PATCH(self): self.route('PATCH')
    def do_DELETE(self): self.route('DELETE')

    def route(self, method):
        u = urlparse(self.path); q = parse_qs(u.query)
        try:
            if u.path.startswith('/api/'): return self.api(method, u.path[5:], q)
            if method != 'GET': return self.send_json(405, {'err': 'metodo'})
            return self.static(u.path)
        except (ConnectionError, BrokenPipeError):
            pass
        except Exception as e:
            try: self.send_json(500, {'err': 'erro', 'msg': str(e)})
            except Exception: pass

    def static(self, path):
        path = path.split('?')[0]
        rel = 'index.html' if path in ('', '/') else path.lstrip('/')
        parts = [x for x in rel.replace('\\', '/').split('/') if x]
        if not parts or any(x in ('..', '.') or x.startswith('.') for x in parts) or parts[0].lower() == 'dados':
            self.send_response(404); self.send_header('Content-Length', '0'); self.end_headers(); return
        f = os.path.join(ROOT, *parts)
        ext = os.path.splitext(f)[1].lower()
        if ext not in STATIC_OK or not os.path.isfile(f):
            self.send_response(404); self.send_header('Content-Length', '0'); self.end_headers(); return
        data = open(f, 'rb').read()
        ct = mimetypes.guess_type(f)[0] or 'application/octet-stream'
        if ext in ('.html', '.js', '.css'): ct += '; charset=utf-8'
        self.send_response(200)
        self.send_header('Content-Type', ct); self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers(); self.wfile.write(data)

    def api(self, method, ep, q):
        p, uid = self.who()
        isadmin = bool(p and p.get('r') == 'a')
        if ep == 'ping': return self.send_json(200, {'ok': True, 'v': 1})
        if ep == 'salt' and method == 'GET':
            u = (q.get('user') or [''])[0]
            d = DOCS.get('logins/' + u)
            return self.send_json(200, {'salt': d.get('salt') if d else None})
        if ep == 'adminsalt' and method == 'GET':
            return self.send_json(200, {'salt': (DOCS.get('config/admin') or {}).get('salt')})
        if ep == 'login' and method == 'POST':
            if self.limited(): return self.send_json(429, {'err': 'rate'})
            b = self.body(); u = str(b.get('user') or ''); h = str(b.get('h') or '')
            d = DOCS.get('logins/' + u)
            if not d: return self.send_json(401, {'err': 'nouser'})
            if not hmac.compare_digest(h, d.get('hash') or ''):
                self.fail(); return self.send_json(401, {'err': 'bad'})
            tok = sign({'r': 's', 'sid': d.get('sid'), 'exp': time.time() + 30 * 86400})
            return self.send_json(200, {'token': tok, 'd': {k: d.get(k) for k in ('sid', 'name', 'status', 'perms')}})
        if ep == 'admin' and method == 'POST':
            if self.limited(): return self.send_json(429, {'err': 'rate'})
            b = self.body(); ad = DOCS.get('config/admin') or {}
            ok = str(b.get('email') or '').strip().lower() == str(ad.get('email') or '').lower() and hmac.compare_digest(str(b.get('h') or ''), ad.get('hash') or '')
            if not ok:
                self.fail(); return self.send_json(401, {'err': 'bad'})
            tok = sign({'r': 'a', 'pv': (ad.get('hash') or '')[:10], 'exp': time.time() + 12 * 3600})
            return self.send_json(200, {'token': tok, 'e': ad.get('email'), 'def': bool(ad.get('def'))})
        if ep == 'doc':
            path = (q.get('path') or [''])[0]
            if not re.match(r'^[a-z]+/[^/]+$', path): return self.send_json(400, {'err': 'caminho'})
            if not self.allowed(method, path, p, uid): return self.send_json(403, {'err': 'negado'})
            with LOCK:
                if method == 'GET':
                    d = DOCS.get(path)
                    return self.send_json(200, {'exists': d is not None, 'data': d})
                b = self.body()
                if not isinstance(b, dict): return self.send_json(400, {'err': 'formato'})
                if method == 'PUT':
                    DOCS[path] = b
                elif method == 'PATCH':
                    if path not in DOCS: return self.send_json(404, {'err': 'nao existe'})
                    DOCS[path] = merge_update(DOCS[path], b)
                elif method == 'DELETE':
                    DOCS.pop(path, None)
                else: return self.send_json(405, {'err': 'metodo'})
                write_db()
            return self.send_json(200, {'ok': True})
        if ep == 'lead' and method == 'POST':
            if self.limited(): return self.send_json(429, {'err': 'rate'})
            b = self.body()
            name = str(b.get('name') or '').strip()
            phone = str(b.get('phone') or '').strip()
            email = str(b.get('email') or '').strip()
            origem = str(b.get('origem') or 'pagina-de-vendas').strip()
            if not (phone or email):
                return self.send_json(400, {'err': 'contato_obrigatorio'})
            clean_phone = re.sub(r'\D', '', phone)
            lead_id = clean_phone if len(clean_phone) >= 8 else re.sub(r'[^a-zA-Z0-9_-]', '', email)
            if not lead_id: lead_id = str(int(time.time()))
            path = 'leads/' + lead_id
            lead_data = {
                'id': lead_id,
                'name': name,
                'phone': phone,
                'email': email,
                'origem': origem,
                'status': 'novo',
                'ts': int(time.time()),
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            with LOCK:
                DOCS[path] = lead_data
                write_db()
            webhook_url = os.environ.get('N8N_LEAD_WEBHOOK') or (DOCS.get('config/webhooks') or {}).get('n8n_lead') or 'https://n8nai.agente3d.net/webhook/lead-capturado'
            try:
                import threading, urllib.request, urllib.parse
                def fwd(url, payload):
                    try:
                        req = urllib.request.Request(
                            url,
                            data=json.dumps(payload).encode('utf-8'),
                            headers={'Content-Type': 'application/json', 'User-Agent': 'CursoN8N-LeadNotifier/1.0'}
                        )
                        urllib.request.urlopen(req, timeout=6)
                    except Exception:
                        pass
                def sync_chatwoot(lead):
                    try:
                        token = 'cnsoWqY9xnWS9NZbKF2avLWX'
                        account_id = 1
                        inbox_id = 19
                        base = 'https://chatwoot.agente3d.net'
                        name = lead.get('name') or 'Visitante'
                        phone = lead.get('phone') or ''
                        email = lead.get('email') or ''
                        digits = re.sub(r'\D', '', phone)
                        if len(digits) <= 11 and not digits.startswith('55'):
                            digits = '55' + digits
                        formatted = '+' + digits if digits else ''

                        contact_id = None
                        if digits:
                            url_s = f"{base}/api/v1/accounts/{account_id}/contacts/search?q={urllib.parse.quote(digits)}"
                            req_s = urllib.request.Request(url_s, headers={'api_access_token': token})
                            try:
                                with urllib.request.urlopen(req_s, timeout=6) as r:
                                    res = json.loads(r.read().decode())
                                    if res.get('payload'):
                                        contact_id = res['payload'][0]['id']
                            except Exception:
                                pass

                        if not contact_id:
                            url_c = f"{base}/api/v1/accounts/{account_id}/contacts"
                            body_c = {'name': name, 'email': email, 'phone_number': formatted, 'custom_attributes': {'origem': 'pagina_de_vendas_modulo1', 'cupom': 'VIP10'}}
                            req_c = urllib.request.Request(url_c, data=json.dumps(body_c).encode('utf-8'), headers={'api_access_token': token, 'Content-Type': 'application/json'})
                            try:
                                with urllib.request.urlopen(req_c, timeout=6) as r:
                                    res = json.loads(r.read().decode())
                                    contact_id = res['payload']['contact']['id']
                            except Exception:
                                pass

                        if contact_id:
                            url_conv = f"{base}/api/v1/accounts/{account_id}/conversations"
                            body_conv = {'inbox_id': inbox_id, 'contact_id': contact_id, 'status': 'open'}
                            req_conv = urllib.request.Request(url_conv, data=json.dumps(body_conv).encode('utf-8'), headers={'api_access_token': token, 'Content-Type': 'application/json'})
                            try:
                                with urllib.request.urlopen(req_conv, timeout=6) as r:
                                    res_conv = json.loads(r.read().decode())
                                    conv_id = res_conv.get('id')
                                    if conv_id:
                                        url_m = f"{base}/api/v1/accounts/{account_id}/conversations/{conv_id}/messages"
                                        txt = f"🎉 *Novo Lead Capturado no Site!*\n\n👤 Nome: {name}\n📱 WhatsApp: {formatted}\n📧 E-mail: {email}\n🎁 Cupom: VIP10\n🚀 Grupo VIP: https://chat.whatsapp.com/CLUu662jFtvL9r2ahPaOJa\n\n📖 *Apostila Inteligente:*\nhttps://curson8n.agente3d.net"
                                        req_m = urllib.request.Request(url_m, data=json.dumps({'content': txt, 'message_type': 'outgoing', 'private': False}).encode('utf-8'), headers={'api_access_token': token, 'Content-Type': 'application/json'})
                                        urllib.request.urlopen(req_m, timeout=6)
                            except Exception:
                                pass
                    except Exception:
                        pass

                if webhook_url:
                    threading.Thread(target=fwd, args=(webhook_url, lead_data), daemon=True).start()
                threading.Thread(target=sync_chatwoot, args=(lead_data,), daemon=True).start()
            except Exception:
                pass
            return self.send_json(200, {'ok': True, 'lead': lead_data})
        if not isadmin: return self.send_json(403, {'err': 'negado'})
        if ep == 'col' and method == 'GET':
            name = (q.get('name') or [''])[0]
            with LOCK:
                docs = [{'id': k.split('/', 1)[1], 'data': v} for k, v in DOCS.items() if k.startswith(name + '/')]
            return self.send_json(200, {'docs': docs})
        if ep == 'backup' and method == 'GET':
            with LOCK: raw = json.dumps({'v': 1, 'docs': DOCS}, ensure_ascii=False).encode('utf-8')
            self.send_response(200); self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(raw)))
            self.send_header('Content-Disposition', 'attachment; filename="copia-curso-%s.json"' % time.strftime('%Y%m%d-%H%M'))
            self.end_headers(); self.wfile.write(raw); return
        if ep == 'backups' and method == 'GET':
            with LOCK: return self.send_json(200, {'list': backups_list()[:30], 'docs': len(DOCS), 'file': DB_FILE})
        if ep == 'restore' and method == 'POST':
            b = self.body()
            with LOCK:
                if b.get('name'):
                    name = os.path.basename(str(b['name']))
                    docs = read_file(os.path.join(BK, name))
                else:
                    docs = b.get('docs')
                    if not valid_docs(docs): return self.send_json(400, {'err': 'formato'})
                snapshot('antes-de-restaurar')
                keep = DOCS.get('config/admin')
                DOCS.clear(); DOCS.update(docs)
                if 'config/admin' not in DOCS and keep: DOCS['config/admin'] = keep
                write_db()
            return self.send_json(200, {'ok': True, 'docs': len(DOCS)})
        if ep == 'import' and method == 'POST':
            b = self.body(); docs = b.get('docs')
            if not valid_docs(docs): return self.send_json(400, {'err': 'formato'})
            n = 0
            with LOCK:
                snapshot('antes-de-importar')
                for k, v in docs.items():
                    if k == 'config/admin' or k in DOCS: continue
                    DOCS[k] = v; n += 1
                write_db()
            return self.send_json(200, {'ok': True, 'novos': n})
        return self.send_json(404, {'err': 'nao existe'})

def backup_loop():
    while True:
        time.sleep(900)
        with LOCK:
            if DIRTY['v']:
                DIRTY['v'] = False
                try: snapshot('auto')
                except Exception: pass

def main():
    global SECRET
    os.makedirs(DATA, exist_ok=True)
    load_db(); SECRET = secret()
    with open(os.path.join(DATA, 'LEIA-ME.txt'), 'w', encoding='utf-8') as f:
        f.write('Esta pasta guarda os dados do curso (alunos, progresso, pagamentos).\nNUNCA apague. Atualizar o curso nao mexe aqui.\nbanco.json = dados atuais | backups/ = copias automaticas.\nPara guardar com seguranca, copie a pasta dados para outro lugar de vez em quando.\n')
    threading.Thread(target=backup_loop, daemon=True).start()
    srv = ThreadingHTTPServer(('0.0.0.0', PORT), H)
    print('Curso no ar em http://localhost:%d' % PORT)
    print('Banco de dados protegido: %s (%d registros)' % (DB_FILE, len(DOCS)))
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
    with LOCK:
        if DIRTY['v']:
            try: snapshot('final')
            except Exception: pass

if __name__ == '__main__':
    main()
