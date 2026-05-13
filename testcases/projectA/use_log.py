from testcases.projectA.log import Log

log = Log.get_logger()
log.error("This is a error message1")
log.info("This is a info message2")
log.warning("This is a warning message3")
