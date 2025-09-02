import os
import argparse
import time
import pexpect
from multiprocessing import Process, Value, Manager, cpu_count

def brute_force_worker(start, end, length, dmg_path, output_path, record_time, found_flag, counter, temp_dir, cleanup_temp):
    try:
        total = end - start + 1
        start_time = time.time() if record_time else None
        for idx, num in enumerate(range(start, end + 1)):
            if found_flag.value:
                return

            password = str(num).zfill(length)
            temp_output = os.path.join(temp_dir, f"{password}.dmg")

            cmd = f"hdiutil convert '{dmg_path}' -format UDRO -o '{temp_output}'"
            child = pexpect.spawn(cmd, timeout=15, encoding='utf-8')
            idx_psw = child.expect([r"请.*：", "created:", pexpect.EOF])

            if idx_psw == 0:
                child.sendline(password)
                idx_final = child.expect(["created:", "Authentication error", "hdiutil: convert failed", pexpect.EOF])
                child.close()
                with counter.get_lock():
                    counter.value += 1

                if idx_final == 0:
                    found_flag.value = True
                    # 构建带密码前缀的新文件名
                    cracked_filename = f"[crack-{password}] - {os.path.basename(output_path)}"
                    cracked_output_path = os.path.join(os.path.dirname(output_path), cracked_filename)
                    os.replace(temp_output, cracked_output_path)
                    print(f"\n✅ 密码找到：{password}")
                    print(f"✅ 文件生成成功：{cracked_output_path}")
                    if record_time:
                        print(f"⏱️ 总用时：{int((time.time()-start_time)//60)}分{int((time.time()-start_time)%60)}秒")
                    return
                else:
                    if cleanup_temp and os.path.exists(temp_output):
                        os.remove(temp_output)

            elif idx_psw == 1:  # 未加密
                found_flag.value = True
                cracked_filename = f"[crack-{password}] - {os.path.basename(output_path)}"
                cracked_output_path = os.path.join(os.path.dirname(output_path), cracked_filename)
                os.replace(temp_output, cracked_output_path)
                print("⚠️ 镜像未加密，直接转换成功")
                return
            else:
                print(f"⚠️ 未知错误：{child.before}")
                child.close()
                if cleanup_temp and os.path.exists(temp_output):
                    os.remove(temp_output)

    except Exception as e:
        print(f"❌ 进程错误：{e}")


def progress_monitor(total, counter, found_flag):
    last_count = 0
    start_time = time.time()
    while not found_flag.value and counter.value < total:
        time.sleep(1)
        with counter.get_lock():
            current_count = counter.value
        elapsed = max(time.time() - start_time, 1e-6)
        tps = current_count / elapsed
        eta = int((total - current_count) / max(tps, 1e-6))
        print(f"📊 已尝试 {current_count}/{total}，TPS {tps:.1f}/s，ETA {eta}s", end='\r')
        last_count = current_count
    print()


def main():
    parser = argparse.ArgumentParser(description="多进程暴力破解加密.dmg文件的密码")
    parser.add_argument("--dmg_path", type=str, required=True, help="加密的.dmg文件路径")
    parser.add_argument("--output_path", type=str, help="输出无密码.dmg文件路径")
    parser.add_argument("--start", type=int, default=0, help="密码起始数字")
    parser.add_argument("--end", type=int, default=999999, help="密码结束数字")
    parser.add_argument("--length", type=int, default=6, help="密码长度")
    parser.add_argument("--processes", type=int, default=cpu_count(), help="并发进程数")
    parser.add_argument("--record_time", action="store_true", help="记录运行时间")
    parser.add_argument("--cleanup_temp", action="store_true", help="每秒清理临时文件，仅保留最终成功文件")

    args = parser.parse_args()

    args.dmg_path = os.path.expanduser(args.dmg_path)
    args.dmg_path = os.path.normpath(args.dmg_path)

    if not os.path.exists(args.dmg_path):
        print(f"❌ 错误：路径 '{args.dmg_path}' 不存在")
        return

    if not args.output_path:
        args.output_path = os.path.join(os.path.expanduser("~/Desktop"), os.path.basename(args.dmg_path))
    args.output_path = os.path.expanduser(args.output_path)
    args.output_path = os.path.normpath(args.output_path)

    temp_dir = os.path.join(os.path.dirname(args.output_path), "tmp_dmg")
    os.makedirs(temp_dir, exist_ok=True)

    total_attempts = args.end - args.start + 1
    print(f"参数确认：路径={args.dmg_path}，输出={args.output_path}，范围={args.start}-{args.end}，长度={args.length}，进程数={args.processes}")

    counter = Value('i', 0, lock=True)
    manager = Manager()
    found_flag = manager.Value('b', False)

    step = total_attempts // args.processes
    processes = []

    monitor = Process(target=progress_monitor, args=(total_attempts, counter, found_flag))
    monitor.start()

    for i in range(args.processes):
        s = args.start + i * step
        e = args.start + (i + 1) * step - 1 if i < args.processes - 1 else args.end
        p = Process(target=brute_force_worker, args=(
            s, e, args.length, args.dmg_path, args.output_path,
            args.record_time, found_flag, counter, temp_dir, args.cleanup_temp
        ))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
    monitor.join()

    if args.cleanup_temp and os.path.exists(temp_dir):
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))
        os.rmdir(temp_dir)

    print("🔍 爆破结束。")


if __name__ == "__main__":
    main()
