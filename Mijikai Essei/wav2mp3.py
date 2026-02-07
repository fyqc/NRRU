import os
import re
import subprocess

# 用于将网络获取的wav音轨，根据cue文件拆分成mp3并写入歌曲信息

def parse_cue_gbk(cue_path):
    # 使用 gbk 编码读取
    with open(cue_path, "r", encoding="gbk") as f:
        content = f.read()

    # 提取专辑信息
    album_match = re.search(r'^TITLE "(.*)"', content, re.M)
    album_artist_match = re.search(r'^PERFORMER "(.*)"', content, re.M)

    album = album_match.group(1) if album_match else "Unknown Album"
    album_artist = (
        album_artist_match.group(1) if album_artist_match else "Unknown Artist"
    )

    # 匹配每一个 TRACK 块
    # 正则解释：匹配 TRACK、TITLE、PERFORMER(可选) 和 INDEX 01
    tracks = []
    track_blocks = re.findall(
        r"TRACK (\d+) AUDIO(.*?)(?=TRACK \d+ AUDIO|$)", content, re.S
    )

    for num, block in track_blocks:
        title = re.search(r'TITLE "(.*?)"', block).group(1)
        # 提取当前曲目的歌手，如果没有则沿用专辑歌手
        perf_match = re.search(r'PERFORMER "(.*?)"', block)
        artist = perf_match.group(1) if perf_match else album_artist

        # 关键：只取 INDEX 01 作为开始时间
        time_match = re.search(r"INDEX 01 (\d+:\d+:\d+)", block)
        if time_match:
            tracks.append(
                {
                    "number": num,
                    "title": title,
                    "artist": artist,
                    "start_time": time_match.group(1),
                }
            )

    return album, tracks


def cue_to_ffmpeg_time(cue_time):
    # CUE: MM:SS:FF -> FFmpeg: MM:SS.ms (1 frame = 1/75s = 0.0133s)
    m, s, f = map(int, cue_time.split(":"))
    ms = round(f / 75.0, 3)
    return f"{m:02d}:{s:02d}{str(ms)[1:]}"  # 格式化为 00:00.xxx


def process_audio(wav_file, cue_file, output_ext="mp3"):
    album, tracks = parse_cue_gbk(cue_file)

    for i, track in enumerate(tracks):
        start = cue_to_ffmpeg_time(track["start_time"])

        # 计算持续时间
        duration_args = []
        if i < len(tracks) - 1:
            # 简单粗暴地用下一首的 INDEX 01 减去当前 INDEX 01
            # FFmpeg 的 -to 参数比手动算时长更方便
            end = cue_to_ffmpeg_time(tracks[i + 1]["start_time"])
            duration_args = ["-to", end]

        # 文件名格式：01. 蔡依林 - 情不自禁 (失落的帝国).mp3
        out_name = f"{track['number'].zfill(2)}. {track['artist']} - {track['title']}.{output_ext}"

        # 编码设置
        if output_ext.lower() == "mp3":
            codec = ["-codec:a", "libmp3lame", "-q:a", "2"]  # 高质量 VBR
        else:  # aac
            codec = ["-codec:a", "aac", "-b:a", "256k"]

        cmd = (
            ["ffmpeg", "-i", wav_file, "-ss", start]
            + duration_args
            + [
                "-metadata",
                f"title={track['title']}",
                "-metadata",
                f"artist={track['artist']}",
                "-metadata",
                f"album={album}",
                "-metadata",
                f"track={track['number']}",
            ]
            + codec
            + [out_name, "-y"]
        )

        print(f"正在转换第 {track['number']} 首: {track['title']}")
        subprocess.run(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )


# --- 执行区 ---
if __name__ == "__main__":
    # 获取脚本所在的当前文件夹路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    # 自动寻找 CUE 文件
    cue_files = [f for f in os.listdir(".") if f.lower().endswith(".cue")]

    if not cue_files:
        print("错误：在当前目录下没找到 .cue 文件！")
    else:
        for cue_file in cue_files:
            # 尝试寻找对应的 WAV 文件
            # 逻辑：先找 CUE 内部指定的文件名，如果找不到，找同名的 .wav
            album_name = os.path.splitext(cue_file)[0]
            wav_file = album_name + ".wav"

            if not os.path.exists(wav_file):
                # 如果找不到，列出所有 wav 让用户确认或自动匹配第一个
                all_wavs = [
                    f for f in os.listdir(".") if f.lower().endswith(".wav")
                ]
                if all_wavs:
                    wav_file = all_wavs[0]
                else:
                    print(f"错误：找不到与 {cue_file} 匹配的 WAV 文件")
                    continue

            print(f"找到资源：\n  CUE: {cue_file}\n  WAV: {wav_file}\n")
            process_audio(wav_file, cue_file, "mp3")
