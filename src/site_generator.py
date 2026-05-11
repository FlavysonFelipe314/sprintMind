import json
from pathlib import Path
from src.utils import ensure_dir


class HtmlSiteGenerator:
    def __init__(self, output_dir="output/site"):
        self.output_dir = output_dir
        ensure_dir(output_dir)

    def load_commented_doc(self, analysis):
        files = list(Path("output/commented").glob("*-comentado.md"))

        if files:
            return files[0].read_text(encoding="utf-8", errors="ignore")

        return "# Documentação comentada não encontrada\n\nGere novamente a análise."

    def save(self, analysis: dict):
        html = self.generate(analysis)
        path = Path(self.output_dir) / "index.html"
        path.write_text(html, encoding="utf-8")
        return str(path)

    def generate(self, analysis: dict):
        data_json = json.dumps(analysis, ensure_ascii=False)
        commented_json = json.dumps(self.load_commented_doc(analysis), ensure_ascii=False)

        return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>OmniFlow - {analysis['entry_name']}</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

<style>
* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Inter, Arial, sans-serif;
    background: #f6f7fb;
    color: #111827;
}}

.header {{
    height: 72px;
    background: #0f172a;
    color: white;
    display: flex;
    align-items: center;
    padding: 0 32px;
}}

.header h1 {{
    margin: 0;
    font-size: 22px;
}}

.header span {{
    margin-left: 14px;
    color: #cbd5e1;
    font-size: 14px;
}}

.layout {{
    display: grid;
    grid-template-columns: 280px 1fr;
    min-height: calc(100vh - 72px);
}}

.sidebar {{
    background: white;
    border-right: 1px solid #e5e7eb;
    padding: 24px 18px;
    height: calc(100vh - 72px);
    position: sticky;
    top: 0;
}}

.sidebar h3 {{
    font-size: 13px;
    color: #6b7280;
    text-transform: uppercase;
}}

.nav-item {{
    padding: 11px 12px;
    border-radius: 8px;
    cursor: pointer;
    margin-bottom: 4px;
}}

.nav-item:hover,
.nav-item.active {{
    background: #eef2ff;
    color: #3730a3;
}}

.main {{
    padding: 42px 64px;
    max-width: 1180px;
}}

.hero {{
    background: linear-gradient(135deg, #111827, #312e81);
    color: white;
    border-radius: 18px;
    padding: 34px;
    margin-bottom: 30px;
}}

.hero h2 {{
    margin: 0 0 12px;
    font-size: 34px;
}}

.hero p {{
    color: #e5e7eb;
    line-height: 1.6;
}}

.tabs {{
    display: flex;
    gap: 10px;
    margin-bottom: 22px;
    flex-wrap: wrap;
}}

.tab {{
    border: 1px solid #dbe1ea;
    background: white;
    padding: 10px 16px;
    border-radius: 999px;
    cursor: pointer;
    font-weight: 600;
}}

.tab.active {{
    background: #4f46e5;
    color: white;
}}

.card {{
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 20px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, .05);
}}

.doc-content {{
    font-size: 16px;
    line-height: 1.75;
}}

.doc-content h1 {{
    font-size: 32px;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 14px;
}}

.doc-content h2 {{
    font-size: 24px;
    margin-top: 34px;
}}

.doc-content p {{
    color: #374151;
}}

.file-card {{
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
    cursor: pointer;
}}

.file-card:hover {{
    border-color: #6366f1;
}}

.badge {{
    display: inline-block;
    padding: 4px 9px;
    background: #e0e7ff;
    color: #3730a3;
    border-radius: 999px;
    font-size: 12px;
    margin-right: 6px;
}}

.method {{
    border-left: 4px solid #6366f1;
    background: #f9fafb;
    padding: 16px;
    border-radius: 10px;
    margin-bottom: 14px;
}}

.route {{
    background: #0f172a;
    color: #e5e7eb;
    padding: 14px;
    border-radius: 10px;
    font-family: Consolas, monospace;
    margin-bottom: 10px;
    overflow-x: auto;
}}

.hidden {{
    display: none;
}}

.chat-button {{
    position: fixed;
    right: 28px;
    bottom: 28px;
    background: #4f46e5;
    color: white;
    border: none;
    border-radius: 999px;
    padding: 15px 22px;
    font-weight: 700;
    cursor: pointer;
}}

.chat-box {{
    position: fixed;
    right: 28px;
    bottom: 88px;
    width: 520px;
    height: 650px;
    background: white;
    border-radius: 18px;
    box-shadow: 0 18px 50px rgba(15,23,42,.30);
    display: none;
    flex-direction: column;
    overflow: hidden;
}}

.chat-header {{
    background: #0f172a;
    color: white;
    padding: 16px;
    font-weight: 700;
}}

.chat-actions {{
    display: flex;
    gap: 8px;
    padding: 10px;
    border-bottom: 1px solid #e5e7eb;
    flex-wrap: wrap;
}}

.chat-actions button {{
    border: 1px solid #ddd;
    background: #f8fafc;
    border-radius: 999px;
    padding: 7px 10px;
    cursor: pointer;
}}

.chat-messages {{
    flex: 1;
    padding: 16px;
    overflow-y: auto;
    background: #f8fafc;
}}

.chat-input {{
    display: flex;
    border-top: 1px solid #e5e7eb;
}}

.chat-input input {{
    flex: 1;
    border: none;
    padding: 15px;
    outline: none;
}}

.chat-input button {{
    border: none;
    background: #4f46e5;
    color: white;
    padding: 0 20px;
    cursor: pointer;
}}

.msg {{
    padding: 12px 14px;
    border-radius: 12px;
    margin-bottom: 12px;
    line-height: 1.55;
    white-space: pre-wrap;
}}

.user {{
    background: #dbeafe;
}}

.bot {{
    background: white;
    border: 1px solid #e5e7eb;
}}

.jira-draft {{
    background: #fff7ed;
    border: 1px solid #fed7aa;
}}

.jira-form {{
    margin-top: 10px;
}}

.jira-form input,
.jira-form select {{
    width: 100%;
    padding: 9px;
    margin: 6px 0;
}}

.jira-form button {{
    background: #16a34a;
    color: white;
    border: 0;
    padding: 10px 14px;
    border-radius: 8px;
    cursor: pointer;
}}

@media(max-width: 900px) {{
    .layout {{
        grid-template-columns: 1fr;
    }}

    .sidebar {{
        display: none;
    }}

    .main {{
        padding: 24px;
    }}

    .chat-box {{
        width: calc(100vw - 32px);
        right: 16px;
    }}
}}
</style>
</head>

<body>

<div class="header">
    <h1>OmniFlow</h1>
    <span>Lab técnico · {analysis['entry_name']} · {analysis['total_files']} arquivos</span>
</div>

<div class="layout">
    <aside class="sidebar">
        <h3>Documentação</h3>
        <div class="nav-item active" onclick="showTab('doc')">Visão comentada</div>
        <div class="nav-item" onclick="showTab('files')">Arquivos</div>
        <div class="nav-item" onclick="showTab('routes')">Rotas</div>
        <div class="nav-item" onclick="showTab('methods')">Métodos</div>
        <div class="nav-item" onclick="showTab('deps')">Dependências</div>
    </aside>

    <main class="main">
        <section class="hero">
            <h2>{analysis['entry_name']}</h2>
            <p>
                Documentação comentada, mapa técnico, análise de fluxo e Lab para conversar sobre desenvolvimento,
                QA, melhorias, refatoração e criação controlada de cards no Jira.
            </p>
        </section>

        <div class="tabs">
            <button class="tab active" onclick="showTab('doc')">Comentada</button>
            <button class="tab" onclick="showTab('files')">Arquivos</button>
            <button class="tab" onclick="showTab('routes')">Rotas</button>
            <button class="tab" onclick="showTab('methods')">Métodos</button>
            <button class="tab" onclick="showTab('deps')">Dependências</button>
        </div>

        <section id="tab-doc" class="tab-content card">
            <div id="commentedDoc" class="doc-content"></div>
        </section>

        <section id="tab-files" class="tab-content hidden">
            <div class="card">
                <h2>Arquivos analisados</h2>
                <div id="fileList"></div>
            </div>
            <div id="fileDetails"></div>
        </section>

        <section id="tab-routes" class="tab-content hidden card">
            <h2>Rotas encontradas</h2>
            <div id="routesList"></div>
        </section>

        <section id="tab-methods" class="tab-content hidden card">
            <h2>Métodos detectados</h2>
            <div id="methodsList"></div>
        </section>

        <section id="tab-deps" class="tab-content hidden card">
            <h2>Dependências navegadas</h2>
            <div id="depsList"></div>
        </section>
    </main>
</div>

<button class="chat-button" onclick="toggleChat()">Abrir Lab</button>

<div class="chat-box" id="chatBox">
    <div class="chat-header">OmniFlow Lab</div>

    <div class="chat-actions">
        <button onclick="quickAsk('Gere cenários de teste para esse fluxo')">Cenários de teste</button>
        <button onclick="quickAsk('Mapeie front e back desse fluxo')">Front x Back</button>
        <button onclick="quickAsk('Quais melhorias e gargalos existem nesse fluxo?')">Melhorias</button>
        <button onclick="quickAsk('Crie um rascunho de card Jira para melhorar esse fluxo')">Rascunho Jira</button>
    </div>

    <div class="chat-messages" id="chatMessages">
        <div class="msg bot">
Converse sobre o fluxo, gargalos, testes, front/back, refatoração ou peça um rascunho de card Jira.
Eu só publico no Jira depois de confirmação explícita.
        </div>
    </div>

    <div class="chat-input">
        <input id="chatInput" placeholder="Ex: explique o fluxo principal" onkeydown="handleEnter(event)">
        <button onclick="sendMessage()">Enviar</button>
    </div>
</div>

<script>
const analysis = {data_json};
const commentedMarkdown = {commented_json};
let currentJiraDraft = null;

function flattenGraph(node, list = []) {{
    if (!node) return list;
    if (node.file) list.push(node);
    if (node.children) node.children.forEach(child => flattenGraph(child, list));
    return list;
}}

const files = flattenGraph(analysis.graph);

function showTab(tab) {{
    document.querySelectorAll(".tab-content").forEach(el => el.classList.add("hidden"));
    document.getElementById("tab-" + tab).classList.remove("hidden");
}}

function renderCommentedDoc() {{
    document.getElementById("commentedDoc").innerHTML = marked.parse(commentedMarkdown);
}}

function renderFiles() {{
    const el = document.getElementById("fileList");
    el.innerHTML = "";

    files.forEach(file => {{
        const div = document.createElement("div");
        div.className = "file-card";
        div.onclick = () => renderFileDetails(file);

        div.innerHTML = `
            <strong>${{file.class || file.type || "Arquivo"}}</strong><br>
            <span class="badge">${{file.type || "php"}}</span>
            <span class="badge">depth ${{file.depth ?? "-"}}</span>
            <p>${{file.file}}</p>
        `;

        el.appendChild(div);
    }});
}}

function renderFileDetails(file) {{
    const el = document.getElementById("fileDetails");

    let html = `
        <div class="card">
            <h2>${{file.class || "Arquivo"}}</h2>
            <p><strong>Arquivo:</strong> ${{file.file}}</p>
            <p><strong>Namespace:</strong> ${{file.namespace || "-"}}</p>
        </div>
    `;

    if (file.uses?.length) {{
        html += `<div class="card"><h3>Imports</h3>`;
        file.uses.forEach(use => html += `<p><code>${{use}}</code></p>`);
        html += `</div>`;
    }}

    if (file.methods?.length) {{
        html += `<div class="card"><h3>Métodos</h3>`;
        file.methods.forEach(method => {{
            html += `
                <div class="method">
                    <h4>${{method.visibility}} function ${{method.name}}(${{method.params}})</h4>
                    <p>${{method.summary}}</p>
                </div>
            `;
        }});
        html += `</div>`;
    }}

    el.innerHTML = html;
}}

function renderRoutes() {{
    const el = document.getElementById("routesList");
    el.innerHTML = "";

    files.forEach(file => {{
        if (file.routes?.length) {{
            file.routes.forEach(route => {{
                el.innerHTML += `<div class="route">${{route.route_file}}<br>${{route.line}}</div>`;
            }});
        }}
    }});

    if (!el.innerHTML) el.innerHTML = "<p>Nenhuma rota encontrada.</p>";
}}

function renderMethods() {{
    const el = document.getElementById("methodsList");
    el.innerHTML = "";

    files.forEach(file => {{
        if (file.methods?.length) {{
            el.innerHTML += `<h3>${{file.class || file.file}}</h3>`;

            file.methods.forEach(method => {{
                el.innerHTML += `
                    <div class="method">
                        <h4>${{method.visibility}} function ${{method.name}}(${{method.params}})</h4>
                        <p><strong>Resumo:</strong> ${{method.summary}}</p>
                    </div>
                `;
            }});
        }}
    }});

    if (!el.innerHTML) el.innerHTML = "<p>Nenhum método encontrado.</p>";
}}

function renderDeps() {{
    const el = document.getElementById("depsList");
    el.innerHTML = "";

    files.forEach(file => {{
        if (file.dependencies?.length) {{
            el.innerHTML += `<h3>${{file.class || file.file}}</h3>`;
            file.dependencies.forEach(dep => el.innerHTML += `<p><code>${{dep}}</code></p>`);
        }}
    }});

    if (!el.innerHTML) el.innerHTML = "<p>Nenhuma dependência encontrada.</p>";
}}

function toggleChat() {{
    const box = document.getElementById("chatBox");
    box.style.display = box.style.display === "flex" ? "none" : "flex";
}}

function handleEnter(event) {{
    if (event.key === "Enter") sendMessage();
}}

function quickAsk(text) {{
    document.getElementById("chatInput").value = text;
    sendMessage();
}}

async function sendMessage() {{
    const input = document.getElementById("chatInput");
    const messages = document.getElementById("chatMessages");
    const question = input.value.trim();

    if (!question) return;

    messages.innerHTML += `<div class="msg user">${{question}}</div>`;
    input.value = "";

    const botMsg = document.createElement("div");
    botMsg.className = "msg bot";
    botMsg.innerText = "Analisando contexto...";
    messages.appendChild(botMsg);

    try {{
        const response = await fetch("/api/lab/chat", {{
            method: "POST",
            headers: {{ "Content-Type": "application/json" }},
            body: JSON.stringify({{ message: question }})
        }});

        const data = await response.json();

        if (data.type === "jira_draft") {{
            currentJiraDraft = data.draft;
            botMsg.classList.add("jira-draft");
            botMsg.innerHTML = renderJiraDraft(data.draft);
        }} else {{
            botMsg.innerText = data.answer || "Sem resposta.";
        }}
    }} catch (e) {{
        botMsg.innerText = "Erro ao conversar com o agente. Verifique o web.py.";
    }}

    messages.scrollTop = messages.scrollHeight;
}}

function renderJiraDraft(draft) {{
    return `
Rascunho de card Jira

Título:
${{draft.summary}}

Tipo:
${{draft.issue_type}}

Prioridade:
${{draft.priority}}

Story points sugerido:
${{draft.story_points}}

Descrição:
${{draft.description}}

Critérios de aceite:
${{(draft.acceptance_criteria || []).map(x => "- " + x).join("\\n")}}

<div class="jira-form">
    <input id="jiraProjectKey" placeholder="Project Key. Ex: IN">
    <select id="jiraIssueType">
        <option>Task</option>
        <option>Story</option>
        <option>Bug</option>
    </select>
    <select id="jiraPriority">
        <option>Medium</option>
        <option>High</option>
        <option>Low</option>
    </select>
    <button onclick="createJiraIssue()">Confirmar e criar no Jira</button>
</div>
`;
}}

async function createJiraIssue() {{
    if (!currentJiraDraft) return;

    const projectKey = document.getElementById("jiraProjectKey").value.trim();
    const issueType = document.getElementById("jiraIssueType").value;
    const priority = document.getElementById("jiraPriority").value;

    if (!projectKey) {{
        alert("Informe o Project Key do Jira.");
        return;
    }}

    const response = await fetch("/api/jira/create-card", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{
            project_key: projectKey,
            issue_type: issueType,
            priority: priority,
            draft: currentJiraDraft
        }})
    }});

    const data = await response.json();

    if (data.success) {{
        alert("Card criado no Jira: " + data.key);
    }} else {{
        alert("Erro ao criar card: " + data.error);
    }}
}}

renderCommentedDoc();
renderFiles();
renderRoutes();
renderMethods();
renderDeps();
</script>

</body>
</html>
"""