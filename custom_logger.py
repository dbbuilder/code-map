import logging


def setup_logger(log_file):
    """
    Sets up a logger for the project analysis.

    Args:
        log_file (str): Path to the log file.

    Returns:
        logging.Logger: Configured logger.
    """
    try:
        logger = logging.getLogger("project_analyzer")
        logger.setLevel(logging.DEBUG)

        # File handler for logging to a file
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)

        # Stream handler for logging to the console
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)

        # Formatting the logs
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # Adding handlers to the logger
        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger
    except Exception as e:
        print(f"Failed to setup logger: {str(e)}")
        raise
