from pathlib import Path
from src.utils import ensure_dir


class CardsSiteGenerator:
    def __init__(self, output_dir="output/site"):
        self.output_dir = output_dir
        ensure_dir(output_dir)

    def save(self):
        path = Path(self.output_dir) / "cards.html"
        path.write_text(self.generate(), encoding="utf-8")
        return str(path)

    def generate(self):
        return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>OmniFlow - Cards Lab</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Inter, Arial, sans-serif;
    background: #f6f7fb;
    color: #111827;
}

.header {
    height: 72px;
    background: #0f172a;
    color: white;
    display: flex;
    align-items: center;
    padding: 0 32px;
}

.header h1 {
    margin: 0;
    font-size: 22px;
}

.header a {
    color: #c7d2fe;
    margin-left: 24px;
    text-decoration: none;
}

.container {
    max-width: 1280px;
    margin: 0 auto;
    padding: 34px;
}

.grid {
    display: grid;
    grid-template-columns: 420px 1fr;
    gap: 24px;
}

.card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, .05);
}

h2 {
    margin-top: 0;
}

label {
    font-weight: 700;
    display: block;
    margin-top: 14px;
    margin-bottom: 6px;
}

input, select, textarea {
    width: 100%;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    padding: 12px;
    font-size: 14px;
}

textarea {
    min-height: 220px;
    resize: vertical;
}

button {
    border: 0;
    border-radius: 10px;
    padding: 12px 16px;
    cursor: pointer;
    font-weight: 700;
}

.btn-primary {
    background: #4f46e5;
    color: white;
    margin-top: 16px;
    width: 100%;
}

.btn-success {
    background: #16a34a;
    color: white;
}

.btn-secondary {
    background: #e5e7eb;
    color: #111827;
}

.actions {
    display: flex;
    gap: 10px;
    margin-bottom: 18px;
}

.card-item {
    border: 1px solid #e5e7eb;
    border-left: 5px solid #4f46e5;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 16px;
    background: #fff;
}

.card-item h3 {
    margin-top: 0;
}

.badge {
    display: inline-block;
    background: #e0e7ff;
    color: #3730a3;
    border-radius: 999px;
    padding: 4px 9px;
    font-size: 12px;
    margin-right: 6px;
}

.criteria li {
    margin-bottom: 6px;
}

.loading {
    color: #4f46e5;
    font-weight: 700;
}

.result {
    background: #ecfdf5;
    border: 1px solid #bbf7d0;
    padding: 14px;
    border-radius: 12px;
    margin-bottom: 16px;
}

.error {
    background: #fef2f2;
    border: 1px solid #fecaca;
    padding: 14px;
    border-radius: 12px;
    margin-bottom: 16px;
}

@media(max-width: 900px) {
    .grid {
        grid-template-columns: 1fr;
    }
}
</style>
</head>

<body>

<div class="header">
    <h1>OmniFlow Cards Lab</h1>
    <a href="/">Voltar para documentação</a>
</div>

<div class="container">
    <div class="grid">
        <aside class="card">
            <h2>Abastecer contexto</h2>
            <p>Use este espaço para explicar o que você quer transformar em cards.</p>

            <label>Tipo de análise</label>
            <select id="analysisType">
                <option value="fluxo">Fluxo específico</option>
                <option value="sistema_inteiro">Sistema inteiro</option>
                <option value="endpoints">Lista de endpoints</option>
                <option value="front_back">Mapeamento Front x Back</option>
                <option value="qa">Cenários de teste / QA</option>
                <option value="refatoracao">Refatoração</option>
            </select>

            <label>Modo de quantidade</label>
            <select id="amountMode">
                <option value="auto">Criar quantos cards forem necessários</option>
                <option value="single">Criar apenas um card consolidado</option>
            </select>

            <label>Objetivo</label>
            <input id="objective" placeholder="Ex: criar endpoints Java para remover dependência do PHP">

            <label>Contexto manual</label>
            <textarea id="manualContext" placeholder="Cole aqui endpoints, requisitos, conversa com cliente, regras de negócio, tela analisada, problemas, melhorias desejadas..."></textarea>

            <button class="btn-primary" onclick="generateCards()">Gerar rascunhos de cards</button>
        </aside>

        <main class="card">
            <h2>Cards gerados</h2>

            <div class="actions">
                <input id="projectKey" placeholder="Project Key Jira. Ex: IN" style="max-width: 220px;">
                <button class="btn-success" onclick="createAllCards()">Criar todos no Jira</button>
                <button class="btn-secondary" onclick="clearCards()">Limpar</button>
            </div>

            <div id="status"></div>
            <div id="cardsList"></div>
        </main>
    </div>
</div>

<script>
let generatedCards = [];

async function generateCards() {
    const status = document.getElementById("status");
    const cardsList = document.getElementById("cardsList");

    status.innerHTML = '<div class="loading">Gerando cards com IA...</div>';
    cardsList.innerHTML = "";

    const payload = {
        analysis_type: document.getElementById("analysisType").value,
        amount_mode: document.getElementById("amountMode").value,
        objective: document.getElementById("objective").value,
        context: document.getElementById("manualContext").value
    };

    try {
        const response = await fetch("/api/cards/generate", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!data.success) {
            status.innerHTML = `<div class="error">${data.error}</div>`;
            return;
        }

        generatedCards = data.cards || [];
        status.innerHTML = `<div class="result">${generatedCards.length} card(s) gerado(s) para revisão.</div>`;
        renderCards();

    } catch (e) {
        status.innerHTML = `<div class="error">Erro ao gerar cards.</div>`;
    }
}

function renderCards() {
    const el = document.getElementById("cardsList");
    el.innerHTML = "";

    generatedCards.forEach((card, index) => {
        el.innerHTML += `
            <div class="card-item">
                <h3 contenteditable="true" oninput="updateCard(${index}, 'summary', this.innerText)">${card.summary || "Sem título"}</h3>

                <p>
                    <span class="badge">${card.area || "Geral"}</span>
                    <span class="badge">${card.issue_type || "Task"}</span>
                    <span class="badge">${card.priority || "Medium"}</span>
                    <span class="badge">${card.story_points || 0} pts</span>
                </p>

                <label>Descrição</label>
                <textarea oninput="updateCard(${index}, 'description', this.value)">${card.description || ""}</textarea>

                <label>Critérios de aceite</label>
                <textarea oninput="updateCardArray(${index}, 'acceptance_criteria', this.value)">${(card.acceptance_criteria || []).join("\\n")}</textarea>

                <label>Notas técnicas</label>
                <textarea oninput="updateCardArray(${index}, 'technical_notes', this.value)">${(card.technical_notes || []).join("\\n")}</textarea>

                <div class="actions">
                    <button class="btn-success" onclick="createOneCard(${index})">Criar este card no Jira</button>
                    <button class="btn-secondary" onclick="removeCard(${index})">Remover</button>
                </div>
            </div>
        `;
    });
}

function updateCard(index, field, value) {
    generatedCards[index][field] = value;
}

function updateCardArray(index, field, value) {
    generatedCards[index][field] = value
        .split("\\n")
        .map(item => item.trim())
        .filter(Boolean);
}

function removeCard(index) {
    generatedCards.splice(index, 1);
    renderCards();
}

function clearCards() {
    generatedCards = [];
    document.getElementById("cardsList").innerHTML = "";
    document.getElementById("status").innerHTML = "";
}

async function createOneCard(index) {
    const projectKey = document.getElementById("projectKey").value.trim();

    if (!projectKey) {
        alert("Informe o Project Key.");
        return;
    }

    await createCardsRequest([generatedCards[index]]);
}

async function createAllCards() {
    const projectKey = document.getElementById("projectKey").value.trim();

    if (!projectKey) {
        alert("Informe o Project Key.");
        return;
    }

    if (!generatedCards.length) {
        alert("Nenhum card gerado.");
        return;
    }

    if (!confirm(`Criar ${generatedCards.length} card(s) no Jira?`)) {
        return;
    }

    await createCardsRequest(generatedCards);
}

async function createCardsRequest(cards) {
    const projectKey = document.getElementById("projectKey").value.trim();
    const status = document.getElementById("status");

    status.innerHTML = '<div class="loading">Criando card(s) no Jira...</div>';

    try {
        const response = await fetch("/api/jira/create-many-cards", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                project_key: projectKey,
                cards
            })
        });

        const data = await response.json();

        if (!data.success) {
            status.innerHTML = `<div class="error">${data.error}</div>`;
            return;
        }

        const created = data.created || [];
        const errors = data.errors || [];

        let html = `<div class="result">${created.length} card(s) criado(s).</div>`;

        created.forEach(item => {
            html += `<p><strong>${item.key}</strong> - ${item.summary}</p>`;
        });

        errors.forEach(item => {
            html += `<div class="error">${item.summary}: ${item.error}</div>`;
        });

        status.innerHTML = html;

    } catch (e) {
        status.innerHTML = `<div class="error">Erro ao criar cards.</div>`;
    }
}
</script>

</body>
</html>
"""