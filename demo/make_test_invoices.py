# -*- coding: utf-8 -*-
"""生成模拟的增值税电子普通发票 PDF（A4 页面，内容仅占上半部分），用于测试合并工具。"""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color, HexColor

FONT = "MSYH"
try:
    pdfmetrics.registerFont(TTFont(FONT, "C:/Windows/Fonts/msyh.ttc", subfontIndex=0))
except Exception as e:
    print("msyh failed:", e)
    FONT = "Helvetica"

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
W, H = A4  # 595.28 x 841.89

RED = HexColor("#9E2B25")
BROWN = HexColor("#A83A2E")
GRAY = HexColor("#888888")


def draw_invoice(c, data):
    """在 A4 页面上半部分绘制一张发票，内容区域约 560 x 400 pt。"""
    left = 18
    right = W - 18
    top = H - 30
    bottom = top - 400          # 内容底部，下面全是空白

    # 外框（双线）
    c.setStrokeColor(BROWN)
    c.setLineWidth(1.4)
    c.rect(left, bottom, right - left, top - bottom)
    c.setLineWidth(0.5)
    c.rect(left + 3, bottom + 3, right - left - 6, top - bottom - 6)

    # 标题
    c.setFillColor(BROWN)
    c.setFont(FONT, 18)
    c.drawCentredString(W / 2, top - 30, "增值税电子普通发票")
    c.setFont(FONT, 9)
    c.drawCentredString(W / 2, top - 44, data["subtitle"])

    # 右上角发票代码/号码
    c.setFillColor(GRAY)
    c.setFont(FONT, 8)
    c.drawRightString(right - 12, top - 22, "发票代码：" + data["code"])
    c.drawRightString(right - 12, top - 34, "发票号码：" + data["no"])
    c.drawRightString(right - 12, top - 46, "开票日期：" + data["date"])

    # 分隔线
    c.setStrokeColor(BROWN)
    c.setLineWidth(0.6)
    c.line(left + 8, top - 56, right - 8, top - 56)

    # 购买方 / 销售方
    y = top - 70
    c.setFillColor(BROWN)
    c.setFont(FONT, 9)
    c.drawString(left + 12, y, "购买方")
    c.setFillColor(HexColor("#222222"))
    c.setFont(FONT, 9)
    c.drawString(left + 60, y, "名称：" + data["buyer"])
    y -= 16
    c.drawString(left + 60, y, "纳税人识别号：" + data["buyer_tax"])
    y -= 16
    c.drawString(left + 60, y, "地址、电话：" + data["buyer_addr"])

    y = top - 70
    c.setFillColor(BROWN)
    c.setFont(FONT, 9)
    c.drawString(W / 2 + 10, y, "销售方")
    c.setFillColor(HexColor("#222222"))
    c.drawString(W / 2 + 62, y, "名称：" + data["seller"])
    y -= 16
    c.drawString(W / 2 + 62, y, "纳税人识别号：" + data["seller_tax"])
    y -= 16
    c.drawString(W / 2 + 62, y, "地址、电话：" + data["seller_addr"])

    # 明细表
    table_top = top - 128
    c.setStrokeColor(BROWN)
    c.setLineWidth(0.8)
    cols = [left + 8, left + 60, left + 230, left + 300, left + 380, right - 8]
    row_h = 20

    # 表头
    c.setFillColor(HexColor("#F7F0EC"))
    c.rect(cols[0], table_top - row_h, cols[-1] - cols[0], row_h, fill=1, stroke=0)
    c.setFillColor(HexColor("#333333"))
    c.setFont(FONT, 8.5)
    heads = ["序号", "货物或应税劳务、服务名称", "规格型号", "数量", "单价", "金额"]
    for i, h in enumerate(heads):
        c.drawString(cols[i] + 5, table_top - row_h + 6, h)

    # 商品行
    c.setFont(FONT, 8.5)
    c.setFillColor(HexColor("#222222"))
    for i, item in enumerate(data["items"]):
        ry = table_top - row_h * (i + 2)
        c.setStrokeColor(HexColor("#CCCCCC"))
        c.setLineWidth(0.4)
        c.rect(cols[0], ry, cols[-1] - cols[0], row_h, fill=0, stroke=1)
        c.setFillColor(HexColor("#222222"))
        c.drawString(cols[0] + 5, ry + 6, str(i + 1))
        c.drawString(cols[1] + 5, ry + 6, item[0])
        c.drawString(cols[2] + 5, ry + 6, "—")
        c.drawString(cols[3] + 5, ry + 6, item[1])
        c.drawString(cols[4] + 5, ry + 6, item[2])
        c.drawString(cols[5] - 60, ry + 6, item[3])

    # 合计行
    total_y = table_top - row_h * (len(data["items"]) + 2)
    c.setStrokeColor(BROWN)
    c.setLineWidth(0.8)
    c.rect(cols[0], total_y - 44, cols[-1] - cols[0], 44, fill=0, stroke=1)
    c.setFont(FONT, 8.5)
    c.setFillColor(HexColor("#333333"))
    c.drawString(cols[1] + 5, total_y - 16, "合计")
    c.drawString(cols[5] - 70, total_y - 16, "¥ " + data["amount"])
    c.drawString(cols[1] + 5, total_y - 34, "价税合计（大写）  " + data["amount_cn"])
    c.setFont(FONT, 11)
    c.setFillColor(HexColor("#C0392B"))
    c.drawString(cols[5] - 70, total_y - 34, "¥ " + data["amount"])

    # 备注 + 开票人
    note_y = total_y - 58
    c.setFont(FONT, 8)
    c.setFillColor(HexColor("#444444"))
    c.drawString(left + 12, note_y, "备注：" + data["note"])
    c.drawString(left + 12, note_y - 16, "收款人：张三          复核：李四          开票人：王五")
    c.setFillColor(BROWN)
    c.setFont(FONT, 8)
    c.drawString(left + 12, bottom + 10, "销售方（章）")

    # 印章（圆形，模拟红色发票专用章）
    c.saveState()
    c.setStrokeColor(Color(0.78, 0.20, 0.18, alpha=0.75))
    c.setFillColor(Color(0.78, 0.20, 0.18, alpha=0.75))
    c.setLineWidth(1.6)
    cx, cy = right - 90, bottom + 42
    c.circle(cx, cy, 34, stroke=1, fill=0)
    c.setFont(FONT, 9)
    c.drawCentredString(cx, cy + 6, "发票专用章")
    c.setFont(FONT, 7)
    c.drawCentredString(cx, cy - 8, data["seller"][:12])
    c.restoreState()


def build(path, data):
    c = canvas.Canvas(path, pagesize=A4)
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    draw_invoice(c, data)
    c.showPage()
    c.save()
    print("created:", path)


samples = [
    dict(code="044001900111", no="28816071", date="2026年10月12日",
         subtitle="全国统一发票监制章 广东税务局",
         buyer="广州某某网络科技有限公司", buyer_tax="91440101MA5CX8XX2B",
         buyer_addr="广州市天河区体育西路 103 号 020-88886666",
         seller="滴滴出行科技有限公司", seller_tax="91110108MA00XXXX1A",
         seller_addr="北京市海淀区东北旺西路 8 号 400-000-0999",
         items=[("运输服务*客运服务费", "1", "45.00", "45.00"),
                ("运输服务*客运服务费", "1", "23.50", "23.50")],
         amount="68.50", amount_cn="陆拾捌圆伍角整", note="行程单号 1234567890"),
    dict(code="044001900111", no="28816072", date="2026年10月18日",
         subtitle="全国统一发票监制章 广东税务局",
         buyer="广州某某网络科技有限公司", buyer_tax="91440101MA5CX8XX2B",
         buyer_addr="广州市天河区体育西路 103 号 020-88886666",
         seller="广州酒家集团股份有限公司", seller_tax="91440101MA59XXXX8C",
         seller_addr="广州市荔湾区文昌南路 2 号 020-81234567",
         items=[("餐饮服务*餐费", "1", "320.00", "320.00")],
         amount="320.00", amount_cn="叁佰贰拾圆整", note="业务招待"),
    dict(code="044001900111", no="28816073", date="2026年10月25日",
         subtitle="全国统一发票监制章 广东税务局",
         buyer="广州某某网络科技有限公司", buyer_tax="91440101MA5CX8XX2B",
         buyer_addr="广州市天河区体育西路 103 号 020-88886666",
         seller="中国移动通信集团广东有限公司", seller_tax="91440000MA4XXXXK3D",
         seller_addr="广州市天河区珠江新城 020-10086",
         items=[("电信服务*通信费", "1", "199.00", "199.00")],
         amount="199.00", amount_cn="壹佰玖拾玖圆整", note="10月账单"),
]

for i, s in enumerate(samples, 1):
    build(os.path.join(OUT_DIR, "test_invoice_%d.pdf" % i), s)

# 再生成一个"多页"的发票包，测试同文件多页
from reportlab.pdfgen import canvas as c2
p = os.path.join(OUT_DIR, "test_invoice_multi.pdf")
c = c2.Canvas(p, pagesize=A4)
for s in samples[:2]:
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    draw_invoice(c, s)
    c.showPage()
c.save()
print("created:", p)
