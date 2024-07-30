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
            re.compile(r'(import|require)\s+[\'"](.+?)[\'"]'),  # JavaScript import/require
            re.compile(r'<!--\s*#include\s*file\s*=\s*[\'"](.+?)[\'"]\s*-->'),  # HTML includes
            re.compile(r'(https?://[^\s\'"]+)'),  # API URLs (HTTP/HTTPS links)
            re.compile(r'<Compile Include="(.+?)"'),  # VBProj includes
            re.compile(r'<ProjectReference Include="(.+?)"')  # Project references in .vbproj and .sln
        ]
        self.method_pattern = re.compile(r'function\s+(\w+)\s*\(')  # JavaScript/VB method definitions
        self.localhost_pattern = re.compile(r'localhost:(\d+)')  # Localhost with port

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
                
                for file in project['files']:
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Find localhost endpoints
                            localhost_matches = self.localhost_pattern.findall(content)
                            for port in localhost_matches:
                                localhost_map[port] = project['name']
                            
                            # Find dependencies
                            for pattern in self.dependency_patterns:
                                matches = pattern.findall(content)
                                for match in matches:
                                    dependency = match[1] if isinstance(match, tuple) else match
                                    # Skip npmjs.org references
                                    if 'npmjs.org' in dependency:
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
                                if method not in methods:
                                    methods[method] = []
                                methods[method].append(file)
                            
                            # Find method usages
                            for method in methods:
                                usage_pattern = re.compile(r'\b' + re.escape(method) + r'\b')
                                if usage_pattern.search(content):
                                    if method not in method_usage_map:
                                        method_usage_map[method] = []
                                    method_usage_map[method].append(file)
                    
                    except Exception as e:
                        # Log any errors that occur during file reading
                        self.logger.error(f"Failed to read file {file}: {str(e)}")
                
                dependency_map[project['name']] = dependencies
                for method, files in methods.items():
                    if method not in method_usage_map:
                        method_usage_map[method] = []
                    method_usage_map[method].extend(files)
        
        except Exception as e:
            # Log any errors that occur during dependency mapping
            self.logger.error(f"Failed to map dependencies: {str(e)}")
        
        # Deduplicate method usage entries
        for method in method_usage_map:
            method_usage_map[method] = list(set(method_usage_map[method]))
        
        # Translate localhost dependencies to project names
        for project, dependencies in dependency_map.items():
            translated_dependencies = []
            for dependency in dependencies:
                if 'localhost' in dependency:
                    match = self.localhost_pattern.search(dependency)
                    if match:
                        port = match.group(1)
                        if port in localhost_map:
                            translated_dependencies.append(localhost_map[port])
                        else:
                            translated_dependencies.append(dependency)
                    else:
          
