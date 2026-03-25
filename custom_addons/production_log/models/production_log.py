from odoo import models, fields

class ProductionLog(models.Model):
    _name = "production.log"
    _description = "Nhật ký sản xuất"
    _order = "log_datetime desc"

    log_datetime = fields.Datetime(
        string="Thời gian",
        default=fields.Datetime.now,
        required=True
    )

    lot_code = fields.Char(string="Mã lô SX", required=True)
    batch_code = fields.Char(string="Mã nẻ")
    shaft_code = fields.Char(string="Mã số trục")

    speed_raw = fields.Float(string="V.tốc cán thô (v/p)")
    thickness_raw = fields.Float(string="Dày lá bột cán thô (mm)")

    speed_finish = fields.Float(string="V.tốc cán tinh (v/p)")
    thickness_finish = fields.Float(string="Dày lá bột cán tinh (mm)")

    condition_after = fields.Text(string="Tình trạng tấm/lá bột sau cán tinh")

    result = fields.Selection(
        [
            ("ok", "Đạt"),
            ("ng", "Không đạt"),
        ],
        string="Kết quả",
        default="ok"
    )

    operator = fields.Char(string="Người vận hành")
    note = fields.Text(string="Ghi chú")
