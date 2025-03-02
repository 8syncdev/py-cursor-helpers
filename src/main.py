#!/usr/bin/env python3
import os
import sys
import uuid
import json
import hashlib
import platform
import subprocess
import logging
import argparse
import signal
import time
from pathlib import Path
from typing import Dict, Optional, Any, Tuple

# Thiết lập logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
log = logging.getLogger(__name__)

# Biến toàn cục
VERSION = "1.0.0"
SET_READ_ONLY = False

class TextResource:
    def __init__(self, lang="vi"):
        self.lang = lang
        self.texts = {
            "vi": {
                "privilege_error": "Lỗi quyền truy cập",
                "run_with_sudo": "Vui lòng chạy với quyền sudo",
                "sudo_example": "Ví dụ: sudo python main.py",
                "run_as_admin": "Vui lòng chạy với quyền quản trị",
                "reading_config": "Đang đọc cấu hình...",
                "generating_ids": "Đang tạo ID mới...",
                "success_message": "Thành công! ID mới đã được tạo.",
                "restart_message": "Vui lòng khởi động lại Cursor để áp dụng thay đổi.",
                "press_enter_to_exit": "Nhấn Enter để thoát..."
            }
        }
    
    def get_text(self, key):
        return self.texts.get(self.lang, self.texts["vi"]).get(key, key)

class Generator:
    @staticmethod
    def generate_machine_id() -> str:
        data = os.urandom(32)
        hash_obj = hashlib.sha256()
        hash_obj.update(data)
        return hash_obj.hexdigest()
    
    @staticmethod
    def generate_mac_machine_id() -> str:
        return Generator.generate_machine_id()
    
    @staticmethod
    def generate_device_id() -> str:
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_sqm_id() -> str:
        return str(uuid.uuid4())

class ConfigManager:
    def __init__(self, username: str):
        self.username = username
        self.config_path = self._get_config_path()
        
    def _get_config_path(self) -> Path:
        system = platform.system()
        if system == "Windows":
            return Path(os.environ.get("APPDATA")) / "Cursor" / "User" / "globalStorage" / "storage.json"
        elif system == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage" / "storage.json"
        else:  # Linux
            return Path.home() / ".config" / "Cursor" / "User" / "globalStorage" / "storage.json"
    
    def read_config(self) -> Optional[Dict[str, Any]]:
        try:
            if not self.config_path.exists():
                log.warning(f"Không tìm thấy file cấu hình tại: {self.config_path}")
                return None
            
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            log.error(f"Lỗi khi đọc cấu hình: {e}")
            return None
    
    def save_config(self, config: Dict[str, Any], read_only: bool = False) -> bool:
        try:
            # Đảm bảo thư mục tồn tại
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Ghi cấu hình
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Đặt quyền chỉ đọc nếu cần
            if read_only:
                if platform.system() == "Windows":
                    os.system(f'attrib +R "{self.config_path}"')
                else:
                    os.chmod(self.config_path, 0o444)
            
            return True
        except Exception as e:
            log.error(f"Lỗi khi lưu cấu hình: {e}")
            return False

class ProcessManager:
    def __init__(self):
        self.system = platform.system()
    
    def kill_cursor_processes(self) -> bool:
        try:
            if self.system == "Windows":
                subprocess.run(["taskkill", "/F", "/IM", "Cursor.exe"], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif self.system == "Darwin":  # macOS
                subprocess.run(["pkill", "-f", "Cursor"], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:  # Linux
                subprocess.run(["pkill", "-f", "cursor"], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Đợi để đảm bảo tiến trình đã đóng
            time.sleep(1)
            return True
        except Exception as e:
            log.error(f"Lỗi khi đóng Cursor: {e}")
            return False
    
    def is_cursor_running(self) -> bool:
        try:
            if self.system == "Windows":
                output = subprocess.check_output(["tasklist", "/FI", "IMAGENAME eq Cursor.exe"])
                return b"Cursor.exe" in output
            else:  # macOS và Linux
                output = subprocess.run(["pgrep", "-f", "Cursor"], 
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return output.returncode == 0
        except Exception:
            return False

class Display:
    def __init__(self):
        self.system = platform.system()
    
    def clear_screen(self):
        if self.system == "Windows":
            os.system("cls")
        else:
            os.system("clear")
    
    def show_logo(self):
        logo = """
        ╔═══════════════════════════════════════════╗
        ║             PY CURSOR TOOLS               ║
        ║      Generate Machine & Device IDs        ║
        ╚═══════════════════════════════════════════╝
        """
        print(logo)
    
    def show_progress(self, message: str):
        print(f"{message}...", end="", flush=True)
    
    def stop_progress(self):
        print(" Hoàn thành!", flush=True)
    
    def show_error(self, message: str):
        print(f"\n[LỖI] {message}")
    
    def show_success(self, *messages):
        for msg in messages:
            print(f"\n[THÀNH CÔNG] {msg}")
    
    def show_info(self, message: str):
        print(f"\n[THÔNG TIN] {message}")
    
    def show_privilege_error(self, *messages):
        for msg in messages:
            print(f"\n[LỖI QUYỀN] {msg}")

def check_admin_privileges() -> Tuple[bool, Optional[Exception]]:
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0, None
        else:  # macOS và Linux
            return os.geteuid() == 0, None
    except Exception as e:
        return False, e

def self_elevate() -> bool:
    try:
        os.environ["AUTOMATED_MODE"] = "1"
        
        if platform.system() == "Windows":
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                script = sys.executable
                params = ' '.join([f'"{x}"' for x in sys.argv])
                ctypes.windll.shell32.ShellExecuteW(None, "runas", script, params, None, 1)
                return True
        else:  # macOS và Linux
            if os.geteuid() != 0:
                args = ['sudo', sys.executable] + sys.argv
                os.execvp('sudo', args)
                return True
        return False
    except Exception as e:
        log.error(f"Lỗi khi nâng cấp quyền: {e}")
        return False

def get_current_user() -> str:
    if "SUDO_USER" in os.environ:
        return os.environ["SUDO_USER"]
    
    try:
        import pwd
        return pwd.getpwuid(os.getuid()).pw_name
    except:
        return os.environ.get("USER", os.environ.get("USERNAME", "unknown"))

def wait_exit():
    input(text.get_text("press_enter_to_exit"))

def setup_error_recovery():
    def handle_exception(exc_type, exc_value, exc_traceback):
        log.error("Đã xảy ra lỗi không mong muốn", exc_info=(exc_type, exc_value, exc_traceback))
        wait_exit()
    
    sys.excepthook = handle_exception

def parse_arguments():
    global SET_READ_ONLY
    
    parser = argparse.ArgumentParser(description="Công cụ tạo ID cho Cursor")
    parser.add_argument("-r", "--read-only", action="store_true", help="đặt storage.json ở chế độ chỉ đọc")
    parser.add_argument("-v", "--version", action="store_true", help="hiển thị thông tin phiên bản")
    
    args = parser.parse_args()
    
    if args.version:
        print(f"Cursor ID Modifier v{VERSION}")
        sys.exit(0)
    
    SET_READ_ONLY = args.read_only

def main():
    setup_error_recovery()
    parse_arguments()
    
    username = get_current_user()
    log.debug(f"Đang chạy với người dùng: {username}")
    
    # Khởi tạo các thành phần
    display = Display()
    config_manager = ConfigManager(username)
    generator = Generator()
    process_manager = ProcessManager()
    
    # Kiểm tra và xử lý quyền
    is_admin, err = check_admin_privileges()
    if err:
        log.error(err)
        wait_exit()
        return
    
    if not is_admin:
        if platform.system() == "Windows":
            print("\nĐang yêu cầu quyền quản trị viên...")
            if not self_elevate():
                display.show_privilege_error(
                    text.get_text("privilege_error"),
                    text.get_text("run_as_admin"),
                    text.get_text("run_with_sudo"),
                    text.get_text("sudo_example")
                )
                wait_exit()
                return
        else:
            display.show_privilege_error(
                text.get_text("privilege_error"),
                text.get_text("run_with_sudo"),
                text.get_text("sudo_example")
            )
            wait_exit()
            return
    
    # Thiết lập hiển thị
    display.clear_screen()
    display.show_logo()
    print()
    
    # Xử lý tiến trình Cursor
    if os.environ.get("AUTOMATED_MODE") != "1":
        display.show_progress("Đang đóng Cursor")
        log.debug("Đang cố gắng đóng tiến trình Cursor")
        
        if not process_manager.kill_cursor_processes():
            display.stop_progress()
            display.show_error("Không thể đóng Cursor. Vui lòng đóng thủ công và thử lại.")
            wait_exit()
            return
        
        if process_manager.is_cursor_running():
            display.stop_progress()
            display.show_error("Không thể đóng Cursor hoàn toàn. Vui lòng đóng thủ công và thử lại.")
            wait_exit()
            return
        
        display.stop_progress()
        print()
    
    # Đọc cấu hình hiện tại
    print()
    display.show_progress(text.get_text("reading_config"))
    old_config = config_manager.read_config()
    display.stop_progress()
    print()
    
    # Tạo cấu hình mới
    display.show_progress(text.get_text("generating_ids"))
    new_config = {}
    
    try:
        new_config["telemetryMachineId"] = generator.generate_machine_id()
        new_config["telemetryMacMachineId"] = generator.generate_mac_machine_id()
        new_config["telemetryDevDeviceId"] = generator.generate_device_id()
        
        if old_config and "telemetrySqmId" in old_config:
            new_config["telemetrySqmId"] = old_config["telemetrySqmId"]
        else:
            new_config["telemetrySqmId"] = generator.generate_sqm_id()
    except Exception as e:
        log.error(f"Lỗi khi tạo ID: {e}")
        display.stop_progress()
        display.show_error(f"Không thể tạo ID: {e}")
        wait_exit()
        return
    
    display.stop_progress()
    print()
    
    # Lưu cấu hình
    display.show_progress("Đang lưu cấu hình")
    if not config_manager.save_config(new_config, SET_READ_ONLY):
        display.stop_progress()
        display.show_error("Không thể lưu cấu hình")
        wait_exit()
        return
    
    display.stop_progress()
    print()
    
    # Hiển thị thông báo hoàn thành
    display.show_success(
        text.get_text("success_message"),
        text.get_text("restart_message")
    )
    print()
    display.show_info("Hoàn tất thao tác!")
    
    if os.environ.get("AUTOMATED_MODE") != "1":
        wait_exit()

if __name__ == "__main__":
    # Khởi tạo tài nguyên văn bản
    text = TextResource()
    main()
