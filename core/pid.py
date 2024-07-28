import psutil
import subprocess
from core.util import ensure_admin
from core.config import config_instance as config
import time
from loguru import logger


def find_process_by_name(process_name: str = config.exec_name) -> psutil.Process:
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"] == process_name:
            logger.debug(f"process {process_name} finded. PID: {proc.pid}")
            return proc
    raise Exception(f"Process with name [{process_name}] not found. ")


def reconn_process_network_by_proc(proc: psutil.Process):
    ensure_admin()
    new_rule_name = config.new_rule_name
    try:
        command = f'netsh advfirewall firewall add rule name="{new_rule_name}" dir=out action=block program="{proc.exe()}"'
        subprocess.run(command, shell=True, check=True)
        logger.info(f"Process {proc.info['name']} network connection blocked.")

        time.sleep(config.sleep_interval)

        # delete rule from firewall
        unblock_command = (
            f'netsh advfirewall firewall delete rule name="{new_rule_name}"'
        )
        subprocess.run(unblock_command, shell=True, check=True)
        logger.info(f"Process {proc.info['name']} network connection unblocked.")

    except Exception as e:
        logger.error(f"Error occured {e}")
