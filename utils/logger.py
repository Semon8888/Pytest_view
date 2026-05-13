# ===========日志配置项=============
import os
import sys

from loguru import logger

# 日志存放目录
LOG_PATH = os.path.join(os.path.dirname(__file__).split("utils")[0], "Logs")

# 日志格式，根据不同级别的日志显示不同颜色，底层颜色字典自动映射
LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss} | "
    "<level>{level: <8}</level> | "
    "from | " "{module} | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"  # 只需要加上这句，就实现了日志级别和颜色的自动匹配和输出
)
# 日志保留天数和切割时间适用于生成环境，测试环境需要每次运行清空旧日志(可选)
# 日志保留天数
LOG_RETENTION = "7 days"

# 日志切割时间，每天0点
LOG_ROTATION = "00:00"

# 日志文件编码(解决中文乱码)
LOG_ENCODING = "utf-8"

# 创建日志目录
os.makedirs(LOG_PATH, exist_ok=True)

# 指定运行日志和错误日志目录
RUNNER_LOG = LOG_PATH + "/running.log"
ERROR_ONLY_LOG = LOG_PATH + "/error_only.log"


# 每次运行清空日志文件，保证每次的日志都是最新的
def clear_old_logs():
    for file in [RUNNER_LOG, ERROR_ONLY_LOG]:
        with open(file, "w") as f:
            f.write("")


class LogUtil:
    """Loguru 日志工具类(通过单例模式，防止重复配置)"""
    _isinstance = None
    _initialized = False

    # 重写__new__方法，生成单例，全局只创建一个实力
    def __new__(cls, *args, **kwargs):
        if not cls._isinstance:
            cls._isinstance = super().__new__(cls)

        return cls._isinstance

    def __init__(self):
        if not self._initialized:
            self._setup_logger() # 如果类没有初始化，那就初始化一个logger
            clear_old_logs()

    @staticmethod
    def _setup_logger():
        """配置日志：控制台 + 文件输出"""
        # 移除默认处理器(handler)，防止重复打印
        logger.remove()

        # ==================== 1. 控制台输出（彩色） ====================
        logger.add(
            sink=sys.stdout,
            format=LOG_FORMAT,
            level="DEBUG",  # 控制台输出debug级别及以上的日志
        )

        # ==================== 2. 文件输出（普通日志） ==================
        logger.add(
            sink=LOG_PATH + "/running.log",
            format=LOG_FORMAT,
            level="INFO",
            encoding=LOG_ENCODING,
            rotation=LOG_ROTATION,
            retention=LOG_RETENTION,
            compression="zip",
        )
        # ==================== 3. 文件输出（错误日志单独存） =============
        logger.add(
            sink=LOG_PATH + "/error_only.log",
            format=LOG_FORMAT,
            level="ERROR",
            rotation=LOG_ROTATION,
            retention=LOG_RETENTION,
            compression="zip",
            colorize=False,
        )
        LogUtil._initialized = True

    @staticmethod
    def get_logger():
        """获取全局日志实例"""
        if not LogUtil._initialized: # 因为静态方法不会实例化类，所以配置的颜色显示不会生效，所以要在方法内部对类进行实例化
            LogUtil()
        return logger
