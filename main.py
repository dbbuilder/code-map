import json
import os
from project_analyzer import ProjectAnalyzer
from dependency_mapper import DependencyMapper
from diagram_generator import DiagramGenerator
from logger import setup_logger


def load_config():
    """
    Loads the configuration from config.json file.

    Returns:
        dict: Configuration dictionary.
    """
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger = setup_logger("error.log")
        logger.error(f"Failed to load configuration: {str(e)}")
        raise


def main():
    """
    Main function to perform project analysis, dependency mapping, and diagram generation.
    """
    # Load configuration
    config = load_config()

    # Setup logger
    logger = setup_logger(config["log_file"])

    try:
        root_folder_path = config["root_folder_path"]
        output_dot_file = config.get("output_dot_file", "project_dependencies.dot")

        # Initialize ProjectAnalyzer and analyze projects
        analyzer = ProjectAnalyzer(logger)
        projects = analyzer.analyze_projects(root_folder_path)

        # Initialize DependencyMapper and map dependencies and methods
        mapper = DependencyMapper(logger)
        dependency_map, shared_methods = mapper.map_dependencies_and_methods(projects)

        # Generate diagram
        diagram_generator = DiagramGenerator(logger)
        diagram_generator.generate_dot_file(
            dependency_map, shared_methods, output_dot_file
        )

        # Print the results
        print(json.dumps(dependency_map, indent=4))
        print(json.dumps(shared_methods, indent=4))
        print(f"Dependency diagram saved to {output_dot_file}")

    except Exception as e:
        # Log any exceptions that occur
        logger.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
