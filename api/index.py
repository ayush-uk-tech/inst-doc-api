from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List
import fitz
import os

app = FastAPI()

# --- PYDANTIC MODELS (n8n se aane wala Data format) ---
class TableRow(BaseModel):
    role: str
    exp: str
    min: str
    mid: str
    max: str

class PDFRequestData(BaseModel):
    # Page 1 Fields
    client_name: str
    address: str
    post_code: str
    company_reg: str
    vat_number: str
    fd_title: str
    fd_name: str
    client_contact: str
    email_address: str
    telephone: str
    position: str
    date: str
    tel: str
    email: str
    role_to_hire: str
    office_cost: str
    tech_cost: str
    client_name_bottom: str
    client_position_bottom: str
    client_date_bottom: str
    potentiam_person: str
    potentiam_position: str
    potentiam_date: str
    
    # Page 2 Fields (Table Array)
    table_data: List[TableRow] = []

# --- TABLE DRAWING FUNCTION ---
def draw_table_on_page2(page, table_data, start_x=41, start_y=430):
    col_widths = [135, 95, 75, 75, 75]
    row_height = 20
    current_y = start_y
    total_width = sum(col_widths)
    total_rows = 2 + len(table_data)
    total_height = row_height * total_rows

    # Outer border
    table_rect = fitz.Rect(start_x, current_y, start_x + total_width, current_y + total_height)
    page.draw_rect(table_rect, color=(0, 0, 0), width=1)

    # Header row backgrounds
    role_rect = fitz.Rect(start_x, current_y, start_x + col_widths[0], current_y + row_height)
    page.draw_rect(role_rect, color=(0, 0, 0), fill=(0.13, 0.27, 0.58))

    exp_rect = fitz.Rect(start_x + col_widths[0], current_y, start_x + col_widths[0] + col_widths[1], current_y + row_height)
    page.draw_rect(exp_rect, color=(0, 0, 0), fill=(0.13, 0.27, 0.58))

    india_rect = fitz.Rect(start_x + col_widths[0] + col_widths[1], current_y, start_x + total_width, current_y + row_height)
    page.draw_rect(india_rect, color=(0, 0, 0), fill=(1, 0.84, 0.13))

    # Header text
    page.insert_text(fitz.Point(start_x + 8, current_y + 13), "Role", fontsize=10, fontname="helv", color=(1, 1, 1))
    page.insert_text(fitz.Point(start_x + col_widths[0] + 8, current_y + 13), "Exp", fontsize=10, fontname="helv", color=(1, 1, 1))

    india_area_width = col_widths[2] + col_widths[3] + col_widths[4]
    india_start_x = start_x + col_widths[0] + col_widths[1]
    india_center_x = india_start_x + (india_area_width / 2) - 12
    page.insert_text(fitz.Point(india_center_x, current_y + 13), "INDIA", fontsize=10, fontname="helv", color=(0, 0, 0))

    current_y += row_height

    # Sub-header row
    role_sub_rect = fitz.Rect(start_x, current_y, start_x + col_widths[0], current_y + row_height)
    page.draw_rect(role_sub_rect, color=(0, 0, 0), fill=(0.95, 0.95, 0.95))

    exp_sub_rect = fitz.Rect(start_x + col_widths[0], current_y, start_x + col_widths[0] + col_widths[1], current_y + row_height)
    page.draw_rect(exp_sub_rect, color=(0, 0, 0), fill=(0.95, 0.95, 0.95))

    subheader_rect = fitz.Rect(start_x + col_widths[0] + col_widths[1], current_y, start_x + total_width, current_y + row_height)
    page.draw_rect(subheader_rect, color=(0, 0, 0), fill=(1, 0.84, 0.13))

    page.insert_text(fitz.Point(start_x + col_widths[0] + col_widths[1] + 8, current_y + 13), "Min", fontsize=9, fontname="helv", color=(0, 0, 0))
    page.insert_text(fitz.Point(start_x + col_widths[0] + col_widths[1] + col_widths[2] + 8, current_y + 13), "Mid", fontsize=9, fontname="helv", color=(0, 0, 0))
    page.insert_text(fitz.Point(start_x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + 8, current_y + 13), "Max", fontsize=9, fontname="helv", color=(0, 0, 0))

    current_y += row_height

    # Data rows
    for row_data in table_data:
        row_rect = fitz.Rect(start_x, current_y, start_x + total_width, current_y + row_height)
        page.draw_rect(row_rect, color=(0, 0, 0), fill=(0.92, 0.92, 0.92))

        page.insert_text(fitz.Point(start_x + 8, current_y + 13), str(row_data.get("role", ""))[:18], fontsize=9, fontname="helv", color=(0, 0, 0))
        page.insert_text(fitz.Point(start_x + col_widths[0] + 8, current_y + 13), str(row_data.get("exp", "")), fontsize=9, fontname="helv", color=(0, 0, 0))
        page.insert_text(fitz.Point(start_x + col_widths[0] + col_widths[1] + 8, current_y + 13), str(row_data.get("min", "")), fontsize=9, fontname="helv", color=(0, 0, 0))
        page.insert_text(fitz.Point(start_x + col_widths[0] + col_widths[1] + col_widths[2] + 8, current_y + 13), str(row_data.get("mid", "")), fontsize=9, fontname="helv", color=(0, 0, 0))
        page.insert_text(fitz.Point(start_x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + 8, current_y + 13), str(row_data.get("max", "")), fontsize=9, fontname="helv", color=(0, 0, 0))

        current_y += row_height

    # Vertical & Horizontal Lines
    page.draw_line(fitz.Point(start_x + col_widths[0], start_y), fitz.Point(start_x + col_widths[0], start_y + total_height), color=(0, 0, 0), width=1)
    page.draw_line(fitz.Point(start_x + col_widths[0] + col_widths[1], start_y), fitz.Point(start_x + col_widths[0] + col_widths[1], start_y + total_height), color=(0, 0, 0), width=1)
    sub_header_y = start_y + row_height
    page.draw_line(fitz.Point(start_x + col_widths[0] + col_widths[1] + col_widths[2], sub_header_y), fitz.Point(start_x + col_widths[0] + col_widths[1] + col_widths[2], start_y + total_height), color=(0, 0, 0), width=1)
    page.draw_line(fitz.Point(start_x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3], sub_header_y), fitz.Point(start_x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3], start_y + total_height), color=(0, 0, 0), width=1)

    for i in range(total_rows + 1):
        y_pos = start_y + (i * row_height)
        page.draw_line(fitz.Point(start_x, y_pos), fitz.Point(start_x + total_width, y_pos), color=(0, 0, 0), width=1)


# --- MAIN API ENDPOINT ---
@app.post("/generate-custom-pdf")
async def generate_custom_pdf_api(data: PDFRequestData):
    try:
        # Template Path resolution
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(current_dir, "merged_final.pdf")
        
        doc = fitz.open(template_path)
        page1 = doc[0]

        # 1. Page 1 Layout Mapping
        insertions = [
            {"text": data.client_name, "x": 120, "y": 190},
            {"text": data.address, "x": 120, "y": 210},
            {"text": data.post_code, "x": 120, "y": 256},
            {"text": data.company_reg, "x": 120, "y": 272},
            {"text": data.vat_number, "x": 120, "y": 286},
            {"text": data.fd_title, "x": 120, "y": 336},
            {"text": data.fd_name, "x": 120, "y": 375},
            {"text": data.client_contact, "x": 419, "y": 190},
            {"text": data.email_address, "x": 419, "y": 211},
            {"text": data.telephone, "x": 419, "y": 241},
            {"text": data.position, "x": 419, "y": 255},
            {"text": data.date, "x": 419, "y": 287},
            {"text": data.tel, "x": 419, "y": 342},
            {"text": data.email, "x": 419, "y": 375},
            {"text": data.role_to_hire, "x": 60, "y": 480},
            {"text": data.office_cost, "x": 330, "y": 480},
            {"text": data.tech_cost, "x": 396, "y": 480},
            {"text": data.client_name_bottom, "x": 80, "y": 703},
            {"text": data.client_position_bottom, "x": 80, "y": 730},
            {"text": data.client_date_bottom, "x": 80, "y": 755},
            {"text": data.potentiam_person, "x": 344, "y": 703},
            {"text": data.potentiam_position, "x": 344, "y": 730},
            {"text": data.potentiam_date, "x": 344, "y": 755},
        ]
        
        # Write to Page 1
        for item in insertions:
            page1.insert_text(fitz.Point(item['x'], item['y']), str(item['text']), fontsize=8, fontname="helv", color=(0, 0, 0))

        # 2. Page 2 Handling
        if len(data.table_data) > 0:
            if len(doc) < 2:
                page2 = doc.new_page(width=595, height=842)
            else:
                page2 = doc[1]

            # Convert Pydantic objects back to dicts for your table function
            table_dicts = [row.model_dump() for row in data.table_data]
            
            # Draw table
            draw_table_on_page2(page2, table_dicts, start_x=41, start_y=430)
            
            # Add top 'India' text
            page2.insert_text(fitz.Point(546, 208), "India", fontsize=10, fontname="helv", color=(0, 0, 0))

        # Save & Return PDF
        pdf_bytes = doc.write()
        doc.close()
        
        # Dynamic filename based on user inputs
        safe_name = data.client_name.replace(" ", "_")
        filename = f"merged_{safe_name}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        return {"error": f"Error aagaya: {str(e)}"}
