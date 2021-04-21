from chardet.universaldetector import UniversalDetector
import os


def detcect_encoding(filepath):
    """检测文件编码
    Args:
        detector: UniversalDetector 对象
        filepath: 文件路径
    Return:
        file_encoding: 文件编码
        confidence: 检测结果的置信度，百分比
    """
    detector = UniversalDetector()
    detector.reset()
    for each in open(filepath, 'rb'):
        detector.feed(each)
        if detector.done:
            break
    detector.close()
    file_encoding = detector.result['encoding']
    confidence = detector.result['confidence']
    if file_encoding is None:
        file_encoding = 'unknown'
        confidence = 0.99
    return file_encoding, confidence * 100


if __name__ == '__main__':

    target_encoding = 'utf-16'

    rootdir = os.path.join(r'D:\RMT\TRY\txt')
    for (_, _, filenames) in os.walk(rootdir):
        for filename in filenames:
            filepath = rootdir + '\\' + filename

            file_encoding, confidence = detcect_encoding(filepath)
            # print(f'[+] {filename}: 编码 -> {encoding} (置信度 {confidence}%) [+]')

            if file_encoding != 'unknown' and confidence > 0.75:

                if file_encoding == 'GB2312':
                    file_encoding = 'GB18030'

                with open(filepath, 'r', encoding=file_encoding, errors='ignore') as f:
                    text = f.read()

                outpath = os.path.join(r'D:\RMT\TRY\TXTresult', filename)
                with open(outpath, 'w', encoding=target_encoding, errors='ignore') as f:
                    f.write(text)

                print(
                    f'[+] 转码成功: {filename}({file_encoding}) -> {outpath}({target_encoding}) [+]')
