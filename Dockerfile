# Sử dụng image Odoo chính thức làm image cơ sở.
# Image này đã có sẵn Python, Odoo, và các thư viện cần thiết.
FROM odoo:17

# Cài đặt các thư viện cần thiết cho py3o
# --no-cache-dir giúp giảm dung lượng image
USER root

# Chỉ cài thư viện kết nối, không cần cài LibreOffice nữa
# Cập nhật và cài đặt các thư viện python cần thiết

# Cài đặt tất cả thư viện trong một lần RUN để tối ưu layer
RUN pip3 install --no-cache-dir \
    xlsxwriter \
    docxtpl \
    xlsxtpl \
    openpyxl \
    docxcompose \
    htmldocx

# Chạy lệnh CMD mặc định của image Odoo chính thức
# CMD ["odoo", "-c", "/etc/odoo/odoo.conf"]

USER odoo
