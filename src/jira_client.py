import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()


class JiraClient:
    def __init__(self):
        self.base_url = os.getenv("JIRA_BASE_URL", "").rstrip("/")
        self.email = os.getenv("JIRA_EMAIL", "")
        self.api_token = os.getenv("JIRA_API_TOKEN", "")

        if not self.base_url or not self.email or not self.api_token:
            raise RuntimeError("Configuração Jira incompleta no .env")

        self.auth = HTTPBasicAuth(self.email, self.api_token)

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_projects(self):
        url = f"{self.base_url}/rest/api/3/project/search"

        response = requests.get(
            url,
            headers=self.headers,
            auth=self.auth,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        return [
            {
                "id": item.get("id"),
                "key": item.get("key"),
                "name": item.get("name")
            }
            for item in data.get("values", [])
        ]

    def get_issue_types(self, project_key: str):
        url = f"{self.base_url}/rest/api/3/issue/createmeta"

        params = {
            "projectKeys": project_key,
            "expand": "projects.issuetypes.fields"
        }

        response = requests.get(
            url,
            headers=self.headers,
            auth=self.auth,
            params=params,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        projects = data.get("projects", [])

        if not projects:
            return []

        return [
            {
                "id": issue_type.get("id"),
                "name": issue_type.get("name")
            }
            for issue_type in projects[0].get("issuetypes", [])
        ]

    def search_epics(self, project_key: str):
        url = f"{self.base_url}/rest/api/3/search/jql"

        jql = f'project = "{project_key}" AND issuetype = Epic ORDER BY created DESC'

        payload = {
            "jql": jql,
            "maxResults": 50,
            "fields": ["summary", "key"]
        }

        response = requests.post(
            url,
            headers=self.headers,
            auth=self.auth,
            json=payload,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        return [
            {
                "key": item.get("key"),
                "summary": item.get("fields", {}).get("summary")
            }
            for item in data.get("issues", [])
        ]

    def create_issue(
        self,
        project_key: str,
        summary: str,
        description: str,
        issue_type: str = "Task",
        priority: str = "Medium",
        labels=None
    ):
        if labels is None:
            labels = ["omniflow"]

        url = f"{self.base_url}/rest/api/3/issue"

        payload = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": summary,
                "issuetype": {
                    "name": issue_type
                },
                "priority": {
                    "name": priority
                },
                "labels": labels,
                "description": self.to_adf(description)
            }
        }

        response = requests.post(
            url,
            headers=self.headers,
            auth=self.auth,
            json=payload,
            timeout=30
        )

        response.raise_for_status()
        return response.json()

    def to_adf(self, text: str):
        paragraphs = []

        for line in text.split("\n"):
            if not line.strip():
                continue

            paragraphs.append({
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": line[:30000]
                    }
                ]
            })

        return {
            "type": "doc",
            "version": 1,
            "content": paragraphs or [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Sem descrição."
                        }
                    ]
                }
            ]
        }
        
    
    def create_many_issues(self, project_key: str, cards: list):
        created = []
        errors = []

        for card in cards:
            try:
                description = card.get("description", "")

                criteria = card.get("acceptance_criteria", [])
                if criteria:
                    description += "\n\nCritérios de aceite:\n"
                    for item in criteria:
                        description += f"- {item}\n"

                notes = card.get("technical_notes", [])
                if notes:
                    description += "\n\nNotas técnicas:\n"
                    for item in notes:
                        description += f"- {item}\n"

                issue = self.create_issue(
                    project_key=project_key,
                    summary=card.get("summary", "Card criado pelo OmniFlow"),
                    description=description,
                    issue_type=card.get("issue_type", "Task"),
                    priority=card.get("priority", "Medium"),
                    labels=card.get("labels", ["omniflow"])
                )

                created.append({
                    "summary": card.get("summary"),
                    "key": issue.get("key"),
                    "issue": issue
                })

            except Exception as e:
                errors.append({
                    "summary": card.get("summary"),
                    "error": str(e)
                })

        return {
            "created": created,
            "errors": errors
        }