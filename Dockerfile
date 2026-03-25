# Sử dụng image Odoo chính thức làm image cơ sở.
# Image này đã có sẵn Python, Odoo, và các thư viện cần thiết.
FROM odoo:18.0

# Chuyển thư mục làm việc vào nơi các addons tùy chỉnh được lưu trữ
WORKDIR /mnt/extra-addons

# Sao chép toàn bộ mã nguồn Odoo từ GitHub vào image.
# Giả sử thư mục chứa mã nguồn Odoo có tên là 'odoo'.
# Điều này là không cần thiết nếu bạn đã có 'odoo-bin' và các file khác ở cùng cấp.
# COPY ./odoo /opt/odoo

# Sao chép các addon tùy chỉnh của bạn vào image.
# Copy addons gốc của Odoo
# Patch module spreadsheet_dashboard_account
COPY ./addons/spreadsheet_dashboard \
     /usr/lib/python3/dist-packages/odoo/addons/spreadsheet_dashboard
# Giả sử thư mục chứa addons tùy chỉnh của bạn có tên là 'custom_addons'.
COPY ./custom_addons /mnt/extra-addons/custom_addons

# Copy file config (nếu có)
COPY ./odoo.conf /etc/odoo/odoo.conf

# Phân quyền cho user odoo
COPY --chown=odoo:odoo ./custom_addons /mnt/extra-addons/
COPY --chown=odoo:odoo ./odoo.conf /etc/odoo/
# RUN chown -R odoo:odoo /mnt/extra-addons /etc/odoo

# (Tùy chọn) Cài đặt các thư viện Python cho các addon tùy chỉnh của bạn.
# Nếu bạn có file requirements.txt trong thư mục 'custom_addons', hãy bật dòng này.
# COPY ./custom_addons/requirements.txt /tmp/requirements.txt
# RUN pip3 install -r /tmp/requirements.txt --no-cache-dir

# Chạy lệnh CMD mặc định của image Odoo chính thức
CMD ["odoo", "-c", "/etc/odoo/odoo.conf"]
