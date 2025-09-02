# DMG Password Brute Force Tool / DMG密码暴力破解工具

## ⚠️ 使用说明 / Legal Notice

**仅限合法用途：**

- 恢复自己忘记密码的 `.dmg` 文件
- 学习和研究目的

**禁止用于破解他人文件**，否则可能违反法律。作者不承担任何违法行为责任。

**For legal purposes only:**

- Recover your own forgotten `.dmg` passwords
- Educational/research purposes

Do **NOT** use this tool on files you do not own or have permission to access. Author is **not responsible** for illegal use.

------

## 📌 功能 Features

- 多进程暴力破解加密 `.dmg` 文件密码
- 显示每秒尝试次数 (TPS) 与估算剩余时间 (ETA)
- 成功生成文件时，在文件名前自动加上 `[crack-<密码>] - ` 前缀
- 可选每秒清理临时文件，仅保留最终成功文件

**Features:**

- Multi-process brute force `.dmg` passwords
- Real-time TPS and ETA display
- Auto rename cracked files with `[crack-<password>] - ` prefix
- Optional temp file cleanup per second

------

## 🛠️ 环境 Environment

- macOS 10.15+

- Python 3.8+

- 依赖库 / Required packages:

  ```bash
  pip install pexpect
  ```

- 支持 Intel/M1/M2 芯片 Mac

------

## 📂 安装 / Installation

1. 克隆或下载本仓库 / Clone or download this repo

2. 确保 Python 环境可用

3. 安装依赖:

   ```bash
   pip install pexpect
   ```

------

## 🚀 使用示例 Usage

```bash
python dmg_password_broker.py \
  --dmg_path "/Users/username/Desktop/my_secret.dmg" \
  --start 0 \
  --end 999999 \
  --length 6 \
  --processes 8 \
  --record_time \
  --cleanup_temp
```

### 参数说明 / Arguments

| 参数             | 描述                                                        | 默认值             |
| ---------------- | ----------------------------------------------------------- | ------------------ |
| `--dmg_path`     | 待破解的加密 `.dmg` 文件路径 / Path to the encrypted `.dmg` | 必填 / required    |
| `--output_path`  | 输出无密码文件路径 / Path for the cracked `.dmg`            | 桌面默认 / Desktop |
| `--start`        | 密码起始数字 / Start number                                 | 0                  |
| `--end`          | 密码结束数字 / End number                                   | 999999             |
| `--length`       | 密码长度 / Password length                                  | 6                  |
| `--processes`    | 并发进程数 / Number of concurrent processes                 | CPU核心数          |
| `--record_time`  | 是否记录总运行时间 / Record total runtime                   | False              |
| `--cleanup_temp` | 是否每秒清理临时文件 / Clean temp files every second        | False              |

------

### ✅ 功能示例

1. 使用 8 个进程，破解 6 位数字密码：

```bash
python dmg_password_broker.py \
  --dmg_path "/Users/username/Desktop/my_secret.dmg" \
  --start 100000 \
  --end 999999 \
  --length 6 \
  --processes 8 \
  --record_time
```

1. 使用临时文件清理，生成带密码前缀的无密码文件：

```bash
python dmg_password_broker.py \
  --dmg_path "/Users/username/Desktop/my_secret.dmg" \
  --start 0 \
  --end 999999 \
  --length 6 \
  --processes 10 \
  --cleanup_temp
```

> 成功后文件示例：
>
> ```
> [crack-123456] - my_secret.dmg
> ```

------

## 📖 代码整体思路 / Code Overview

1. **多进程分割任务**
   - 将总密码范围按进程数均分，每个进程独立尝试一部分密码
2. **暴力破解函数 `brute_force_worker`**
   - 使用 `pexpect` 执行 `hdiutil convert`
   - 判断密码是否正确
   - 成功后将文件重命名加 `[crack-<密码>] - ` 前缀
   - 可选清理临时文件
3. **进度监控 `progress_monitor`**
   - 每秒显示已尝试次数
   - 实时计算 TPS 和 ETA
4. **主函数 `main`**
   - 解析命令行参数
   - 创建临时目录
   - 启动监控进程和工作进程
   - 等待完成并清理临时文件（可选）

------

### 🔄 流程图 / Flow Diagram

```
           ┌───────────────────────────┐
           │       main()解析参数       │
           └────────────┬──────────────┘
                        │
                        ▼
           ┌───────────────────────────┐
           │   创建临时目录 & 初始化   │
           │  counter & found_flag     │
           └────────────┬──────────────┘
                        │
                        ▼
        ┌─────────────────────────────┐
        │ 启动 progress_monitor 进程  │
        └────────────┬────────────────┘
                     │
                     ▼
       ┌───────────────────────────────┐
       │ 启动 N 个 brute_force_worker   │
       │  每个进程尝试不同密码区间      │
       └────────────┬──────────────────┘
                    │
                    ▼
         ┌─────────────────────────┐
         │  worker 尝试密码循环      │
         │  1. 调用 hdiutil convert │
         │  2. 判断是否成功        │
         │  3. 更新 counter         │
         └────────────┬────────────┘
                      │
            ┌─────────┴─────────┐
            ▼                   ▼
 ┌────────────────────┐  ┌────────────────────┐
 │ 密码错误/失败       │  │ 密码成功           │
 │ 删除临时文件(可选) │  │ 生成新文件         │
 │                    │  │ 文件名加前缀       │
 │                    │  │ found_flag=True   │
 └────────────────────┘  └────────────────────┘
            │                   │
            └─────────┬─────────┘
                      ▼
          ┌─────────────────────┐
          │   所有进程结束       │
          │   清理临时目录       │
          └─────────┬───────────┘
                    ▼
          ┌─────────────────────┐
          │      爆破结束        │
          │  输出 TPS / ETA      │
          └─────────────────────┘
```

**说明 / Explanation：**

- 每个 `brute_force_worker` 负责尝试一段密码区间
- `progress_monitor` 实时显示 TPS 和 ETA
- 成功后自动生成 `[crack-<密码>] - <原文件名>` 文件
- 可选每秒清理临时文件，避免占用磁盘

------

## 📝 笔记 Notes

- `pexpect` 用于自动交互输入密码
- 使用 `multiprocessing.Value` 共享计数器
- 成功后文件命名方式方便识别
- 临时文件避免污染目标目录

------

## 🛡️ 许可 License

MIT License

- 欢迎贡献 / Contributions welcome
- 仅用于学习和合法用途

------

## 💡 贡献指南 Contributing

1. Fork 仓库
2. 创建功能分支 `git checkout -b feature-name`
3. 提交修改 `git commit -m "Add feature"`
4. 推送分支 `git push origin feature-name`
5. 创建 Pull Request

