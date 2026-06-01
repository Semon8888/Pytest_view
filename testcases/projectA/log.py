# 1、新建一个类，并使用单例初始化，保证使用时都是用同一个类，没有多占用内存
# 2、类中创建一个是否初始化的类变量，默认赋值为False,根据此变量去判断是否需要初始化
# 3、新建一个类方法，用来装饰日志输出
# 4、新建一个对外的静态方法，用来调用日志输出
import sys

from loguru import logger

LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss} | "
    "<level>{level: <8}</level> | "
    "from | " "{module} | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"  # 只需要加上这句，就实现了日志级别和颜色的自动匹配和输出
)


class Log:
    _isinstance = None
    _initialized = False

    # 重写new方法，构造单例模式
    def __new__(cls, *args, **kwargs):
        if not cls._isinstance:
            cls._isinstance = super().__new__(cls, *args, **kwargs)
        return cls._isinstance

    def __init__(self, *args, **kwargs):
        if not self._initialized:
            self._set_logger()

    @staticmethod
    def _set_logger():
        logger.remove()
        logger.add(
            sink=sys.stdout,
            format=LOG_FORMAT
        )
        Log._initialized = True

    @staticmethod
    def get_logger():
        if not Log._initialized:
            Log()
        return logger
