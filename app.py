"""
Flask Web Dashboard for Company Profiling Bots
"""
from flask import (
    Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, flash
)
import urllib.parse
import os
import json
from datetime import datetime
from bots.crawler import crawl_company_website
from bots.aggregator import aggregate_company_info
from utils.storage import list_data_files, load_json, DATA_DIR
from config import FLASK_CONFIG

app = Flask(__name__)


@app.route('/')
def index():
    """Main dashboard page"""
    # List existing data files
    data_files = list_data_files()

    return render_template('index.html', data_files=data_files)


@app.route('/crawl', methods=['POST'])
def crawl():
    """Endpoint to trigger website crawling"""
    try:
        data = request.get_json()
        url = data.get('url')
        max_pages = data.get('max_pages', 20)

        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Run crawler
        result = crawl_company_website(url, max_pages)

        return jsonify({
            'success': True,
            'message': f'Successfully crawled {len(result["pages"])} pages',
            'data': result
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/aggregate', methods=['POST'])
def aggregate():
    """Endpoint to trigger company info aggregation"""
    try:
        data = request.get_json()
        company_name = data.get('company_name')
        urls = data.get('urls', [])

        if not company_name:
            return jsonify({'error': 'Company name is required'}), 400

        # Run aggregator
        result = aggregate_company_info(company_name, urls if urls else None)

        return jsonify({
            'success': True,
            'message': f'Successfully aggregated data from {len(result["sources"])} sources',
            'data': result
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/data/<filename>')
def get_data(filename):
    """Retrieve saved data file"""
    try:
        data = load_json(filename)
        if data is None:
            return jsonify({'error': 'File not found'}), 404

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/data/<path:filename>', methods=['POST'])
def delete_data(filename):
    """Delete saved data file safely without using sessions"""
    # Decode URL-encoded filename
    filename = urllib.parse.unquote(filename)
    filepath = os.path.join("data", filename)

    if not os.path.exists(filepath):
        # Simply return JSON instead of flash
        return jsonify({'success': False, 'error': 'File not found'}), 404

    try:
        os.remove(filepath)
        return jsonify({'success': True, 'message': f'Deleted {filename}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/data/list')
def list_data():
    """List all saved data files"""
    try:
        files = list_data_files()

        file_info = []
        for filename in files:
            filepath = os.path.join(DATA_DIR, filename)
            stat = os.stat(filepath)

            file_info.append({
                'filename': filename,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

        return jsonify({'files': file_info})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/results')
def results():
    """Results page showing all extracted data"""
    filename = request.args.get('file')

    if not filename:
        return "No file specified", 400

    data = load_json(filename)

    if data is None:
        return "File not found", 404

    return render_template('results.html', data=data, filename=filename)


if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # Run Flask app
    print(f"\n{'='*60}")
    print("🚀 Company Profiling Bots Dashboard")
    print(f"{'='*60}")
    print(f"📍 Running on: http://{FLASK_CONFIG['host']}:{FLASK_CONFIG['port']}")
    print(f"📁 Data directory: {DATA_DIR}")
    print(f"{'='*60}\n")

    app.run(
        host=FLASK_CONFIG['host'],
        port=FLASK_CONFIG['port'],
        debug=FLASK_CONFIG['debug']
    )
