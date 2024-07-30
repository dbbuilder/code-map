import graphviz
import os


class DiagramGenerator:
    def __init__(self, logger):
        """
        Initializes the DiagramGenerator with a logger.

        Args:
            logger (logging.Logger): Logger instance for logging information.
        """
        self.logger = logger

    def generate_dot_file(self, dependency_map, shared_methods, output_file):
        """
        Generates a DOT file for visualizing dependencies and shared methods.

        Args:
            dependency_map (dict): Dictionary of project dependencies.
            shared_methods (dict): Dictionary of shared methods across projects.
            output_file (str): Path to the output DOT file.
        """
        try:
            dot = graphviz.Digraph(comment="Project Dependencies and Methods")

            # Add nodes for each project
            for project in dependency_map:
                dot.node(project, project)

            # Add edges for dependencies
            for project, dependencies in dependency_map.items():
                for dependency in dependencies:
                    dot.edge(project, dependency, label="uses")

            # Add edges for shared methods
            for method, files in shared_methods.items():
                method_node = f"method_{method}"
                dot.node(method_node, method, shape="box")
                for file in files:
                    project_name = self.extract_project_name(file)
                    dot.edge(project_name, method_node, label="has method")

            # Save the DOT file
            dot.save(output_file)
            self.logger.info(f"Dependency diagram saved to {output_file}")
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
