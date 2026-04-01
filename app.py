from flask import Flask, request, jsonify, send_file
import fitz  # PyMuPDF library
import io
import os
import tempfile
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


def draw_table_on_page2(page, table_data, start_x=41, start_y=430):
    """
    Page 2 par clean and simple table
    table_data format: [{"role": "...", "exp": "...", "min": "...", "mid": "...", "max": "..."}]
    """
    if not table_data:
        return

    # Simple fixed column widths for clean look
    col_widths = [135, 95, 75, 75, 75]  # Role, Exp, Min, Mid, Max
    row_height = 20  # Clean row height
    current_y = start_y

    # Complete table border first
    total_width = sum(col_widths)
    total_rows = 2 + len(table_data)  # Header + subheader + data rows
    total_height = row_height * total_rows

    # Outer border
    table_rect = fitz.Rect(start_x, current_y, start_x + total_width, current_y + total_height)
    page.draw_rect(table_rect, color=(0, 0, 0), width=1)

    # Header row backgrounds
    # Role cell - dark blue
    role_rect = fitz.Rect(start_x, current_y, start_x + col_widths[0], current_y + row_height)
    page.draw_rect(role_rect, color=(0, 0, 0), fill=(0.13, 0.27, 0.58))

    # Exp cell - dark blue
    exp_rect = fitz.Rect(start_x + col_widths[0], current_y, start_x + col_widths[0] + col_widths[1], current_y + row_height)
    page.draw_rect(exp_rect, color=(0, 0, 0), fill=(0.13, 0.27, 0.58))

    # INDIA merged cell - yellow background (spans Min+Mid+Max)
    india_rect = fitz.Rect(start_x + col_widths[0] + col_widths[1], current_y, start_x + total_width, current_y + row_height)
    page.draw_rect(india_rect, color=(0, 0, 0), fill=(1, 0.84, 0.13))

    # Header text
    page.insert_text(fitz.Point(start_x + 8, current_y + 13), "Role", fontsize=10, fontname="helv", color=(1, 1, 1))
    page.insert_text(fitz.Point(start_x + col_widths[0] + 8, current_y + 13), "Exp", fontsize=10, fontname="helv", color=(1, 1, 1))

    # INDIA text perfectly centered in merged cell
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

    # Sub-header for INDIA section - yellow background
    subheader_rect = fitz.Rect(start_x + col_widths[0] + col_widths[1], current_y, start_x + total_width, current_y + row_height)
    page.draw_rect(subheader_rect, color=(0, 0, 0), fill=(1, 0.84, 0.13))

    # Sub-header text (Min, Mid, Max)
    page.insert_text(fitz.Point(start_x + col_widths[0] + col_widths[1] + 8, current_y + 13), "Min", fontsize=9, fontname="helv", color=(0, 0, 0))
    page.insert_text(fitz.Point(start_x + col_widths[0] + col_widths[1] + col_widths[2] + 8, current_y + 13), "Mid", fontsize=9, fontname="helv", color=(0, 0, 0))
    page.insert_text(fitz.Point(start_x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + 8, current_y + 13), "Max", fontsize=9, fontname="helv", color=(0, 0, 0))

    current_y += row_height

    # Simple data rows - clean and straightforward
    for i, row_data in enumerate(table_data):
        if not row_data:
            continue

        # Row background - light gray
        row_rect = fitz.Rect(start_x, current_y, start_x + total_width, current_y + row_height)
        page.draw_rect(row_rect, color=(0, 0, 0), fill=(0.92, 0.92, 0.92))

        # Simple data cells with clean positioning
        page.insert_text(fitz.Point(start_x + 8, current_y + 13),
                        str(row_data.get("role", ""))[:18], fontsize=9, fontname="helv", color=(0, 0, 0))
        page.insert_text(fitz.Point(start_x + col_widths[0] + 8, current_y + 13),
                        str(row_data.get("exp", "")), fontsize=9, fontname="helv", color=(0, 0, 0))
        page.insert_text(fitz.Point(start_x + col_widths[0] + col_widths[1] + 8, current_y + 13),
                        str(row_data.get("min", "")), fontsize=9, fontname="helv", color=(0, 0, 0))
        page.insert_text(fitz.Point(start_x + col_widths[0] + col_widths[1] + col_widths[2] + 8, current_y + 13),
                        str(row_data.get("mid", "")), fontsize=9, fontname="helv", color=(0, 0, 0))
        page.insert_text(fitz.Point(start_x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + 8, current_y + 13),
                        str(row_data.get("max", "")), fontsize=9, fontname="helv", color=(0, 0, 0))

        current_y += row_height

    # Draw grid lines properly for merged header
    # Vertical lines
    x_pos = start_x + col_widths[0]
    page.draw_line(fitz.Point(x_pos, start_y), fitz.Point(x_pos, start_y + total_height), color=(0, 0, 0), width=1)

    x_pos = start_x + col_widths[0] + col_widths[1]
    page.draw_line(fitz.Point(x_pos, start_y), fitz.Point(x_pos, start_y + total_height), color=(0, 0, 0), width=1)

    # Lines within INDIA section (only from sub-header row onwards)
    sub_header_y = start_y + row_height
    x_pos = start_x + col_widths[0] + col_widths[1] + col_widths[2]
    page.draw_line(fitz.Point(x_pos, sub_header_y), fitz.Point(x_pos, start_y + total_height), color=(0, 0, 0), width=1)

    x_pos = start_x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3]
    page.draw_line(fitz.Point(x_pos, sub_header_y), fitz.Point(x_pos, start_y + total_height), color=(0, 0, 0), width=1)

    # Horizontal lines for all rows
    for i in range(total_rows + 1):
        y_pos = start_y + (i * row_height)
        page.draw_line(fitz.Point(start_x, y_pos), fitz.Point(start_x + total_width, y_pos), color=(0, 0, 0), width=1)


def generate_custom_pdf(template_file, page1_data, page2_data=None):
    """
    Generate custom PDF with page 1 and page 2 data
    """
    try:
        # Check if template file exists
        if not os.path.exists(template_file):
            raise FileNotFoundError(f"Template file {template_file} not found")

        # Open template PDF
        doc = fitz.open(template_file)

        # Page 1 - Fill user data
        if len(doc) > 0:
            page1 = doc[0]

            # Fill page 1 data
            for item in page1_data:
                text = str(item['text'])
                x = item['x']
                y = item['y']

                page1.insert_text(
                    fitz.Point(x, y),
                    text,
                    fontsize=8,
                    fontname="helv",
                    color=(0, 0, 0)
                )

        # Page 2 - Add table and India text
        if len(doc) < 2:
            page2 = doc.new_page(width=595, height=842)
        else:
            page2 = doc[1]

        # Add table if data provided
        if page2_data and page2_data.get('table_data'):
            draw_table_on_page2(page2, page2_data['table_data'], start_x=41, start_y=430)

        # Add top India text
        page2.insert_text(
            fitz.Point(546, 208),
            "India",
            fontsize=10,
            fontname="helv",
            color=(0, 0, 0)
        )

        # Save PDF to bytes
        pdf_bytes = doc.tobytes()
        doc.close()

        return pdf_bytes

    except Exception as e:
        raise Exception(f"PDF generation failed: {str(e)}")


@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf_api():
    """
    API endpoint to generate PDF
    """
    try:
        data = request.json

        # Validate input
        if not data:
            return jsonify({"error": "No data provided"}), 400

        if "page1_data" not in data:
            return jsonify({"error": "page1_data is required"}), 400

        page1_data = data['page1_data']
        page2_data = data.get('page2_data', None)

        # Template file path
        template_file = "static/merged_final.pdf"

        # Generate PDF
        pdf_bytes = generate_custom_pdf(template_file, page1_data, page2_data)

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name

        # Return PDF file
        return send_file(
            tmp_file_path,
            as_attachment=True,
            download_name='custom_document.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({"status": "healthy", "message": "PDF Generator API is running"})


@app.route('/api/test', methods=['POST'])
def test_api():
    """
    Test endpoint with sample data
    """
    try:
        # Sample data structure
        sample_data = {
            "page1_data": [
                {"text": "Test Client", "x": 120, "y": 190},
                {"text": "Test Address", "x": 120, "y": 210},
                {"text": "Test@email.com", "x": 419, "y": 211},
            ],
            "page2_data": {
                "table_data": [
                    {
                        "role": "Test Role",
                        "exp": "2-3 yrs",
                        "min": "£25,000",
                        "mid": "£30,000",
                        "max": "£35,000"
                    }
                ]
            }
        }

        template_file = "static/merged_final.pdf"
        pdf_bytes = generate_custom_pdf(template_file, sample_data['page1_data'], sample_data['page2_data'])

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name

        return send_file(
            tmp_file_path,
            as_attachment=True,
            download_name='test_document.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Root route for Vercel
@app.route('/')
def index():
    """
    Root endpoint
    """
    return jsonify({
        "message": "PDF Generator API is running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "generate": "/api/generate-pdf",
            "test": "/api/test"
        }
    })

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)