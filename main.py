import json
import os
import logging
from project_analyzer import ProjectAnalyzer
from dependency_mapper import DependencyMapper
from diagram_generator import DiagramGenerator
from custom_logger import setup_logger


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
    base_path = config["root_folder_path"]
    log_file = os.path.join(base_path, "project_analysis.log")
    output_dot_file_projects = os.path.join(base_path, "project_dependencies.dot")
    output_dot_file_all = os.path.join(base_path, "all_dependencies.dot")

    logger = setup_logger(log_file)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    try:
        root_folder_path = config["root_folder_path"]

        # Initialize ProjectAnalyzer and analyze projects
        analyzer = ProjectAnalyzer(logger)
        logger.info("Starting project analysis...")
        projects = analyzer.analyze_projects(root_folder_path)
        logger.info("Project analysis completed.")

        # Initialize DependencyMapper and map dependencies and methods
        mapper = DependencyMapper(logger, base_path)
        logger.info("Starting dependency mapping...")
        dependency_map, shared_methods = mapper.map_dependencies_and_methods(projects)
        logger.info("Dependency mapping completed.")

        # Generate project and external API dependencies diagram
        diagram_generator = DiagramGenerator(logger)
        logger.info(
            "Starting diagram generation for project and external API dependencies..."
        )
        diagram_generator.generate_dot_file(
            dependency_map,
            shared_methods,
            output_dot_file_projects,
            include_methods=False,
        )
        logger.info(
            "Diagram generation for project and external API dependencies completed."
        )

        # Generate full dependencies diagram including methods
        logger.info("Starting diagram generation for all dependencies...")
        diagram_generator.generate_dot_file(
            dependency_map, shared_methods, output_dot_file_all, include_methods=True
        )
        logger.info("Diagram generation for all dependencies completed.")

        # Print the results
        print(json.dumps(dependency_map, indent=4))
        print(json.dumps(shared_methods, indent=4))
        print(
            f"Project and external API dependency diagram saved to {output_dot_file_projects.replace('.dot', '.pdf')}"
        )
        print(
            f"Full dependency diagram saved to {output_dot_file_all.replace('.dot', '.pdf')}"
        )

    except Exception as e:
        # Log any exceptions that occur
        logger.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
