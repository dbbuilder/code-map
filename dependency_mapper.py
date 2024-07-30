import re
from urllib.parse import urlparse
from collections import defaultdict, Counter
import os


class DependencyMapper:
    def __init__(self, logger, base_path):
        """
        Initializes the DependencyMapper with a logger and sets up regex patterns for dependencies and methods.

        Args:
            logger (logging.Logger): Logger instance for logging information.
            base_path (str): Base path for saving logs.
        """
        self.logger = logger
        self.base_path = base_path
        # Regex patterns to identify various types of dependencies and methods
        self.dependency_patterns = [
            re.compile(
                r'(import|require)\s+[\'"](.+?)[\'"]'
            ),  # JavaScript import/require
            re.compile(
                r'<!--\s*#include\s*file\s*=\s*[\'"](.+?)[\'"]\s*-->'
            ),  # HTML includes
            re.compile(r'(https?://[^\s\'"]+)'),  # API URLs (HTTP/HTTPS links)
            re.compile(r'<Compile Include="(.+?)"'),  # VBProj includes
            re.compile(
                r'<ProjectReference Include="(.+?)"'
            ),  # Project references in .vbproj and .sln
        ]
        self.method_pattern = re.compile(
            r"function\s+(\w+)\s*\("
        )  # JavaScript/VB method definitions
        self.localhost_pattern = re.compile(r"localhost:(\d+)")  # Localhost with port
        self.supported_extensions = (".vb", ".vue", ".js")

    def map_dependencies_and_methods(self, projects):
        """
        Maps dependencies and shared methods across multiple projects.

        Args:
            projects (list): List of projects with their respective files.

        Returns:
            tuple: Two dictionaries containing dependency maps and method usage maps respectively.
        """
        dependency_map = {}
        method_usage_map = {}
        localhost_map = {}
        domain_count = Counter()

        try:
            for project in projects:
                self.logger.info(f"Mapping dependencies for project: {project['name']}")
                dependencies = []
                methods = {}

                for file in project["files"]:
                    if not file.endswith(self.supported_extensions):
                        continue
                    try:
                        with open(file, "r", encoding="utf-8") as f:
                            content = f.read()

                            # Find localhost endpoints
                            localhost_matches = self.localhost_pattern.findall(content)
                            for port in localhost_matches:
                                localhost_map[port] = project["name"]

                            # Find dependencies
                            for pattern in self.dependency_patterns:
                                matches = pattern.findall(content)
                                for match in matches:
                                    dependency = (
                                        match[1] if isinstance(match, tuple) else match
                                    )
                                    # Skip npmjs.org references
                                    if "npmjs.org" in dependency:
                                        continue
                                    dependencies.append(dependency)
                                    # Extract domain and count occurrences
                                    domain = self.extract_domain(dependency)
                                    if domain:
                                        root_domain = self.get_root_domain(domain)
                                        domain_count[root_domain] += 1

                            # Find method definitions
                            method_matches = self.method_pattern.findall(content)
                            for method in method_matches:
                                method_name = f"{method}_{os.path.basename(file)}"
                                if method_name not in methods:
                                    methods[method_name] = []
                                methods[method_name].append(file)

                            # Find method usages
                            for method_name in methods:
                                method = method_name.split("_")[0]
                                usage_pattern = re.compile(
                                    r"\b" + re.escape(method) + r"\b"
                                )
                                if usage_pattern.search(content):
                                    if method_name not in method_usage_map:
                                        method_usage_map[method_name] = []
                                    method_usage_map[method_name].append(file)

                    except Exception as e:
                        # Log any errors that occur during file reading
                        self.logger.error(f"Failed to read file {file}: {str(e)}")

                dependency_map[project["name"]] = dependencies
                for method_name, files in methods.items():
                    if method_name not in method_usage_map:
                        method_usage_map[method_name] = []
                    method_usage_map[method_name].extend(files)

        except Exception as e:
            # Log any errors that occur during dependency mapping
            self.logger.error(f"Failed to map dependencies: {str(e)}")

        # Deduplicate method usage entries
        for method_name in method_usage_map:
            method_usage_map[method_name] = list(set(method_usage_map[method_name]))

        # Translate localhost dependencies to project names
        for project, dependencies in dependency_map.items():
            translated_dependencies = []
            for dependency in dependencies:
                if "localhost" in dependency:
                    match = self.localhost_pattern.search(dependency)
                    if match:
                        port = match.group(1)
                        if port in localhost_map:
                            translated_dependencies.append(localhost_map[port])
                        else:
                            translated_dependencies.append(dependency)
                    else:
                        translated_dependencies.append(dependency)
                else:
                    translated_dependencies.append(dependency)
            dependency_map[project] = translated_dependencies

        # Log domain references
        self.log_domain_references(domain_count)

        return dependency_map, method_usage_map

    def extract_domain(self, url):
        """
        Extracts the domain from a URL.

        Args:
            url (str): The URL to extract the domain from.

        Returns:
            str: The extracted domain or None if extraction fails.
        """
        try:
            parsed_url = urlparse(url)
            return parsed_url.netloc
        except Exception as e:
            self.logger.error(f"Failed to extract domain from URL {url}: {str(e)}")
            return None

    def get_root_domain(self, domain):
        """
        Extracts the root domain (last two components) from a full domain.

        Args:
            domain (str): The full domain.

        Returns:
            str: The root domain.
        """
        parts = domain.split(".")
        if len(parts) >= 2:
            return ".".join(parts[-2:])
        return domain

    def log_domain_references(self, domain_count):
        """
        Logs the domain references and their counts to a separate log file, sorted by root domain.

        Args:
            domain_count (dict): A dictionary with domains as keys and their counts as values.
        """
        log_file = os.path.join(self.base_path, "domain_references.log")
        sorted_domains = sorted(domain_count.items())
        with open(log_file, "w") as f:
            for domain, count in sorted_domains:
                f.write(f"{domain}: {count}\n")
        self.logger.info(f"Domain references logged to {log_file}")
