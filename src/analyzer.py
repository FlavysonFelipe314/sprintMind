import re
from pathlib import Path
from src.utils import read_file


class PhpControllerAnalyzer:
    def __init__(self, project_path: str, max_depth: int = 3):
        self.project_path = Path(project_path)
        self.max_depth = max_depth
        self.visited = set()
        
        self.ignore_dirs = {
            "vendor",
            "node_modules",
            "storage",
            "bootstrap",
            ".git",
            "dist",
            "build",
            "coverage",
            "tmp",
            "logs"
        }

        self.allowed_extensions = {
            ".php",
            ".js",
            ".css",
            ".html",
            ".blade.php"
        }

    def analyze(self, entry_file: str) -> dict:
        entry = Path(entry_file)
        graph = self.walk_file(entry, depth=0)

        return {
            "entry_file": str(entry),
            "entry_name": entry.stem,
            "graph": graph,
            "total_files": len(self.visited),
            "visited_files": list(self.visited),
        }

    def walk_file(self, file_path: Path, depth: int):
        file_path = file_path.resolve()

        if str(file_path) in self.visited:
            return {"file": str(file_path), "already_visited": True}

        if depth > self.max_depth:
            return {"file": str(file_path), "max_depth_reached": True}

        if not file_path.exists():
            return {"file": str(file_path), "not_found": True}

        self.visited.add(str(file_path))

        content = read_file(str(file_path))

        analysis = {
            "file": str(file_path),
            "type": self.detect_file_type(file_path),
            "depth": depth,
            "namespace": self.extract_namespace(content),
            "uses": self.extract_uses(content),
            "class": self.extract_class(content),
            "methods": self.extract_methods(content),
            "views": self.extract_laravel_views(content),
            "json_responses": self.extract_json_responses(content),
            "routes": self.find_routes_for_controller(file_path),
            "facades": self.extract_facades(content),
            "jobs": self.extract_jobs(content),
            "events": self.extract_events(content),
            "models": self.extract_laravel_models(content),
            "services": self.extract_services(content),
            "ajax_calls": self.extract_ajax_calls(content),
            "jquery_events": self.extract_jquery_events(content),
            "forms": self.extract_forms(content),
            "dependencies": [],
            "children": []
        }

        dependency_files = self.resolve_dependencies(content, file_path)

        for dep in dependency_files:
            analysis["dependencies"].append(str(dep))
            child = self.walk_file(dep, depth + 1)
            analysis["children"].append(child)

        return analysis

    def detect_file_type(self, file_path: Path):
        path = str(file_path).replace("\\", "/").lower()

        if "/controllers/" in path:
            return "controller"
        if "/models/" in path:
            return "model"
        if "/services/" in path:
            return "service"
        if "/jobs/" in path:
            return "job"
        if "/events/" in path:
            return "event"
        if "/requests/" in path:
            return "form_request"
        if "/resources/views/" in path:
            return "view"
        if "/routes/" in path:
            return "route"
        if path.endswith(".js"):
            return "javascript"
        if path.endswith(".css"):
            return "css"
        if path.endswith(".blade.php"):
            return "blade_view"

        return "php_file"

    def extract_namespace(self, content: str):
        match = re.search(r"namespace\s+(.+?);", content)
        return match.group(1).strip() if match else None

    def extract_class(self, content: str):
        match = re.search(r"class\s+(\w+)", content)
        return match.group(1).strip() if match else None

    def extract_uses(self, content: str):
        return re.findall(r"use\s+([^;]+);", content)

    def extract_methods(self, content: str):
        pattern = r"(public|protected|private)\s+function\s+(\w+)\s*\((.*?)\)"
        matches = re.findall(pattern, content, re.DOTALL)

        methods = []

        for visibility, name, params in matches:
            body = self.extract_method_body(content, name)

            methods.append({
                "visibility": visibility,
                "name": name,
                "params": params.strip(),
                "summary": self.summarize_method(body),
                "calls": self.extract_method_calls(body),
                "uses_request": "Request" in params or "$request" in body,
                "returns_view": "view(" in body,
                "returns_json": "json(" in body or "response()->json" in body,
                "dispatches_job": "::dispatch" in body or "dispatch(" in body,
            })

        return methods

    def extract_method_body(self, content: str, method_name: str):
        pattern = rf"function\s+{method_name}\s*\(.*?\)\s*\{{"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return ""

        start = match.end()
        brace_count = 1
        i = start

        while i < len(content) and brace_count > 0:
            if content[i] == "{":
                brace_count += 1
            elif content[i] == "}":
                brace_count -= 1
            i += 1

        return content[start:i - 1]

    def summarize_method(self, body: str):
        items = []

        if "view(" in body:
            items.append("retorna view")
        if "response()->json" in body or "json(" in body:
            items.append("retorna JSON")
        if "::dispatch" in body or "dispatch(" in body:
            items.append("dispara job/evento")
        if "Http::" in body:
            items.append("faz chamada HTTP externa")
        if "DB::" in body:
            items.append("usa query direta via DB")
        if "Mail::" in body:
            items.append("envia e-mail")
        if "Log::" in body:
            items.append("registra logs")
        if "Storage::" in body:
            items.append("usa storage")

        return ", ".join(items) if items else "sem comportamento crítico identificado automaticamente"

    def extract_method_calls(self, body: str):
        calls = []
        calls.extend(re.findall(r"\$this->(\w+)\(", body))
        calls.extend([f"{a}::{b}" for a, b in re.findall(r"(\w+)::(\w+)\(", body)])
        calls.extend(re.findall(r"->(\w+)\(", body))
        return list(set([str(c) for c in calls]))

    def extract_laravel_views(self, content: str):
        return list(set(re.findall(r"view\(['\"](.+?)['\"]", content)))

    def extract_json_responses(self, content: str):
        return list(set(re.findall(r"response\(\)->json\((.*?)\)", content, re.DOTALL)))

    def extract_facades(self, content: str):
        facades = [
            "DB", "Log", "Http", "Mail", "Storage", "Cache",
            "Auth", "Route", "Validator", "Hash", "Crypt", "Queue"
        ]

        return [facade for facade in facades if f"{facade}::" in content]

    def extract_jobs(self, content: str):
        return list(set(re.findall(r"(\w+Job)::dispatch", content)))

    def extract_events(self, content: str):
        events = []
        events.extend(re.findall(r"event\(new\s+(\w+)", content))
        events.extend(re.findall(r"(\w+Event)::dispatch", content))
        return list(set(events))

    def extract_laravel_models(self, content: str):
        models = []
        for item in self.extract_uses(content):
            if "\\Models\\" in item:
                models.append(item)
        return list(set(models))

    def extract_services(self, content: str):
        services = []
        for item in self.extract_uses(content):
            if "\\Services\\" in item or item.endswith("Service"):
                services.append(item)
        return list(set(services))

    def extract_ajax_calls(self, content: str):
        calls = []

        patterns = [
            r"\$\.ajax\s*\((.*?)\)",
            r"\$\.get\s*\((.*?)\)",
            r"\$\.post\s*\((.*?)\)",
            r"fetch\s*\((.*?)\)",
            r"axios\.(get|post|put|delete)\s*\((.*?)\)"
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                calls.append(str(match)[:500])

        return calls

    def extract_jquery_events(self, content: str):
        pattern = r"\$\(['\"](.+?)['\"]\)\.(on|click|change|submit)\s*\("
        return [
            {"selector": selector, "event": event}
            for selector, event in re.findall(pattern, content)
        ]

    def extract_forms(self, content: str):
        forms = []
        forms.extend(re.findall(r"<form[^>]*>", content, re.IGNORECASE))
        return forms[:20]

    def resolve_dependencies(self, content: str, current_file: Path):
        files = []

        files.extend(self.resolve_use_imports(content))
        files.extend(self.resolve_views(content))
        files.extend(self.resolve_routes_if_controller(current_file))
        files.extend(self.resolve_constructor_types(content))
        files.extend(self.resolve_asset_references(content))

        unique = []

        for file in files:
            if file and file.exists() and file not in unique:
                unique.append(file)

        return unique

    def resolve_use_imports(self, content: str):
        files = []

        for use in self.extract_uses(content):
            use = use.strip()

            if not use.startswith("App\\"):
                continue

            relative = use.replace("App\\", "app\\").replace("\\", "/") + ".php"
            path = self.project_path / relative

            if path.exists():
                files.append(path)

        return files

    def resolve_constructor_types(self, content: str):
        files = []
        matches = re.findall(r"__construct\s*\((.*?)\)", content, re.DOTALL)

        for params in matches:
            types = re.findall(r"(\w+)\s+\$\w+", params)

            for type_name in types:
                found = self.find_php_class_file(type_name)
                if found:
                    files.append(found)

        return files

    def resolve_views(self, content: str):
        files = []

        for view in self.extract_laravel_views(content):
            blade_path = view.replace(".", "/") + ".blade.php"
            path = self.project_path / "resources" / "views" / blade_path

            if path.exists():
                files.append(path)

        return files

    def resolve_routes_if_controller(self, current_file: Path):
        files = []
        path = str(current_file).replace("\\", "/").lower()

        if "/controllers/" not in path:
            return files

        for route_file in [
            self.project_path / "routes" / "web.php",
            self.project_path / "routes" / "api.php",
        ]:
            if route_file.exists():
                files.append(route_file)

        return files

    def resolve_asset_references(self, content: str):
        files = []

        refs = []
        refs.extend(re.findall(r"['\"]([^'\"]+\.js)['\"]", content))
        refs.extend(re.findall(r"['\"]([^'\"]+\.css)['\"]", content))

        for ref in refs:
            ref = ref.lstrip("/")
            possible = [
                self.project_path / "public" / ref,
                self.project_path / ref,
                self.project_path / "resources" / ref,
            ]

            for path in possible:
                if path.exists():
                    files.append(path)

        return files

    def find_routes_for_controller(self, controller_file: Path):
        routes = []
        controller_name = controller_file.stem

        for route_file in [
            self.project_path / "routes" / "web.php",
            self.project_path / "routes" / "api.php",
        ]:
            if not route_file.exists():
                continue

            content = read_file(str(route_file))

            for line in content.splitlines():
                if controller_name in line:
                    routes.append({
                        "route_file": str(route_file),
                        "line": line.strip()
                    })

        return routes

    def find_php_class_file(self, class_name: str):
        for file in self.project_path.rglob("*.php"):
            if file.name == f"{class_name}.php":
                return file
        return None
    
    
    def analyze_project(self):
        graph = {
            "file": str(self.project_path),
            "type": "project",
            "children": []
        }

        for file in self.scan_project_files():
            try:
                child = self.walk_file(file, depth=0)
                graph["children"].append(child)
            except Exception as e:
                graph["children"].append({
                    "file": str(file),
                    "error": str(e)
                })

        return {
            "entry_file": str(self.project_path),
            "entry_name": self.project_path.name,
            "graph": graph,
            "total_files": len(self.visited),
            "visited_files": list(self.visited),
        }
        
    
    def scan_project_files(self):
        files = []

        for file in self.project_path.rglob("*"):
            if not file.is_file():
                continue

            path_parts = set(file.parts)

            if path_parts & self.ignore_dirs:
                continue

            filename = file.name.lower()

            if filename.endswith(".min.js"):
                continue

            if filename.endswith(".map"):
                continue

            if filename.endswith(".lock"):
                continue

            full_name = file.name.lower()

            if full_name.endswith(".blade.php"):
                files.append(file)
                continue

            if file.suffix.lower() in self.allowed_extensions:
                files.append(file)

        return files