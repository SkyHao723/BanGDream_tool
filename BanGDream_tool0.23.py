import os
import sys
import json
import shutil
import random
import logging
import threading
import subprocess
from pathlib import Path
from PIL import Image
from PIL import ImageTk
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from tkinter import font
from tkinter import simpledialog
from tkinter import scrolledtext
import requests
import psutil
import re
import time
import webbrowser
import ctypes
import sv_ttk
from datetime import datetime
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import platform
import math
import time

# 高DPI支持
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except (AttributeError, OSError):
    pass



# 角色ID到名称映射
character_id_to_name = {
    1: "户山香澄", 2: "花园多惠", 3: "牛込里美", 4: "山吹沙绫", 5: "市谷有咲",
    6: "美竹兰", 7: "青叶摩卡", 8: "上原绯玛丽", 9: "宇田川巴", 10: "羽泽鸫",
    11: "弦卷心", 12: "濑田薰", 13: "北泽育美", 14: "松原花音", 15: "米歇尔",
    16: "丸山彩", 17: "冰川日菜", 18: "白鹭千圣", 19: "大和麻弥", 20: "若宫伊芙",
    21: "凑友希那", 22: "冰川纱夜", 23: "今井莉莎", 24: "宇田川亚子", 25: "白金燐子",
    26: "仓田真白", 27: "桐谷透子", 28: "广町七深", 29: "二叶筑紫", 30: "八潮瑠唯",
    31: "和奏瑞依LAYER", 32: "朝日六花LOCK", 33: "佐藤益木MASKING",
    34: "鳰原令王那PAREO", 35: "珠手知由CHU²",
    36: "高松灯", 37: "千早爱音", 38: "要乐奈", 39: "長崎爽世", 40: "椎名立希"
}

# 角色外号和简称映射（请在此处填写，每个角色名对应一个list）
CHARACTER_ALIASES = {
    "户山香澄": ['ppp','PoppinParty','戸山香澄','とやまかすみ','Toyama Kasumi','ksm','cdd','爱美','猫耳','主唱','吉他手'],
    "花园多惠": ['ppp','PoppinParty','花園（はなぞの）たえ','Hanazono Tae','大冢纱英','otae','tea','吉他手','兔子'],
    "牛込里美": ['ppp','PoppinParty','牛込（うしごめ）りみ','Ushigome Rimi','西本里美','りみりん','李美丽','贝斯手','巧克力螺'],
    "山吹沙绫": ['ppp','PoppinParty','山吹（やまぶき） 沙綾（さあや）','大桥彩香','Yamabuki Saya','面包','鼓手','妈'],
    "市谷有咲": ['ppp','PoppinParty','市ヶ谷（いちがや） 有咲（ありさ）','伊藤彩沙','Ichigaya Arisa','ars','傲娇','键盘手'],
    "美竹兰": ['ag','Afterglow','夕阳红','美竹（みたけ） 蘭（らん)','Mitake Ran','佐仓绫音','没煮烂','挑染','主唱','吉他手'],
    "青叶摩卡": ['ag','Afterglow','夕阳红','青葉（あおば） モカ','Aoba Moka','吉他手','三泽纱千香','毛力'],
    "上原绯玛丽": ['ag','Afterglow','夕阳红','上原（うえはら） ひまり','Uehara Himari','hmr','一呼零应','肥玛丽','贝斯手','加藤英美里','Ei!Ei!Oh!'],
    "宇田川巴": ['ag','Afterglow','夕阳红','宇田川（うだがわ） 巴（ともえ)','Udagawa Tomoe','soiya','鼓手','日笠阳子'],
    "羽泽鸫": ['ag','Afterglow','夕阳红', '羽沢（はざわ） つぐみ','Hazawa Tsugumi','つぐ tsugu','茨菇','ycm','键盘手','金元寿子'],
    "弦卷心": ['Hello, Happy World!','hhw','弦巻（つるまき） こころ','Tsurumaki Kokoro','kkr','主唱','伊藤美来'],
    "濑田薰": ['Hello, Happy World!','hhw','瀬田（せた） 薫かおる','Seta Kaoru','哈卡奈','儚い','田所梓','吉他手'],
    "北泽育美": ['Hello, Happy World!','hhw','北沢（きたざわ） はぐみ','Kitazawa Hagumi','hgm','贝斯手','吉田有里'],
    "松原花音": ['Hello, Happy World!','hhw','松原（まつばら） 花音（かのん）','Matsubara Kanon','迷宫水母','呼诶诶~','鼓手','丰田萌绘'],
    "米歇尔": ['Hello, Happy World!','hhw','奥沢（おくさわ） 美咲（みさき）','奥泽美咲','Okusawa Misaki','ミッシェル','msk','mask','DJ','黑泽朋世'],
    "丸山彩": ['Pastel*Palettes','pp','丸山（まるやま） 彩（あや)','Maruyama Aya','主唱','前岛亚美','劈瓦','修车'],
    "冰川日菜": ['Pastel*Palettes','pp','氷川（ひかわ） 日菜（ひな)','Hikawa Hina','彩黑头子','噜','吉他手','小泽亚李','947'],
    "白鹭千圣": ['Pastel*Palettes','pp','白鷺（しらさぎ） 千聖（ちさと）','Shirasagi Chisato','cst','贝斯手','上坂堇','腹黑'],
    "大和麻弥": ['Pastel*Palettes','pp','呼嘿嘿','大和（やまと） 麻弥（まや','Yamato Maya','12321','鼓手','中上育实'],
    "若宫伊芙": ['Pastel*Palettes','pp','若宮（わかみや） イヴ','Wakamiya Eve','武士道','键盘手','秦佐和子','eve'],
    "凑友希那": ['Roselia','r组','湊（みなと） 友希那（ゆきな)','Minato Yukina','ykn','主唱','相羽爱奈','摔角手','企鹅'],
    "冰川纱夜": ['Roselia','r组','氷川（ひかわ） 紗夜（さよ','薯条妹','打火机','吉他手','工藤晴香','Hikawa Sayo'],
    "今井莉莎": ['Roselia','r组','今井（いまい） リサ','Imai Lisa','贝斯手','远藤祐里香','中岛由贵'],
    "宇田川亚子": ['Roselia','r组','宇田川（うだがわ） あこ','Udagawa Ako','引起黑暗波动略黑的堕天使','暗之大魔姬','黑暗的统治者','樱川惠','鼓手'],
    "白金燐子": ['Roselia','r组','白金（しろかね） 燐子（りんこ）','Shirokane Rinko','燐燐','RinRin','键盘','明坂聪美','志崎桦音'],
    "仓田真白": ['Morfonica','Monica','蝶团','倉田（くらた） ましろ','八岐大蛇','Kurata Mashiro','小白','msr','进藤天音','主唱'],
    "桐谷透子": ['Morfonica','Monica','蝶团','桐ヶ谷（きりがや） 透子（とうこ）','Kirigaya Tōko','TOKO','直田姬奈','吉他手'],
    "广町七深": ['Morfonica','Monica','蝶团','広町（ひろまち） 七深（ななみ）','Hiromachi Nanami','西尾夕香','贝斯手','猫嘴'],
    "二叶筑紫": ['Morfonica','Monica','蝶团','二葉（ふたば） つくし','Futaba Tsukushi','二叶土笔','二爷柱子','mika','鼓手'],
    "八潮瑠唯": ['Morfonica','Monica','蝶团','八潮（やしお） 瑠唯（るい)','Yashio Rui','600W','小提琴','Ayasa'],
    "和奏瑞依LAYER": ['RAISE A SUILEN','ras','和奏（わかな） レイ','Wakana Rei','レイヤ','大姐头','Raychell','主唱','贝斯手'],
    "朝日六花LOCK": ['RAISE A SUILEN','ras','朝日（あさひ） 六花（ろっか）','Asahi Rokka','ロック','ROCK','吉他手','小原莉子'],
    "佐藤益木MASKING": ['RAISE A SUILEN','ras','佐藤（さとう） ますき','Satō Masuki','狂犬','鼓手','夏芽','マスキング','キング'],
    "鳰原令王那PAREO": ['RAISE A SUILEN','ras','鳰原（にゅうばら） 令王那（れおな)','パレオ','暗黑丸山彩','键盘手','仓知玲凤'],
    "珠手知由CHU²": ['RAISE A SUILEN','ras','珠手（たまで） ちゆ','Tamade Chiyu','チュチュ','CHU平方','楚萍芳','他妈的吃鱼','DJ','纺木吏佐','牙白'],
    "高松灯": ['MyGO!!!!!','我去','高松（たかまつ） 燈（ともり）','Takamatsu Tomori','ともりん','偷摸零','主唱','羊宫妃那'],
    "千早爱音": ['MyGO!!!!!','我去','千早（ちはや） 愛音（あのん）','Chihaya Anon','Ann','吉他手','立石凛'],
    "要乐奈": ['MyGO!!!!!','我去','要（かなめ） 楽奈（らーな）','Kaname Rāna','猫','异色瞳','吉他','青木阳菜'],
    "長崎爽世": ['MyGO!!!!!','我去','長崎（ながさき） そよ','Nagasaki Soyo','一ノ瀬（いちのせ） そよ','Ichinose Soyo','长崎素世','Soyorin','そよりん','长期素食','贝斯手','小日向美香'],
    "椎名立希": ['MyGO!!!!!','我去','椎名（しいな） 立希（たき）','Shiina Taki','りっきー','Rikki','鼓手','林鼓子'],
}


# 角色ID到乐队映射
def get_band_name(character_id):
    if 1 <= character_id <= 5:
        return "Poppin'Party"
    elif 6 <= character_id <= 10:
        return "Afterglow"
    elif 11 <= character_id <= 15:
        return "Hello, Happy World!"
    elif 16 <= character_id <= 20:
        return "Pastel_Palettes"
    elif 21 <= character_id <= 25:
        return "Roselia"
    elif 26 <= character_id <= 30:
        return "Morfonica"
    elif 31 <= character_id <= 35:
        return "RAISE_A_SUILEN"
    elif 36 <= character_id <= 40:
        return "MyGO!!!!!"
    return "未知乐队"


def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '_', name)


# 支持的图片扩展名
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.webp')

# 配置文件路径
CONFIG_FILE = "bangdream_tool_config.json"

# 卡面信息API URL
CARDS_API_URL = "https://bestdori.com/api/cards/all.5.json"

SERVERS = ["jp", "en", "tw", "cn", "kr"]
SERVER_NAMES = {
    "jp": "日服",
    "en": "国际服",
    "tw": "繁中服",
    "cn": "简中服",
    "kr": "韩服"
}

# 卡面类型
CARD_TYPES = [
    "initial", "permanent", "event", "campaign",
    "limited", "dreamfes", "kirafes", "birthday",
    "others", "special"
]

TYPE_NAMES = {
    "initial": "初始",
    "permanent": "无期限",
    "event": "活动",
    "campaign": "联名合作",
    "limited": "期间限定",
    "dreamfes": "梦限",
    "kirafes": "闪限",
    "birthday": "生日",
    "others": "其他",
    "special": "特殊"
}


IMAGE_TYPE_MAP = {
    "card_normal": "cn",
    "card_after_training": "ca",
    "trim_normal": "tn",
    "trim_after_training": "ta"
}
# 超分模型简写映射
MODEL_NAME_MAP = {
    # Real-ESRGAN
    "realesrgan-x4plus-anime": "realesrgan-x4-anime",
    "realesrgan-x4plus": "realesrgan-x4",
    "realesr-animevideov3-x2": "realesr-x2",
    "realesr-animevideov3-x3": "realesr-x3",
    "realesr-animevideov3-x4": "realesr-x4",
    
    # waifu2x
    "noise0_model": "waifu-n0",
    "noise0_scale2.0x_model": "waifu-n0-x2",
    "noise1_model": "waifu-n1",
    "noise1_scale2.0x_model": "waifu-n1-x2",
    "noise2_model": "waifu-n2",
    "noise2_scale2.0x_model": "waifu-n2-x2",
    "noise3_model": "waifu-n3",
    "noise3_scale2.0x_model": "waifu-n3-x2",
    "scale2.0x_model": "waifu-x2"
}


# 自定义日志记录器
class DownloadLogger:
    def __init__(self):
        self.success_logger = self.setup_logger("download_success.log")
        self.failure_logger = self.setup_logger("download_failure.log")
        self.skip_logger = self.setup_logger("download_skip.log")
        self.cleanup_old_logs()

    def setup_logger(self, filename):
        logger = logging.getLogger(filename)
        logger.setLevel(logging.INFO)

        # 创建文件处理器并设置格式
        file_handler = logging.FileHandler(filename, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(formatter)

        # 确保只有一个处理器
        if not logger.handlers:
            logger.addHandler(file_handler)

        # 防止日志传播到根日志记录器
        logger.propagate = False
        return logger

    

    def log_success(self, card_id, url, server):
        self.success_logger.info(f"成功下载 - 卡面ID: {card_id}, 服务器: {server}, URL: {url}")

    def log_failure(self, card_id, url, error, server):
        self.failure_logger.error(f"下载失败 - 卡面ID: {card_id}, 服务器: {server}, URL: {url}, 错误: {error}")

    def log_skip(self, card_id, url, reason, server=None):
        server_info = f", 服务器: {server}" if server else ""
        self.skip_logger.info(f"跳过下载 - 卡面ID: {card_id}{server_info}, URL: {url}, 原因: {reason}")

    def cleanup_old_logs(self, force_cleanup=False):
        """清理日志文件中过旧的条目（超过2天）
        
        Args:
            force_cleanup (bool): 是否强制清理，忽略时间检查
        """
        try:
            now = datetime.now()
            log_files = ["download_success.log", "download_failure.log", "download_skip.log"]
            
            print(f"开始清理旧日志条目，当前时间: {now}")
            if force_cleanup:
                print("强制清理模式：将删除所有日志文件")
                for log_file in log_files:
                    if os.path.exists(log_file):
                        try:
                            os.remove(log_file)
                            print(f"已删除日志文件: {log_file}")
                        except Exception as e:
                            print(f"删除日志文件失败: {log_file}, 错误: {str(e)}")
                return
            
            total_removed_lines = 0
            for log_file in log_files:
                if not os.path.exists(log_file):
                    print(f"文件不存在: {log_file}")
                    continue
                
                print(f"处理日志文件: {log_file}")
                try:
                    # 读取所有行
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    if not lines:
                        print(f"  文件为空: {log_file}")
                        continue
                    
                    # 过滤出需要保留的行
                    kept_lines = []
                    removed_count = 0
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # 尝试解析时间戳
                        try:
                            # 时间戳格式: 2025-07-21 19:25:19,057
                            timestamp_str = line[:23]  # 取前23个字符作为时间戳
                            log_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                            
                            # 计算时间差
                            time_diff = now - log_time
                            days_diff = time_diff.days
                            
                            # 保留2天内的日志条目
                            if days_diff <= 2:
                                kept_lines.append(line)
                            else:
                                removed_count += 1
                                
                        except (ValueError, IndexError) as e:
                            # 如果无法解析时间戳，保留该行
                            print(f"  警告: 无法解析时间戳的行: {line[:50]}...")
                            kept_lines.append(line)
                    
                    # 写回文件
                    with open(log_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(kept_lines))
                        if kept_lines:  # 如果还有内容，添加换行符
                            f.write('\n')
                    
                    print(f"  处理完成: 保留 {len(kept_lines)} 行，删除 {removed_count} 行")
                    total_removed_lines += removed_count
                    
                except Exception as e:
                    print(f"  处理文件 {log_file} 时发生错误: {str(e)}")
            
            print(f"清理完成，共删除 {total_removed_lines} 行旧日志条目")
                    
        except Exception as e:
            print(f"清理旧日志文件时发生错误: {str(e)}")


class BangDreamTool(tk.Tk):

    def __init__(self):
        super().__init__()
        sv_ttk.use_light_theme()
        self.load_result_images()
        
        # 超分引擎和模型设置（需要在创建StringVar之前定义）
        self.upscale_engine = "Real-ESRGAN"  # 默认引擎
        self.realesrgan_model = "realesrgan-x4plus-anime"  # 默认Real-ESRGAN模型
        self.waifu2x_model_dir = "models-upconv_7_anime_style_art_rgb"  # 默认waifu2x模型目录
        self.waifu2x_model_anime = "noise3_scale2.0x_model"  # 默认anime模型
        self.waifu2x_model_photo = "noise3_scale2.0x_model"  # 默认photo模型
        self.waifu2x_model_cunet = "noise3_scale2.0x_model"  # 默认cunet模型
        self.realesrgan_threads = "1:2:2"  # 默认Real-ESRGAN线程配置
        self.waifu2x_threads = "1:2:2"  # 默认waifu2x线程配置
        self.realesrgan_normal_format = "jpg"  # 默认Real-ESRGAN普通卡面输出格式
        self.realesrgan_trim_format = "png"  # 默认Real-ESRGAN无背景卡面输出格式
        self.waifu2x_normal_format = "jpg"  # 默认waifu2x普通卡面输出格式
        self.waifu2x_trim_format = "png"  # 默认waifu2x无背景卡面输出格式
        
        self.upscale_engine_var = tk.StringVar(value=self.upscale_engine)

        self.title("BanG Dream! 卡面工具")
        self.geometry("1680x1020")
        self.minsize(800, 600)
        self.configure(bg="#f0f0f0")

        # 设置图标
        app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        try:
            icon_path = os.path.join(app_dir, "app.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except:
            pass

        # 设置默认路径为程序目录下的BangDream文件夹
        self.bangdream_dir = os.path.join(app_dir, "BangDream")
        # RealESRGAN路径固定为程序目录下的realesrgan-ncnn-vulkan
        self.realesrgan_dir = os.path.join(app_dir, "realesrgan-ncnn-vulkan")
        self.card_info = {}
        self.last_fetch_time = None
        self.download_logger = DownloadLogger()  # 初始化下载日志记录器

        # 筛选状态
        self.rarity_vars = {r: tk.BooleanVar(value=True) for r in range(1, 6)}
        self.attribute_vars = {a: tk.BooleanVar(value=True) for a in ["cool", "powerful", "pure", "happy"]}
        self.type_vars = {t: tk.BooleanVar(value=True) for t in CARD_TYPES}

        # 超分格式选择
        self.normal_format_var = tk.StringVar(value="jpg")  # 默认JPG
        self.trim_format_var = tk.StringVar(value="png")  # 默认PNG
        
        
        self.realesrgan_model_var = tk.StringVar(value=self.realesrgan_model)
        self.waifu2x_exe = "waifu2x-ncnn-vulkan\\waifu2x-ncnn-vulkan.exe"  # 添加默认路径
        
        # 下载线程数设置
        self.download_threads = 16

        # waifu2x设置默认值
        self.waifu2x_exe = "waifu2x-ncnn-vulkan\\waifu2x-ncnn-vulkan.exe"  # 默认路径

        # 选择的图片
        self.selected_normal_images = {}
        self.selected_trim_images = {}
        self.selected_counts = {}

        # 下载控制变量
        self.pause_download = False
        self.download_canceled = False
        self.timeout_count = 0
        self.last_timeout_time = 0
        self.download_lock = threading.Lock()  # 用于同步超时计数
        self.failed_downloads = []  # 存储失败的下载记录
        self.total_cards = 0  # 总卡面数量
        self.download_in_progress = False  # 下载进行中标志
        self.upscale_process = None  # 存储超分进程
        self.upscale_canceled = False  # 超分取消标志

        # 加载配置
        self.load_config()
        self.ensure_directories()
        self.clean_realesrgan_temp()

        # 确保必要的目录存在
        self.ensure_directories()

        # 清理RealESRGAN临时文件夹
        self.clean_realesrgan_temp()

        # 状态栏 - 提前创建
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(
            self,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 创建主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        style = ttk.Style()

        self.setup_fonts()

        style = ttk.Style()
        style.configure("Big.TRadiobutton", font=("微软雅黑", 11))

        # 设置样式
        self.setup_styles()

        # 创建标签页
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 设置标签页
        self.setup_tab = ttk.Frame(self.notebook)
        self.download_tab = ttk.Frame(self.notebook)
        self.single_download_tab = ttk.Frame(self.notebook)
        self.upscale_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.setup_tab, text="设置")
        self.notebook.add(self.download_tab, text="批量下载")
        self.notebook.add(self.single_download_tab, text="清单下载")
        self.notebook.add(self.upscale_tab, text="卡面超分")

        # 初始化各个标签页
        self.setup_setup_tab()
        self.setup_download_tab()
        self.setup_single_download_tab()
        self.setup_upscale_tab()

        # 加载卡面信息（如果存在）
        self.load_card_info()

    def setup_fonts(self):
        # 统一全局字体
        default_font = ("微软雅黑", 11)
        self.option_add("*Font", default_font)
        self.option_add("*TCombobox*Listbox.font", default_font)
        self.option_add("*TButton.font", default_font)
        self.option_add("*TLabel.font", default_font)
        self.option_add("*TEntry.font", default_font)
        self.option_add("*TRadiobutton.font", default_font)
        self.option_add("*TCheckbutton.font", default_font)
        self.option_add("*Message.font", default_font)
        self.option_add("*Text.font", default_font)
        self.option_add("*Listbox.font", default_font)
        self.option_add("*Menu.font", default_font)
        self.option_add("*Menubutton.font", default_font)
        self.option_add("*Labelframe.font", default_font)
        self.option_add("*TMenubutton.font", default_font)
        self.option_add("*TNotebook.Tab.font", default_font)
        self.option_add("*TNotebook.font", default_font)
        self.option_add("*Treeview.font", default_font)
        self.option_add("*Treeview.Heading.font", default_font)
        self.option_add("*TScrollbar.font", default_font)
        self.option_add("*TProgressbar.font", default_font)
        self.option_add("*TSpinbox.font", default_font)
        self.option_add("*TScale.font", default_font)
        self.option_add("*TSeparator.font", default_font)
        self.option_add("*TSizegrip.font", default_font)
        self.option_add("*TFrame.font", default_font)
        self.option_add("*Toplevel.font", default_font)
        self.option_add("*TCombobox.font", default_font)
        self.option_add("*TEntry.font", default_font)
        self.option_add("*TLabelFrame.font", default_font)
        self.option_add("*TCheckbutton.font", default_font)
        self.option_add("*TButton.font", default_font)
        self.option_add("*TLabel.font", default_font)
        self.option_add("*TRadiobutton.font", default_font)
        self.option_add("*TNotebook.Tab.font", default_font)
        self.option_add("*TNotebook.font", default_font)
        self.option_add("*Treeview.font", default_font)
        self.option_add("*Treeview.Heading.font", default_font)
        self.option_add("*TScrollbar.font", default_font)
        self.option_add("*TProgressbar.font", default_font)
        self.option_add("*TSpinbox.font", default_font)
        self.option_add("*TScale.font", default_font)
        self.option_add("*TSeparator.font", default_font)
        self.option_add("*TSizegrip.font", default_font)
        self.option_add("*TFrame.font", default_font)
        self.option_add("*Toplevel.font", default_font)
        self.option_add("*TCombobox.font", default_font)
        self.option_add("*TEntry.font", default_font)
        self.option_add("*TLabelFrame.font", default_font)
        self.option_add("*TCheckbutton.font", default_font)
        self.option_add("*TButton.font", default_font)
        self.option_add("*TLabel.font", default_font)
        self.option_add("*TRadiobutton.font", default_font)

    def setup_styles(self):
        """设置自定义样式"""
        style = ttk.Style()

        style.configure("Custom.Horizontal.TProgressbar", thickness=50)

        

        # 按钮样式
        style.configure("TButton", font=("微软雅黑", 11), padding=(10, 2))
        style.map("TButton",
                  foreground=[("active", "blue"), ("pressed", "darkblue")],
                  background=[("active", "#e0e0e0")])


        # 框架样式
        style.configure("TLabelframe", padding=10)
        style.configure("TLabelframe.Label", font=("微软雅黑", 10))

        

        style.configure("TNotebook.Tab", font=("微软雅黑", 10))

    def load_result_images(self):
        """加载结果图片资源"""
        self.result_images = {
            "happy": [],
            "sad": [],
            "normal": []
        }

        # 获取程序所在目录
        app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        pico_dir = os.path.join(app_dir, "assets", "pico")

        target_width = 240
        target_height = 300

        # happy
        for i in range(1, 6):
            img_path = os.path.join(pico_dir, f"happy{i}.png")
            if os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    # 保持原始比例进行缩放
                    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    self.result_images["happy"].append(ImageTk.PhotoImage(img))
                except Exception as e:
                    logging.error(f"加载happy{i}.png失败: {str(e)}")

        # 加载sad图片
        for i in range(1, 6):
            img_path = os.path.join(pico_dir, f"sad{i}.png")
            if os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    # 保持原始比例进行缩放
                    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    self.result_images["sad"].append(ImageTk.PhotoImage(img))
                except Exception as e:
                    logging.error(f"加载sad{i}.png失败: {str(e)}")

        # 加载normal图片
        for i in range(1, 6):
            img_path = os.path.join(pico_dir, f"normal{i}.png")
            if os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    # 保持原始比例进行缩放
                    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    self.result_images["normal"].append(ImageTk.PhotoImage(img))
                except Exception as e:
                    logging.error(f"加载normal{i}.png失败: {str(e)}")

    def get_char_dir(self, band_name, char_name):
        """获取角色目录路径"""
        safe_band = sanitize_filename(band_name)
        safe_char = sanitize_filename(char_name)
        return os.path.join(self.bangdream_dir, safe_band, safe_char)

    def get_card_dir(self, char_dir):
        """获取卡面目录路径"""
        return os.path.join(char_dir, "卡面")

    def get_trim_dir(self, char_dir):
        """获取无背景卡面目录路径"""
        return os.path.join(char_dir, "无背景卡面")

    def get_upscaled_card_dir(self, char_dir):
        """获取已超分卡面目录路径"""
        return os.path.join(char_dir, "卡面_已超分")

    def get_upscaled_trim_dir(self, char_dir):
        """获取已超分无背景卡面目录路径"""
        return os.path.join(char_dir, "无背景卡面_已超分")

    def clean_realesrgan_temp(self):
        """清理RealESRGAN临时文件夹"""
        input_dir = os.path.join(self.realesrgan_dir, "input")
        output_dir = os.path.join(self.realesrgan_dir, "output")

        # 清理输入文件夹
        if os.path.exists(input_dir):
            for filename in os.listdir(input_dir):
                file_path = os.path.join(input_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    logging.error(f"清理RealESRGAN输入文件夹失败: {str(e)}")

        # 清理输出文件夹
        if os.path.exists(output_dir):
            for filename in os.listdir(output_dir):
                file_path = os.path.join(output_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    logging.error(f"清理RealESRGAN输出文件夹失败: {str(e)}")

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.bangdream_dir = config.get('bangdream_dir', self.bangdream_dir)
                    # 不再加载realesrgan_dir，使用固定路径
                    self.last_fetch_time = config.get('last_fetch_time')
                    
                    # 加载Real-ESRGAN设置
                    # 更新Real-ESRGAN模型变量
                    self.realesrgan_model_var.set(self.realesrgan_model)
                    
                    # 加载下载线程数设置
                    self.download_threads = config.get('download_threads', 16)
                    
                                    # 加载超分引擎和模型设置
                self.upscale_engine = config.get('upscale_engine', 'Real-ESRGAN')
                self.realesrgan_model = config.get('realesrgan_model', 'realesrgan-x4plus-anime')
                self.waifu2x_model_dir = config.get('waifu2x_model_dir', 'models-upconv_7_anime_style_art_rgb')
                self.waifu2x_model_anime = config.get('waifu2x_model_anime', 'noise3_scale2.0x_model')
                self.waifu2x_model_photo = config.get('waifu2x_model_photo', 'noise3_scale2.0x_model')
                self.waifu2x_model_cunet = config.get('waifu2x_model_cunet', 'noise3_scale2.0x_model')
                self.realesrgan_threads = config.get('realesrgan_threads', '1:2:2')
                self.waifu2x_threads = config.get('waifu2x_threads', '1:2:2')
                self.realesrgan_normal_format = config.get('realesrgan_normal_format', 'jpg')
                self.realesrgan_trim_format = config.get('realesrgan_trim_format', 'png')
                self.waifu2x_normal_format = config.get('waifu2x_normal_format', 'jpg')
                self.waifu2x_trim_format = config.get('waifu2x_trim_format', 'png')
                
                # 更新UI变量的值（如果已经创建）
                if hasattr(self, 'upscale_engine_var'):
                    self.upscale_engine_var.set(self.upscale_engine)
                if hasattr(self, 'realesrgan_model_var'):
                    self.realesrgan_model_var.set(self.realesrgan_model)
                if hasattr(self, 'realesrgan_normal_format_var'):
                    self.realesrgan_normal_format_var.set(self.realesrgan_normal_format)
                if hasattr(self, 'waifu2x_normal_format_var'):
                    self.waifu2x_normal_format_var.set(self.waifu2x_normal_format)
            except (json.JSONDecodeError, IOError, OSError) as e:
                logging.error(f"加载配置文件失败: {str(e)}")
                # 如果配置文件损坏，创建默认配置文件
                self.create_default_config()
        else:
            # 如果配置文件不存在，创建默认配置文件
            self.create_default_config()
            
    def create_default_config(self):
        """创建默认配置文件"""
        # 设置默认的BanG Dream目录为程序所在目录的"BanGDream文件夹"
        default_bangdream_dir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "BanGDream")
        self.bangdream_dir = default_bangdream_dir
        
        # 确保默认目录存在
        os.makedirs(default_bangdream_dir, exist_ok=True)
        
        
        # 创建配置
        config = {
            'bangdream_dir': self.bangdream_dir,
            'last_fetch_time': None,
            'download_threads': 16,
            'upscale_engine': 'Real-ESRGAN',
            'realesrgan_model': 'realesrgan-x4plus-anime',
            'waifu2x_model_dir': 'models-upconv_7_anime_style_art_rgb',
            'waifu2x_model_anime': 'noise3_scale2.0x_model',
            'waifu2x_model_photo': 'noise3_scale2.0x_model',
            'waifu2x_model_cunet': 'noise3_scale2.0x_model',
            'realesrgan_threads': '1:2:2',
            'waifu2x_threads': '1:2:2',
            'realesrgan_normal_format': 'jpg',
            'realesrgan_trim_format': 'png',
            'waifu2x_normal_format': 'jpg',
            'waifu2x_trim_format': 'png',
            '_comment': {
                'bangdream_dir': '图片下载目录路径',
                'last_fetch_time': '上次获取卡面信息的时间（程序自动更新）',
                'download_threads': '下载线程数，建议16-32，数值越大下载速度越快但可能被服务器限制',
                'upscale_engine': '默认超分引擎：Real-ESRGAN（画质更好但速度慢）或 waifu2x（速度快但只支持2x）',
                'realesrgan_model': 'Real-ESRGAN默认模型，可选：realesrgan-x4plus-anime（推荐）、realesrgan-x4plus、realesr-animevideov3-x2、realesr-animevideov3-x3、realesr-animevideov3-x4',
                'waifu2x_model_dir': 'waifu2x默认模型目录，可选：models-upconv_7_anime_style_art_rgb（动漫风格）、models-upconv_7_photo（照片风格）、models-cunet（通用）',
                'waifu2x_model_anime': 'models-upconv_7_anime_style_art_rgb目录的默认模型，可选：noise0_scale2.0x_model、noise1_scale2.0x_model、noise2_scale2.0x_model、noise3_scale2.0x_model（推荐）、scale2.0x_model',
                'waifu2x_model_photo': 'models-upconv_7_photo目录的默认模型，可选：noise0_scale2.0x_model、noise1_scale2.0x_model、noise2_scale2.0x_model、noise3_scale2.0x_model（推荐）、scale2.0x_model',
                'waifu2x_model_cunet': 'models-cunet目录的默认模型，可选：noise0_model、noise0_scale2.0x_model、noise1_model、noise1_scale2.0x_model、noise2_model、noise2_scale2.0x_model、noise3_model、noise3_scale2.0x_model（推荐）、scale2.0x_model',
                'realesrgan_threads': 'Real-ESRGAN线程配置，格式为"CPU线程:GPU线程:GPU数量"，建议"1:2:2"，具体可查看github仓库README.md',
                'waifu2x_threads': 'waifu2x线程配置，格式为"CPU线程:GPU线程:GPU数量"，建议"1:2:2"，具体可查看github仓库README.md',
                'realesrgan_normal_format': 'Real-ESRGAN普通卡面输出格式，可选：png（无损）、jpg（推荐）、webp',
                'realesrgan_trim_format': 'Real-ESRGAN无背景卡面输出格式（支持透明通道）',
                'waifu2x_normal_format': 'waifu2x普通卡面输出格式，可选：png（无损）、jpg（推荐）、webp',
                'waifu2x_trim_format': 'waifu2x无背景卡面输出格式（支持透明通道）',
            }
        }
        
        
        # 直接写入配置文件
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"已创建默认配置文件，BanG Dream目录设置为: {default_bangdream_dir}")
        except Exception as e:
            logging.error(f"创建默认配置文件失败: {str(e)}")

    def save_config(self):
        """保存配置文件 - 只保存bangdream_dir和last_fetch_time"""
        try:
            # 先读取现有配置，保持其他配置项不变
            existing_config = {}
            if os.path.exists(CONFIG_FILE):
                try:
                    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                        existing_config = json.load(f)
                except (json.JSONDecodeError, IOError, OSError):
                    pass
            
            # 只更新允许程序修改的配置项
            config = existing_config.copy()
            config['bangdream_dir'] = self.bangdream_dir
            config['last_fetch_time'] = self.last_fetch_time
            
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except (IOError, OSError, TypeError) as e:
            logging.error(f"保存配置文件失败: {str(e)}")

    def load_card_info(self):
        """加载卡面信息 - 现在从程序所在目录加载"""
        # 尝试从程序所在目录加载card_info.json
        app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        card_info_path = os.path.join(app_dir, "card_info.json")
        all5_json_path = os.path.join(app_dir, "all.5.json")

        # 如果文件存在且一周内更新过，直接加载
        if os.path.exists(card_info_path) and os.path.exists(all5_json_path):
            file_mtime = datetime.fromtimestamp(os.path.getmtime(card_info_path))
            if (datetime.now() - file_mtime).days < 7:
                try:
                    with open(card_info_path, 'r', encoding='utf-8') as f:
                        self.card_info = json.load(f)
                    self.log_message("从本地加载卡面信息")
                    return
                except (json.JSONDecodeError, IOError) as e:
                    logging.error(f"加载卡面信息失败: {str(e)}")

        # 否则从网络获取最新卡面信息
        self.log_message("正在获取最新卡面信息...")
        self.update_card_info_from_api()
        self.log_message("卡面信息更新完成")

    def update_card_info_from_api(self):
        """从API获取最新的卡面信息 - 添加服务器可用性信息"""
        # 创建等待窗口
        wait_win = tk.Toplevel(self)
        wait_win.title("正在更新")
        wait_win.geometry("520x440")
        wait_win.transient(self)
        wait_win.grab_set()
        # 插入normal图片
        normal_imgs = self.result_images.get('normal', [])
        if normal_imgs:
            img = random.choice(normal_imgs)
            ttk.Label(wait_win, image=img).pack(pady=10)

        ttk.Label(wait_win, text="正在更新卡面信息，请稍候...", font=("微软雅黑", 11)).pack(pady=20)
        wait_win.update()

        try:
            response = requests.get(CARDS_API_URL, timeout=30)
            response.raise_for_status()
            all_cards_data = response.json()

            # 保存原始all.5.json文件
            app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            all5_json_path = os.path.join(app_dir, "all.5.json")
            with open(all5_json_path, 'w', encoding='utf-8') as f:
                json.dump(all_cards_data, f, ensure_ascii=False, indent=2)

            # 重新组织数据结构
            self.card_info = {}

            # 遍历所有卡面数据
            for card_id_str, card_data in all_cards_data.items():
                try:
                    card_id = int(card_id_str)
                    char_id = str(card_data["characterId"])
                    char_name = character_id_to_name.get(int(char_id), "未知角色")
                    band_name = get_band_name(int(char_id))

                    # 处理资源集名称
                    res_name = card_data.get("resourceSetName", "")

                    # 确定卡面类型
                    card_type = card_data.get("type", "others")

                    # 解析服务器可用性
                    prefix_list = card_data.get("prefix", [])
                    available_servers = []

                    # 检查每个服务器是否有前缀
                    for i, prefix in enumerate(prefix_list):
                        if prefix is not None:
                            server = SERVERS[i]
                            available_servers.append(server)

                    # 如果角色ID不存在，创建新条目
                    if char_id not in self.card_info:
                        self.card_info[char_id] = {
                            "name": char_name,
                            "band": band_name,
                            "cards": []
                        }

                    # 添加卡面信息
                    self.card_info[char_id]["cards"].append({
                        "card_id": card_id,
                        "rarity": card_data.get("rarity", 1),
                        "attribute": card_data.get("attribute", "happy"),
                        "levelLimit": card_data.get("levelLimit", 0),
                        "resourceSetName": res_name,
                        "type": card_type,
                        "available_servers": available_servers  # 添加服务器信息
                    })

                except (KeyError, ValueError, TypeError) as e:
                    logging.error(f"处理卡面ID {card_id_str} 失败: {str(e)}")

            # 保存卡面信息到文件
            self.save_card_info()

            # 更新获取时间
            self.last_fetch_time = datetime.now().strftime('%Y-%m-%d %H:%M')
            self.save_config()

            # 更新界面
            if hasattr(self, 'last_fetch_var'):
                self.last_fetch_var.set(f"{self.last_fetch_time}")

            # 填充角色列表
            if hasattr(self, 'char_list_frame'):
                self.populate_character_list()

        except (requests.RequestException, ValueError) as e:
            self.log_message(f"获取卡面信息失败: {str(e)}")
            messagebox.showerror("错误", f"无法获取卡面信息: {str(e)}")
        finally:
            # 关闭等待窗口
            wait_win.destroy()

    def save_card_info(self):
        """保存卡面信息到文件（程序所在目录）"""
        # 获取程序所在目录
        app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        json_file = os.path.join(app_dir, "card_info.json")

        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.card_info, f, ensure_ascii=False, indent=2)
            self.log_message("卡面信息已保存到文件")
        except (IOError, OSError) as e:
            self.log_message(f"保存卡面信息失败: {str(e)}")

    def ensure_directories(self):
        """确保所有必要的目录存在"""
        # 确保BangDream目录存在
        try:
            os.makedirs(self.bangdream_dir, exist_ok=True)
        except OSError as e:
            logging.error(f"创建目录失败 {self.bangdream_dir}: {str(e)}")
            messagebox.showerror("错误", f"无法创建目录: {str(e)}")

        # 确保RealESRGAN目录存在
        if self.realesrgan_dir:
            try:
                os.makedirs(self.realesrgan_dir, exist_ok=True)
                # 确保input和output目录存在
                input_dir = os.path.join(self.realesrgan_dir, "input")
                output_dir = os.path.join(self.realesrgan_dir, "output")
                os.makedirs(input_dir, exist_ok=True)
                os.makedirs(output_dir, exist_ok=True)
            except OSError as e:
                logging.error(f"创建目录失败 {self.realesrgan_dir}: {str(e)}")

    def log_message(self, message):
        """记录消息到状态栏和日志"""
        self.status_var.set(message)
        logging.info(message)

    def open_bangdream_folder(self):
        """打开BangDream文件夹"""
        try:
            if platform.system() == "Windows":
                os.startfile(self.bangdream_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", self.bangdream_dir])
            else:  # Linux
                subprocess.Popen(["xdg-open", self.bangdream_dir])
        except OSError as e:
            self.log_message(f"无法打开文件夹: {str(e)}")
            messagebox.showerror("错误", f"无法打开文件夹: {str(e)}")

    def setup_setup_tab(self):
        """设置标签页"""
        # 文件夹设置框架
        folder_frame = ttk.LabelFrame(self.setup_tab, text="文件夹设置")
        folder_frame.pack(fill=tk.X, padx=10, pady=10)

        container = ttk.Frame(self.setup_tab)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 文件夹设置
        folder_frame = ttk.LabelFrame(container, text="文件夹设置", padding=10)
        folder_frame.pack(fill=tk.X, pady=(0, 20))

        path_frame = ttk.Frame(folder_frame)
        path_frame.pack(fill=tk.X, pady=5)

        ttk.Label(path_frame, text="图片下载目录:", width=12).pack(side=tk.LEFT)
        self.bangdream_dir_var = tk.StringVar(value=self.bangdream_dir)
        dir_entry = ttk.Entry(path_frame, textvariable=self.bangdream_dir_var, width=50)
        dir_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(
            path_frame,
            text="浏览...",
            command=self.select_bangdream_dir,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)

        # 支持回车
        def on_dir_entry_return(event=None):
            path = self.bangdream_dir_var.get().strip()
            if path:
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
                self.bangdream_dir = path
                self.save_config()
                self.log_message(f"已设置BangDream目录: {path}")
        dir_entry.bind('<Return>', on_dir_entry_return)

       

        

        # 帮助链接框架
        help_frame = ttk.Frame(self.setup_tab)
        help_frame.pack(fill=tk.X, padx=10, pady=10)

        # 超链接文本
        help_link = tk.Label(
            help_frame,
            text="不会用就点我",
            fg="blue",
            cursor="hand2",
            font=("微软雅黑", 14, "underline")
        )
        help_link.pack(pady=5)
        help_link.bind("<Button-1>", lambda e: webbrowser.open("https://www.bilibili.com/video/BV1ZAhGzoEZK/"))

        # 其他帮助链接
        links = [
            ("卡面来源： Bestdori", "https://bestdori.com"),
            ("Real-ESRGAN", "https://github.com/xinntao/Real-ESRGAN/"),
            ("Real-ESRGAN-ncnn-vulkan","https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan"),
            ("waifu2x","https://github.com/nagadomi/waifu2x"),
            ("waifu2x-ncnn-vulkan","https://github.com/nihui/waifu2x-ncnn-vulkan"),
            ("作者主页", "https://space.bilibili.com/302382499")
        ]

        help_container = ttk.Frame(container)
        help_container.pack(fill=tk.BOTH, expand=True)

        info_frame = ttk.LabelFrame(help_container, text="使用说明", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)

        info_text = """     欢迎使用 BanG Dream! 卡面工具！

                下载功能：
                • 支持批量下载角色卡面
                • 可按稀有度、属性、类型、是否超分筛选
                • 可手动添加卡面ID下载
                • 自动筛选可用服务器
                • 可下载国服，外服独占卡面

                超分功能：
                • 可选择 Real-ESRGAN 或 waifu2x
                • 可自定义超分模型
                • 支持普通卡面和无背景卡面
                • 可自定义输出格式"""

        info_label = ttk.Label(
            info_frame,
            text=info_text,
            justify=tk.LEFT,
            font=("微软雅黑", 10)
        )
        info_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        for text, url in links:
            link_frame = ttk.Frame(self.setup_tab)
            link_frame.pack(fill=tk.X, padx=10, pady=0)
            help_link = tk.Label(
                link_frame,
                text=text,
                fg="blue",
                cursor="hand2",
                font=("微软雅黑", 10, "underline")
            )
            help_link.pack(pady=2)
            help_link.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))

        

    def select_bangdream_dir(self):
        """选择BangDream文件夹"""
        dir_path = filedialog.askdirectory(initialdir=os.path.expanduser('~'))
        if dir_path:
            self.bangdream_dir_var.set(os.path.normpath(dir_path))
            self.bangdream_dir = dir_path
            self.ensure_directories()  # 确保目录存在
            self.save_config()  # 自动保存配置

    def setup_download_tab(self):
        """卡面下载标签页"""
        # 进入下载标签页时自动加载卡面信息
        self.attr_icons = {}
        for attr in ["cool", "powerful", "pure", "happy"]:
            image = Image.open(f"assets/{attr}.png").resize((35, 35))  # 可以根据需要调整尺寸
            self.attr_icons[attr] = ImageTk.PhotoImage(image)

        self.star_icons = {}
        for r in range(1, 6):
            img = Image.open(f"assets/star_{r}.png").resize((35, 35))  # 可调整大小
            self.star_icons[r] = ImageTk.PhotoImage(img)

        # 加载乐队图标
        self.band_icons = {}
        for i in range(1, 9):  # band_1.png 到 band_8.png
            try:
                img = Image.open(f"assets/band_{i}.png").resize((35, 35))  # 调整大小
                self.band_icons[i] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"加载乐队图标 band_{i}.png 失败: {str(e)}")

        if not self.card_info:
            self.load_card_info()

        # 上次获取信息显示
        info_frame = ttk.Frame(self.download_tab)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(info_frame, text="上次获取:").pack(side=tk.LEFT)
        self.last_fetch_var = tk.StringVar(value="从未获取")
        if self.last_fetch_time:
            self.last_fetch_var.set(f"{self.last_fetch_time}")
        ttk.Label(info_frame, textvariable=self.last_fetch_var).pack(side=tk.LEFT, padx=5)

        # 更新卡面信息按钮
        ttk.Button(
            info_frame,
            text="更新卡面信息",
            command=self.update_card_info_from_api
        ).pack(side=tk.RIGHT, padx=5)

        # 打开文件夹按钮
        ttk.Button(
            info_frame,
            text="打开文件夹",
            command=self.open_bangdream_folder
        ).pack(side=tk.RIGHT, padx=5)

       

        # 添加全局筛选框架
        filter_frame = ttk.LabelFrame(self.download_tab, text="筛选")
        filter_frame.pack(fill=tk.X, pady=10)

        # 添加稀有度筛选
        rarity_frame = ttk.Frame(filter_frame)
        rarity_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(rarity_frame, text="稀有度:", ).pack(side=tk.LEFT, padx=5)

        for rarity in range(1, 6):
            frame = ttk.Frame(rarity_frame)
            frame.pack(side=tk.LEFT, padx=20)

            var = self.rarity_vars[rarity]
            chk = ttk.Checkbutton(frame, variable=var, command=self.update_filtered_counts)
            chk.pack(side=tk.LEFT)

            # 用图片代替文字
            lbl = ttk.Label(frame, image=self.star_icons[rarity])
            lbl.pack(side=tk.LEFT)

            # 点击图片也能切换
            lbl.bind("<Button-1>", lambda e, cb=chk: cb.invoke())

        # 将稀有度按钮添加到稀有度行右侧
        ttk.Button(rarity_frame, text="全不选稀有度",width=12, command=self.deselect_all_rarity).pack(
            side=tk.RIGHT, padx=5)

        ttk.Button(rarity_frame, text="全选稀有度",width=10, command=self.select_all_rarity).pack(
            side=tk.RIGHT, padx=5)




        # 添加属性筛选
        attribute_frame = ttk.Frame(filter_frame)
        attribute_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(attribute_frame, text="  属性:").pack(side=tk.LEFT, padx=5)
        attributes = ["powerful", "cool", "happy", "pure"]
        attr_names = {"cool": "COOL", "powerful": "POWERFUL", "pure": "PURE", "happy": "HAPPY"}
        for attr in attributes:
            frame = ttk.Frame(attribute_frame)
            frame.pack(side=tk.LEFT, padx=20)

            var = self.attribute_vars[attr]
            chk = ttk.Checkbutton(frame, variable=var, command=self.update_filtered_counts)
            chk.pack(side=tk.LEFT)

            lbl = ttk.Label(
                frame,
                text=attr_names[attr],
                image=self.attr_icons[attr],
                compound="left",  # 图在左，字在右
                padding=1
            )
            lbl.pack(side=tk.LEFT)

            lbl.bind("<Button-1>", lambda e, cb=chk: cb.invoke())

        # 将属性按钮添加到属性行右侧

        ttk.Button(attribute_frame, text="全不选属性",width=12, command=self.deselect_all_attributes, ).pack(
            side=tk.RIGHT, padx=5)
        ttk.Button(attribute_frame, text="全选属性",width=10, command=self.select_all_attributes, ).pack(
            side=tk.RIGHT, padx=5)


        # 添加类型筛选
        type_frame = ttk.Frame(filter_frame)
        type_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(type_frame, text="  类型:").pack(side=tk.LEFT, padx=5)
        for card_type in CARD_TYPES:
            frame = ttk.Frame(type_frame)
            frame.pack(side=tk.LEFT, padx=12)

            var = self.type_vars[card_type]
            chk = ttk.Checkbutton(frame, variable=var, command=self.update_filtered_counts)
            chk.pack(side=tk.LEFT)

            lbl = ttk.Label(frame, text=TYPE_NAMES.get(card_type, card_type))
            lbl.pack(side=tk.LEFT)
            # 修复lambda函数变量捕获问题 - 使用默认参数
            lbl.bind("<Button-1>", lambda e, v=var: self.toggle_type_selection(v))

        # 将类型按钮添加到类型行右侧
        ttk.Button(type_frame, text="全不选类型",width=12, command=self.deselect_all_types).pack(
            side=tk.RIGHT, padx=5)

        ttk.Button(type_frame, text="全选类型", width=10,command=self.select_all_types).pack(side=tk.RIGHT,
                                                                                                    padx=5)

        # 下载内容和特训阶段选择
        option_frame = ttk.Frame(filter_frame)
        option_frame.pack(fill=tk.X, padx=5, pady=5)
        # 下载内容
        ttk.Label(option_frame, text="图片类型：").pack(side=tk.LEFT, padx=5)
        self.batch_type_var = tk.StringVar(value="all")
        
        ttk.Radiobutton(option_frame, text="普通卡面", variable=self.batch_type_var, value="normal", style="Big.TRadiobutton").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(option_frame, text="无背景卡面", variable=self.batch_type_var, value="trim", style="Big.TRadiobutton").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(option_frame, text="全部", variable=self.batch_type_var, value="all", style="Big.TRadiobutton").pack(side=tk.LEFT, padx=5)

        # 特训阶段
        ttk.Label(option_frame, text="              是否特训：").pack(side=tk.LEFT, padx=15)
        self.batch_stage_var = tk.StringVar(value="all")
        
        ttk.Radiobutton(option_frame, text="特训前", variable=self.batch_stage_var, value="normal", style="Big.TRadiobutton").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(option_frame, text="特训后", variable=self.batch_stage_var, value="after", style="Big.TRadiobutton").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(option_frame, text="全部", variable=self.batch_stage_var, value="all", style="Big.TRadiobutton").pack(side=tk.LEFT, padx=5)

        # 角色选择框架
        char_frame = ttk.LabelFrame(self.download_tab, text="选择角色")
        char_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tip_label = ttk.Label(
            self.download_tab,
            text="提示: 程序会自动跳过已下载的卡面",
            foreground="#666",
            font=('Segoe UI', 9, 'italic')
        )
        tip_label.pack(pady=5)

        # 角色列表容器
        self.char_list_frame = ttk.Frame(char_frame)
        self.char_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建滚动区域
        canvas = tk.Canvas(self.char_list_frame)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # 添加滚轮支持
        scrollbar = self.add_scroll_support(canvas, self.scrollable_frame)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 按钮框架
        btn_frame = ttk.Frame(char_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(btn_frame, text="全选", command=self.select_all_chars).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="全不选", command=self.deselect_all_chars).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="开始下载",  style="Accent.TButton",command=self.start_download).pack(side=tk.RIGHT, padx=5)

        # 如果已有卡面信息，填充角色列表
        if self.card_info:
            self.populate_character_list()

    def add_scroll_support(self, canvas, frame):
        """为Canvas添加滚轮支持，兼容Windows/Mac/Linux"""
        import platform
        os_name = platform.system()
        scrollbar = ttk.Scrollbar(canvas.master, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_mousewheel(event, c=canvas):
            if os_name == 'Windows':
                c.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif os_name == 'Darwin':
                c.yview_scroll(int(-1 * (event.delta)), "units")
            else:  # Linux
                if event.num == 4:
                    c.yview_scroll(-1, "units")
                elif event.num == 5:
                    c.yview_scroll(1, "units")
            return "break"

        # Windows/Mac: <MouseWheel>，Linux: <Button-4>/<Button-5>
        if os_name in ('Windows', 'Darwin'):
            for widget in [canvas, frame]:
                widget.bind("<MouseWheel>", _on_mousewheel)
            scrollbar.bind("<MouseWheel>", _on_mousewheel)
        else:
            for widget in [canvas, frame]:
                widget.bind("<Button-4>", _on_mousewheel)
                widget.bind("<Button-5>", _on_mousewheel)
            scrollbar.bind("<Button-4>", _on_mousewheel)
            scrollbar.bind("<Button-5>", _on_mousewheel)

        self.bind_mousewheel_recursive(frame, canvas, os_name)
        return scrollbar

    def bind_mousewheel_recursive(self, widget, canvas, os_name=None):
        """递归绑定鼠标滚轮事件，兼容多平台"""
        import platform
        if os_name is None:
            os_name = platform.system()
        def _on_mousewheel(event):
            if os_name == 'Windows':
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif os_name == 'Darwin':
                canvas.yview_scroll(int(-1 * (event.delta)), "units")
            else:
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")
            return "break"
        if os_name in ('Windows', 'Darwin'):
            widget.bind("<Enter>", lambda e: widget.bind_all("<MouseWheel>", _on_mousewheel))
            widget.bind("<Leave>", lambda e: widget.unbind_all("<MouseWheel>"))
        else:
            widget.bind("<Enter>", lambda e: [widget.bind_all("<Button-4>", _on_mousewheel), widget.bind_all("<Button-5>", _on_mousewheel)])
            widget.bind("<Leave>", lambda e: [widget.unbind_all("<Button-4>"), widget.unbind_all("<Button-5>")])
        for child in widget.winfo_children():
            self.bind_mousewheel_recursive(child, canvas, os_name)

    def select_all_types(self):
        """全选所有类型"""
        for var in self.type_vars.values():
            var.set(True)
        self.update_filtered_counts()

    def deselect_all_types(self):
        """全不选所有类型"""
        for var in self.type_vars.values():
            var.set(False)
        self.update_filtered_counts()

    def select_all_rarity(self):
        """全选所有稀有度"""
        for var in self.rarity_vars.values():
            var.set(True)
        self.update_filtered_counts()

    def deselect_all_rarity(self):
        """全不选所有稀有度"""
        for var in self.rarity_vars.values():
            var.set(False)
        self.update_filtered_counts()

    def select_all_attributes(self):
        """全选所有属性"""
        for var in self.attribute_vars.values():
            var.set(True)
        self.update_filtered_counts()

    def deselect_all_attributes(self):
        """全不选所有属性"""
        for var in self.attribute_vars.values():
            var.set(False)
        self.update_filtered_counts()

   

    def populate_character_list(self, characters=None):
        """填充角色选择列表 - 按乐队分组显示"""
        # 清空现有列表
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # 如果没有提供特定角色列表，使用全部角色
        if characters is None:
            characters = self.card_info

        # 如果没有角色信息，显示提示
        if not characters:
            ttk.Label(
                self.scrollable_frame,
                text="没有角色信息，请先获取卡面信息",
                font=("微软雅黑", 11)
            ).pack(pady=20)
            return

        # 角色选择变量
        self.char_vars = {}
        self.filtered_count_labels = {}
        self.band_vars = {}  # 乐队选择变量

        # 按乐队分组角色
        band_characters = {}
        for char_id, char_info in characters.items():
            band_name = char_info["band"]
            if band_name not in band_characters:
                band_characters[band_name] = []
            band_characters[band_name].append((char_id, char_info))

        # 乐队显示顺序（按照角色ID范围）
        band_order = [
            "Poppin'Party",
            "Afterglow", 
            "Hello, Happy World!",
            "Pastel_Palettes",
            "Roselia",
            "Morfonica",
            "RAISE_A_SUILEN",
            "MyGO!!!!!"
        ]

        # 乐队图标映射
        band_icon_mapping = {
            "Poppin'Party": 1,
            "Afterglow": 2,
            "Hello, Happy World!": 3,
            "Pastel_Palettes": 4,
            "Roselia": 5,
            "Morfonica": 6,
            "RAISE_A_SUILEN": 7,
            "MyGO!!!!!": 8
        }

        # 按顺序显示乐队
        row = 0
        for band_name in band_order:
            if band_name not in band_characters:
                continue
                
            # 创建乐队标题框架
            band_title_frame = ttk.Frame(self.scrollable_frame)
            band_title_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=(10, 5))  # 增加乐队间距
            row += 1
            
            # 乐队标题和全选按钮
            title_frame = ttk.Frame(band_title_frame)
            title_frame.pack(fill=tk.X)
            
            # 乐队全选复选框
            band_var = tk.BooleanVar(value=False)  # 默认全不选
            self.band_vars[band_name] = band_var
            band_chk = ttk.Checkbutton(title_frame, variable=band_var, 
                                     command=lambda b=band_name: self.toggle_band_selection(b))
            band_chk.pack(side=tk.LEFT, padx=5)
            
            # 乐队名称标签
            band_label = ttk.Label(title_frame, text=band_name, font=("微软雅黑", 11, "bold"))
            band_label.pack(side=tk.LEFT, padx=5)
            band_label.bind("<Button-1>", lambda e, b=band_name: self.toggle_band_selection(b))
            # 让乐队名点击时也能切换复选框
            band_label.bind("<Button-1>", lambda e, b=band_name: self.band_vars[b].set(not self.band_vars[b].get()) or self.toggle_band_selection(b))
            
            # 添加乐队图标
            band_icon_id = band_icon_mapping.get(band_name)
            if band_icon_id and band_icon_id in self.band_icons:
                band_icon_label = ttk.Label(title_frame, image=self.band_icons[band_icon_id])
                band_icon_label.pack(side=tk.LEFT, padx=5)
                band_icon_label.bind("<Button-1>", lambda e, b=band_name: self.toggle_band_selection(b))
            
            # 创建角色网格框架
            chars_frame = ttk.Frame(band_title_frame)
            chars_frame.pack(fill=tk.X, padx=25, pady=12)  # 增加左边距和上下间距
            
            # 计算每行显示的角色数量（根据窗口宽度调整）
            chars_per_row = 5  # 每行5个角色，确保一个乐队的角色在一行显示
            
            # 显示该乐队的角色
            for i, (char_id, char_info) in enumerate(band_characters[band_name]):
                char_name = char_info["name"]
                card_count = len(char_info["cards"])
                
                # 计算筛选后的数量
                filtered_count = self.calculate_filtered_count(char_info["cards"])
                
                # 创建角色框架
                char_frame = ttk.Frame(chars_frame)
                char_frame.grid(row=i // chars_per_row, column=i % chars_per_row, 
                               sticky="ew", padx=8, pady=2)  # 增加角色间距
                
                # 角色选择复选框
                var = tk.BooleanVar(value=False)  # 默认不选
                self.char_vars[char_id] = var
                chk = ttk.Checkbutton(char_frame, variable=var)
                chk.pack(side=tk.LEFT, padx=3)
                
                # 角色名称标签
                char_label = ttk.Label(char_frame, text=char_name, font=("微软雅黑", 11))  
                char_label.pack(side=tk.LEFT, padx=3)
                char_label.bind("<Button-1>", lambda e, v=var: v.set(not v.get()))
                
                # 卡面数量信息（小字体）
                count_label = ttk.Label(char_frame, text=f"({card_count})", 
                                       font=("微软雅黑", 9), foreground="gray")
                count_label.pack(side=tk.LEFT, padx=3)
                count_label.bind("<Button-1>", lambda e, v=var: v.set(not v.get()))
                
                # 筛选后数量显示（小字体）
                filtered_label = ttk.Label(char_frame, text=f"[{filtered_count}]", 
                                          font=("微软雅黑", 9), foreground="blue")
                filtered_label.pack(side=tk.LEFT, padx=3)
                self.filtered_count_labels[char_id] = filtered_label
                
                # 绑定点击事件到整个角色框架
                char_frame.bind("<Button-1>", lambda e, v=var: v.set(not v.get()))
            
            # 添加乐队选择状态更新
            self.update_band_selection_state(band_name)

    def toggle_band_selection(self, band_name):
        """切换乐队选择状态"""
        if not hasattr(self, 'band_vars') or band_name not in self.band_vars:
            return
            
        band_selected = self.band_vars[band_name].get()
        
        # 获取该乐队的所有角色
        band_char_ids = []
        for char_id, char_info in self.card_info.items():
            if char_info["band"] == band_name:
                band_char_ids.append(char_id)
        
        # 设置该乐队所有角色的选择状态
        for char_id in band_char_ids:
            if char_id in self.char_vars:
                self.char_vars[char_id].set(band_selected)

    def update_filtered_counts(self):
        """更新所有角色的筛选后数量显示"""
        if not self.card_info:
            return

        for char_id, char_info in self.card_info.items():
            if char_id in self.filtered_count_labels:
                filtered_count = self.calculate_filtered_count(char_info["cards"])
                self.filtered_count_labels[char_id].config(text=f"[{filtered_count}]")

    def calculate_filtered_count(self, cards):
        """计算筛选后的卡面数量"""
        filtered_count = 0
        for card in cards:
            # 检查稀有度筛选
            rarity_selected = self.rarity_vars[card["rarity"]].get()

            # 检查属性筛选
            attr_selected = self.attribute_vars[card["attribute"]].get()

            # 检查类型筛选
            type_selected = self.type_vars[card["type"]].get()

            if rarity_selected and attr_selected and type_selected:
                filtered_count += 1
        return filtered_count

    def select_all_chars(self):
        """全选所有角色"""
        for var in self.char_vars.values():
            var.set(True)
        # 更新所有乐队的选择状态
        for band_name in self.band_vars.keys():
            self.update_band_selection_state(band_name)

    def deselect_all_chars(self):
        """取消全选所有角色"""
        for var in self.char_vars.values():
            var.set(False)
        # 更新所有乐队的选择状态
        for band_name in self.band_vars.keys():
            self.update_band_selection_state(band_name)

    def download_image(self, url, save_path, log_func, card_id, server):
        """下载图片并保存"""
        try:
            # 检查下载是否暂停
            while self.pause_download:
                time.sleep(0.5)
                if self.download_canceled:
                    self.download_logger.log_skip(card_id, url, "下载已取消", server)
                    return False, "下载已取消"

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # 检查文件大小
            if len(response.content) < 20 * 1024:  # 小于20KB
                log_func(f"跳过小文件: {url}")
                self.download_logger.log_skip(card_id, url, "文件过小（<20KB）", server)
                return True, "文件过小（跳过）"  # 这里改为返回True表示跳过

            with open(save_path, 'wb') as f:
                f.write(response.content)

            log_func(f"已下载: {os.path.basename(save_path)}")
            self.download_logger.log_success(card_id, url, server)
            return True, None
        except requests.exceptions.Timeout:
            # 使用锁来保护超时计数
            with self.download_lock:
                current_time = time.time()
                if current_time - self.last_timeout_time > 30:  # 30秒内算连续超时
                    self.timeout_count = 1
                else:
                    self.timeout_count += 1

                self.last_timeout_time = current_time

                if self.timeout_count >= 8:
                    # 根据总卡面数量决定暂停时间
                    if self.total_cards < 100:
                        pause_seconds = 10  # 10秒
                    elif self.total_cards < 1000:
                        pause_seconds = 180  # 3分钟
                    else:
                        pause_seconds = 300  # 5分钟

                    log_func(f"连续三次超时，暂停{pause_seconds}秒...")
                    # 设置全局暂停状态
                    self.pause_download = True
                    # 更新暂停状态显示
                    if hasattr(self, 'pause_status_var'):
                        self.pause_status_var.set(f"状态: 暂停中（连续超时）")
                    # 等待
                    for i in range(pause_seconds):
                        if self.download_canceled:
                            self.download_logger.log_skip(card_id, url, "下载已取消", server)
                            return False, "下载已取消"
                        time.sleep(1)
                    # 重置超时计数
                    self.timeout_count = 0
                    # 恢复下载
                    self.pause_download = False
                    if hasattr(self, 'pause_status_var'):
                        self.pause_status_var.set("状态: 运行中")
                    log_func(f"暂停结束，继续下载...")

            error_msg = f"超时: {url}"
            log_func(error_msg)
            self.download_logger.log_failure(card_id, url, "请求超时", server)
            return False, error_msg

        except requests.exceptions.ConnectionError as e:
            # 新增：处理连接错误
            error_msg = f"连接错误: {url} - {str(e)}"
            log_func(error_msg)
            # 修改：连接错误记录为失败而非跳过
            self.download_logger.log_failure(card_id, url, str(e), server)
            return False, error_msg

        except Exception as e:
            error_msg = f"下载失败: {url} - {str(e)}"
            log_func(error_msg)
            self.download_logger.log_failure(card_id, url, str(e), server)
            return False, error_msg

    def start_download(self):
        """开始下载选中的角色卡面，包含自动重试功能"""
        # 检查是否有未完成的下载任务
        has_unfinished_task, task_message = self.check_download_status()
        if has_unfinished_task:
            # 提供重置选项
            result = messagebox.askyesno("警告", 
                f"检测到未完成的任务：{task_message}\n\n是否要重置下载状态并继续？")
            if result:
                self.reset_download_status()
            else:
                return
        
        # 获取选中的角色ID
        selected_char_ids = [char_id for char_id, var in self.char_vars.items() if var.get()]

        if not selected_char_ids:
            self.show_custom_message("警告", "请至少选择一个角色", msg_type='normal')
            return

        # 重置下载控制变量
        self.pause_download = False
        self.download_canceled = False
        self.timeout_count = 0
        self.last_timeout_time = 0
        self.failed_downloads = []  # 清空失败记录
        self.download_in_progress = True  # 设置下载进行中标志

        # 创建进度窗口
        progress_win = tk.Toplevel(self)
        progress_win.title("下载卡面")
        progress_win.geometry("900x700")
        progress_win.transient(self)
        # 移除grab_set()以解决窗口无法通过任务栏恢复的问题
        # progress_win.grab_set()
        
        # 确保窗口在最小化后可以通过任务栏图标恢复
        progress_win.lift()
        progress_win.focus_force()

        # 绑定窗口关闭事件
        progress_win.protocol("WM_DELETE_WINDOW", lambda: self.cancel_download(progress_win))

        ttk.Label(progress_win, text="正在下载卡面...", font=("微软雅黑", 12)).pack(pady=10)

        # 控制按钮框架
        control_frame = ttk.Frame(progress_win)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # 添加暂停/继续按钮
        self.pause_button = ttk.Button(
            control_frame,
            text="暂停",
            command=lambda: self.toggle_pause_download(progress_win)
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)

        # 添加取消按钮
        ttk.Button(
            control_frame,
            text="取消",
            command=lambda: self.cancel_download(progress_win)
        ).pack(side=tk.LEFT, padx=5)

        # 暂停状态标签
        self.pause_status_var = tk.StringVar(value="状态: 运行中")
        ttk.Label(control_frame, textvariable=self.pause_status_var).pack(side=tk.LEFT, padx=10)

        # 超时计数标签
        self.timeout_var = tk.StringVar(value="超时计数: 0")
        ttk.Label(control_frame, textvariable=self.timeout_var).pack(side=tk.LEFT, padx=10)

        # 阶段标签
        self.stage_var = tk.StringVar(value="阶段: 初次下载")
        ttk.Label(control_frame, textvariable=self.stage_var).pack(side=tk.LEFT, padx=10)

        # 进度条
        progress_var = tk.IntVar()
        progress_bar = ttk.Progressbar(progress_win, variable=progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, padx=20, pady=10)

        # 状态标签
        status_var = tk.StringVar(value="下载中...")
        ttk.Label(progress_win, textvariable=status_var).pack(pady=5)

        # 剩余时间标签
        time_remaining_var = tk.StringVar(value="剩余时间: 计算中...")
        time_label = ttk.Label(progress_win, textvariable=time_remaining_var)
        time_label.pack(pady=5)

        # 处理速度标签
        speed_var = tk.StringVar(value="处理速度: 0 张/秒")
        speed_label = ttk.Label(progress_win, textvariable=speed_var)
        speed_label.pack(pady=5)

        # 日志区域
        log_frame = ttk.Frame(progress_win)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD, font=("微软雅黑", 11))
        log_text.pack(fill=tk.BOTH, expand=True)
        log_text.config(state=tk.DISABLED)

        def log(msg):
            log_text.config(state=tk.NORMAL)
            log_text.insert(tk.END, msg + "\n")
            log_text.config(state=tk.DISABLED)
            log_text.yview_moveto(1.0)  # 平滑滚动到底部

        # 失败日志区域
        failure_frame = ttk.LabelFrame(progress_win, text="失败日志")
        failure_frame.pack(fill=tk.X, padx=10, pady=5)

        failure_text = scrolledtext.ScrolledText(failure_frame, height=5, wrap=tk.WORD, font=("微软雅黑", 11))
        failure_text.pack(fill=tk.BOTH, expand=True)
        failure_text.config(state=tk.DISABLED)

        def log_failure(msg):
            failure_text.config(state=tk.NORMAL)
            failure_text.insert(tk.END, msg + "\n")
            failure_text.config(state=tk.DISABLED)
            failure_text.yview_moveto(1.0)  # 平滑滚动到底部

        # 在后台线程中下载卡面
        def download_thread():
            # 第一阶段：初次下载
            log("=== 开始初次下载 ===")
            self.stage_var.set("阶段: 初次下载")
            
            # 收集所有下载任务
            download_tasks = []
            char_dirs = {}

            total_chars = len(selected_char_ids)
            processed_chars = 0
            total_downloaded = 0
            total_skipped = 0
            total_failed = 0
            failure_log = []  # 存储失败日志

            # 计算总卡面数（过滤后）
            self.total_cards = 0
            for char_id in selected_char_ids:
                char_info = self.card_info[char_id]
                for card in char_info["cards"]:
                    # 应用筛选条件
                    if (self.rarity_vars[card["rarity"]].get() and
                            self.attribute_vars[card["attribute"]].get() and
                            self.type_vars[card["type"]].get()):
                        self.total_cards += 1

            if self.total_cards == 0:
                progress_win.destroy()
                messagebox.showinfo("提示", "没有符合筛选条件的卡面")
                return

            # 创建所有必要的目录
            for char_id in selected_char_ids:
                char_info = self.card_info[char_id]
                char_name = char_info["name"]
                band_name = char_info["band"]

                # 清理名称
                safe_band_name = sanitize_filename(band_name)
                safe_char_name = sanitize_filename(char_name)

                # 创建角色目录
                char_dir = self.get_char_dir(safe_band_name, safe_char_name)
                card_dir = self.get_card_dir(char_dir)
                trim_dir = self.get_trim_dir(char_dir)

                for path in [char_dir, card_dir, trim_dir]:
                    os.makedirs(path, exist_ok=True)

                char_dirs[char_id] = {
                    "card_dir": card_dir,
                    "trim_dir": trim_dir
                }

            start_time = time.time()
            last_update_time = start_time
            processed_since_last_update = 0
            total_processed = 0

            # 创建线程池
            with ThreadPoolExecutor(max_workers=self.download_threads) as executor:
                # 提交所有下载任务
                futures = []
                for char_id in selected_char_ids:
                    char_info = self.card_info[char_id]
                    char_name = char_info["name"]
                    cards = char_info["cards"]

                    for card in cards:
                        # 应用筛选条件 - 提前过滤
                        if not (self.rarity_vars[card["rarity"]].get() and
                                self.attribute_vars[card["attribute"]].get() and
                                self.type_vars[card["type"]].get()):
                            continue

                        # 获取目录
                        card_dir = char_dirs[char_id]["card_dir"]
                        trim_dir = char_dirs[char_id]["trim_dir"]

                        # 提交任务
                        futures.append(executor.submit(
                            self.process_card_download,
                            card, char_id, char_name, card_dir, trim_dir, log, log_failure, failure_log
                        ))

                # 处理完成的任务
                for future in as_completed(futures):
                    try:
                        if self.download_canceled:
                            log("下载已取消")
                            break

                        result = future.result()
                        total_processed += 1
                        processed_since_last_update += 1

                        # 更新进度
                        progress = min(100, int(total_processed / self.total_cards * 100))
                        progress_var.set(progress)

                        # 更新统计
                        total_downloaded += result["downloaded"]
                        total_skipped += result["skipped"]
                        total_failed += result["failed"]

                        # 更新超时计数显示
                        self.timeout_var.set(f"超时计数: {self.timeout_count}")

                        # 实时刷新剩余时间和速度
                        current_time = time.time()
                        elapsed_time = current_time - start_time
                        time_per_card = elapsed_time / total_processed if total_processed > 0 else 0
                        remaining_cards = self.total_cards - total_processed
                        remaining_time = remaining_cards * time_per_card
                        if remaining_time < 60:
                            time_str = f"{int(remaining_time)}秒"
                        elif remaining_time < 3600:
                            minutes = int(remaining_time // 60)
                            seconds = int(remaining_time % 60)
                            time_str = f"{minutes}分{seconds}秒"
                        else:
                            hours = int(remaining_time // 3600)
                            minutes = int((remaining_time % 3600) // 60)
                            time_str = f"{hours}小时{minutes}分"
                        speed = processed_since_last_update / (current_time - last_update_time) if (current_time - last_update_time) > 0 else 0
                        time_remaining_var.set(f"剩余时间: {time_str}")
                        speed_var.set(f"处理速度: {speed:.1f} 张/秒")
                        if current_time - last_update_time > 5:
                            last_update_time = current_time
                            processed_since_last_update = 0
                    except Exception as e:
                        log(f"处理卡面时出错: {str(e)}")

            

            # 初次下载完成
            log(f"=== 初次下载完成 ===")
            log(f"下载: {total_downloaded}, 跳过: {total_skipped}, 失败: {total_failed}")

            # 第二阶段：如果有失败，自动重试
            max_retry_rounds = 3
            retry_round = 0
            while total_failed > 0 and not self.download_canceled and retry_round < max_retry_rounds:
                retry_round += 1
                log(f"=== 开始第{retry_round}轮重试失败的下载 ===")
                self.stage_var.set(f"阶段: 第{retry_round}轮重试")
                progress_var.set(0)
                retry_start_time = time.time()
                retry_total = len(self.failed_downloads)
                retry_success = 0
                retry_processed = 0
                processed_since_last_update = 0
                last_update_time = retry_start_time
                new_failed_downloads = []
                if retry_total > 0:
                    with ThreadPoolExecutor(max_workers=self.download_threads) as executor:
                        futures = []
                        for failure in self.failed_downloads:
                            futures.append(executor.submit(
                                self.download_image,
                                failure['url'],
                                failure['save_path'],
                                log,
                                failure['card_id'],
                                failure.get('server', '未知')
                            ))
                        for i, future in enumerate(futures):
                            if self.download_canceled:
                                log("重试已取消")
                                break
                            try:
                                success, error = future.result()
                                retry_processed += 1
                                processed_since_last_update += 1
                                progress = min(100, int(retry_processed / retry_total * 100))
                                progress_var.set(progress)
                                # 剩余时间和速度
                                current_time = time.time()
                                if current_time - last_update_time > 5:
                                    elapsed_time = current_time - retry_start_time
                                    time_per_card = elapsed_time / retry_processed if retry_processed > 0 else 0
                                    remaining_cards = retry_total - retry_processed
                                    remaining_time = remaining_cards * time_per_card
                                    if remaining_time < 60:
                                        time_str = f"{int(remaining_time)}秒"
                                    elif remaining_time < 3600:
                                        minutes = int(remaining_time // 60)
                                        seconds = int(remaining_time % 60)
                                        time_str = f"{minutes}分{seconds}秒"
                                    else:
                                        hours = int(remaining_time // 3600)
                                        minutes = int((remaining_time % 3600) // 60)
                                        time_str = f"{hours}小时{minutes}分"
                                    speed = processed_since_last_update / (current_time - last_update_time)
                                    time_remaining_var.set(f"剩余时间: {time_str}")
                                    speed_var.set(f"处理速度: {speed:.1f} 张/秒")
                                    last_update_time = current_time
                                    processed_since_last_update = 0
                                if success:
                                    retry_success += 1
                                    log(f"重试成功: {self.failed_downloads[i]['url']}")
                                else:
                                    log(f"重试失败: {self.failed_downloads[i]['url']} - {error}")
                                    # 记录新失败
                                    new_failed_downloads.append(self.failed_downloads[i])
                                status_var.set(f"重试进度: {retry_processed}/{retry_total}")
                            except Exception as e:
                                log(f"重试处理出错: {str(e)}")
                    # 更新最终统计
                    total_downloaded += retry_success
                    total_failed = len(new_failed_downloads)
                    self.failed_downloads = new_failed_downloads
                    log(f"=== 第{retry_round}轮重试完成 ===")
                    log(f"重试成功: {retry_success}, 重试失败: {total_failed}")
                else:
                    break

            # 关闭进度窗口
            progress_win.destroy()

            # 重置下载状态
            self.download_in_progress = False
            self.pause_download = False
            self.download_canceled = False

            if not self.download_canceled:
                self.log_message(f"卡面下载完成！下载: {total_downloaded}, 跳过: {total_skipped}, 失败: {total_failed}")

                # 显示最终结果
                self.show_download_result(total_downloaded, total_skipped, total_failed)
            else:
                self.log_message("下载已取消")
                messagebox.showinfo("取消", "下载已取消")

        threading.Thread(target=download_thread, daemon=True).start()
        progress_win.update()

    def show_download_result(self, downloaded, skipped, failed):
        """显示下载结果窗口"""
        # 增大窗口尺寸，确保按钮可见
        width = 700  # 增加宽度以容纳图片和文字并排
        height = 520 if failed > 0 else 420  # 增加高度

        result_win = tk.Toplevel(self)
        result_win.title("下载完成")
        result_win.geometry(f"{width}x{height}")
        result_win.transient(self)
        # 移除grab_set()以解决窗口无法通过任务栏恢复的问题
        # result_win.grab_set()
        
        # 确保窗口在最小化后可以通过任务栏图标恢复
        result_win.lift()
        result_win.focus_force()
        
        # 设置窗口最小尺寸
        result_win.minsize(600, 400)

        # 创建主内容框架，使用水平布局
        main_frame = ttk.Frame(result_win)
        main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        # 左侧文字信息框架
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

        # 显示结果信息
        result_text = f"卡面下载完成！\n下载卡面: {downloaded}\n跳过卡面: {skipped}\n失败: {failed}"
        ttk.Label(text_frame, text=result_text, wraplength=400, justify="left", 
                 font=("Arial", 12)).pack(pady=15, anchor=tk.W)

        # 如果有失败，显示提示信息
        if failed > 0:
            ttk.Label(text_frame, text="部分卡面下载失败，已自动重试。\n失败记录已保存到日志文件。", 
                     wraplength=400, justify="left", foreground="orange",
                     font=("Arial", 11)).pack(pady=10, anchor=tk.W)

        # 右侧图片框架
        img_frame = ttk.Frame(main_frame)
        img_frame.pack(side=tk.RIGHT, padx=(20, 0))

        # 根据是否有失败选择图片类型
        if failed > 0:
            # 有失败，显示sad图片
            if self.result_images["sad"]:
                img_label = ttk.Label(img_frame, image=random.choice(self.result_images["sad"]))
                img_label.pack()
        else:
            # 无失败，显示happy图片
            if self.result_images["happy"]:
                img_label = ttk.Label(img_frame, image=random.choice(self.result_images["happy"]))
                img_label.pack()

        # 按钮框架
        btn_frame = ttk.Frame(result_win)
        btn_frame.pack(pady=20, side=tk.BOTTOM)

        ttk.Button(
            btn_frame,
            text="确定",
            command=result_win.destroy,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=15)

        # 如果有失败，添加查看日志按钮
        if failed > 0:
            ttk.Button(
                btn_frame,
                text="查看失败日志",
                command=lambda: self.open_failure_log()
            ).pack(side=tk.LEFT, padx=15)

    def toggle_pause_download(self, progress_win):
        """切换下载暂停状态"""
        if self.pause_download:
            self.pause_download = False
            self.pause_button.config(text="暂停")
            self.pause_status_var.set("状态: 运行中")
        else:
            self.pause_download = True
            self.pause_button.config(text="继续")
            self.pause_status_var.set("状态: 已暂停")

    def cancel_download(self, progress_win):
        """取消下载"""
        self.download_canceled = True
        self.pause_download = False  # 确保线程可以退出
        self.download_in_progress = False  # 清除下载进行中标志
        self.pause_button.config(state=tk.DISABLED)
        self.pause_status_var.set("状态: 正在取消...")

    def process_card_download(self, card, char_id, char_name, card_dir, trim_dir, log_func, log_failure, failure_log):
        """处理单个卡面的下载 - 根据稀有度和类型采用不同下载策略"""
        result = {
            "downloaded": 0,
            "skipped": 0,
            "failed": 0
        }

        card_id = card["card_id"]
        res_name = card["resourceSetName"]
        available_servers = card.get("available_servers", [])
        server_list = ", ".join([SERVER_NAMES.get(s, s) for s in available_servers])

        log_func(f"卡面ID: {card_id} - 可用服务器: {server_list if server_list else '未知'}")

        # 1. 根据批量下载用户设置决定图片类型
        type_mode = getattr(self, 'batch_type_var', None)
        stage_mode = getattr(self, 'batch_stage_var', None)
        if type_mode is not None and stage_mode is not None:
            type_mode = type_mode.get()
            stage_mode = stage_mode.get()
            image_types = []
            # 1-2星卡面只能下载特训前
            if card["rarity"] <= 2:
                if type_mode == "normal":
                    if stage_mode == "normal" or stage_mode == "all":
                        image_types = ["card_normal.png"]
                elif type_mode == "trim":
                    if stage_mode == "normal" or stage_mode == "all":
                        image_types = ["trim_normal.png"]
                else:  # all
                    if stage_mode == "normal" or stage_mode == "all":
                        image_types = ["card_normal.png", "trim_normal.png"]
                # 1-2星卡面没有特训后
                search_type = "card_normal.png"
            # 生日/闪限卡面只能下载特训后
            elif card["type"] in ["birthday", "kirafes"]:
                if type_mode == "normal":
                    if stage_mode == "after" or stage_mode == "all":
                        image_types = ["card_after_training.png"]
                elif type_mode == "trim":
                    if stage_mode == "after" or stage_mode == "all":
                        image_types = ["trim_after_training.png"]
                else:  # all
                    if stage_mode == "after" or stage_mode == "all":
                        image_types = ["card_after_training.png", "trim_after_training.png"]
                # 生日/闪限卡面没有特训前
                search_type = "card_after_training.png"
            # 其他卡面按用户选择
            else:
                if type_mode == "normal":
                    if stage_mode == "normal":
                        image_types = ["card_normal.png"]
                    elif stage_mode == "after":
                        image_types = ["card_after_training.png"]
                    else:
                        image_types = ["card_normal.png", "card_after_training.png"]
                elif type_mode == "trim":
                    if stage_mode == "normal":
                        image_types = ["trim_normal.png"]
                    elif stage_mode == "after":
                        image_types = ["trim_after_training.png"]
                    else:
                        image_types = ["trim_normal.png", "trim_after_training.png"]
                else:  # all
                    if stage_mode == "normal":
                        image_types = ["card_normal.png", "trim_normal.png"]
                    elif stage_mode == "after":
                        image_types = ["card_after_training.png", "trim_after_training.png"]
                    else:
                        image_types = [
                            "card_normal.png", "card_after_training.png",
                            "trim_normal.png", "trim_after_training.png"
                        ]
                # 服务器选择类型
                if "card_normal.png" in image_types:
                    search_type = "card_normal.png"
                elif "card_after_training.png" in image_types:
                    search_type = "card_after_training.png"
                elif image_types:
                    search_type = image_types[0]
                else:
                    search_type = "card_normal.png"
            # 如果类型过滤后没有可下载项，直接跳过
            if not image_types:
                return result

        # 2. 查找有效的服务器
        selected_server = None
        servers_to_try = available_servers if available_servers else SERVERS
        network_error_count = 0  # 统计网络错误次数
        server_found = False
        tried_card_normal = False
        # 新增：特殊回退逻辑
        if "card_normal.png" in image_types:
            tried_card_normal = True
            for server in servers_to_try:
                if self.download_canceled:
                    return result
                base_url = f"https://bestdori.com/assets/{server}/characters/resourceset/{res_name}_rip/card_normal.png"
                try:
                    response = requests.get(base_url, timeout=10, stream=True)
                    if response.status_code == 200:
                        content = b""
                        for chunk in response.iter_content(chunk_size=1024):
                            content += chunk
                            if len(content) >= 1024:
                                break
                        if len(content) >= 512:
                            try:
                                full_response = requests.get(base_url, timeout=10)
                                if full_response.status_code == 200:
                                    file_size = len(full_response.content)
                                    log_func(f"服务器 {server} 文件大小: {file_size / 1024:.1f}KB")
                                    if file_size >= 20 * 1024:
                                        selected_server = server
                                        log_func(f"选择服务器: {SERVER_NAMES.get(selected_server, selected_server)} (文件大小: {file_size / 1024:.1f}KB)")
                                        server_found = True
                                        break
                                    else:
                                        log_func(f"跳过服务器 {server}: 文件过小 ({file_size / 1024:.1f}KB < 20KB)")
                                else:
                                    log_func(f"跳过服务器 {server}: HTTP状态 {full_response.status_code}")
                            except Exception as e:
                                log_func(f"获取服务器 {server} 文件大小失败: {str(e)}")
                        else:
                            log_func(f"跳过服务器 {server}: 文件数据不足 ({len(content)} 字节)")
                    else:
                        log_func(f"跳过服务器 {server}: HTTP状态 {response.status_code}")
                except Exception as e:
                    network_error_count += 1
                    log_func(f"检查服务器 {server} 失败: {str(e)}")
            # 如果没找到，再用card_after_training.png
            if not server_found:
                log_func("card_normal.png所有服务器都不可用，尝试用card_after_training.png确定服务器")
                for server in servers_to_try:
                    if self.download_canceled:
                        return result
                    base_url = f"https://bestdori.com/assets/{server}/characters/resourceset/{res_name}_rip/card_after_training.png"
                    try:
                        response = requests.get(base_url, timeout=10, stream=True)
                        if response.status_code == 200:
                            content = b""
                            for chunk in response.iter_content(chunk_size=1024):
                                content += chunk
                                if len(content) >= 1024:
                                    break
                            if len(content) >= 512:
                                try:
                                    full_response = requests.get(base_url, timeout=10)
                                    if full_response.status_code == 200:
                                        file_size = len(full_response.content)
                                        log_func(f"服务器 {server} 文件大小: {file_size / 1024:.1f}KB")
                                        if file_size >= 20 * 1024:
                                            selected_server = server
                                            log_func(f"选择服务器: {SERVER_NAMES.get(selected_server, selected_server)} (文件大小: {file_size / 1024:.1f}KB)")
                                            server_found = True
                                            break
                                        else:
                                            log_func(f"跳过服务器 {server}: 文件过小 ({file_size / 1024:.1f}KB < 20KB)")
                                    else:
                                        log_func(f"跳过服务器 {server}: HTTP状态 {full_response.status_code}")
                                except Exception as e:
                                    log_func(f"获取服务器 {server} 文件大小失败: {str(e)}")
                            else:
                                log_func(f"跳过服务器 {server}: 文件数据不足 ({len(content)} 字节)")
                        else:
                            log_func(f"跳过服务器 {server}: HTTP状态 {response.status_code}")
                    except Exception as e:
                        network_error_count += 1
                        log_func(f"检查服务器 {server} 失败: {str(e)}")
                # 如果用card_after_training.png找到服务器，只下载训练后两种
                if server_found:
                    # 只选普通卡面时，回退只下载card_after_training.png
                    if image_types == ["card_normal.png"]:
                        image_types = ["card_after_training.png"]
                    # 只选无背景卡面时，回退只下载trim_after_training.png
                    elif image_types == ["trim_normal.png"]:
                        image_types = ["trim_after_training.png"]
                    # 普通+无背景都选时，回退下载训练后两种
                    else:
                        # 只保留训练后类型
                        new_types = []
                        if "card_after_training.png" in ["card_after_training.png", "trim_after_training.png"]:
                            new_types.append("card_after_training.png")
                        if "trim_after_training.png" in ["card_after_training.png", "trim_after_training.png"]:
                            new_types.append("trim_after_training.png")
                        image_types = new_types if new_types else ["card_after_training.png", "trim_after_training.png"]
        else:
            # 原有逻辑
            for server in servers_to_try:
                if self.download_canceled:
                    return result
                base_url = f"https://bestdori.com/assets/{server}/characters/resourceset/{res_name}_rip/{search_type}"
                try:
                    response = requests.get(base_url, timeout=10, stream=True)
                    if response.status_code == 200:
                        content = b""
                        for chunk in response.iter_content(chunk_size=1024):
                            content += chunk
                            if len(content) >= 1024:
                                break
                        if len(content) >= 512:
                            try:
                                full_response = requests.get(base_url, timeout=10)
                                if full_response.status_code == 200:
                                    file_size = len(full_response.content)
                                    log_func(f"服务器 {server} 文件大小: {file_size / 1024:.1f}KB")
                                    if file_size >= 20 * 1024:
                                        selected_server = server
                                        log_func(f"选择服务器: {SERVER_NAMES.get(selected_server, selected_server)} (文件大小: {file_size / 1024:.1f}KB)")
                                        server_found = True
                                        break
                                    else:
                                        log_func(f"跳过服务器 {server}: 文件过小 ({file_size / 1024:.1f}KB < 20KB)")
                                else:
                                    log_func(f"跳过服务器 {server}: HTTP状态 {full_response.status_code}")
                            except Exception as e:
                                log_func(f"获取服务器 {server} 文件大小失败: {str(e)}")
                        else:
                            log_func(f"跳过服务器 {server}: 文件数据不足 ({len(content)} 字节)")
                    else:
                        log_func(f"跳过服务器 {server}: HTTP状态 {response.status_code}")
                except Exception as e:
                    network_error_count += 1
                    log_func(f"检查服务器 {server} 失败: {str(e)}")

        # 3. 如果没有找到有效服务器，判定为下载失败
        if not selected_server:
            if network_error_count > 0:
                # 如果有网络错误，判定为网络连接失败
                log_func(f"网络连接失败，无法访问任何服务器")
                result["failed"] = len(image_types)
                
                # 记录失败日志
                self.download_logger.log_failure(card_id, "网络连接失败", "无法访问任何服务器", "网络错误")
                
                # 添加到失败日志
                failure_log.append({
                    "card_id": card_id,
                    "url": "网络连接失败",
                    "error": "无法访问任何服务器"
                })
                
                # 记录失败信息
                log_failure(f"卡面 {card_id} 下载失败: 网络连接失败")
            else:
                # 如果没有网络错误但也没有可用服务器，可能是服务器问题
                log_func(f"所有服务器均不可用，下载失败")
                result["failed"] = len(image_types)
                
                # 记录失败日志
                self.download_logger.log_failure(card_id, "服务器选择失败", "所有服务器均不可用", "无可用服务器")
                
                # 添加到失败日志
                failure_log.append({
                    "card_id": card_id,
                    "url": "服务器选择失败",
                    "error": "所有服务器均不可用"
                })
                
                # 记录失败信息
                log_failure(f"卡面 {card_id} 下载失败: 所有服务器均不可用")
            
            return result

        # 4. 下载所有需要的图片类型
        for img_type in image_types:
            # 检查是否已取消下载
            if self.download_canceled:
                return result

            # 确定保存目录
            if "card_" in img_type:
                save_dir = card_dir
            else:
                save_dir = trim_dir

            # 构建文件名
            file_name = f"{char_name}_{card_id}_{self.get_image_type_short(img_type)}.png"
            safe_file_name = sanitize_filename(file_name)
            save_path = os.path.join(save_dir, safe_file_name)

            # 检查文件是否已存在
            if os.path.exists(save_path):
                log_func(f"跳过已存在文件: {safe_file_name}")
                result["skipped"] += 1
                self.download_logger.log_skip(card_id, save_path, "文件已存在", selected_server)
                continue

            # 构建完整URL
            img_url = f"https://bestdori.com/assets/{selected_server}/characters/resourceset/{res_name}_rip/{img_type}"

            # 下载图片
            log_func(f"下载: {img_url}")
            success, error = self.download_image(img_url, save_path, log_func, card_id, selected_server)

            if success and (error is None or error == ""):
                result["downloaded"] += 1
            elif success and error and "文件过小" in error:
                result["skipped"] += 1
                self.download_logger.log_skip(card_id, img_url, "文件过小", selected_server)
            else:
                result["failed"] += 1
                log_failure(f"下载失败: {img_url}")
                log_failure(f"错误: {error}")
                self.failed_downloads.append({
                    "url": img_url,
                    "save_path": save_path,
                    "error": error,
                    "card_id": card_id,
                    "server": selected_server
                })
                failure_log.append({
                    "card_id": card_id,
                    "url": img_url,
                    "error": error
                })

        return result

    def setup_upscale_tab(self):
        """卡面超分标签页"""
        # 扫描按钮和搜索框
        scan_frame = ttk.Frame(self.upscale_tab)
        scan_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(scan_frame, text="扫描超分进度", command=self.scan_upscale_progress).pack(side=tk.RIGHT, padx=5)

        # 打开文件夹按钮
        ttk.Button(
            scan_frame,
            text="打开文件夹",
            command=self.open_bangdream_folder
        ).pack(side=tk.RIGHT, padx=5)

        # 超分界面搜索框
        ttk.Label(scan_frame, text="搜索角色:").pack(side=tk.LEFT, padx=5)
        self.upscale_search_var = tk.StringVar()
        upscale_search_entry = ttk.Entry(scan_frame, textvariable=self.upscale_search_var, width=30)
        upscale_search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(scan_frame, text="搜索", command=self.filter_upscale_chars).pack(side=tk.LEFT, padx=5)
        ttk.Button(scan_frame, text="重置", command=self.reset_upscale_search).pack(side=tk.LEFT, padx=5)

        # 实时搜索
        def on_upscale_var_change(*args):
            self.filter_upscale_chars()

        self.upscale_search_var.trace_add('write', lambda *args: on_upscale_var_change())

        # 超分设置框架
        upscale_settings_frame = ttk.LabelFrame(self.upscale_tab, text="超分设置")
        upscale_settings_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # 新增：横向主Frame
        settings_main_frame = ttk.Frame(upscale_settings_frame)
        settings_main_frame.pack(fill=tk.X, padx=0, pady=0)

        # 左侧：引擎选择+帮助
        left_frame = ttk.Frame(settings_main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0, anchor="n")
        engine_frame = ttk.Frame(left_frame)
        engine_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(engine_frame, text="超分引擎: ").pack(side=tk.LEFT, padx=5)
        self.upscale_engine_combo = ttk.Combobox(engine_frame, textvariable=self.upscale_engine_var, width=20, state="readonly")
        self.upscale_engine_combo['values'] = ("Real-ESRGAN", "waifu2x")
        self.upscale_engine_combo.pack(side=tk.LEFT, padx=5)
        self.upscale_engine_combo.bind("<<ComboboxSelected>>", self.on_upscale_engine_changed)
        # 帮助按钮
        help_frame = ttk.Frame(left_frame)
        help_frame.pack(fill=tk.X, padx=5, pady=0)
        ttk.Button(
            help_frame,
            text="❓超分设置帮助",
            command=self.show_upscale_settings_help,
            width=20
        ).pack(side=tk.LEFT, pady=5)

        # 右侧：具体引擎设置
        right_frame = ttk.Frame(settings_main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0, anchor="n")
        # Real-ESRGAN设置子框架
        self.realesrgan_frame = ttk.LabelFrame(right_frame, text="Real-ESRGAN 设置")
        self.realesrgan_frame.pack(fill=tk.X, padx=5, pady=5)
        # ...原有Real-ESRGAN设置内容...
        # waifu2x设置子框架
        self.waifu2x_frame = ttk.LabelFrame(right_frame, text="waifu2x 设置")
        # ...原有waifu2x设置内容...
        self.waifu2x_frame.pack_forget()
        
        # 暂时隐藏两个框架，等所有内容创建完成后再显示
        self.realesrgan_frame.pack_forget()
        self.waifu2x_frame.pack_forget()

        # 模型选择和输出格式选择
        model_frame = ttk.Frame(self.realesrgan_frame)
        model_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(model_frame, text="超分模型: ").pack(side=tk.LEFT, padx=5)
        model_combo = ttk.Combobox(model_frame, textvariable=self.realesrgan_model_var, width=25, state="readonly")
        model_combo['values'] = (
            'realesrgan-x4plus-anime',  # 动漫优化模型
            'realesrgan-x4plus',        # 通用模型
            'realesr-animevideov3-x2',  # 动漫视频模型2x
            'realesr-animevideov3-x3',  # 动漫视频模型3x
            'realesr-animevideov3-x4'   # 动漫视频模型4x
        )
        model_combo.pack(side=tk.LEFT, padx=5)
        model_combo.bind("<<ComboboxSelected>>", self.on_model_changed)
        
        # 普通卡面输出格式选择
        ttk.Label(model_frame, text="普通卡面输出格式: ").pack(side=tk.LEFT, padx=(20,5))
        self.realesrgan_normal_format_var = tk.StringVar(value=self.realesrgan_normal_format)
        normal_format_combo = ttk.Combobox(model_frame, textvariable=self.realesrgan_normal_format_var, width=10, state="readonly")
        normal_format_combo['values'] = ('png', 'jpg', 'webp')
        normal_format_combo.pack(side=tk.LEFT, padx=5)
        normal_format_combo.bind("<<ComboboxSelected>>", self.on_realesrgan_normal_format_changed)

        # 进度显示框架
        progress_frame = ttk.LabelFrame(self.upscale_tab, text="选择角色")
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建滚动区域
        canvas = tk.Canvas(progress_frame)
        self.upscale_frame = ttk.Frame(canvas)

        self.upscale_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.upscale_frame, anchor="nw")

        # 添加滚轮支持
        scrollbar = self.add_scroll_support(canvas, self.upscale_frame)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 操作按钮框架
        btn_frame = ttk.Frame(self.upscale_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        # 添加全选/全不选按钮
        ttk.Button(btn_frame, text="全选普通卡面", command=self.select_all_normal).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="全不选普通卡面", command=self.deselect_all_normal).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="全选无背景卡面", command=self.select_all_trim).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="全不选无背景卡面", command=self.deselect_all_trim).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="开始超分", style="Accent.TButton", command=self.start_upscale).pack(side=tk.RIGHT, padx=5)

        



        # 自动扫描超分进度
        self.scan_upscale_progress()

        # ====== waifu2x设置区域 ======
        self.waifu2x_frame = ttk.LabelFrame(right_frame, text="waifu2x 设置")
        
        # 模型文件选择和输出格式选择
        waifu_model_frame = ttk.Frame(self.waifu2x_frame)
        waifu_model_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(waifu_model_frame, text="模型文件: ").pack(side=tk.LEFT, padx=5)
        # 根据配置的模型目录选择对应的默认模型
        if self.waifu2x_model_dir == "models-upconv_7_anime_style_art_rgb":
            default_model = self.waifu2x_model_anime
        elif self.waifu2x_model_dir == "models-upconv_7_photo":
            default_model = self.waifu2x_model_photo
        else:  # models-cunet
            default_model = self.waifu2x_model_cunet
            
        self.waifu_model_var = tk.StringVar(value=default_model)
        # 自动扫描模型文件夹，只保留noise0/1/2/3_scale2.0x_model和scale2.0x_model
        waifu_model_dir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "waifu2x-ncnn-vulkan", self.waifu2x_model_dir)
        waifu_model_files = []
        waifu_model_noise_map = {}
        # 先加noise0-3
        for n in range(0, 4):
            fname = f"noise{n}_scale2.0x_model"
            if os.path.exists(os.path.join(waifu_model_dir, fname + ".bin")):
                waifu_model_files.append(fname)
                waifu_model_noise_map[fname] = n
        # 再加scale2.0x_model（无降噪）
        fname = "scale2.0x_model"
        if os.path.exists(os.path.join(waifu_model_dir, fname + ".bin")):
            waifu_model_files.append(fname)
            waifu_model_noise_map[fname] = -1
        if waifu_model_files and default_model not in waifu_model_files:
            self.waifu_model_var.set(waifu_model_files[0])
        self.waifu_model_combo = ttk.Combobox(waifu_model_frame, textvariable=self.waifu_model_var, width=30, state="readonly")
        self.waifu_model_combo['values'] = waifu_model_files
        self.waifu_model_combo.pack(side=tk.LEFT, padx=5)
        self.waifu_model_combo.bind("<<ComboboxSelected>>", self.on_waifu_model_changed)
        self.waifu_model_noise_map = waifu_model_noise_map
        
        # 普通卡面输出格式选择
        ttk.Label(waifu_model_frame, text="普通卡面输出格式: ").pack(side=tk.LEFT, padx=(20,5))
        self.waifu2x_normal_format_var = tk.StringVar(value=self.waifu2x_normal_format)
        waifu_normal_format_combo = ttk.Combobox(waifu_model_frame, textvariable=self.waifu2x_normal_format_var, width=10, state="readonly")
        waifu_normal_format_combo['values'] = ('png', 'jpg', 'webp')
        waifu_normal_format_combo.pack(side=tk.LEFT, padx=5)
        waifu_normal_format_combo.bind("<<ComboboxSelected>>", self.on_waifu2x_normal_format_changed)

        # 噪声等级（隐藏，但保留变量用于内部处理）
        self.waifu_noise_var = tk.IntVar()
        # 初始化噪声等级
        self.update_waifu_noise_options(self.waifu_model_var.get())


        # 根据配置文件设置初始引擎显示
        if self.upscale_engine == "Real-ESRGAN":
            self.realesrgan_frame.pack(fill=tk.X, padx=5, pady=5)
            self.waifu2x_frame.pack_forget()
        else:
            self.realesrgan_frame.pack_forget()
            self.waifu2x_frame.pack(fill=tk.X, padx=5, pady=5)

    def scan_upscale_progress(self):
        """扫描超分进度 - 使用线程池优化"""
        self.log_message("正在扫描超分进度...")

        # 清空现有内容
        for widget in self.upscale_frame.winfo_children():
            widget.destroy()

        # 显示扫描进度条
        progress_frame = ttk.Frame(self.upscale_frame)
        progress_frame.pack(fill=tk.X, padx=10, pady=20)

        ttk.Label(progress_frame, text="扫描中...").pack(side=tk.LEFT, padx=5)
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, expand=True, padx=5)
        self.update()

        # 存储所有角色路径
        self.all_upscale_chars = []

        # 扫描所有乐队和角色
        bands = [b for b in os.listdir(self.bangdream_dir)
                 if os.path.isdir(os.path.join(self.bangdream_dir, b))]

        # 使用线程池并行扫描
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
            futures = []
            for band in bands:
                band_path = os.path.join(self.bangdream_dir, band)
                futures.append(executor.submit(self.scan_characters, band_path))

            # 处理结果并更新进度
            total = len(futures)
            for i, future in enumerate(futures):
                self.all_upscale_chars.extend(future.result())
                progress = (i + 1) / total * 100
                progress_var.set(progress)
                self.update()

        # 移除进度条
        progress_frame.destroy()

        # 显示所有角色
        self.display_upscale_progress(self.all_upscale_chars)
        self.log_message(f"扫描完成！找到 {len(self.all_upscale_chars)} 个角色")

    def scan_characters(self, band_path):
        """扫描单个乐队中的角色"""
        characters = []
        for char in os.listdir(band_path):
            char_path = os.path.join(band_path, char)
            if os.path.isdir(char_path):
                characters.append(char_path)
        return characters

    def on_format_changed(self, event=None):
        """当超分格式改变时重新扫描进度"""
        self.log_message("超分格式已更改，重新扫描进度...")
        self.scan_upscale_progress()

    def select_all_normal(self):
        """全选所有普通卡面"""
        if hasattr(self, 'card_vars'):
            for var in self.card_vars.values():
                var.set(True)
            # 取消所有部分选择
            self.selected_normal_images.clear()
            # 更新计数显示
            for char_path in self.card_vars:
                card_source = self.get_card_dir(char_path)
                if os.path.exists(card_source):
                    card_total, _ = self.calculate_progress(card_source, self.get_upscaled_card_dir(char_path),
                                                            self.normal_format_var.get())
                    self.selected_counts[char_path]["卡面"].set(card_total)

    def deselect_all_normal(self):
        """全不选所有普通卡面"""
        if hasattr(self, 'card_vars'):
            for var in self.card_vars.values():
                var.set(False)
            # 取消所有部分选择
            self.selected_normal_images.clear()
            # 更新计数显示
            for char_path in self.card_vars:
                self.selected_counts[char_path]["卡面"].set(0)

    def select_all_trim(self):
        """全选所有无背景卡面"""
        if hasattr(self, 'trim_vars'):
            for var in self.trim_vars.values():
                var.set(True)
            # 取消所有部分选择
            self.selected_trim_images.clear()
            # 更新计数显示
            for char_path in self.trim_vars:
                trim_source = self.get_trim_dir(char_path)
                if os.path.exists(trim_source):
                    trim_total, _ = self.calculate_progress(trim_source, self.get_upscaled_trim_dir(char_path),
                                                            self.trim_format_var.get())
                    self.selected_counts[char_path]["无背景卡面"].set(trim_total)

    def deselect_all_trim(self):
        """全不选所有无背景卡面"""
        if hasattr(self, 'trim_vars'):
            for var in self.trim_vars.values():
                var.set(False)
            # 取消所有部分选择
            self.selected_trim_images.clear()
            # 更新计数显示
            for char_path in self.trim_vars:
                self.selected_counts[char_path]["无背景卡面"].set(0)

    def show_upscale_settings_help(self):
        """显示超分设置帮助信息"""
        help_text = """超分设置说明：

省流版本：
如果你有独立显卡，想要追求更高的画质，
可以使用Real-ESRGAN引擎，其余设置默认即可
（经过测试，轻薄本的11代i5核显也能跑，只不过速度非常感人
如果你时间充足，并且不害怕电脑会出现问题，也可以使用）

如果你没有独立显卡，或显卡性能较低，对画质无很高要求
可以使用waifu2x引擎，其余设置默认即可
        

详细说明：
        
🔧 模型设置：

    Real-ESRGAN：
• realesrgan-x4plus-anime：效果最好的模型，同时速度很慢
（5060 laptop 超分50张需要大概100秒的时间）
• realesr-animevideov3-x2/3/4：视频模型，但也可以超分图片
    支持2x/3x/4x缩放

    Waifu2x：
• 速度极快，但所有模型最高只支持2x
（5060 laptop 超分50张需要不到10秒的时间）
• 噪声等级越高，降噪效果越好，-1为无降噪，建议用3

🔍 放大倍率

• 普通卡面原始分辨率为1334×1002 
    4x：5336×4008
    3x：4002×3006
    2x：2668×2004
• 普通卡面原始分辨率为1024×1024
    4x：4096×4096
    3x：3072×3072
    2x：2048×2048

📤 输出格式：

普通卡面 :
• PNG格式: 无损质量，文件较大
• JPG格式: 有损压缩，文件较小 (推荐)

无背景卡面 :
• PNG格式: 支持透明通道 (推荐)
• JPG格式: 不支持透明通道，背景会变成白色
"""
        messagebox.showinfo("超分设置帮助", help_text)

    def filter_upscale_chars(self):
        """根据搜索条件过滤超分角色列表，支持外号和简称"""
        search_text = self.upscale_search_var.get().lower()
        if not search_text:
            self.scan_upscale_progress()
            return
        if not hasattr(self, 'all_upscale_chars'):
            self.scan_upscale_progress()
        filtered_chars = []
        for char_path in self.all_upscale_chars:
            char_name = os.path.basename(char_path)
            band_name = os.path.basename(os.path.dirname(char_path))
            aliases = CHARACTER_ALIASES.get(char_name, [])
            all_keywords = [char_name.lower(), band_name.lower()] + [a.lower() for a in aliases]
            if any(search_text in kw for kw in all_keywords):
                filtered_chars.append(char_path)
        self.display_upscale_progress(filtered_chars)

    def reset_upscale_search(self):
        """重置超分搜索"""
        self.upscale_search_var.set("")
        if hasattr(self, 'all_upscale_chars'):
            self.display_upscale_progress(self.all_upscale_chars)

    def display_upscale_progress(self, char_paths):
        """显示超分进度（乐队图标、复选框彻底左右居中，总计一列在最右侧，统计全部）"""
        # 清空现有内容
        for widget in self.upscale_frame.winfo_children():
            widget.destroy()

        # 列定义
        columns = [
            ("乐队", 6),
            ("角色名", 14),
            ("全选卡面", 10),
            ("部分选择", 8),
            ("进度", 8),
            ("全选无背景", 10),
            ("部分选择", 8),
            ("进度", 8),
            ("共选择", 8)
        ]
        # 表头
        for col, (text, width) in enumerate(columns):
            ttk.Label(self.upscale_frame, text=text, width=width, anchor="center", font=("微软雅黑", 11, "bold")).grid(row=0, column=col, padx=2, pady=2, sticky="nsew")

        # 存储角色UI元素
        self.card_vars = {}
        self.trim_vars = {}
        self.selected_counts = getattr(self, 'selected_counts', {})

        for row, char_path in enumerate(char_paths, start=1):
            # 初始化计数器，兼容所有老逻辑
            if char_path not in self.selected_counts:
                self.selected_counts[char_path] = {
                    "卡面": tk.IntVar(value=0),
                    "无背景卡面": tk.IntVar(value=0),
                    "总计": tk.IntVar(value=0)
                }
            char_name = os.path.basename(char_path)
            band_name = os.path.basename(os.path.dirname(char_path))
            # 乐队图标左右绝对居中
            band_frame = ttk.Frame(self.upscale_frame)
            band_frame.grid(row=row, column=0, padx=2, pady=4, sticky="nsew")
            self.upscale_frame.grid_columnconfigure(0, weight=1)  # 让乐队图标列可拉伸
            band_frame.grid_columnconfigure(1, weight=1)
            ttk.Label(band_frame, text="").grid(row=0, column=0, sticky="ew")
            band_icon_id = {
                "Poppin'Party": 1,
                "Afterglow": 2,
                "Hello, Happy World!": 3,
                "Pastel_Palettes": 4,
                "Roselia": 5,
                "Morfonica": 6,
                "RAISE_A_SUILEN": 7,
                "MyGO!!!!!": 8
            }.get(band_name)
            if band_icon_id and hasattr(self, 'band_icons') and band_icon_id in self.band_icons:
                ttk.Label(band_frame, image=self.band_icons[band_icon_id], anchor="center").grid(row=0, column=1, sticky="ew")
            else:
                ttk.Label(band_frame, text=band_name, anchor="center").grid(row=0, column=1, sticky="ew")
            ttk.Label(band_frame, text="").grid(row=0, column=2, sticky="ew")

            # 角色名（确保显示且不被遮挡）
            self.upscale_frame.grid_columnconfigure(1, weight=2)  # 角色名列更宽
            ttk.Label(self.upscale_frame, text=char_name, width=14, anchor="center", font=("微软雅黑", 11, )).grid(row=row, column=1, padx=2, pady=4, sticky="nsew")

            # 全选卡面复选框左右绝对居中且点击空白不触发
            card_var = tk.BooleanVar(value=False)
            self.card_vars[char_path] = card_var
            cardcol_frame = ttk.Frame(self.upscale_frame)
            cardcol_frame.grid(row=row, column=2, padx=2, pady=4, sticky="nsew")
            self.upscale_frame.grid_columnconfigure(2, weight=1)
            cardcol_frame.grid_columnconfigure(1, weight=1)

            card_chk = ttk.Checkbutton(cardcol_frame, text="", variable=card_var, command=lambda cp=char_path: self.update_upscale_count(cp))
            card_chk.grid(row=0, column=1, sticky="")

            # 卡面部分选择
            card_btn = ttk.Button(self.upscale_frame, text="预览", width=6, command=lambda cp=char_path: self.select_cards(cp, "卡面", True))
            card_btn.grid(row=row, column=3, padx=2, pady=4, sticky="nsew")

            # 卡面进度
            card_source = self.get_card_dir(char_path)
            card_target = self.get_upscaled_card_dir(char_path)
            # 根据当前引擎选择对应的输出格式
            if self.upscale_engine == "Real-ESRGAN":
                card_format = self.realesrgan_normal_format
            else:  # waifu2x
                card_format = self.waifu2x_normal_format
            card_total, card_done = self.calculate_progress(card_source, card_target, card_format)
            card_progress = f"{card_done}/{card_total}" if card_total > 0 else "0/0"
            ttk.Label(self.upscale_frame, text=card_progress, width=8, anchor="center").grid(row=row, column=4, padx=2, pady=4, sticky="nsew")

            # 全选无背景复选框左右绝对居中且点击空白不触发
            trim_var = tk.BooleanVar(value=False)
            self.trim_vars[char_path] = trim_var
            trimcol_frame = ttk.Frame(self.upscale_frame)
            trimcol_frame.grid(row=row, column=5, padx=2, pady=4, sticky="nsew")
            self.upscale_frame.grid_columnconfigure(5, weight=1)
            trimcol_frame.grid_columnconfigure(1, weight=1)
            ttk.Label(trimcol_frame, text="").grid(row=0, column=0, sticky="ew")
            trim_chk = ttk.Checkbutton(trimcol_frame, text="", variable=trim_var, command=lambda cp=char_path: self.update_upscale_count(cp))
            trim_chk.grid(row=0, column=1, sticky="")
            ttk.Label(trimcol_frame, text="").grid(row=0, column=2, sticky="ew")

            # 无背景部分选择
            trim_btn = ttk.Button(self.upscale_frame, text="预览", width=6, command=lambda cp=char_path: self.select_cards(cp, "无背景卡面", True))
            trim_btn.grid(row=row, column=6, padx=2, pady=4, sticky="nsew")

            # 无背景进度
            trim_source = self.get_trim_dir(char_path)
            trim_target = self.get_upscaled_trim_dir(char_path)
            # 根据当前引擎选择对应的输出格式
            if self.upscale_engine == "Real-ESRGAN":
                trim_format = self.realesrgan_trim_format
            else:  # waifu2x
                trim_format = self.waifu2x_trim_format
            trim_total, trim_done = self.calculate_progress(trim_source, trim_target, trim_format)
            trim_progress = f"{trim_done}/{trim_total}" if trim_total > 0 else "0/0"
            ttk.Label(self.upscale_frame, text=trim_progress, width=8, anchor="center").grid(row=row, column=7, padx=2, pady=4, sticky="nsew")

            # 总计（普通+无背景）
            total_label = ttk.Label(self.upscale_frame, textvariable=self.selected_counts[char_path]["总计"], width=8, anchor="center", font=("微软雅黑", 11))
            total_label.grid(row=row, column=8, padx=2, pady=4, sticky="nsew")

            # 初始刷新
            self.update_upscale_count(char_path)

            # 添加分割线
            sep = ttk.Separator(self.upscale_frame, orient='horizontal')
            sep.grid(row=row+1, column=0, columnspan=len(columns), sticky='ew', padx=2, pady=1)

        # 让所有列都可拉伸
        for col in range(len(columns)):
            self.upscale_frame.grid_columnconfigure(col, weight=1)

    def select_cards(self, char_path, folder_type, refresh_total=False):
        """选择要超分的图片，选择后自动关闭并刷新总计"""
        source_dir = os.path.join(char_path, folder_type)
        # 确定目标目录和格式
        if folder_type == "卡面":
            target_dir = self.get_upscaled_card_dir(char_path)
            # 根据当前引擎选择对应的输出格式
            if self.upscale_engine == "Real-ESRGAN":
                output_format = self.realesrgan_normal_format
            else:  # waifu2x
                output_format = self.waifu2x_normal_format
        else:
            target_dir = self.get_upscaled_trim_dir(char_path)
            # 根据当前引擎选择对应的输出格式
            if self.upscale_engine == "Real-ESRGAN":
                output_format = self.realesrgan_trim_format
            else:  # waifu2x
                output_format = self.waifu2x_trim_format
        if not os.path.exists(source_dir):
            self.show_custom_message("提示", f"没有找到{folder_type}文件夹", msg_type='normal')
            return
        # 预览窗口的图片过滤逻辑
        def get_image_files():
            all_files = [(filename, os.path.join(source_dir, filename)) for filename in os.listdir(source_dir) if filename.lower().endswith(IMAGE_EXTENSIONS)]
            if not hasattr(self, 'hide_upscaled_var'):
                self.hide_upscaled_var = tk.BooleanVar(value=False)
            if not self.hide_upscaled_var.get():
                return all_files
            # 只显示未超分的图片
            upscaled_names = set()
            if os.path.exists(target_dir):
                for fname in os.listdir(target_dir):
                    if fname.lower().endswith(output_format):
                        # 去掉模型后缀
                        name_part = fname.rsplit('_', 1)[0]
                        upscaled_names.add(name_part)
            filtered = []
            for filename, filepath in all_files:
                name_part = os.path.splitext(filename)[0]
                if name_part not in upscaled_names:
                    filtered.append((filename, filepath))
            return filtered
        def refresh_images():
            image_files = get_image_files()
            self.set_thumb_size(5, thumb_frame, image_files, folder_type)
        image_files = get_image_files()
        if not image_files:
            self.show_custom_message("提示", f"没有需要超分的{folder_type}图片", msg_type='normal')
            return
        selection_win = tk.Toplevel(self)
        selection_win.title(f"选择{folder_type}图片 - {os.path.basename(char_path)}")
        selection_win.geometry("1000x700")
        selection_win.state('zoomed')
        selection_win.transient(self)
        selection_win.grab_set()
        self.selection_vars = {}
        for img in image_files:
            source_file = img[1]
            if folder_type == "卡面":
                selected = source_file in self.selected_normal_images.get(char_path, [])
            else:
                selected = source_file in self.selected_trim_images.get(char_path, [])
            self.selection_vars[source_file] = tk.BooleanVar(value=selected)
        self.selection_win = selection_win
        self.thumb_labels = {}
        btn_frame = ttk.Frame(selection_win)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        # 删除隐藏已超分图片Checkbutton
        ttk.Label(btn_frame, text="预览大小:").pack(side=tk.LEFT, padx=5)
        small_btn = ttk.Button(
            btn_frame,
            text="小",
            width=3,
            command=lambda: self.set_thumb_size(8, thumb_frame, image_files, folder_type)
        )
        small_btn.pack(side=tk.LEFT, padx=5)
        medium_btn = ttk.Button(
            btn_frame,
            text="中",
            width=3,
            command=lambda: self.set_thumb_size(5, thumb_frame, image_files, folder_type)
        )
        medium_btn.pack(side=tk.LEFT, padx=5)
        large_btn = ttk.Button(
            btn_frame,
            text="大",
            width=3,
            command=lambda: self.set_thumb_size(3, thumb_frame, image_files, folder_type)
        )
        large_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="全选", command=lambda: self.toggle_all_selection(True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="全不选", command=lambda: self.toggle_all_selection(False)).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame,
            text="确定",
            command=lambda: self.save_selection(char_path, folder_type, selection_win, refresh_total)
        ).pack(side=tk.RIGHT, padx=5)
        container = ttk.Frame(selection_win)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        canvas = tk.Canvas(container)
        thumb_frame = ttk.Frame(canvas)
        thumb_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=thumb_frame, anchor="nw")
        scrollbar = self.add_scroll_support(canvas, thumb_frame)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.set_thumb_size(5, thumb_frame, image_files, folder_type)

    def save_selection(self, char_path, folder_type, window, refresh_total=False):
        """保存选择的图片，选择后自动关闭并刷新总计"""
        selected_files = []
        for filepath, var in self.selection_vars.items():
            if var.get():
                selected_files.append(filepath)
        if folder_type == "卡面":
            self.selected_normal_images[char_path] = selected_files
        else:
            self.selected_trim_images[char_path] = selected_files
        window.destroy()
        self.update_upscale_count(char_path)

    def update_upscale_count(self, char_path):
        """刷新单个角色的总计（普通+无背景）"""
        card_source = self.get_card_dir(char_path)
        card_target = self.get_upscaled_card_dir(char_path)
        trim_source = self.get_trim_dir(char_path)
        trim_target = self.get_upscaled_trim_dir(char_path)
        # 根据当前引擎选择对应的输出格式
        if self.upscale_engine == "Real-ESRGAN":
            card_format = self.realesrgan_normal_format
            trim_format = self.realesrgan_trim_format
        else:  # waifu2x
            card_format = self.waifu2x_normal_format
            trim_format = self.waifu2x_trim_format
        card_total, card_done = self.calculate_progress(card_source, card_target, card_format)
        trim_total, trim_done = self.calculate_progress(trim_source, trim_target, trim_format)
        card_count = 0
        trim_count = 0
        if self.card_vars[char_path].get():
            card_count = card_total - card_done
        elif hasattr(self, 'selected_normal_images') and char_path in self.selected_normal_images:
            card_count = len(self.selected_normal_images[char_path])
        if self.trim_vars[char_path].get():
            trim_count = trim_total - trim_done
        elif hasattr(self, 'selected_trim_images') and char_path in self.selected_trim_images:
            trim_count = len(self.selected_trim_images[char_path])
        self.selected_counts[char_path]["卡面"].set(card_count)
        self.selected_counts[char_path]["无背景卡面"].set(trim_count)
        total = card_count + trim_count
        self.selected_counts[char_path]["总计"].set(total)

    def calculate_progress(self, source_dir, target_dir, output_format):
        """计算进度 - 支持模型简称，避免重复计算已超分图片"""
        total = 0
        done = 0
        if os.path.exists(source_dir):
            for filename in os.listdir(source_dir):
                if filename.lower().endswith(IMAGE_EXTENSIONS):
                    total += 1
                    name_part, ext = os.path.splitext(filename)
                    # 检查是否已超分（任何模型处理过的版本都算作已超分）
                    found = False
                    # 先检查带模型简称的文件
                    for model_short in MODEL_NAME_MAP.values():
                        if os.path.exists(os.path.join(target_dir, f"{name_part}_{model_short}.{output_format}")):
                            found = True
                            break
                    # 再检查不带模型简称的原始文件名
                    if not found and os.path.exists(os.path.join(target_dir, f"{name_part}.{output_format}")):
                        found = True
                    if found:
                        done += 1
        return total, done

        # 确保目录存在
        if not os.path.exists(source_dir):
            messagebox.showinfo("提示", f"没有找到{folder_type}文件夹")
            return

        # 获取所有图片
        image_files = []
        for filename in os.listdir(source_dir):
            if filename.lower().endswith(IMAGE_EXTENSIONS):
                source_file = os.path.join(source_dir, filename)
                base_name = os.path.splitext(filename)[0]
                target_file = os.path.join(target_dir, f"{base_name}.{output_format}")

                # 跳过已超分的图片
                if os.path.exists(target_file):
                    continue

                image_files.append((filename, source_file))

        if not image_files:
            messagebox.showinfo("提示", f"没有需要超分的{folder_type}图片")
            return

        # 创建选择窗口
        selection_win = tk.Toplevel(self)
        selection_win.title(f"选择{folder_type}图片 - {os.path.basename(char_path)}")
        selection_win.geometry("1000x700")
        selection_win.state('zoomed')  # 最大化窗口
        selection_win.transient(self)
        selection_win.grab_set()

        # 存储选择的图片
        # 初始化选择变量 - 记住之前的选择
        self.selection_vars = {}
        for img in image_files:
            source_file = img[1]
            # 如果之前已经选择过，保持选择状态
            if folder_type == "卡面":
                selected = source_file in self.selected_normal_images.get(char_path, [])
            else:
                selected = source_file in self.selected_trim_images.get(char_path, [])
            self.selection_vars[source_file] = tk.BooleanVar(value=selected)

        self.selection_win = selection_win  # 存储当前选择窗口
        self.thumb_labels = {}  # 存储缩略图标签

        # 顶部按钮框架
        btn_frame = ttk.Frame(selection_win)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        # 预览图大小控制
        ttk.Label(btn_frame, text="预览大小:").pack(side=tk.LEFT, padx=5)

        # 小按钮
        small_btn = ttk.Button(
            btn_frame,
            text="小",
            width=3,
            command=lambda: self.set_thumb_size(8, thumb_frame, image_files, folder_type)
        )
        small_btn.pack(side=tk.LEFT, padx=5)

        # 中按钮
        medium_btn = ttk.Button(
            btn_frame,
            text="中",
            width=3,
            command=lambda: self.set_thumb_size(5, thumb_frame, image_files, folder_type)
        )
        medium_btn.pack(side=tk.LEFT, padx=5)

        # 大按钮
        large_btn = ttk.Button(
            btn_frame,
            text="大",
            width=3,
            command=lambda: self.set_thumb_size(3, thumb_frame, image_files, folder_type)
        )
        large_btn.pack(side=tk.LEFT, padx=5)

        # 全选/全不选按钮
        ttk.Button(btn_frame, text="全选", command=lambda: self.toggle_all_selection(True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="全不选", command=lambda: self.toggle_all_selection(False)).pack(side=tk.LEFT,
                                                                                                    padx=5)

        # 确定按钮
        ttk.Button(
            btn_frame,
            text="确定",
            command=lambda: self.save_selection(char_path, folder_type, selection_win)
        ).pack(side=tk.RIGHT, padx=5)

        # 创建滚动区域
        container = ttk.Frame(selection_win)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 使用Canvas和Frame实现滚动
        canvas = tk.Canvas(container)
        thumb_frame = ttk.Frame(canvas)

        thumb_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=thumb_frame, anchor="nw")

        # 添加滚轮支持
        scrollbar = self.add_scroll_support(canvas, thumb_frame)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 初始显示中等大小
        self.set_thumb_size(5, thumb_frame, image_files, folder_type)

    def set_thumb_size(self, cols_per_row, thumb_frame, image_files, folder_type):
        """设置缩略图大小"""
        self.cols_per_row = cols_per_row
        self.update_thumbnails(thumb_frame, image_files, folder_type)

    def update_thumbnails(self, thumb_frame, image_files, folder_type):
        """更新预览图显示 - 使用固定列数并优化性能"""
        # 清除现有缩略图
        for widget in thumb_frame.winfo_children():
            widget.destroy()

        # 计算屏幕宽度
        screen_width = self.winfo_screenwidth()

        # 计算每个缩略图的宽度 (屏幕宽度 / 每行图片数量) * 0.8
        thumb_width = math.ceil((screen_width / self.cols_per_row) * 0.85)

        # 计算边框宽度 (缩略图宽度的2%)
        border_width = max(1, math.ceil(thumb_width * 0.02))

        # 创建缩略图缓存
        self.photo_cache = {}

        # 使用进度条显示加载进度
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            thumb_frame,
            variable=progress_var,
            maximum=len(image_files),
            mode='determinate'
        )
        progress_bar.grid(row=0, column=0, columnspan=self.cols_per_row, sticky="ew", padx=5, pady=5)

        # 更新显示
        self.update()

        # 创建网格布局框架
        grid_frame = tk.Frame(thumb_frame, bg='SystemButtonFace')
        grid_frame.grid(row=1, column=0, columnspan=self.cols_per_row, sticky="nsew")

        row = 0
        col = 0

        for idx, (filename, filepath) in enumerate(image_files):
            try:
                # 更新进度条
                progress_var.set(idx + 1)
                progress_bar.update()

                # 加载图片（如果已缓存则使用缓存）
                if filepath in self.photo_cache:
                    photo = self.photo_cache[filepath]
                else:
                    img = Image.open(filepath)

                    # 计算高度保持宽高比
                    width, height = img.size
                    ratio = thumb_width / width
                    new_height = int(height * ratio)

                    # 修复：使用正确的重采样滤镜
                    try:
                        resample_filter = Image.Resampling.LANCZOS
                    except AttributeError:
                        resample_filter = Image.LANCZOS
                        
                    img = img.resize((thumb_width, new_height), resample_filter)
                    photo = ImageTk.PhotoImage(img)
                    self.photo_cache[filepath] = photo

                # 创建缩略图框架
                thumb_cell = tk.Frame(grid_frame, bg='SystemButtonFace')
                thumb_cell.grid(row=row, column=col, padx=10, pady=10)

                # 创建图片容器框架 - 用于边框
                container = tk.Frame(thumb_cell, bg='SystemButtonFace')
                container.pack(padx=5, pady=5)

                # 显示预览图 - 直接点击图片选择
                # 使用tk.Label并设置背景色
                label = tk.Label(
                    container,
                    image=photo,
                    borderwidth=0,  # 初始无边框
                    relief="flat",
                    bg='SystemButtonFace'
                )
                label.image = photo  # 保持引用
                label.pack(padx=border_width, pady=border_width)  # 预留边框空间

                # 保存标签引用
                self.thumb_labels[filepath] = label

                # 添加点击事件 - 点击图片即可选择
                label.bind("<Button-1>", lambda e, fp=filepath: self.toggle_image_selection(e.widget, fp, border_width))

                # 添加文件名标签
                file_label = ttk.Label(
                    thumb_cell,
                    text=filename,
                    wraplength=thumb_width,
                    justify="center"
                )
                file_label.pack(pady=5)

                # 初始设置边框
                self.update_border(filepath, border_width)

                col += 1
                if col >= self.cols_per_row:
                    col = 0
                    row += 1

            except Exception as e:
                logging.error(f"加载预览图失败 {filename}: {str(e)}")

        # 移除进度条
        progress_bar.destroy()

    def update_border(self, filepath, border_width):
        """更新图片边框状态"""
        label = self.thumb_labels[filepath]
        if self.selection_vars[filepath].get():
            # 选中状态：绿色实线边框，宽度为border_width
            label.config(
                highlightbackground="green",
                highlightcolor="green",
                highlightthickness=border_width
            )
        else:
            # 未选中状态：无边框
            label.config(
                highlightbackground='SystemButtonFace',
                highlightthickness=0
            )

    def toggle_image_selection(self, widget, filepath, border_width):
        """切换图片选择状态"""
        current_value = self.selection_vars[filepath].get()
        self.selection_vars[filepath].set(not current_value)
        self.update_border(filepath, border_width)

    def toggle_all_selection(self, select_all):
        """全选或全不选"""
        for var in self.selection_vars.values():
            var.set(select_all)

        # 更新所有图片的边框状态
        if hasattr(self, 'thumb_labels'):
            # 获取第一个标签的边框宽度作为参考
            if self.thumb_labels:
                first_label = next(iter(self.thumb_labels.values()))
                border_width = first_label.cget("highlightthickness")
                if border_width == 0:
                    # 如果没有边框，使用默认计算
                    screen_width = self.winfo_screenwidth()
                    thumb_width = math.ceil((screen_width / self.cols_per_row) * 0.8)
                    border_width = max(1, math.ceil(thumb_width * 0.02))

                for filepath in self.thumb_labels:
                    self.update_border(filepath, border_width)

    def start_upscale(self):
        """开始超分处理"""
        # 检查是否有未完成的下载任务
        has_unfinished_task, task_message = self.check_download_status()
        if has_unfinished_task:
            # 提供重置选项
            result = messagebox.askyesno("警告", 
                f"检测到未完成的任务：{task_message}\n\n是否要重置下载状态并继续？")
            if result:
                self.reset_download_status()
            else:
                return
        
        # 获取选中的角色和选项
        selected_chars = self.all_upscale_chars if hasattr(self, 'all_upscale_chars') else []

        if not selected_chars:
            self.show_custom_message("警告", "请先扫描超分进度", msg_type='normal')
            return

        # 创建进度窗口
        progress_win = tk.Toplevel(self)
        progress_win.title("超分处理")
        progress_win.geometry("900x700")
        progress_win.transient(self)
        progress_win.grab_set()

        # 绑定窗口关闭事件
        progress_win.protocol("WM_DELETE_WINDOW", lambda: self.cancel_upscale(progress_win))

        ttk.Label(progress_win, text="正在处理超分...", font=("Arial", 12)).pack(pady=10)

        # 进度条
        progress_var = tk.IntVar()
        progress_bar = ttk.Progressbar(progress_win, variable=progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, padx=20, pady=10)

        # 状态标签
        status_var = tk.StringVar(value="下载中...")
        ttk.Label(progress_win, textvariable=status_var).pack(pady=5)

        # 剩余时间标签
        time_remaining_var = tk.StringVar(value="剩余时间: 计算中...")
        time_label = ttk.Label(progress_win, textvariable=time_remaining_var)
        time_label.pack(pady=5)

        # 处理速度标签
        speed_var = tk.StringVar(value="处理速度: 0 张/秒")
        speed_label = ttk.Label(progress_win, textvariable=speed_var)
        speed_label.pack(pady=5)

        # 日志区域
        log_frame = ttk.Frame(progress_win)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD, font=("微软雅黑", 11))
        log_text.pack(fill=tk.BOTH, expand=True)
        log_text.config(state=tk.DISABLED)

        def log(msg):
            log_text.config(state=tk.NORMAL)
            log_text.insert(tk.END, msg + "\n")
            log_text.config(state=tk.DISABLED)
            log_text.yview_moveto(1.0)  # 平滑滚动到底部

        # 控制按钮框架
        control_frame = ttk.Frame(progress_win)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # 添加取消按钮
        cancel_button = ttk.Button(
            control_frame,
            text="取消",
            command=lambda: self.cancel_upscale(progress_win)
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)

        # 在后台线程中处理超分
        def upscale_thread():
            # 计算总图片数
            total_images = 0
            for char_path in selected_chars:
                # 普通卡面 - 全选模式
                if self.card_vars[char_path].get():
                    card_source = self.get_card_dir(char_path)
                    if os.path.exists(card_source):
                        # 获取所有需要处理的图片
                        card_files = [os.path.join(card_source, f) for f in os.listdir(card_source) 
                                     if f.lower().endswith(IMAGE_EXTENSIONS)]
                        total_images += len(card_files)

                # 普通卡面 - 部分选择模式
                elif char_path in self.selected_normal_images:
                    total_images += len(self.selected_normal_images[char_path])

                # 无背景卡面 - 全选模式
                if self.trim_vars[char_path].get():
                    trim_source = self.get_trim_dir(char_path)
                    if os.path.exists(trim_source):
                        # 获取所有需要处理的图片
                        trim_files = [os.path.join(trim_source, f) for f in os.listdir(trim_source) 
                                     if f.lower().endswith(IMAGE_EXTENSIONS)]
                        total_images += len(trim_files)

                # 无背景卡面 - 部分选择模式
                elif char_path in self.selected_trim_images:
                    total_images += len(self.selected_trim_images[char_path])

            if total_images == 0:
                progress_win.destroy()
                messagebox.showinfo("提示", "没有需要处理的图片")
                return

            processed_images = 0
            start_time = time.time()
            last_update_time = start_time
            processed_since_last_update = 0
            total_success = 0  # 新增：统计所有处理的图片数

            for char_path in selected_chars:
                char_name = os.path.basename(char_path)
                band_name = os.path.basename(os.path.dirname(char_path))

                # 更新状态
                status_var.set(f"正在处理: {char_name} ({band_name})")
                log(f"开始处理角色: {char_name} ({band_name})")

                # 处理卡面文件夹
                card_count = 0
                if self.card_vars[char_path].get():
                    # 根据当前引擎选择对应的输出格式
                    if self.upscale_engine == "Real-ESRGAN":
                        output_format = self.realesrgan_normal_format
                    else:  # waifu2x
                        output_format = self.waifu2x_normal_format
                    # 获取所有卡面图片
                    card_source = self.get_card_dir(char_path)
                    selected_files = []
                    if os.path.exists(card_source):
                        selected_files = [os.path.join(card_source, f) for f in os.listdir(card_source) 
                                         if f.lower().endswith(IMAGE_EXTENSIONS)]
                    # 使用全选模式
                    card_count = self.process_folder(char_path, "卡面", log, selected_files, output_format,
                                                     progress_win, progress_var, status_var,
                                                     time_remaining_var, speed_var, start_time,
                                                     processed_images, total_images)
                    processed_images += card_count
                    total_success += card_count
                    log(f"卡面文件夹处理完成: {card_count}张图片")
                    # 清除选择状态
                    self.card_vars[char_path].set(False)
                    self.selected_normal_images.pop(char_path, None)
                elif char_path in self.selected_normal_images:
                    # 根据当前引擎选择对应的输出格式
                    if self.upscale_engine == "Real-ESRGAN":
                        output_format = self.realesrgan_normal_format
                    else:  # waifu2x
                        output_format = self.waifu2x_normal_format
                    selected_files = self.selected_normal_images[char_path]
                    card_count = self.process_folder(char_path, "卡面", log, selected_files, output_format,
                                                     progress_win, progress_var, status_var,
                                                     time_remaining_var, speed_var, start_time,
                                                     processed_images, total_images)
                    processed_images += card_count
                    total_success += card_count
                    log(f"卡面文件夹处理完成: {card_count}张图片")
                    # 清除选择状态
                    self.selected_normal_images.pop(char_path, None)

                # 处理无背景卡面文件夹
                trim_count = 0
                if self.trim_vars[char_path].get():
                    # 根据当前引擎选择对应的输出格式
                    if self.upscale_engine == "Real-ESRGAN":
                        output_format = self.realesrgan_trim_format
                    else:  # waifu2x
                        output_format = self.waifu2x_trim_format
                    # 获取所有无背景卡面图片
                    trim_source = self.get_trim_dir(char_path)
                    selected_files = []
                    if os.path.exists(trim_source):
                        selected_files = [os.path.join(trim_source, f) for f in os.listdir(trim_source) 
                                         if f.lower().endswith(IMAGE_EXTENSIONS)]
                    # 使用全选模式
                    trim_count = self.process_folder(char_path, "无背景卡面", log, selected_files, output_format,
                                                     progress_win, progress_var, status_var,
                                                     time_remaining_var, speed_var, start_time,
                                                     processed_images, total_images)
                    processed_images += trim_count
                    total_success += trim_count
                    log(f"无背景卡面文件夹处理完成: {trim_count}张图片")
                    # 清除选择状态
                    self.trim_vars[char_path].set(False)
                    self.selected_trim_images.pop(char_path, None)
                elif char_path in self.selected_trim_images:
                    # 根据当前引擎选择对应的输出格式
                    if self.upscale_engine == "Real-ESRGAN":
                        output_format = self.realesrgan_trim_format
                    else:  # waifu2x
                        output_format = self.waifu2x_trim_format
                    selected_files = self.selected_trim_images[char_path]
                    trim_count = self.process_folder(char_path, "无背景卡面", log, selected_files, output_format,
                                                     progress_win, progress_var, status_var,
                                                     time_remaining_var, speed_var, start_time,
                                                     processed_images, total_images)
                    processed_images += trim_count
                    total_success += trim_count
                    log(f"无背景卡面文件夹处理完成: {trim_count}张图片")
                    # 清除选择状态
                    self.selected_trim_images.pop(char_path, None)

                # 更新计数显示
                self.selected_counts[char_path]["卡面"].set(0)
                self.selected_counts[char_path]["无背景卡面"].set(0)

                log(f"角色处理完成: 卡面={card_count}, 无背景卡面={trim_count}")

            # 关闭进度窗口
            progress_win.destroy()
            self.log_message("超分处理完成！")
            # 重新扫描进度
            self.scan_upscale_progress()
            # 清理临时文件夹
            self.clean_realesrgan_temp()
            # 只弹一次happy图片窗口
            try:
                import random
                if self.result_images["happy"]:
                    happy_img = random.choice(self.result_images["happy"])
                    win = tk.Toplevel(self)
                    win.title("超分完成！")
                    win.geometry("520x440")
                    label = tk.Label(win, image=happy_img)
                    label.image = happy_img
                    label.pack(pady=10)
                    msg = tk.Label(win, text=f"成功超分{total_success}张图片！", font=("YaHei", 14, "bold"))
                    msg.pack(pady=10)
                    btn = ttk.Button(win, text="确定", command=win.destroy)
                    btn.pack(pady=10)
                    win.transient(self)
                    # 移除grab_set()以解决窗口无法通过任务栏恢复的问题
                    # win.grab_set()
                    
                    # 确保窗口在最小化后可以通过任务栏图标恢复
                    win.lift()
                    win.focus_force()
                else:
                    messagebox.showinfo("超分完成", f"成功超分{total_success}张图片！")
            except Exception as e:
                logging.error(f"弹出happy图片失败: {str(e)}")
                messagebox.showinfo("超分完成", f"成功超分{total_success}张图片！")

        # 启动超分线程
        self.upscale_thread = threading.Thread(target=upscale_thread, daemon=True)
        self.upscale_thread.start()
        progress_win.update()

    def cancel_upscale(self, progress_win):
        """取消超分处理"""
        self.upscale_canceled = True

        # 如果超分进程正在运行，终止它
        if self.upscale_process:
            try:
                self.upscale_process.terminate()
            except Exception as e:
                logging.error(f"终止超分进程失败: {str(e)}")

        # 清理临时文件夹
        self.clean_realesrgan_temp()

        # 关闭进度窗口
        progress_win.destroy()
        self.log_message("超分处理已取消")
        messagebox.showinfo("取消", "超分处理已取消")

    def process_folder(self, char_path, folder_type, log_func, selected_files, output_format,
                       progress_win, progress_var, status_var, time_remaining_var, speed_var, start_time,
                       processed_images=0, total_images=0):
        """重写：全新实现的超分处理逻辑"""

        # 停止之前的监控线程（如果存在）
        if hasattr(self, 'current_monitor_thread') and self.current_monitor_thread and self.current_monitor_thread.is_alive():
            self.monitor_stop_flag = True
            self.current_monitor_thread.join(timeout=1)  # 等待最多1秒

        # 检查是否有需要处理的图片
        if not selected_files:
            log_func("没有需要处理的图片，跳过。")
            return 0

        # 获取引擎设置
        if self.upscale_engine_var.get() == "waifu2x":
            engine = "waifu2x"
            exe_dir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "waifu2x-ncnn-vulkan")
            exe_path = os.path.join(exe_dir, "waifu2x-ncnn-vulkan.exe")
            # 使用配置的waifu2x模型路径
            model_dir = os.path.join(exe_dir, self.waifu2x_model_dir)
            model_name = None  # waifu2x不需要模型名称参数
            # 使用正确的变量名
            noise = self.waifu_noise_var.get()
            scale = 2  # waifu2x固定为2倍缩放
            
            # 获取当前使用的waifu2x模型
            current_waifu_model = self.waifu_model_var.get()
            # 获取模型简写
            model_short = MODEL_NAME_MAP.get(current_waifu_model, "waifu")
        else:
            engine = "realesrgan"
            exe_dir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "realesrgan-ncnn-vulkan")
            exe_path = os.path.join(exe_dir, "realesrgan-ncnn-vulkan.exe")
            model_dir = os.path.join(exe_dir, "models")
            model_name = self.realesrgan_model
            # 根据模型自动确定缩放倍数
            if "x2" in model_name:
                scale = 2
            elif "x3" in model_name:
                scale = 3
            elif "x4" in model_name:
                scale = 4
            else:
                scale = 4  # 默认4倍
            noise = None  # realesrgan不需要
            # 获取模型简写
            model_short = MODEL_NAME_MAP.get(model_name, "realesrgan")

        input_dir = os.path.join(exe_dir, "input")
        output_dir = os.path.join(exe_dir, "output")

        # 1. 清空input/output目录
        self.clear_directory(input_dir)
        self.clear_directory(output_dir)
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        # 2. 将用户选择的图片复制到input目录
        total_files = len(selected_files)
        for idx, source_file in enumerate(selected_files):
            filename = os.path.basename(source_file)
            
            # 对于无背景卡面，需要转换为RGBA模式
            if folder_type == "无背景卡面":
                try:
                    with Image.open(source_file) as img:
                        # 转换为RGBA模式
                        rgba_img = img.convert("RGBA")
                        # 保存为PNG格式
                        target_path = os.path.join(input_dir, os.path.splitext(filename)[0] + ".png")
                        rgba_img.save(target_path, "PNG")
                        log_func(f"已转换并复制无背景卡面: {filename}")
                except Exception as e:
                    log_func(f"处理无背景卡面失败 {filename}: {str(e)}")
                    continue
            else:
                # 普通卡面直接复制
                target_path = os.path.join(input_dir, filename)
                try:
                    shutil.copy2(source_file, target_path)
                    log_func(f"已复制普通卡面: {filename}")
                except Exception as e:
                    log_func(f"复制普通卡面失败 {filename}: {str(e)}")
                    continue
            
            # 更新进度
            progress = int((idx + 1) / total_files * 5)  # 占总进度的5%
            if total_images > 0:
                overall_progress = int((processed_images + (idx + 1) * 0.05) / total_images * 100)
                progress_var.set(overall_progress)
            else:
                progress_var.set(progress)
            status_var.set(f"正在准备图片: {idx + 1}/{total_files}")

        log_func(f"已将{total_files}张图片复制到input目录")

        # 3. 构建超分命令
        if engine == "waifu2x":
            cmd = [
                exe_path,
                "-i", input_dir,
                "-o", output_dir,
                "-m", model_dir,
                "-n", str(noise),
                "-s", str(scale),
                "-f", output_format,
                "-j", self.waifu2x_threads  # 使用配置的线程设置
            ]
        else:  # realesrgan
            cmd = [
                exe_path,
                "-i", input_dir,
                "-o", output_dir,
                "-n", model_name,
                "-s", str(scale),
                "-f", output_format,
                "-j", self.realesrgan_threads  # 使用配置的线程设置
            ]

        log_func(f"执行命令: {' '.join(cmd)}")

        # 4. 执行超分命令
        try:
            self.upscale_canceled = False
            start_process_time = time.time()
            
            # 使用Popen启动进程，以便可以监控进度
            self.upscale_process = subprocess.Popen(
                cmd,
                cwd=exe_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 启动监控线程
            monitor_thread = threading.Thread(
                target=self.monitor_upscale_progress,
                args=(output_dir, total_files, progress_var, status_var, time_remaining_var, speed_var, start_process_time, processed_images, total_images)
            )
            monitor_thread.daemon = True
            monitor_thread.start()

             # 保存监控线程引用，以便后续可以停止它
            self.current_monitor_thread = monitor_thread
            
            # 等待进程完成
            stdout, stderr = self.upscale_process.communicate()
            
            if self.upscale_canceled:
                log_func("超分处理已被用户取消")
                self.clear_directory(input_dir)
                self.clear_directory(output_dir)
                return 0

            if self.upscale_process.returncode != 0:
                log_func(f"超分失败: {stderr}")
                self.clear_directory(input_dir)
                self.clear_directory(output_dir)
                return 0

        except Exception as e:
            log_func(f"超分过程中发生错误: {str(e)}")
            self.clear_directory(input_dir)
            self.clear_directory(output_dir)
            return 0

        # 5. 计算处理时间和速度
        end_process_time = time.time()
        process_duration = end_process_time - start_process_time
        if process_duration > 0:
            speed = total_files / process_duration
            speed_var.set(f"处理速度: {speed:.1f} 张/秒")
            time_remaining_var.set("剩余时间: 0秒")

        # 6. 将超分后的图片移动到目标文件夹
        if folder_type == "卡面":
            target_dir = self.get_upscaled_card_dir(char_path)
        else:
            target_dir = self.get_upscaled_trim_dir(char_path)
        
        os.makedirs(target_dir, exist_ok=True)
        
        # 获取output目录中的所有文件
        out_files = [f for f in os.listdir(output_dir) 
                    if f.lower().endswith(f'.{output_format}') or 
                       (folder_type == "无背景卡面" and output_format == "jpg" and f.lower().endswith('.png'))]
        
        success_count = 0
        for fname in out_files:
            src = os.path.join(output_dir, fname)
            base_name = os.path.splitext(fname)[0]
            
            # 添加模型简称到文件名
            # 根据引擎类型获取正确的模型简称
            if engine == "waifu2x":
                current_waifu_model = self.waifu_model_var.get()
                model_short = MODEL_NAME_MAP.get(current_waifu_model, "waifu")
            else:
                model_short = MODEL_NAME_MAP.get(model_name, "realesrgan")
                
            if not base_name.endswith(f"_{model_short}"):
                base_name = f"{base_name}_{model_short}"
            
            # 特殊处理：无背景卡面输出为JPG但实际为PNG的情况
            if folder_type == "无背景卡面" and output_format == "jpg" and fname.lower().endswith('.png'):
                dst = os.path.join(target_dir, f"{base_name}.png")
                shutil.move(src, dst)
            else:
                dst = os.path.join(target_dir, f"{base_name}.{output_format}")
                
                # 对于JPG格式的无背景卡面，需要处理透明度
                if output_format == "jpg" and folder_type == "无背景卡面":
                    with Image.open(src) as img:
                        if img.mode in ["RGBA", "LA"]:
                            # 创建白色背景
                            background = Image.new("RGB", img.size, (255, 255, 255))
                            # 粘贴图像（使用alpha通道作为蒙版）
                            background.paste(img, mask=img.split()[-1])
                            background.save(dst, "JPEG")
                        else:
                            img.convert("RGB").save(dst, "JPEG")
                    # 删除源文件
                    os.remove(src)
                else:
                    shutil.move(src, dst)
            
            success_count += 1

        # 7. 清空input/output目录
        self.clear_directory(input_dir)
        self.clear_directory(output_dir)

        # 8. 完成日志记录
        if total_images > 0:
            overall_progress = int((processed_images + total_files) / total_images * 100)
            progress_var.set(min(overall_progress, 100))
        else:
            progress_var.set(100)
        log_func(f"超分完成！成功超分{success_count}张图片。")
        return success_count

    def clear_directory(self, directory):
        """清空目录内容"""
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    logging.error(f"删除文件失败 {file_path}: {e}")

    def monitor_upscale_progress(self, output_dir, total_files, progress_var, status_var, time_remaining_var, speed_var,
                                 start_time, processed_images=0, total_images=0):
        """监控超分进度"""
        last_count = 0
        last_time = time.time()
        # 累计显示计数，确保只能增加不能减少
        accumulated_display_count = processed_images
        last_progress = 0
        # 记录当前角色的起始计数
        role_start_count = 0
        role_initialized = False
        
        # 用于计算平均速度的变量
        speed_history = []  # 存储最近的速度值
        time_history = []   # 存储时间戳
        
        # 设置停止标志
        self.monitor_stop_flag = False
        
        while True:
            # 检查是否已取消或停止
            if self.upscale_canceled or self.monitor_stop_flag:
                break

            # 获取当前已处理的文件数量
            try:
                current_count = len([f for f in os.listdir(output_dir) if f.lower().endswith(('.png', '.jpg'))])
            except:
                current_count = 0

            # 初始化当前角色的起始计数（只在第一次检测到文件时）
            if not role_initialized and current_count > 0:
                role_start_count = current_count
                role_initialized = True

            # 计算当前角色实际新增的处理数量
            current_role_processed = max(0, current_count - role_start_count)
            
            # 如果输出目录为空且已经初始化过，说明角色切换了，重置计数
            if role_initialized and current_count == 0:
                role_start_count = 0
                role_initialized = False
            
            # 计算当前总处理数量（之前已处理的 + 当前角色新增的）
            current_total_processed = processed_images + current_role_processed
            
            # 确保显示的计数不会减少，只会增加或保持不变
            accumulated_display_count = max(accumulated_display_count, current_total_processed)
            
            # 更新状态显示
            if total_images > 0:
                # 如果有总图片数信息，显示全局进度
                accumulated_display_count = min(accumulated_display_count, total_images)
                status_var.set(f"正在超分处理: {accumulated_display_count}/{total_images}")
                
                # 计算全局进度百分比
                progress_percent = int((accumulated_display_count / total_images) * 100)
                progress_percent = min(progress_percent, 100)
            else:
                # 如果没有总图片数信息，显示当前角色进度
                status_var.set(f"正在超分处理: {current_role_processed}/{total_files}")
                
                # 计算当前角色进度百分比
                if total_files > 0:
                    progress_percent = int((current_role_processed / total_files) * 100)
                    progress_percent = min(progress_percent, 95)  # 防止在完成前显示100%
                else:
                    progress_percent = 0
            
            # 确保进度条不会回退
            progress_percent = max(progress_percent, last_progress)
            last_progress = progress_percent
            progress_var.set(progress_percent)

            # 计算处理速度和剩余时间
            current_time = time.time()
            processed_since_last = current_role_processed - last_count
            time_since_last = current_time - last_time

            if time_since_last >= 1.0 and processed_since_last >= 0:  # 至少间隔1秒再计算
                # 计算瞬时速度（每秒处理的图片数）
                instant_speed = processed_since_last / time_since_last if time_since_last > 0 else 0
                
                # 维护速度历史记录（最多保存10个数据点）
                speed_history.append(instant_speed)
                time_history.append(current_time)
                
                if len(speed_history) > 10:
                    speed_history.pop(0)
                    time_history.pop(0)
                
                # 使用加权平均计算速度，最近的速度权重更高
                if len(speed_history) > 0:
                    weighted_sum = 0
                    weight_total = 0
                    
                    for i, (speed_val, time_val) in enumerate(zip(speed_history, time_history)):
                        # 计算权重（最近的数据权重更高）
                        weight = i + 1
                        weighted_sum += speed_val * weight
                        weight_total += weight
                    
                    avg_speed = weighted_sum / weight_total if weight_total > 0 else 0
                else:
                    avg_speed = instant_speed
                
                # 显示处理速度（每张图片需要的秒数）
                if avg_speed > 0:
                    seconds_per_image = 1.0 / avg_speed
                    speed_var.set(f"处理速度: {seconds_per_image:.2f} 秒/张")
                else:
                    speed_var.set("处理速度: 计算中...")
                
                # 估算剩余时间
                if total_images > 0:
                    # 基于全局进度估算
                    remaining_images = total_images - accumulated_display_count
                else:
                    # 基于当前角色进度估算
                    remaining_images = total_files - current_role_processed
                
                if remaining_images > 0 and avg_speed > 0:
                    # 使用平均速度估算剩余时间
                    remaining_time = remaining_images / avg_speed
                    
                    # 格式化剩余时间显示
                    if remaining_time < 60:
                        time_remaining_var.set(f"剩余时间: {remaining_time:.0f}秒")
                    elif remaining_time < 3600:
                        time_remaining_var.set(f"剩余时间: {remaining_time/60:.1f}分钟")
                    elif remaining_time < 86400:  # 24小时
                        time_remaining_var.set(f"剩余时间: {remaining_time/3600:.1f}小时")
                    else:
                        days = int(remaining_time // 86400)
                        hours = (remaining_time % 86400) / 3600
                        time_remaining_var.set(f"剩余时间: {days}天{hours:.1f}小时")
                else:
                    time_remaining_var.set("剩余时间: 计算中...")
                
                last_count = current_role_processed
                last_time = current_time

            # 检查是否完成
            if current_role_processed >= total_files and total_files > 0:
                break

            # 短暂休眠以减少CPU使用，避免资源竞争
            time.sleep(0.5)


    def open_failure_log(self):
        """打开失败日志文件"""
        try:
            log_file = "download_failure.log"
            if os.path.exists(log_file):
                # 检查文件是否为空
                file_size = os.path.getsize(log_file)
                if file_size == 0:
                    self.log_message("失败日志文件为空，没有失败记录")
                    return
                
                # 使用系统默认程序打开日志文件
                if sys.platform.startswith('win'):
                    os.startfile(log_file)
                elif sys.platform.startswith('darwin'):  # macOS
                    os.system(f'open "{log_file}"')
                else:  # Linux
                    os.system(f'xdg-open "{log_file}"')
                self.log_message(f"已打开失败日志文件: {log_file}")
            else:
                # 如果文件不存在，创建一个空的日志文件
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write("")
                self.log_message("失败日志文件不存在，已创建空文件")
        except Exception as e:
            self.log_message(f"打开失败日志文件时发生错误: {str(e)}")

    def update_band_selection_state(self, band_name):
        """更新乐队选择状态（根据该乐队角色的选择情况）"""
        if not hasattr(self, 'band_vars') or band_name not in self.band_vars:
            return
            
        # 获取该乐队的所有角色
        band_char_ids = []
        for char_id, char_info in self.card_info.items():
            if char_info["band"] == band_name:
                band_char_ids.append(char_id)
        
        if not band_char_ids:
            return
            
        # 检查该乐队角色的选择状态
        selected_count = 0
        total_count = 0
        
        for char_id in band_char_ids:
            if char_id in self.char_vars:
                total_count += 1
                if self.char_vars[char_id].get():
                    selected_count += 1
        
        # 更新乐队复选框状态
        if selected_count == 0:
            self.band_vars[band_name].set(False)
        elif selected_count == total_count:
            self.band_vars[band_name].set(True)
        else:
            # 部分选择状态，保持当前状态（不改变）
            pass

    def toggle_type_selection(self, var):
        """切换类型选择状态"""
        var.set(not var.get())
        self.update_filtered_counts()

    def setup_single_download_tab(self):
        """单独下载Tab骨架"""
        # 顶部按钮区
        top_frame = ttk.Frame(self.single_download_tab)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        # 左上角显示上次获取时间
        ttk.Label(top_frame, text="上次获取:").pack(side=tk.LEFT)
        self.single_last_fetch_var = tk.StringVar(value="从未获取")
        if self.last_fetch_time:
            self.single_last_fetch_var.set(f"{self.last_fetch_time}")
        ttk.Label(top_frame, textvariable=self.single_last_fetch_var).pack(side=tk.LEFT, padx=5)

        # 右上角按钮顺序调整：先更新卡面信息，后打开文件夹
        ttk.Button(top_frame, text="更新卡面信息", command=self.update_card_info_from_api).pack(side=tk.RIGHT, padx=5)
        ttk.Button(top_frame, text="打开文件夹", command=self.open_bangdream_folder).pack(side=tk.RIGHT, padx=5)

        # 搜索区
        search_frame = ttk.Frame(self.single_download_tab)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(search_frame, text="输入卡面ID:").pack(side=tk.LEFT)
        self.single_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.single_search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="添加", command=self.add_single_card).pack(side=tk.LEFT, padx=5)

        # 回车等同于"添加"
        def on_single_entry_return(event=None):
            self.add_single_card()
        search_entry.bind('<Return>', on_single_entry_return)

        # 图片类型+特训阶段三选一合并为一行
        option_frame = ttk.Frame(self.single_download_tab)
        option_frame.pack(fill=tk.X, padx=10, pady=5)
        self.single_type_var = tk.StringVar(value="all")
        self.single_stage_var = tk.StringVar(value="all")
        ttk.Label(option_frame, text="图片类型:").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(option_frame, text="普通卡面", variable=self.single_type_var, value="normal", style="Big.TRadiobutton").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(option_frame, text="无背景卡面", variable=self.single_type_var, value="trim", style="Big.TRadiobutton").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(option_frame, text="全部", variable=self.single_type_var, value="all", style="Big.TRadiobutton").pack(side=tk.LEFT, padx=5)
        ttk.Label(option_frame, text="              是否特训：").pack(side=tk.LEFT, padx=15)
        ttk.Radiobutton(option_frame, text="特训前", variable=self.single_stage_var, value="normal", style="Big.TRadiobutton").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(option_frame, text="特训后", variable=self.single_stage_var, value="after", style="Big.TRadiobutton").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(option_frame, text="全部", variable=self.single_stage_var, value="all", style="Big.TRadiobutton").pack(side=tk.LEFT, padx=5)

        # 卡面信息列表区（可滚动）
        list_container = ttk.Frame(self.single_download_tab)
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.single_card_canvas = tk.Canvas(list_container)
        self.single_card_list_frame = ttk.Frame(self.single_card_canvas)
        self.single_card_list_frame.bind(
            "<Configure>",
            lambda e: self.single_card_canvas.configure(scrollregion=self.single_card_canvas.bbox("all"))
        )
        self.single_card_canvas.create_window((0, 0), window=self.single_card_list_frame, anchor="nw")
        # 滚动条
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.single_card_canvas.yview)
        self.single_card_canvas.configure(yscrollcommand=scrollbar.set)
        self.single_card_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        # 鼠标滚轮支持
        self.add_scroll_support(self.single_card_canvas, self.single_card_list_frame)

        # 右下角开始下载按钮和一键删除按钮
        btn_frame = ttk.Frame(self.single_download_tab)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)
        ttk.Button(btn_frame, text="一键删除所有添加卡面", command=self.clear_single_card_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="开始下载", style="Accent.TButton", command=self.start_single_download).pack(side=tk.RIGHT)

        # 存储已添加的卡面ID
        self.single_card_ids = []
        self.single_card_info = []

        # Radiobutton大字体样式
        style = ttk.Style()
        style.configure("Big.TRadiobutton", font=("微软雅黑", 11))

    def clear_single_card_list(self):
        """一键删除所有添加的卡面"""
        self.single_card_ids.clear()
        self.single_card_info.clear()
        self.update_single_card_list()

    def add_single_card(self):
        card_id_str = self.single_search_var.get().strip()
        if not card_id_str:
            return
        # 彩蛋
        if card_id_str == "947":
            if random.random() < 0.01:
                self.show_easter_egg()
        # 检查是否为数字
        if not card_id_str.isdigit():
            self.show_custom_message("输入错误", "请输入正确的卡面ID（数字）", msg_type='sad')
            return
        card_id = int(card_id_str)
        found = False
        found_char_id = None
        found_card_info = None
        # 在card_info中查找卡面
        for char_id, char_info in self.card_info.items():
            for card in char_info["cards"]:
                if card["card_id"] == card_id:
                    found = True
                    found_char_id = char_id
                    found_card_info = card
                    break
            if found:
                break
        if not found:
            # 随机sad图片
            sad_img = None
            if hasattr(self, 'result_images') and self.result_images.get('sad'):
                sad_img = random.choice(self.result_images['sad'])
            err_win = tk.Toplevel(self)
            err_win.title("未找到卡面信息")
            err_win.geometry("520x540")
            err_win.transient(self)
            err_win.grab_set()
            # 插入图片
            if sad_img:
                ttk.Label(err_win, image=sad_img).pack(pady=10)
            frame = ttk.Frame(err_win)
            frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            # 左侧文字
            ttk.Label(frame, text="未找到该卡面ID的信息\n请检查输入或更新卡面信息。", font=("YaHei", 12), foreground="red").pack(side=tk.LEFT, padx=10)
            btn = ttk.Button(err_win, text="确定", command=err_win.destroy)
            btn.pack(pady=18)
            err_win.bind('<Return>', lambda e: err_win.destroy())
            btn.focus_set()
            return
        # 检查是否已添加
        if card_id in self.single_card_ids:
            self.show_custom_message("已存在", "该卡面ID已在列表中", msg_type='normal')
            return
        # 添加到列表
        self.single_card_ids.append(card_id)
        self.single_card_info.append((card_id, found_char_id, found_card_info))
        self.update_single_card_list()
        self.single_search_var.set("")  # 成功添加后清空输入框

    def show_easter_egg(self):
        # 加载图片
        try:
            from PIL import Image, ImageTk
            img = Image.open("assets/pico/你在找我？.png")
            img = img.resize((900, 900))
            tk_img = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"彩蛋图片加载失败: {e}")
            return
        # 创建覆盖层
        if hasattr(self, '_easter_egg_label') and self._easter_egg_label:
            self._easter_egg_label.destroy()
        self._easter_egg_label = tk.Label(self.single_download_tab, image=tk_img, bg="#fff")
        self._easter_egg_label.image = tk_img
        self._easter_egg_label.place(relx=0.5, rely=0.5, anchor="center")
        # 2秒后消失
        def hide():
            if hasattr(self, '_easter_egg_label') and self._easter_egg_label:
                self._easter_egg_label.destroy()
                self._easter_egg_label = None
        self.single_download_tab.after(2000, hide)

    def update_single_card_list(self):
        """刷新单独下载卡面信息列表（表头和内容全部用grid对齐）"""
        for widget in self.single_card_list_frame.winfo_children():
            widget.destroy()
        if not self.single_card_info:
            ttk.Label(self.single_card_list_frame, text="请添加卡面ID", font=("YaHei", 11)).pack(pady=20)
            return
        # 列定义
        columns = [
            ("卡面ID", 10),
            ("角色名", 14),
            ("乐队", 7),
            ("稀有度", 10),
            ("属性", 12),
            ("类型", 10),
            ("", 6)  # 删除按钮
        ]
        # 表头
        for col, (text, width) in enumerate(columns):
            ttk.Label(self.single_card_list_frame, text=text, width=width, anchor="center", font=("微软雅黑", 11, "bold")).grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
        # 内容
        for idx, (card_id, char_id, card) in enumerate(self.single_card_info):
            row_idx = idx + 1
            # 卡面ID
            ttk.Label(self.single_card_list_frame, text=str(card_id), width=10, anchor="center").grid(row=row_idx, column=0, padx=2, pady=2, sticky="nsew")
            # 角色名
            char_name = self.card_info[char_id]["name"]
            ttk.Label(self.single_card_list_frame, text=char_name, width=14, anchor="center").grid(row=row_idx, column=1, padx=2, pady=2, sticky="nsew")
            # 乐队
            band_name = self.card_info[char_id]["band"]
            band_icon_id = {
                "Poppin'Party": 1,
                "Afterglow": 2,
                "Hello, Happy World!": 3,
                "Pastel_Palettes": 4,
                "Roselia": 5,
                "Morfonica": 6,
                "RAISE_A_SUILEN": 7,
                "MyGO!!!!!": 8
            }.get(band_name)
            band_frame = ttk.Frame(self.single_card_list_frame)
            # 左右加空白Label实现居中
            ttk.Label(band_frame, text="").pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            if band_icon_id and band_icon_id in self.band_icons:
                ttk.Label(band_frame, image=self.band_icons[band_icon_id]).pack(side=tk.LEFT)
            else:
                ttk.Label(band_frame, text=band_name, anchor="center").pack(side=tk.LEFT)
            ttk.Label(band_frame, text="").pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            band_frame.grid(row=row_idx, column=2, padx=2, pady=2, sticky="nsew")
            # 稀有度
            rarity = card.get("rarity", 1)
            rarity_frame = ttk.Frame(self.single_card_list_frame)
            ttk.Label(rarity_frame, text="").pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            ttk.Label(rarity_frame, text=f"{rarity}★", width=4, anchor="center").pack(side=tk.LEFT)
            if hasattr(self, 'star_icons') and rarity in self.star_icons:
                ttk.Label(rarity_frame, image=self.star_icons[rarity]).pack(side=tk.LEFT)
            ttk.Label(rarity_frame, text="").pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            rarity_frame.grid(row=row_idx, column=3, padx=2, pady=2, sticky="nsew")
            # 属性
            attr = card.get("attribute", "")
            attr_frame = ttk.Frame(self.single_card_list_frame)
            ttk.Label(attr_frame, text="").pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            ttk.Label(attr_frame, text=attr.upper(), width=6, anchor="center").pack(side=tk.LEFT)
            if hasattr(self, 'attr_icons') and attr in self.attr_icons:
                ttk.Label(attr_frame, image=self.attr_icons[attr]).pack(side=tk.LEFT)
            ttk.Label(attr_frame, text="").pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            attr_frame.grid(row=row_idx, column=4, padx=2, pady=2, sticky="nsew")
            # 类型
            type_name = TYPE_NAMES.get(card.get("type", "others"), card.get("type", "others"))
            ttk.Label(self.single_card_list_frame, text=type_name, width=10, anchor="center").grid(row=row_idx, column=5, padx=2, pady=2, sticky="nsew")
            # 删除按钮
            del_btn = ttk.Button(self.single_card_list_frame, text="删除", width=5, command=lambda i=idx: self.remove_single_card(i))
            del_btn.grid(row=row_idx, column=6, padx=2, pady=2, sticky="nsew")

            # 添加分割线
            sep = ttk.Separator(self.single_card_list_frame, orient='horizontal')
            sep.grid(row=row_idx+1, column=0, columnspan=7, sticky='ew', padx=2, pady=1)
            


        # 让所有列都可拉伸
        for col in range(len(columns)):
            self.single_card_list_frame.grid_columnconfigure(col, weight=1)

    def remove_single_card(self, idx):
        """移除单独下载卡面"""
        if 0 <= idx < len(self.single_card_ids):
            self.single_card_ids.pop(idx)
            self.single_card_info.pop(idx)
            self.update_single_card_list()

    def start_single_download(self):
        """开始单独下载"""
        # 检查是否有未完成的下载任务
        has_unfinished_task, task_message = self.check_download_status()
        if has_unfinished_task:
            # 提供重置选项
            result = messagebox.askyesno("警告", 
                f"检测到未完成的任务：{task_message}\n\n是否要重置下载状态并继续？")
            if result:
                self.reset_download_status()
            else:
                return
        
        if not self.single_card_info:
            messagebox.showwarning("警告", "请先添加至少一个卡面ID")
            return
        # 获取用户设置
        type_mode = self.single_type_var.get()  # normal/trim/all
        stage_mode = self.single_stage_var.get()  # after/normal/all
        # 组装下载任务
        download_tasks = []
        for card_id, char_id, card in self.single_card_info:
            char_name = self.card_info[char_id]["name"]
            band_name = self.card_info[char_id]["band"]
            res_name = card["resourceSetName"]
            # 根据三选一过滤图片类型
            image_types = []
            if type_mode == "normal":
                if stage_mode == "normal":
                    image_types = ["card_normal.png"]
                elif stage_mode == "after":
                    image_types = ["card_after_training.png"]
                else:
                    image_types = ["card_normal.png", "card_after_training.png"]
            elif type_mode == "trim":
                if stage_mode == "normal":
                    image_types = ["trim_normal.png"]
                elif stage_mode == "after":
                    image_types = ["trim_after_training.png"]
                else:
                    image_types = ["trim_normal.png", "trim_after_training.png"]
            else:  # all
                if stage_mode == "normal":
                    image_types = ["card_normal.png", "trim_normal.png"]
                elif stage_mode == "after":
                    image_types = ["card_after_training.png", "trim_after_training.png"]
                else:
                    image_types = [
                        "card_normal.png", "card_after_training.png",
                        "trim_normal.png", "trim_after_training.png"
                    ]
            # 新增：如果用户选择只下载普通卡面，但该卡面没有普通卡面，且有训练后卡面，则自动回退
            # 只在type_mode=="normal"且stage_mode=="normal"时生效
            if type_mode == "normal" and stage_mode == "normal":
                # 检查服务器上card_normal.png是否可用，不可用则尝试card_after_training.png
                available_servers = card.get("available_servers", [])
                servers_to_try = available_servers if available_servers else SERVERS
                found = False
                for server in servers_to_try:
                    url = f"https://bestdori.com/assets/{server}/characters/resourceset/{res_name}_rip/card_normal.png"
                    try:
                        resp = requests.get(url, timeout=10, stream=True)
                        if resp.status_code == 200:
                            content = b""
                            for chunk in resp.iter_content(chunk_size=1024):
                                content += chunk
                                if len(content) >= 1024:
                                    break
                            if len(content) >= 512:
                                full_resp = requests.get(url, timeout=10)
                                if full_resp.status_code == 200 and len(full_resp.content) >= 20 * 1024:
                                    found = True
                                    break
                    except Exception:
                        continue
                if not found:
                    # card_normal.png不可用，尝试card_after_training.png
                    for server in servers_to_try:
                        url = f"https://bestdori.com/assets/{server}/characters/resourceset/{res_name}_rip/card_after_training.png"
                        try:
                            resp = requests.get(url, timeout=10, stream=True)
                            if resp.status_code == 200:
                                content = b""
                                for chunk in resp.iter_content(chunk_size=1024):
                                    content += chunk
                                    if len(content) >= 1024:
                                        break
                                if len(content) >= 512:
                                    full_resp = requests.get(url, timeout=10)
                                    if full_resp.status_code == 200 and len(full_resp.content) >= 20 * 1024:
                                        image_types = ["card_after_training.png"]
                                        break
                        except Exception:
                            continue
            # 新增：如果只选trim_normal/trim_after_training，且card_normal不可用，自动用card_after_training确定服务器
            if type_mode == "trim":
                # 只选一个trim类型时
                if len(image_types) == 1 and image_types[0] in ("trim_normal.png", "trim_after_training.png"):
                    available_servers = card.get("available_servers", [])
                    servers_to_try = available_servers if available_servers else SERVERS
                    found = False
                    # 先尝试card_normal.png
                    for server in servers_to_try:
                        url = f"https://bestdori.com/assets/{server}/characters/resourceset/{res_name}_rip/card_normal.png"
                        try:
                            resp = requests.get(url, timeout=10, stream=True)
                            if resp.status_code == 200:
                                content = b""
                                for chunk in resp.iter_content(chunk_size=1024):
                                    content += chunk
                                    if len(content) >= 1024:
                                        break
                                if len(content) >= 512:
                                    full_resp = requests.get(url, timeout=10)
                                    if full_resp.status_code == 200 and len(full_resp.content) >= 20 * 1024:
                                        found = True
                                        break
                        except Exception:
                            continue
                    if not found:
                        # card_normal.png不可用，尝试card_after_training.png
                        for server in servers_to_try:
                            url = f"https://bestdori.com/assets/{server}/characters/resourceset/{res_name}_rip/card_after_training.png"
                            try:
                                resp = requests.get(url, timeout=10, stream=True)
                                if resp.status_code == 200:
                                    content = b""
                                    for chunk in resp.iter_content(chunk_size=1024):
                                        content += chunk
                                        if len(content) >= 1024:
                                            break
                                    if len(content) >= 512:
                                        full_resp = requests.get(url, timeout=10)
                                        if full_resp.status_code == 200 and len(full_resp.content) >= 20 * 1024:
                                            # 不修改image_types，只是让服务器选择逻辑能用card_after_training
                                            found = True
                                            break
                            except Exception:
                                continue
            download_tasks.append({
                "card": card,
                "char_id": char_id,
                "char_name": char_name,
                "band_name": band_name,
                "image_types": image_types
            })
        # 进入下载进度窗口
        self.run_single_download_tasks(download_tasks)

    def run_single_download_tasks(self, download_tasks):
        """执行单独下载任务，复用批量下载的进度与结果窗口风格"""
        # 创建进度窗口
        progress_win = tk.Toplevel(self)
        progress_win.title("下载卡面")
        progress_win.geometry("900x700")
        progress_win.transient(self)
        # 移除grab_set()以解决窗口无法通过任务栏恢复的问题
        # progress_win.grab_set()
        
        # 确保窗口在最小化后可以通过任务栏图标恢复
        progress_win.lift()
        progress_win.focus_force()

        # 绑定窗口关闭事件
        progress_win.protocol("WM_DELETE_WINDOW", lambda: self.cancel_download(progress_win))

        ttk.Label(progress_win, text="正在下载卡面...", font=("微软雅黑", 12)).pack(pady=10)

        # 控制按钮框架
        control_frame = ttk.Frame(progress_win)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        self.pause_button = ttk.Button(
            control_frame,
            text="暂停",
            command=lambda: self.toggle_pause_download(progress_win)
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="取消",
            command=lambda: self.cancel_download(progress_win)
        ).pack(side=tk.LEFT, padx=5)

        self.pause_status_var = tk.StringVar(value="状态: 运行中")
        ttk.Label(control_frame, textvariable=self.pause_status_var).pack(side=tk.LEFT, padx=10)

        self.timeout_var = tk.StringVar(value="超时计数: 0")
        ttk.Label(control_frame, textvariable=self.timeout_var).pack(side=tk.LEFT, padx=10)

        self.stage_var = tk.StringVar(value="阶段: 单独下载")
        ttk.Label(control_frame, textvariable=self.stage_var).pack(side=tk.LEFT, padx=10)

        progress_var = tk.IntVar()
        progress_bar = ttk.Progressbar(progress_win, variable=progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, padx=20, pady=10)

        status_var = tk.StringVar(value="下载中...")
        ttk.Label(progress_win, textvariable=status_var).pack(pady=5)

        time_remaining_var = tk.StringVar(value="剩余时间: 计算中...")
        time_label = ttk.Label(progress_win, textvariable=time_remaining_var)
        time_label.pack(pady=5)

        speed_var = tk.StringVar(value="处理速度: 0 张/秒")
        speed_label = ttk.Label(progress_win, textvariable=speed_var)
        speed_label.pack(pady=5)

        log_frame = ttk.Frame(progress_win)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD, font=("微软雅黑", 11))
        log_text.pack(fill=tk.BOTH, expand=True)
        log_text.config(state=tk.DISABLED)

        def log(msg):
            log_text.config(state=tk.NORMAL)
            log_text.insert(tk.END, msg + "\n")
            log_text.config(state=tk.DISABLED)
            log_text.yview_moveto(1.0)

        failure_frame = ttk.LabelFrame(progress_win, text="失败日志")
        failure_frame.pack(fill=tk.X, padx=10, pady=5)

        failure_text = scrolledtext.ScrolledText(failure_frame, height=5, wrap=tk.WORD, font=("微软雅黑", 11))
        failure_text.pack(fill=tk.BOTH, expand=True)
        failure_text.config(state=tk.DISABLED)

        def log_failure(msg):
            failure_text.config(state=tk.NORMAL)
            failure_text.insert(tk.END, msg + "\n")
            failure_text.config(state=tk.DISABLED)
            failure_text.yview_moveto(1.0)

        # 下载线程
        def download_thread():
            self.pause_download = False
            self.download_canceled = False
            self.timeout_count = 0
            self.last_timeout_time = 0
            self.failed_downloads = []
            self.download_in_progress = True  # 设置下载进行中标志
            self.total_cards = len(download_tasks)
            total_downloaded = 0
            total_skipped = 0
            total_failed = 0
            failure_log = []
            start_time = time.time()
            last_update_time = start_time
            processed_since_last_update = 0
            total_processed = 0
            with ThreadPoolExecutor(max_workers=self.download_threads) as executor:
                futures = []
                for task in download_tasks:
                    futures.append(executor.submit(
                        self.process_single_card_download,
                        task, log, log_failure, failure_log
                    ))
                for future in as_completed(futures):
                    if self.download_canceled:
                        log("下载已取消")
                        break
                    result = future.result()
                    total_processed += 1
                    processed_since_last_update += 1
                    progress = min(100, int(total_processed / self.total_cards * 100))
                    progress_var.set(progress)
                    total_downloaded += result["downloaded"]
                    total_skipped += result["skipped"]
                    total_failed += result["failed"]
                    self.timeout_var.set(f"超时计数: {self.timeout_count}")
                    current_time = time.time()
                    if current_time - last_update_time > 5:
                        elapsed_time = current_time - start_time
                        time_per_card = elapsed_time / total_processed if total_processed > 0 else 0
                        remaining_cards = self.total_cards - total_processed
                        remaining_time = remaining_cards * time_per_card
                        if remaining_time < 60:
                            time_str = f"{int(remaining_time)}秒"
                        elif remaining_time < 3600:
                            minutes = int(remaining_time // 60)
                            seconds = int(remaining_time % 60)
                            time_str = f"{minutes}分{seconds}秒"
                        else:
                            hours = int(remaining_time // 3600)
                            minutes = int((remaining_time % 3600) // 60)
                            time_str = f"{hours}小时{minutes}分"
                        speed = processed_since_last_update / (current_time - last_update_time)
                        time_remaining_var.set(f"剩余时间: {time_str}")
                        speed_var.set(f"处理速度: {speed:.1f} 张/秒")
                        if current_time - last_update_time > 5:
                            last_update_time = current_time
                            processed_since_last_update = 0
            
            progress_win.destroy()
            self.download_in_progress = False  # 清除下载进行中标志
            if not self.download_canceled:
                self.log_message(f"卡面下载完成！下载: {total_downloaded}, 跳过: {total_skipped}, 失败: {total_failed}")
                self.show_download_result(total_downloaded, total_skipped, total_failed)
            else:
                self.log_message("下载已取消")
                messagebox.showinfo("取消", "下载已取消")
        threading.Thread(target=download_thread, daemon=True).start()
        progress_win.update()

    def process_single_card_download(self, task, log_func, log_failure, failure_log):
        """处理单独下载的单个卡面，支持自定义图片类型"""
        result = {"downloaded": 0, "skipped": 0, "failed": 0}
        card = task["card"]
        char_id = task["char_id"]
        char_name = task["char_name"]
        band_name = task["band_name"]
        image_types = task["image_types"]
        card_id = card["card_id"]
        res_name = card["resourceSetName"]
        available_servers = card.get("available_servers", [])
        server_list = ", ".join([SERVER_NAMES.get(s, s) for s in available_servers])
        log_func(f"卡面ID: {card_id} - 可用服务器: {server_list if server_list else '未知'}")
        # 服务器选择逻辑与批量下载一致
        selected_server = None
        servers_to_try = available_servers if available_servers else SERVERS
        network_error_count = 0
        server_found = False
        # 新增：特殊回退逻辑
        if "card_normal.png" in image_types:
            # 先尝试用card_normal.png
            for server in servers_to_try:
                if self.download_canceled:
                    return result
                base_url = f"https://bestdori.com/assets/{server}/characters/resourceset/{res_name}_rip/card_normal.png"
                try:
                    response = requests.get(base_url, timeout=10, stream=True)
                    if response.status_code == 200:
                        content = b""
                        for chunk in response.iter_content(chunk_size=1024):
                            content += chunk
                            if len(content) >= 1024:
                                break
                        if len(content) >= 512:
                            try:
                                full_response = requests.get(base_url, timeout=10)
                                if full_response.status_code == 200:
                                    file_size = len(full_response.content)
                                    log_func(f"服务器 {server} 文件大小: {file_size / 1024:.1f}KB")
                                    if file_size >= 20 * 1024:
                                        selected_server = server
                                        log_func(f"选择服务器: {SERVER_NAMES.get(selected_server, selected_server)} (文件大小: {file_size / 1024:.1f}KB)")
                                        server_found = True
                                        break
                                    else:
                                        log_func(f"跳过服务器 {server}: 文件过小 ({file_size / 1024:.1f}KB < 20KB)")
                                else:
                                    log_func(f"跳过服务器 {server}: HTTP状态 {full_response.status_code}")
                            except Exception as e:
                                log_func(f"获取服务器 {server} 文件大小失败: {str(e)}")
                        else:
                            log_func(f"跳过服务器 {server}: 文件数据不足 ({len(content)} 字节)")
                    else:
                        log_func(f"跳过服务器 {server}: HTTP状态 {response.status_code}")
                except Exception as e:
                    network_error_count += 1
                    log_func(f"检查服务器 {server} 失败: {str(e)}")
            # 如果没找到，再用card_after_training.png
            if not server_found:
                log_func("card_normal.png所有服务器都不可用，尝试用card_after_training.png确定服务器")
                for server in servers_to_try:
                    if self.download_canceled:
                        return result
                    base_url = f"https://bestdori.com/assets/{server}/characters/resourceset/{res_name}_rip/card_after_training.png"
                    try:
                        response = requests.get(base_url, timeout=10, stream=True)
                        if response.status_code == 200:
                            content = b""
                            for chunk in response.iter_content(chunk_size=1024):
                                content += chunk
                                if len(content) >= 1024:
                                    break
                            if len(content) >= 512:
                                try:
                                    full_response = requests.get(base_url, timeout=10)
                                    if full_response.status_code == 200:
                                        file_size = len(full_response.content)
                                        log_func(f"服务器 {server} 文件大小: {file_size / 1024:.1f}KB")
                                        if file_size >= 20 * 1024:
                                            selected_server = server
                                            log_func(f"选择服务器: {SERVER_NAMES.get(selected_server, selected_server)} (文件大小: {file_size / 1024:.1f}KB)")
                                            server_found = True
                                            break
                                        else:
                                            log_func(f"跳过服务器 {server}: 文件过小 ({file_size / 1024:.1f}KB < 20KB)")
                                    else:
                                        log_func(f"跳过服务器 {server}: HTTP状态 {full_response.status_code}")
                                except Exception as e:
                                    log_func(f"获取服务器 {server} 文件大小失败: {str(e)}")
                            else:
                                log_func(f"跳过服务器 {server}: 文件数据不足 ({len(content)} 字节)")
                        else:
                            log_func(f"跳过服务器 {server}: HTTP状态 {response.status_code}")
                    except Exception as e:
                        network_error_count += 1
                        log_func(f"检查服务器 {server} 失败: {str(e)}")
                # 如果用card_after_training.png找到服务器，只下载训练后两种
                if server_found:
                    # 只选card_normal时，回退只下载card_after_training
                    if image_types == ["card_normal.png"]:
                        image_types = ["card_after_training.png"]
                    # 全部下载或包含其它类型时，回退只下载训练后两种
                    elif set(image_types) == set(["card_normal.png", "card_after_training.png", "trim_normal.png", "trim_after_training.png"]):
                        image_types = ["card_after_training.png", "trim_after_training.png"]
                    # 其它情况（如card_normal+card_after_training），只保留card_after_training
                    elif "card_after_training.png" in image_types:
                        image_types = ["card_after_training.png"]
        else:
            # 原有逻辑
            for server in servers_to_try:
                if self.download_canceled:
                    return result
                base_url = f"https://bestdori.com/assets/{server}/characters/resourceset/{res_name}_rip/card_normal.png"
                try:
                    response = requests.get(base_url, timeout=10, stream=True)
                    if response.status_code == 200:
                        content = b""
                        for chunk in response.iter_content(chunk_size=1024):
                            content += chunk
                            if len(content) >= 1024:
                                break
                        if len(content) >= 512:
                            try:
                                full_response = requests.get(base_url, timeout=10)
                                if full_response.status_code == 200:
                                    file_size = len(full_response.content)
                                    log_func(f"服务器 {server} 文件大小: {file_size / 1024:.1f}KB")
                                    if file_size >= 20 * 1024:
                                        selected_server = server
                                        log_func(f"选择服务器: {SERVER_NAMES.get(selected_server, selected_server)} (文件大小: {file_size / 1024:.1f}KB)")
                                        server_found = True
                                        break
                                    else:
                                        log_func(f"跳过服务器 {server}: 文件过小 ({file_size / 1024:.1f}KB < 20KB)")
                                else:
                                    log_func(f"跳过服务器 {server}: HTTP状态 {full_response.status_code}")
                            except Exception as e:
                                log_func(f"获取服务器 {server} 文件大小失败: {str(e)}")
                        else:
                            log_func(f"跳过服务器 {server}: 文件数据不足 ({len(content)} 字节)")
                    else:
                        log_func(f"跳过服务器 {server}: HTTP状态 {response.status_code}")
                except Exception as e:
                    network_error_count += 1
                    log_func(f"检查服务器 {server} 失败: {str(e)}")
        # 下载所有需要的图片类型
        char_dir = self.get_char_dir(band_name, char_name)
        card_dir = self.get_card_dir(char_dir)
        trim_dir = self.get_trim_dir(char_dir)
        os.makedirs(card_dir, exist_ok=True)
        os.makedirs(trim_dir, exist_ok=True)
        # 新增：如果selected_server为None，直接判定为失败
        if not selected_server:
            log_func("未能找到可用服务器，下载失败")
            result["failed"] = len(image_types)
            self.download_logger.log_failure(card_id, "服务器选择失败", "所有服务器均不可用", "无可用服务器")
            failure_log.append({
                "card_id": card_id,
                "url": "服务器选择失败",
                "error": "所有服务器均不可用"
            })
            log_failure(f"卡面 {card_id} 下载失败: 所有服务器均不可用")
            return result
        for img_type in image_types:
            if self.download_canceled:
                return result
            if "card_" in img_type:
                save_dir = card_dir
            else:
                save_dir = trim_dir
            file_name = f"{char_name}_{card_id}_{self.get_image_type_short(img_type)}.png"
            safe_file_name = sanitize_filename(file_name)
            save_path = os.path.join(save_dir, safe_file_name)
            if os.path.exists(save_path):
                log_func(f"跳过已存在文件: {safe_file_name}")
                result["skipped"] += 1
                self.download_logger.log_skip(card_id, save_path, "文件已存在", selected_server)
                continue
            img_url = f"https://bestdori.com/assets/{selected_server}/characters/resourceset/{res_name}_rip/{img_type}"
            log_func(f"下载: {img_url}")
            success, error = self.download_image(img_url, save_path, log_func, card_id, selected_server)
            if success and (error is None or error == ""):
                result["downloaded"] += 1
            elif success and error and "文件过小" in error:
                result["skipped"] += 1
                self.download_logger.log_skip(card_id, img_url, "文件过小", selected_server)
            else:
                result["failed"] += 1
                log_failure(f"下载失败: {img_url}")
                log_failure(f"错误: {error}")
                self.failed_downloads.append({
                    "url": img_url,
                    "save_path": save_path,
                    "error": error,
                    "card_id": card_id,
                    "server": selected_server
                })
                failure_log.append({
                    "card_id": card_id,
                    "url": img_url,
                    "error": error
                })
        return result

    def on_model_changed(self, event=None):
        """模型切换时，更新配置"""
        model = self.realesrgan_model_var.get()
        self.realesrgan_model = model  # 更新当前使用的模型
        
    def on_realesrgan_normal_format_changed(self, event=None):
        """Real-ESRGAN普通卡面输出格式变化时，更新配置"""
        format_value = self.realesrgan_normal_format_var.get()
        self.realesrgan_normal_format = format_value  # 更新当前使用的格式
        
    def on_waifu2x_normal_format_changed(self, event=None):
        """waifu2x普通卡面输出格式变化时，更新配置"""
        format_value = self.waifu2x_normal_format_var.get()
        self.waifu2x_normal_format = format_value  # 更新当前使用的格式



    def on_upscale_engine_changed(self, event=None):
        """切换超分引擎时，动态显示对应设置区域"""
        engine = self.upscale_engine_var.get()
        self.upscale_engine = engine  # 更新当前使用的引擎
        
        if engine == "Real-ESRGAN":
            self.realesrgan_frame.pack(fill=tk.X, padx=5, pady=5)
            self.waifu2x_frame.pack_forget()
        else:
            self.realesrgan_frame.pack_forget()
            self.waifu2x_frame.pack(fill=tk.X, padx=5, pady=5)
            # 切换到waifu2x时，根据配置的模型目录选择对应的默认模型
            if self.waifu2x_model_dir == "models-upconv_7_anime_style_art_rgb":
                default_model = self.waifu2x_model_anime
            elif self.waifu2x_model_dir == "models-upconv_7_photo":
                default_model = self.waifu2x_model_photo
            else:  # models-cunet
                default_model = self.waifu2x_model_cunet
            
            waifu_models = self.waifu_model_noise_map.keys()
            if default_model in waifu_models:
                self.waifu_model_var.set(default_model)
                self.update_waifu_noise_options(default_model)
                
            # 更新输出格式变量的值
            if hasattr(self, 'realesrgan_normal_format_var'):
                self.realesrgan_normal_format_var.set(self.realesrgan_normal_format)
            if hasattr(self, 'waifu2x_normal_format_var'):
                self.waifu2x_normal_format_var.set(self.waifu2x_normal_format)

    def on_waifu_model_changed(self, event=None):
        model = self.waifu_model_var.get()
        self.update_waifu_noise_options(model)
        # 根据当前模型目录更新对应的配置项
        if self.waifu2x_model_dir == "models-upconv_7_anime_style_art_rgb":
            self.waifu2x_model_anime = model
        elif self.waifu2x_model_dir == "models-upconv_7_photo":
            self.waifu2x_model_photo = model
        else:  # models-cunet
            self.waifu2x_model_cunet = model
        

    def update_waifu_noise_options(self, model):
        # 只显示唯一噪声等级
        noise = self.waifu_model_noise_map.get(model, 0)
        self.waifu_noise_var.set(noise)

    def get_image_type_short(self, img_type):
        # img_type: card_normal.png, trim_after_training.png
        key = img_type.replace('.png', '')
        return IMAGE_TYPE_MAP.get(key, key)

    def get_model_short(self, model_name):
        return MODEL_NAME_MAP.get(model_name, model_name)

    def show_custom_message(self, title, message, msg_type='normal'):
        # msg_type: 'happy', 'sad', 'normal'
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("520x540")
        win.transient(self)
        win.grab_set()
        # 随机图片
        img_list = self.result_images.get(msg_type, [])
        img = random.choice(img_list) if img_list else None
        if img:
            ttk.Label(win, image=img).pack(pady=10)
        ttk.Label(win, text=message, font=("YaHei", 12), wraplength=380).pack(pady=10)
        btn = ttk.Button(win, text="确定", command=win.destroy)
        btn.pack(pady=18)
        # 绑定回车关闭
        win.bind('<Return>', lambda e: win.destroy())
        btn.focus_set()

    def check_download_status(self):
        """检测是否有未完成的下载任务（包括暂停的任务）"""
        # 检查是否有正在进行的下载任务
        if hasattr(self, 'download_in_progress') and self.download_in_progress:
            if hasattr(self, 'pause_download') and self.pause_download:
                return True, "有暂停的下载任务"
            else:
                return True, "有正在进行的下载任务"
        
        # 检查是否有正在进行的超分任务
        if hasattr(self, 'upscale_process') and self.upscale_process:
            if hasattr(self, 'upscale_canceled') and self.upscale_canceled:
                return True, "有已取消的超分任务"
            else:
                return True, "有正在进行的超分任务"
        
        # 检查是否有暂停的下载任务（即使download_in_progress为False）
        if hasattr(self, 'pause_download') and self.pause_download:
            return True, "有暂停的下载任务"
        
        return False, None

    def reset_download_status(self):
        """强制重置所有下载相关状态，用于处理异常情况"""
        self.download_in_progress = False
        self.pause_download = False
        self.download_canceled = False
        self.upscale_canceled = False
        if hasattr(self, 'upscale_process') and self.upscale_process:
            try:
                self.upscale_process.terminate()
            except:
                pass
            self.upscale_process = None
        self.log_message("已重置下载状态")


if __name__ == "__main__":
    app = BangDreamTool()
    app.mainloop()
