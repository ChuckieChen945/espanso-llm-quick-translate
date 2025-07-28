# espanso-llm-quick-translate

一个基于 espanso 的快速翻译包，支持 LLM 翻译、TTS 音频生成和 diff 显示。

## 🚀 新特性

### 重构优化

- ✅ **跑马灯效果**：为 ShowDiffs.ini 添加了动态滚动效果
- ✅ **更好的错误处理**：添加了重试机制、连接池管理和资源清理
- ✅ **线程安全**：使用锁机制确保多线程环境下的安全性
- ✅ **优雅关闭**：支持信号处理和资源清理
- ✅ **原子文件操作**：使用临时文件确保文件写入的原子性

### 核心功能

- 🔄 **即时翻译**：立即返回翻译结果，后台异步处理其他任务
- 🎵 **TTS 音频生成**：自动生成翻译文本的语音
- 📊 **Diff 显示**：在 Rainmeter 皮肤中显示原文与译文的差异
- 🎮 **快捷键播放**：使用 `<Ctrl-Q>` 播放最后生成的音频
- 🔧 **配置管理**：支持代理、重试、超时等高级配置

## 📋 系统要求

- Python 3.8+
- espanso
- Rainmeter （可选，用于 diff 显示）
- 网络连接 （用于 LLM API)

## 🛠️ 安装

1. 克隆项目到 espanso 包目录：

```bash
cd ~/.config/espanso/match/packages/
git clone <repository-url> espanso-llm-quick-translate
```

2. 安装依赖：

```bash
cd espanso-llm-quick-translate
pip install -r requirements.txt
```

3. 配置 API 密钥：

```bash
cp .espanso-llm-quick-translate.json.tmpl .espanso-llm-quick-translate.json
# 编辑配置文件，填入你的 API 密钥
```

## ⚙️ 配置

编辑 `.espanso-llm-quick-translate.json` 文件：

```json
{
    "api_key": "your-api-key",
    "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "model": "gemini-2.5-flash",
    "auto_play": "true",
    "diff_output_path": "path/to/diffs.ini",
    "showdiffs_skin_path": "path/to/ShowDiffs.ini",
    "audio_file_path": "translated.mp3",
    "sound_name": "en-GB-LibbyNeural",
    "target_language": "English",
    "system_prompt_path": "src/resources/system_prompt.txt",
    "timeout": 30,
    "max_retries": 3,
    "log_level": "INFO"
}
```

### 配置说明

| 配置项                | 说明               | 默认值            |
| --------------------- | ------------------ | ----------------- |
| `api_key`             | LLM API 密钥       | 必需              |
| `base_url`            | API 基础 URL       | 必需              |
| `model`               | 使用的模型名称     | 必需              |
| `auto_play`           | 是否自动播放音频   | false             |
| `diff_output_path`    | diff 文件输出路径  | diffs_text.txt    |
| `showdiffs_skin_path` | Rainmeter 皮肤路径 | 必需              |
| `audio_file_path`     | 音频文件路径       | translated.mp3    |
| `sound_name`          | TTS 语音名称       | en-GB-LibbyNeural |
| `target_language`     | 目标语言           | English           |
| `timeout`             | API 超时时间（秒） | 30                |
| `max_retries`         | 最大重试次数       | 3                 |
| `log_level`           | 日志级别           | INFO              |

## 🎯 使用方法

### 翻译文本

1. 输入 `::` 触发翻译
2. 在弹出的表单中输入要翻译的文本
3. 系统会立即返回翻译结果
4. 后台会自动生成音频和 diff 文件

### 播放音频

- 按 `<Ctrl-Q>` 播放最后生成的音频

## 🔧 开发

### 项目结构

```
espanso-llm-quick-translate/
├── src/
│   ├── config/          # 配置管理
│   ├── core/            # 核心服务
│   ├── services/        # 业务服务
│   ├── sound/           # 音频处理
│   ├── utils/           # 工具函数
│   └── resources/       # 资源文件
├── tests/               # 测试文件
├── logs/                # 日志文件
└── package.yml          # espanso 配置
```

### 运行测试

```bash
python tests/test_integration.py
```

### 日志文件

- `logs/translation.log` - 翻译相关日志
- `logs/audio.log` - 音频相关日志

## 🐛 故障排除

### 常见问题

1. **翻译失败**
   - 检查 API 密钥是否正确
   - 确认网络连接正常
   - 查看日志文件获取详细错误信息

2. **音频播放失败**
   - 确认系统音频设备正常
   - 检查音频文件是否生成
   - 验证 TTS 服务连接

3. **Diff 显示问题**
   - 确认 Rainmeter 已安装并运行
   - 检查皮肤文件路径是否正确
   - 验证 diff 文件是否生成

### 调试模式

设置日志级别为 DEBUG 获取更详细的信息：

```json
{
    "log_level": "DEBUG"
}
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [espanso](https://espanso.org/) - 文本扩展工具
- [Rainmeter](https://www.rainmeter.net/) - 桌面定制工具
- [Edge TTS](https://github.com/rany2/edge-tts) - 文本转语音服务
