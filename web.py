from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from src.rag import CodeRag
from src.lab_agent import LabAgent
from src.jira_client import JiraClient
from src.card_agent import CardAgent

app = Flask(__name__)
CORS(app)

rag = CodeRag()
lab = LabAgent()
card_agent = CardAgent()

@app.route("/")
def index():
    return send_from_directory("output/site", "index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    question = data.get("question", "")

    if not question:
        return jsonify({"answer": "Pergunta vazia."}), 400

    response = rag.ask(question)

    return jsonify({
        "answer": response["result"]
    })


@app.route("/api/lab/chat", methods=["POST"])
def lab_chat():
    data = request.get_json() or {}
    message = data.get("message", "")

    if not message:
        return jsonify({
            "type": "error",
            "answer": "Mensagem vazia."
        }), 400

    response = lab.ask(message)
    return jsonify(response)


@app.route("/api/jira/projects", methods=["GET"])
def jira_projects():
    try:
        jira = JiraClient()
        projects = jira.get_projects()

        return jsonify({
            "success": True,
            "projects": projects
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/jira/epics", methods=["GET"])
def jira_epics():
    project_key = request.args.get("project_key")

    if not project_key:
        return jsonify({
            "success": False,
            "error": "project_key é obrigatório"
        }), 400

    try:
        jira = JiraClient()
        epics = jira.search_epics(project_key)

        return jsonify({
            "success": True,
            "epics": epics
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/jira/create-card", methods=["POST"])
def jira_create_card():
    data = request.get_json() or {}

    project_key = data.get("project_key")
    issue_type = data.get("issue_type", "Task")
    priority = data.get("priority", "Medium")
    draft = data.get("draft", {})

    if not project_key:
        return jsonify({
            "success": False,
            "error": "project_key é obrigatório"
        }), 400

    if not draft:
        return jsonify({
            "success": False,
            "error": "draft é obrigatório"
        }), 400

    try:
        criteria = draft.get("acceptance_criteria", [])

        description = draft.get("description", "")

        if criteria:
            description += "\n\nCritérios de aceite:\n"
            for item in criteria:
                description += f"- {item}\n"

        jira = JiraClient()

        issue = jira.create_issue(
            project_key=project_key,
            summary=draft.get("summary", "Card criado pelo OmniFlow"),
            description=description,
            issue_type=issue_type,
            priority=priority,
            labels=draft.get("labels", ["omniflow"])
        )

        return jsonify({
            "success": True,
            "key": issue.get("key"),
            "issue": issue
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/cards")
def cards_page():
    return send_from_directory("output/site", "cards.html")


@app.route("/api/cards/generate", methods=["POST"])
def generate_cards():
    data = request.get_json() or {}

    try:
        result = card_agent.generate_cards(data)

        return jsonify({
            "success": True,
            "cards": result.get("cards", [])
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/jira/create-many-cards", methods=["POST"])
def jira_create_many_cards():
    data = request.get_json() or {}

    project_key = data.get("project_key")
    cards = data.get("cards", [])

    if not project_key:
        return jsonify({
            "success": False,
            "error": "project_key é obrigatório"
        }), 400

    if not cards:
        return jsonify({
            "success": False,
            "error": "cards é obrigatório"
        }), 400

    try:
        jira = JiraClient()
        result = jira.create_many_issues(project_key, cards)

        return jsonify({
            "success": True,
            "created": result["created"],
            "errors": result["errors"]
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
        
        
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8000,
        debug=True
    )