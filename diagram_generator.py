import graphviz
import os
import subprocess


class DiagramGenerator:
    def __init__(self, logger):
        """
        Initializes the DiagramGenerator with a logger.

        Args:
            logger (logging.Logger): Logger instance for logging information.
        """
        self.logger = logger

    def generate_dot_file(
        self, dependency_map, shared_methods, output_file, include_methods=True
    ):
        """
        Generates a DOT file for visualizing dependencies and shared methods.

        Args:
            dependency_map (dict): Dictionary of project dependencies.
            shared_methods (dict): Dictionary of shared methods across projects.
            output_file (str): Path to the output DOT file.
            include_methods (bool): Whether to include method dependencies in the DOT file.
        """
        try:
            dot = graphviz.Digraph(comment="Project Dependencies and Methods")

            # Add nodes for each project
            for project in dependency_map:
                self.logger.info(f"Adding node for project: {project}")
                dot.node(project, project)

            # Track added edges to prevent duplicates
            added_edges = set()

            # Add edges for dependencies
            for project, dependencies in dependency_map.items():
                for dependency in dependencies:
                    edge = (project, dependency)
                    if edge not in added_edges:
                        self.logger.info(f"Adding edge from {project} to {dependency}")
                        # Properly format URLs by quoting and escaping them
                        if dependency.startswith(("http://", "https://")):
                            formatted_dependency = dependency.replace(":", "\\:")
                            dot.edge(project, formatted_dependency, label="uses")
                        else:
                            dot.edge(project, dependency, label="uses")
                        added_edges.add(edge)

            # Add edges for shared methods if include_methods is True
            if include_methods:
                for method, files in shared_methods.items():
                    method_node = f"method_{method}"
                    self.logger.info(f"Adding method node: {method_node}")
                    dot.node(method_node, method, shape="box")
                    for file in files:
                        project_name = self.extract_project_name(file)
                        edge = (project_name, method_node)
                        if edge not in added_edges:
                            self.logger.info(
                                f"Adding edge from {project_name} to {method_node}"
                            )
                            dot.edge(project_name, method_node, label="has method")
                            added_edges.add(edge)

            # Save the DOT file
            dot.save(output_file)
            self.logger.info(f"Dependency diagram saved to {output_file}")

            # Render the DOT file to a PDF file using subprocess
            output_pdf = output_file.replace(".dot", ".pdf")
            self.logger.info(f"Rendering DOT file to PDF: {output_pdf}")
            self.render_dot_to_pdf(output_file, output_pdf)
            self.logger.info(f"Dependency diagram rendered to {output_pdf}")

        except Exception as e:
            self.logger.error(f"Failed to generate DOT file: {str(e)}")

    def extract_project_name(self, file_path):
        """
        Extracts the project name from the file path.

        Args:
            file_path (str): Path to the file.

        Returns:
            str: Name of the project.
        """
        try:
            parts = file_path.split(os.sep)
            return parts[-3]  # Adjust this based on your directory structure
        except Exception as e:
            self.logger.error(
                f"Failed to extract project name from {file_path}: {str(e)}"
            )
            return "unknown"

    def render_dot_to_pdf(self, dot_file, pdf_file):
        """
        Renders a DOT file to a PDF using the Graphviz dot command.

        Args:
            dot_file (str): Path to the DOT file.
            pdf_file (str): Path to the output PDF file.
        """
        try:
            command = ["dot", "-Tpdf", dot_file, "-o", pdf_file]
            self.logger.info(f"Running command: {' '.join(command)}")
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            self.logger.info(f"dot command output: {result.stdout}")
            if result.stderr:
                self.logger.error(f"dot command error: {result.stderr}")
        except subprocess.CalledProcessError as e:
            self.logger.error(
                f"Failed to render DOT file to PDF: {str(e)}, stderr: {e.stderr}"
            )
        except Exception as e:
            self.logger.error(f"Unexpected error during PDF rendering: {str(e)}")
