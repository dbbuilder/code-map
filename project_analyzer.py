import os


class ProjectAnalyzer:
    def __init__(self, logger):
        """
        Initializes the ProjectAnalyzer with a logger.

        Args:
            logger (logging.Logger): Logger instance for logging information.
        """
        self.logger = logger

    def analyze_projects(self, root_folder_path):
        """
        Analyzes the projects in the specified root folder path.

        Args:
            root_folder_path (str): Path to the root folder containing projects.

        Returns:
            list: List of dictionaries containing project names and file paths.
        """
        projects = []
        try:
            # Iterate through each directory in the root folder
            for directory in os.listdir(root_folder_path):
                dir_path = os.path.join(root_folder_path, directory)
                if os.path.isdir(dir_path):
                    self.logger.info(f"Analyzing project: {directory}")
                    project = {"name": directory, "files": []}
                    # Recursively gather all relevant files in the project directory
                    for root, _, files in os.walk(dir_path):
                        for file in files:
                            if file.endswith(
                                (
                                    ".vbproj",
                                    ".js",
                                    ".resx",
                                    ".json",
                                    ".sln",
                                    ".asax",
                                    ".aspx",
                                    ".vb",
                                    ".vue",
                                    ".html",
                                )
                            ):
                                project["files"].append(os.path.join(root, file))
                    projects.append(project)
        except Exception as e:
            # Log any errors that occur during project analysis
            self.logger.error(f"Failed to analyze projects: {str(e)}")
        return projects
