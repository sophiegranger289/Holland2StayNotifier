# Holland2Stay 房源监控通知机器人

一个自动监控 Holland2Stay 网站并通过 Telegram 发送新房源通知的机器人。

[English](#english) | [中文说明](#chinese)

<a name="english"></a>
## English

### Features
- Automatically monitors Holland2Stay website for new house listings
- Sends notifications to Telegram groups when new houses are available
- Supports multiple cities and groups
- Customizable monitoring intervals
- Supports different contract types and room configurations

### Requirements
- Python 3.8 or higher
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
- Telegram Group ID (add [@RawDataBot](https://t.me/RawDataBot) to your group to get it)

### Installation
```bash
# Clone the repository
git clone https://github.com/YourUsername/Holland2StayNotifier.git
cd Holland2StayNotifier/h2snotifier

# Create and activate virtual environment
python -m venv venv
# For Windows
venv\Scripts\activate
# For Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup configuration
cp config_example.json config.json 
cp env_example .env 
```

### Configuration
1. Edit `.env` file:
   ```
   TELEGRAM_API_KEY=your_bot_token_here
   DEBUGGING_CHAT_ID=your_debug_group_id
   ```

2. Edit `config.json`:
   ```json
   {
     "telegram": {
       "groups": [
         {
           "name": "YourGroupName",
           "join_link": "https://t.me/your_group_link",
           "cities": ["24", "90"],
           "chat_id": -100000000000
         }
       ]
     }
   }
   ```

   Available city codes:
   ```
   24: Amsterdam       90: Den Haag        29: Eindhoven
   320: Arnhem        110: Diemen         545: Groningen
   619: Capelle       620: Dordrecht      616: Haarlem
   26: Delft         6099: Helmond       6209: Maarssen
   28: Den Bosch     6090: Maastricht    6051: Nieuwegein
   6217: Nijmegen     25: Rotterdam      6224: Rijswijk
   6211: Sittard     6093: Tilburg        27: Utrecht
   6145: Zeist       6088: Zoetermeer
   ```

### Usage
1. Test run:
   ```bash
   python main.py
   ```

2. Setup automatic monitoring:
   - For Linux/Mac (using cron):
     ```bash
     crontab -e
     # Add this line to check every 5 minutes
     */5 * * * * cd /path/to/Holland2StayNotifier/h2snotifier/ && python main.py
     ```
   - For Windows (using Task Scheduler):
     1. Open Task Scheduler
     2. Create Basic Task
     3. Set trigger to run every 5 minutes
     4. Action: Start a program
     5. Program: `path_to_python.exe`
     6. Arguments: `main.py`
     7. Start in: `path_to_h2snotifier_folder`

<a name="chinese"></a>
## 中文说明

### 功能特点
- 自动监控 Holland2Stay 网站的新房源
- 当有新房源时通过 Telegram 发送通知
- 支持监控多个城市和群组
- 可自定义监控间隔
- 支持不同的合同类型和房间配置

### 系统要求
- Python 3.8 或更高版本
- Telegram 机器人 Token (从 [@BotFather](https://t.me/botfather) 获取)
- Telegram 群组 ID (将 [@RawDataBot](https://t.me/RawDataBot) 添加到群组获取)

### 安装步骤
```bash
# 克隆仓库
git clone https://github.com/YourUsername/Holland2StayNotifier.git
cd Holland2StayNotifier/h2snotifier

# 创建并激活虚拟环境
python -m venv venv
# Windows系统
venv\Scripts\activate
# Linux/Mac系统
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 设置配置文件
cp config_example.json config.json 
cp env_example .env 
```

### 配置说明
1. 编辑 `.env` 文件：
   ```
   TELEGRAM_API_KEY=你的机器人Token
   DEBUGGING_CHAT_ID=调试群组ID
   ```

2. 编辑 `config.json`：
   ```json
   {
     "telegram": {
       "groups": [
         {
           "name": "你的群组名称",
           "join_link": "https://t.me/你的群组链接",
           "cities": ["24", "90"],
           "chat_id": -100000000000
         }
       ]
     }
   }
   ```

   可用的城市代码：
   ```
   24: 阿姆斯特丹    90: 海牙          29: 埃因霍温
   320: 阿纳姆      110: 迪门          545: 格罗宁根
   619: 卡佩勒      620: 多德雷赫特     616: 哈勒姆
   26: 代尔夫特    6099: 海尔蒙德      6209: 马尔森
   28: 登博斯      6090: 马斯特里赫特   6051: 新海恩
   6217: 奈梅亨     25: 鹿特丹        6224: 雷斯韦克
   6211: 锡塔德    6093: 蒂尔堡        27: 乌特勒支
   6145: 赛斯特    6088: 佐特尔梅尔
   ```

### 使用方法
1. 测试运行：
   ```bash
   python main.py
   ```

2. 设置自动监控：
   - Linux/Mac系统 (使用 cron)：
     ```bash
     crontab -e
     # 添加下面这行来每5分钟检查一次
     */5 * * * * cd /path/to/Holland2StayNotifier/h2snotifier/ && python main.py
     ```
   - Windows系统 (使用任务计划程序)：
     1. 打开任务计划程序
     2. 创建基本任务
     3. 设置每5分钟运行一次的触发器
     4. 操作：启动程序
     5. 程序：`python.exe的路径`
     6. 参数：`main.py`
     7. 起始于：`h2snotifier文件夹的路径`

## 注意事项
1. 确保您的 Telegram 机器人有足够的权限在群组中发送消息
2. 建议先在测试群组中运行程序，确保一切正常后再在正式群组中使用
3. 如果遇到问题，请检查日志文件 `house_sync.log`

## 许可证
MIT License
