import logging

def setup_logger():
    logging.basicConfig(filename='log/recent.log', 
                        encoding='utf-8', 
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(message)s')
    return logging.getLogger(__name__)
