import numpy as np
import scipy.io
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from flask import Flask, request, render_template
from mpl_toolkits.basemap import Basemap
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Load data
#mat = scipy.io.loadmat('data_input_VERmat_7harilalu.mat')
#data_matrix = mat['data7harilalu']

import os
import scipy.io

# Menemukan file .mat terbaru di direktori saat ini
directory = '.'  # Ganti dengan path direktori jika diperlukan
files = [f for f in os.listdir(directory) if f.endswith('.mat')]
latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(directory, x)))

# Load data dari file .mat terbaru
mat = scipy.io.loadmat(latest_file)
data_matrix = mat['data7harikedepan']

print(f"Data di-load dari file: {latest_file}")



app = Flask(__name__)

@app.route('/')
def index():
    # Generate the initial map of Indonesia
    fig, ax = plt.subplots(figsize=(10, 8))
    m = Basemap(projection='merc', llcrnrlat=-10, urcrnrlat=0, llcrnrlon=105, urcrnrlon=115, resolution='i', ax=ax)
    m.drawcoastlines()
    m.drawcountries()
    m.drawparallels(np.arange(-10, 0, 1), labels=[1, 0, 0, 0])
    m.drawmeridians(np.arange(105, 115, 1), labels=[0, 0, 0, 1])
    m.drawmapboundary(fill_color='lightblue')
    m.fillcontinents(color='lightgreen', lake_color='lightblue')
    plt.title('History HotSpot Penangkapan Ikan - "Silahkan Pilih Tanggal"')
    
    # Save the initial map to a PNG image in memory
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    map_url = base64.b64encode(buf.getvalue()).decode('utf8')
    
    return render_template('index6_3harikedepan.html', map_url=map_url)

@app.route('/process', methods=['POST'])
def process():
    try:
        # Get the selected day from the form
        day = int(request.form['day'])
        if day < 1 or day > 4:
            return "Tanggal tidak valid", 400
        
        # Extract data for the selected day
        data = data_matrix[:, :, day - 1]
        lon = data[:, 0]
        lat = data[:, 1]
        kelas = data[:, 5]
        
        # Filter data where kelas == 2
        filter_mask = (kelas == 2)
        lon_filtered = lon[filter_mask]
        lat_filtered = lat[filter_mask]
        
        # Plot data
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create basemap instance
        m = Basemap(projection='merc', llcrnrlat=-10, urcrnrlat=0, llcrnrlon=105, urcrnrlon=115, resolution='i', ax=ax)
        m.drawcoastlines()
        m.drawcountries()
        m.drawparallels(np.arange(-10, 0, 1), labels=[1, 0, 0, 0])
        m.drawmeridians(np.arange(105, 115, 1), labels=[0, 0, 0, 1])
        m.drawmapboundary(fill_color='lightblue')
        m.fillcontinents(color='lightgreen', lake_color='lightblue')
        
        # Load image
        img = plt.imread('ikan.png')
        imagebox = OffsetImage(img, zoom=0.05)
        
        for x, y in zip(lon_filtered, lat_filtered):
            x, y = m(x, y)
            ab = AnnotationBbox(imagebox, (x, y), frameon=False)
            ax.add_artist(ab)
        
        # Set title based on selected day
        from datetime import datetime, timedelta
        base_date = datetime.now() + timedelta(days=0)  # 0 hari ke depan hari ini
        selected_date = base_date + timedelta(days=(day - 1))
        plt.title(f'HotSpot Penangkapan Ikan per- {selected_date.strftime("%d %B %Y")}')
        
        # Save the plot to a PNG image in memory
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plot_url = base64.b64encode(buf.getvalue()).decode('utf8')
        
        return render_template('index6_3harikedepan.html', plot_url=plot_url, map_url=None)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
