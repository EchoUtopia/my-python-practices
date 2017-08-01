#coding=utf-8
def find_tail_lines(fname, rev_n, line_num):
    '''
    函数功能：从文件倒数第rev_n开始打印line_num行内容
    :param fname: 文件地址
    :param rev_n: 从倒数第rev_n开始读取
    :param line_num: 读取多少行
    :return: 读取的内容
    '''
    with open(fname, 'rb') as f:
        buf_len = min(1024 * line_num, 4096)
        f.seek(0, 2)
        cur_pos = f.tell()  #找到末尾位置
        new_line_count = 0
        while cur_pos > 0:  #获取往回走的长度
            prev_pos = cur_pos
            cur_pos -= buf_len
            if cur_pos < 0:
                cur_pos = 0
                block_size = prev_pos
            else:
                block_size = buf_len
            f.seek(cur_pos)
            content = f.read(block_size)
            new_line_count += content.count('\n')  #找当前块有多少个换行符
            extra_count = new_line_count - rev_n  #内容块多了多少行
            if extra_count >= 0:
                start_pos = 0
                for i in range(0, extra_count):  #找到倒数第rev_n行位置
                    start_pos = content.find('\n', start_pos) + 1
                f.seek(cur_pos + start_pos)
                # print "---",f.read(), "---"
                for _ in range(0, line_num):  #读取line_num行
                    print "--", f.readline()
                break

def test():
    fname = "a.txt"
    find_tail_lines(fname, 5, 5)

if __name__ == "__main__":
    test()
