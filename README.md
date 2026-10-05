# TÀI LÊ MMO Multi Downloader V5

Web downloader đa nền tảng dựa trên yt-dlp + FFmpeg.

## Chức năng
- Phân tích URL và nhận diện nền tảng.
- Facebook, TikTok, YouTube, Instagram, X/Twitter, Reddit, Vimeo và các site yt-dlp hỗ trợ.
- Chọn chất lượng video.
- Tách MP3 192 kbps.
- Giao diện responsive cho mobile.
- Docker + render.yaml để triển khai Render.

## Render
Tạo repo GitHub mới, upload toàn bộ nội dung thư mục này vào root repo.
Render > New Web Service > chọn repo > Runtime Docker > Free > Deploy.

## Lưu ý
Khả năng tải phụ thuộc vào extractor của yt-dlp và chính sách/chặn truy cập của từng nền tảng.
Không có cơ chế vượt đăng nhập, private content hoặc DRM.
Chỉ tải nội dung bạn có quyền lưu/sử dụng.

## Nguồn cảm hứng
Kiến trúc tính năng tham khảo dự án mã nguồn mở Yoink (coah80/yoink, MIT).
V5 này là implementation riêng bằng FastAPI/HTML/CSS/JS, không sao chép source Yoink.
