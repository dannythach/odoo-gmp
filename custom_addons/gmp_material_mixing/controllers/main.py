from odoo import http
from odoo.http import request

class MixingQRController(http.Controller):
    @http.route('/mixing/create/<int:plan_id>', type='http', auth="user")
    def create_mixing_from_qr(self, plan_id, **kw):
        # 1. Tìm ID của action "Nhào trộn NPL"
        action = request.env.ref('gmp_material_mixing.action_gmp_material_mixing_create')
        
        # 2. Tạo URL điều hướng với context được nhúng chặt vào bên trong
        menu_id = request.env.ref('gmp_material_mixing.menu_gmp_material_mixing').id # Thay bằng ID menu của bạn
        
        url = "/web#action=%s&model=gmp.material.mixing&view_type=form&menu_id=%s" % (action.id, menu_id)
        
        # 3. Ép Odoo phải nhận context này thông qua session
        # Đây là cách "vượt rào" chắc chắn nhất
        return request.redirect(url + "&default_productionplan_id=%s" % plan_id)