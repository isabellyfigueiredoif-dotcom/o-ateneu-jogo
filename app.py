# O ATENEU — jogo multiplayer local para Pydroid 3
# Instale Flask no Pydroid 3: Pip > flask
# Execute este arquivo e mantenha o Pydroid aberto.

from flask import Flask, request, jsonify, render_template_string
import random
import secrets
import socket
import time
import math

app = Flask(__name__)
ROOMS = {}

QUESTIONS = [
    [
        {"q": "Quem escreveu O Ateneu?", "a": ["Machado de Assis", "Raul Pompeia", "Aluísio Azevedo", "José de Alencar"], "c": 1, "why": "O romance foi escrito por Raul Pompeia."},
        {"q": "Em que ano O Ateneu foi publicado?", "a": ["1875", "1881", "1888", "1895"], "c": 2, "why": "A obra foi publicada em 1888."},
        {"q": "Quem narra a história?", "a": ["Aristarco", "Ema", "Sérgio adulto, relembrando o passado", "Rebelo"], "c": 2, "why": "A narrativa é feita em primeira pessoa por Sérgio, que recorda sua experiência no internato."},
        {"q": "Qual é o principal cenário da narrativa?", "a": ["Uma fazenda", "Um internato chamado Ateneu", "Um quartel", "Uma universidade"], "c": 1, "why": "Grande parte da história se passa no internato Ateneu."},
        {"q": "A qual período literário a obra costuma ser associada?", "a": ["Romantismo", "Arcadismo", "Realismo/Naturalismo", "Modernismo"], "c": 2, "why": "A obra é geralmente associada ao Realismo, com traços naturalistas e impressionistas."}
    ],
    [
        {"q": "Quem é o diretor do internato?", "a": ["Dr. Cláudio", "Aristarco", "Sanches", "Rômulo"], "c": 1, "why": "Aristarco é o diretor do Ateneu."},
        {"q": "Como Sérgio chega ao Ateneu?", "a": ["É levado pelo pai para estudar no internato", "Foge de casa", "É contratado como professor", "Vai visitar um parente"], "c": 0, "why": "O pai de Sérgio o apresenta ao ambiente escolar e o deixa no internato."},
        {"q": "Qual característica de Aristarco é importante para a crítica da obra?", "a": ["Sua humildade", "Sua ausência de autoridade", "Sua preocupação com a imagem e o poder", "Seu desejo de abandonar a escola"], "c": 2, "why": "Aristarco representa a autoridade do internato e valoriza sua reputação."},
        {"q": "O Ateneu funciona como uma representação de quê?", "a": ["Uma sociedade em miniatura", "Uma ilha deserta", "Uma família sem conflitos", "Um reino fantástico"], "c": 0, "why": "As relações do internato reproduzem disputas de poder, hierarquias e conflitos sociais."},
        {"q": "Qual é o foco da memória de Sérgio?", "a": ["Uma viagem pela Europa", "Sua experiência de formação no internato", "Uma batalha histórica", "A construção de uma cidade"], "c": 1, "why": "O narrador revisita suas experiências e descobertas durante a vida escolar."}
    ],
    [
        {"q": "Qual crítica social aparece com força no romance?", "a": ["À desigualdade e à hipocrisia das instituições", "À tecnologia moderna", "À vida rural", "À navegação"], "c": 0, "why": "A obra expõe contradições entre o discurso moral da instituição e suas práticas."},
        {"q": "Como são retratadas muitas relações entre os estudantes?", "a": ["Sempre solidárias e sem conflitos", "Marcadas por competição, hierarquia e violência simbólica", "Sem influência do ambiente", "Como relações exclusivamente familiares"], "c": 1, "why": "O cotidiano escolar é atravessado por disputas, pressões e relações de poder."},
        {"q": "O que o internato simboliza na leitura crítica da obra?", "a": ["Um espaço perfeito de liberdade", "Um ambiente isolado das questões sociais", "Uma sociedade autoritária em miniatura", "Um lugar sem regras"], "c": 2, "why": "O internato espelha estruturas de autoridade e desigualdade da sociedade."},
        {"q": "Por que a narrativa é considerada memorialística?", "a": ["Porque apresenta leis e documentos", "Porque Sérgio narra lembranças de sua infância", "Porque é escrita em forma de diário de Aristarco", "Porque relata fatos futuros"], "c": 1, "why": "Sérgio reconstrói, a partir da memória, sua passagem pelo Ateneu."},
        {"q": "Qual alternativa melhor descreve o tom crítico da obra?", "a": ["Idealização da escola", "Exaltação sem questionamentos da autoridade", "Questionamento das aparências e das relações de poder", "Defesa de um internato perfeito"], "c": 2, "why": "O romance questiona a imagem de excelência do colégio e revela suas contradições."}
    ],
    [
        {"q": "Qual interpretação resume melhor o sentido crítico de O Ateneu?", "a": ["A escola é apresentada como espaço sempre justo", "A formação de Sérgio revela conflitos entre aparência, poder e experiência", "O romance é apenas uma aventura de férias", "A obra não apresenta crítica social"], "c": 1, "why": "A experiência de Sérgio expõe as contradições do internato e da sociedade que ele representa."},
        {"q": "A visão do passado apresentada por Sérgio é...", "a": ["Totalmente neutra e sem emoções", "Uma lembrança filtrada por sua perspectiva adulta", "Narrada por Aristarco", "Um relatório científico"], "c": 1, "why": "A memória e a perspectiva do narrador influenciam a maneira como os acontecimentos são apresentados."},
        {"q": "O título O Ateneu se refere principalmente...", "a": ["Ao nome do internato central da narrativa", "A um personagem chamado Ateneu", "A uma cidade fictícia", "A um navio"], "c": 0, "why": "Ateneu é o nome da instituição escolar onde se desenvolve grande parte da narrativa."},
        {"q": "Qual tema NÃO combina com a leitura crítica da obra?", "a": ["Autoritarismo", "Hipocrisia social", "Disputas de poder", "Idealização absoluta e incontestável do internato"], "c": 3, "why": "A obra não idealiza o internato; ela revela suas contradições."},
        {"q": "Uma boa conclusão sobre a obra é que ela...", "a": ["Mostra a escola como um microcosmo social e questiona suas estruturas", "Defende que autoridade nunca deve ser questionada", "Trata somente de esportes", "Não apresenta narrador"], "c": 0, "why": "O internato funciona como um retrato concentrado de relações sociais e de poder."}
    ]
]

STAGE_NAMES = ["A entrada no Ateneu", "A rotina do internato", "Por trás das aparências", "O arquivo de Sérgio"]

PAGE = r"""
<!doctype html><html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>O Ateneu — Desafio do Internato</title>
<style>
:root{--bg:#171310;--panel:#28201a;--gold:#c9a66b;--cream:#f1e6d2;--muted:#b9aa96;--red:#8b3434}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#403025,#171310 58%);color:var(--cream);font-family:Georgia,serif;min-height:100vh}
main{max-width:760px;margin:auto;padding:22px 16px 45px}.brand{text-align:center;border-bottom:1px solid #8f744e;padding:15px 0 20px;margin-bottom:22px}
.kicker{letter-spacing:4px;color:var(--gold);font:12px Arial;text-transform:uppercase}.brand h1{font-size:clamp(30px,7vw,48px);margin:10px 0 5px}.brand p{color:var(--muted);margin:0;font-style:italic}
.panel{background:rgba(40,32,26,.96);border:1px solid #725a3b;border-radius:14px;padding:20px;margin:14px 0;box-shadow:0 12px 30px #0005}
h2{color:var(--gold);margin-top:0}button,input{font:16px Arial;border-radius:9px;padding:13px;border:1px solid #9c8056}
input{width:100%;background:#f4ead9;color:#211a14;margin:7px 0 12px}button{background:var(--gold);color:#211a14;font-weight:bold;cursor:pointer;margin:5px 4px 5px 0}button.secondary{background:transparent;color:var(--cream);border-color:#8c7557}button:disabled{opacity:.4}
.option{display:block;width:100%;text-align:left;background:#382c22;color:var(--cream);border:1px solid #806747;margin:9px 0;padding:14px;line-height:1.35}
.option.selected{border:2px solid var(--gold);background:#59432d}.muted{color:var(--muted)}.big{font-size:28px;color:var(--gold);font-weight:bold;letter-spacing:3px}
.row{display:flex;gap:10px;flex-wrap:wrap}.row>*{flex:1;min-width:130px}.hidden{display:none}.status{padding:10px;background:#1c1713;border-radius:8px;margin:10px 0}.player{display:flex;justify-content:space-between;border-bottom:1px solid #594734;padding:9px 0;gap:12px}
.small{font:13px Arial;color:var(--muted)}.correct{color:#9ed6a0}.wrong{color:#f19a8d}
</style></head><body><main>
<div class="brand"><div class="kicker">Desafio literário • Raul Pompeia</div><h1>O ATENEU</h1><p>Uma jornada pelas regras, relações e segredos do internato</p></div>
<section id="home" class="panel">
<h2>Entre no jogo</h2><p class="muted">O apresentador cria a sala. Os participantes entram pelo próprio celular usando o código.</p>
<div class="row"><button onclick="createRoom()">Criar sala (apresentador)</button><button class="secondary" onclick="showJoin()">Entrar como participante</button></div>
<div id="joinBox" class="hidden"><label> Código da sala</label><input id="joinCode" placeholder="Ex.: 482193" maxlength="6"><label>Seu nome</label><input id="playerName" placeholder="Digite seu nome"><button onclick="joinRoom()">Entrar</button></div>
<div id="homeMsg" class="small"></div>
</section>
<section id="host" class="hidden">
<div class="panel"><div class="small">CÓDIGO PARA A TURMA</div><div class="big" id="roomCode"></div><p class="muted">Peça para todos acessarem este endereço no navegador e digitarem o código acima.</p><div id="hostStatus" class="status">Aguardando participantes...</div><div class="row"><button onclick="startStage()">Iniciar etapa</button><button class="secondary" onclick="nextQuestion()">Próxima pergunta</button><button class="secondary" onclick="finishStage()">Encerrar etapa</button></div><div id="hostQuestion" class="status">A etapa ainda não começou.</div><div id="hostPlayers"></div></div>
</section>
<section id="player" class="hidden">
<div class="panel"><div class="small" id="playerWelcome"></div><h2 id="stageTitle">Aguardando o apresentador</h2><div id="playerQuestion" class="status">Aguarde o início da etapa.</div><div id="answers"></div><div id="playerFeedback" class="small"></div><div class="status">Sua pontuação: <b id="myScore">0</b></div><div id="playerRanking"></div></div>
</section>
</main>
<script>
let role=null, code=null, token=null, pid=null, selected=null, lastQ=-1, answered=false;
const $=id=>document.getElementById(id);
async function api(url,data){let r=await fetch(url,{method:data?'POST':'GET',headers:data?{'Content-Type':'application/json'}:{},body:data?JSON.stringify(data):undefined});let j=await r.json();if(!r.ok)throw Error(j.error||'Erro');return j}
function showJoin(){$('joinBox').classList.remove('hidden')}
function msg(t){$('homeMsg').textContent=t}
async function createRoom(){try{let d=await api('/create',{});role='host';code=d.code;token=d.token;$('home').classList.add('hidden');$('host').classList.remove('hidden');$('roomCode').textContent=code;poll()}catch(e){msg(e.message)}}
async function joinRoom(){try{let d=await api('/join',{code:$('joinCode').value.trim(),name:$('playerName').value.trim()});role='player';code=d.code;pid=d.pid;$('home').classList.add('hidden');$('player').classList.remove('hidden');$('playerWelcome').textContent='Participante: '+d.name+' • Sala '+code;poll()}catch(e){msg(e.message)}}
async function hostAction(path){try{return await api(path,{code,token})}catch(e){alert(e.message)}}
async function startStage(){await hostAction('/start')}
async function nextQuestion(){await hostAction('/next')}
async function finishStage(){await hostAction('/finish')}
async function choose(i){if(answered)return;selected=i;document.querySelectorAll('.option').forEach((b,n)=>b.classList.toggle('selected',n===i));try{let d=await api('/answer',{code,pid,index:i});answered=true;$('playerFeedback').textContent=d.message;$('playerFeedback').className=d.correct?'correct':'wrong';$('myScore').textContent=d.score;document.querySelectorAll('.option').forEach(b=>b.disabled=true)}catch(e){$('playerFeedback').textContent=e.message}}
async function poll(){try{let d=await api('/state?code='+code+(role==='host'?'&token='+token:'&pid='+pid));if(role==='host')drawHost(d);else drawPlayer(d)}catch(e){}setTimeout(poll,1100)}
function drawHost(d){$('hostStatus').textContent=d.status+' • Etapa '+d.stage+'/4 • Participantes ativos: '+d.active;
$('hostQuestion').innerHTML=d.question?'<b>'+d.stageName+'</b><p>'+d.question.q+'</p><span class="small">Pergunta '+d.qnum+' de '+d.totalQ+'</span>':'Aguardando o apresentador iniciar ou avançar.';
$('hostPlayers').innerHTML='<h2>Placar ao vivo</h2>'+d.players.map((p,i)=>'<div class="player"><span>'+(i+1)+'. '+esc(p.name)+(p.active?'':' <span class="muted">(fora da disputa)</span>')+'</span><b>'+p.score+' pts</b></div>').join('');
}
function drawPlayer(d){$('stageTitle').textContent=d.status+' • '+(d.stageName||'');$('myScore').textContent=d.myScore;
$('playerRanking').innerHTML='<p class="small">Participantes ativos: '+d.active+'</p>'+d.players.slice(0,5).map((p,i)=>'<div class="player"><span>'+(i+1)+'. '+esc(p.name)+'</span><b>'+p.score+' pts</b></div>').join('');
if(d.questionId!==lastQ){lastQ=d.questionId;answered=false;selected=null;$('playerFeedback').textContent='';$('answers').innerHTML='';}
if(d.question){$('playerQuestion').textContent=d.question.q;$('answers').innerHTML=d.question.a.map((a,i)=>'<button class="option" onclick="choose('+i+')" '+(answered?'disabled':'')+'>'+String.fromCharCode(65+i)+') '+esc(a)+'</button>').join('')}
else{$('playerQuestion').textContent=d.status==='Jogo encerrado'?'A disputa terminou! Confira o resultado com o apresentador.':'Aguarde a próxima pergunta.';$('answers').innerHTML=''}
}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
</script></body></html>
"""

def get_room(code):
    return ROOMS.get(str(code or "").strip().upper())

def host_ok(room, token):
    return room and secrets.compare_digest(room["token"], str(token or ""))

def public_players(room):
    return sorted(
        [{"name": p["name"], "score": p["score"], "active": p["active"]} for p in room["players"].values()],
        key=lambda x: (-x["score"], x["name"].lower())
    )

@app.route("/")
def index():
    return render_template_string(PAGE)

@app.post("/create")
def create():
    code = str(random.randint(100000, 999999))
    while code in ROOMS:
        code = str(random.randint(100000, 999999))
    token = secrets.token_urlsafe(20)
    ROOMS[code] = {
        "token": token, "players": {}, "stage": 0, "q_index": -1,
        "current": None, "question_id": 0, "status": "Sala aberta",
        "finished": False, "stage_questions": [], "stage_answers": set()
    }
    return jsonify(code=code, token=token)

@app.post("/join")
def join():
    data = request.get_json(silent=True) or {}
    room = get_room(data.get("code"))
    name = str(data.get("name", "")).strip()[:24]
    if not room:
        return jsonify(error="Código de sala não encontrado."), 404
    if room["finished"] or room["stage"] > 0:
        return jsonify(error="A partida já começou. Não é possível entrar agora."), 400
    if not name:
        return jsonify(error="Digite seu nome."), 400
    if any(p["name"].lower() == name.lower() for p in room["players"].values()):
        return jsonify(error="Esse nome já está sendo usado nesta sala."), 400
    pid = secrets.token_urlsafe(12)
    room["players"][pid] = {"name": name, "score": 0, "active": True, "answered": {}}
    return jsonify(code=data.get("code").strip().upper(), pid=pid, name=name)

@app.get("/state")
def state():
    code = request.args.get("code")
    room = get_room(code)
    if not room:
        return jsonify(error="Sala não encontrada."), 404
    is_host = host_ok(room, request.args.get("token"))
    pid = request.args.get("pid")
    if not is_host and pid not in room["players"]:
        return jsonify(error="Participante não encontrado."), 403
    q = room["current"]
    data = {
        "status": room["status"], "stage": room["stage"],
        "stageName": STAGE_NAMES[room["stage"]-1] if room["stage"] else "",
        "active": sum(1 for p in room["players"].values() if p["active"]),
        "players": public_players(room), "questionId": room["question_id"],
        "myScore": room["players"].get(pid, {}).get("score", 0),
        "finished": room["finished"]
    }
    if q:
        data["question"] = {"q": q["q"], "a": q["a"]}
        data["qnum"] = room["q_index"] + 1
        data["totalQ"] = len(room["stage_questions"])
    else:
        data["question"] = None
    return jsonify(data)

@app.post("/start")
def start():
    data = request.get_json(silent=True) or {}
    room = get_room(data.get("code"))
    if not host_ok(room, data.get("token")):
        return jsonify(error="Ação não autorizada."), 403
    if not room["players"]:
        return jsonify(error="Espere pelo menos um participante entrar."), 400
    if room["stage"] >= 4:
        return jsonify(error="Todas as etapas já foram realizadas."), 400
    room["stage"] += 1
    room["stage_questions"] = random.sample(QUESTIONS[room["stage"]-1], 3)
    room["q_index"] = 0
    room["current"] = room["stage_questions"][0]
    room["question_id"] += 1
    room["stage_answers"] = set()
    room["status"] = "Etapa iniciada"
    return jsonify(ok=True)

@app.post("/next")
def next_question():
    data = request.get_json(silent=True) or {}
    room = get_room(data.get("code"))
    if not host_ok(room, data.get("token")):
        return jsonify(error="Ação não autorizada."), 403
    if room["stage"] == 0 or room["current"] is None:
        return jsonify(error="Inicie uma etapa primeiro."), 400
    if room["q_index"] + 1 >= len(room["stage_questions"]):
        return jsonify(error="As perguntas desta etapa acabaram. Encerre a etapa."), 400
    room["q_index"] += 1
    room["current"] = room["stage_questions"][room["q_index"]]
    room["question_id"] += 1
    room["stage_answers"] = set()
    room["status"] = "Etapa em andamento"
    return jsonify(ok=True)

@app.post("/answer")
def answer():
    data = request.get_json(silent=True) or {}
    room = get_room(data.get("code"))
    pid = data.get("pid")
    player = room["players"].get(pid) if room else None
    if not player or not player["active"]:
        return jsonify(error="Você não está mais na disputa."), 403
    if not room["current"] or room["finished"]:
        return jsonify(error="Ainda não há pergunta aberta."), 400
    if room["question_id"] in player["answered"]:
        return jsonify(error="Você já respondeu esta pergunta."), 400
    try:
        choice = int(data.get("index"))
    except (TypeError, ValueError):
        return jsonify(error="Resposta inválida."), 400
    if choice not in range(4):
        return jsonify(error="Resposta inválida."), 400
    correct = choice == room["current"]["c"]
    if correct:
        player["score"] += 10
    player["answered"][room["question_id"]] = choice
    room["stage_answers"].add(pid)
    return jsonify(correct=correct, score=player["score"],
                   message="Resposta correta! +10 pontos." if correct else "Resposta registrada. Continue na disputa!")

@app.post("/finish")
def finish():
    data = request.get_json(silent=True) or {}
    room = get_room(data.get("code"))
    if not host_ok(room, data.get("token")):
        return jsonify(error="Ação não autorizada."), 403
    if room["stage"] == 0:
        return jsonify(error="Nenhuma etapa foi iniciada."), 400
    active = [p for p in room["players"].values() if p["active"]]
    if room["stage"] < 3 and len(active) > 3:
        keep = max(3, math.ceil(len(active) * (0.70 if room["stage"] == 1 else 0.55)))
        ordered = sorted(active, key=lambda p: (-p["score"], -sum(1 for qid, ans in p["answered"].items() if ans is not None), p["name"].lower()))
        survivors = set(id(p) for p in ordered[:keep])
        for p in active:
            if id(p) not in survivors:
                p["active"] = False
    elif room["stage"] == 3 and len(active) > 3:
        ordered = sorted(active, key=lambda p: (-p["score"], p["name"].lower()))
        survivors = set(id(p) for p in ordered[:3])
        for p in active:
            if id(p) not in survivors:
                p["active"] = False
    room["current"] = None
    room["status"] = "Etapa encerrada"
    if room["stage"] == 4:
        room["finished"] = True
        room["status"] = "Jogo encerrado"
    return jsonify(ok=True, active=sum(1 for p in room["players"].values() if p["active"]))

def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "IP não identificado — veja os detalhes da rede Wi-Fi"
    finally:
        s.close()

if __name__ == "__main__":
    print("\\n" + "="*48)
    print(" O ATENEU — SERVIDOR DO JOGO")
    print("="*48)
    print("Neste celular: http://127.0.0.1:5000")
    print("Na mesma rede Wi-Fi: http://" + local_ip() + ":5000")
    print("Mantenha o Pydroid aberto durante a partida.\\n")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
