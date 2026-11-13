# webget.py
# 实验2 Part D: 手写 HTTP 客户端
# 仓库地址: https://github.com/ximiluoer/netlab2
# 用法: python webget.py host path [port]
import socket
import sys


def main():
    # 参数不够就打用法，免得后面 sys.argv 越界
    if len(sys.argv) < 3:
        print("usage: python webget.py <host> <path> [port]")
        sys.exit(1)

    host = sys.argv[1]
    path = sys.argv[2]
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 80      # 没给端口就用 80

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)          # 10 秒没数据就放弃，防止挂在坏服务器上
    s.connect((host, port))

    # HTTP/1.1 必须带 Host 头。写 Connection: close 是让服务器发完就断开，
    # 这样响应里就算没有 Content-Length，也能靠对端关闭来结束读取
    request = ("GET " + path + " HTTP/1.1\r\n"
               "Host: " + host + "\r\n"
               "Connection: close\r\n"
               "\r\n")
    s.sendall(request.encode())

    buf = b""        # 收到的字节全堆在这里
    n = 0            # recv 调用次数
    length = None    # 响应头里的 Content-Length
    head_end = -1    # 空行的位置，也即头和 body 的分界

    # 循环 recv 直到收完。结束条件只有两种：
    # 1) 响应头里有 Content-Length，body 够数了就停
    # 2) 没有 Content-Length，recv 返回空字节串（对端关闭）就停
    # 一次 recv 拿到多少字节是不确定的，所以必须循环，不能只调一次
    while True:
        try:
            chunk = s.recv(4096)
        except socket.timeout:
            break              # 超时，说明对方迟迟不发数据
        n += 1
        if not chunk:
            break              # 空字节串 = 对端关闭连接
        print("recv #%d: %d bytes" % (n, len(chunk)))
        buf += chunk

        if head_end < 0:
            # 头还没解析过，先找空行（\r\n\r\n）
            head_end = buf.find(b"\r\n\r\n")
            if head_end >= 0:
                head_text = buf[:head_end].decode("iso-8859-1")
                for line in head_text.split("\r\n")[1:]:
                    if line.lower().startswith("content-length:"):
                        length = int(line.split(":", 1)[1].strip())

        if head_end >= 0 and length is not None:
            if len(buf) - (head_end + 4) >= length:
                break          # body 收够了

    s.close()
    print("--- recv calls: %d, total bytes: %d ---" % (n, len(buf)))

    if head_end < 0:
        print("no complete response header")
        return

    # 按空行切成两块：前面是状态行 + 响应头，后面是 body
    head_text = buf[:head_end].decode("iso-8859-1")
    body = buf[head_end + 4:]

    lines = head_text.split("\r\n")
    print("--- status line ---")
    print(lines[0])
    print("--- response headers ---")
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            print(k.strip(), "=", v.strip())

    if length is not None and len(body) > length:
        body = body[:length]

    # 用 wb 二进制写，文本模式会把图片之类的数据改坏
    with open("response_body.bin", "wb") as f:
        f.write(body)
    print("--- body saved: %d bytes ---" % len(body))


if __name__ == "__main__":
    main()
