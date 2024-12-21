# Heatmap and Mask Image Processing Web Application  

This project is a Flask-based web application designed as part of a larger initiative for developing a robot that collects microplastics on beaches. The tool processes images to detect **microplastics (in pellet form)** and **obstacles (e.g., plastic palm trees)**, generating a heatmap and a matrix representation. This information guides the robot to prioritize areas for collection.  

---

## 🏆 Award-Winning Project  

This project was awarded the **Sustainability Prize** at the **URV Robotics Hackathon 2024**. Recognized for its innovative approach to environmental cleanup, the project showcases the potential of robotics and computer vision to address global challenges such as pollution on beaches.  

---

## Project Context  

The application supports a robotic system aimed at cleaning beaches by collecting microplastics efficiently. It provides:  

- A **heatmap matrix** that the robot can interpret to prioritize regions with high pellet density.  
- Visual detection of **obstacles** (like plastic palm trees) to help the robot avoid them during navigation.  
- Integration with the robot’s control logic by generating actionable data in the form of a grid.  

By enabling the detection of microplastics and obstacles, this tool contributes to the broader goal of **reducing environmental pollution on beaches**.  

---  

## Features  

- **Image Upload**: Users can upload `.png`, `.jpg`, `.jpeg`, or `.bmp` images.  
- **Mask Generation**:  
  - **White objects (pellets)**: Highlighted in white.  
  - **Green objects (obstacles)**: Highlighted in green.  
  - All other areas are set to black.  
- **Heatmap Creation**:  
  - Generates a heatmap showing the density of white pellets.  
  - Heatmap values are normalized to a range of 0–10.  
  - Obstacles (green objects) are excluded from heatmap calculations.  
- **Superimposed Visualization**: Combines the heatmap with the original image for better context.  
- **Matrix Representation**: Produces a grid-based matrix of the heatmap, interpretable by the robot’s algorithms for collection prioritization.  
- **Customizable Grid**: Users can adjust the grid's rows and columns for heatmap and matrix generation.  

---  

## Installation and Setup  

1. **Install Python dependencies**:  
   Run the following command to install the required libraries:  
   ```bash  
   pip install flask opencv-python numpy  
   ```  

2. **Directory Setup**:  
   Ensure the following folder structure exists in the project root:  
   ```  
   ├── static  
   │   ├── img  
   │   │   ├── uploads  
   │   │   └── processed  
   └── app.py  
   ```  
   The application will automatically create missing directories.  

3. **Run the Application**:  
   Start the Flask server with:  
   ```bash  
   python app.py  
   ```  
   The application will be available at `http://127.0.0.1:5000`.  

---  

## Usage  

1. Open the web application in your browser.  
2. Upload an image containing pellets (white) and obstacles (green).  
3. Set the desired number of rows and columns for the grid.  
4. Click "Submit" to process the image.  
5. The application will display:  
   - The original image.  
   - The mask highlighting white and green objects.  
   - The heatmap visualizing the density of pellets.  
   - A superimposed image of the heatmap on the original.  
   - The **matrix** representing the heatmap data for robotic processing.  

---  

## Output Details  

- **Mask**:  
  - Pellets are shown in white.  
  - Obstacles (e.g., plastic palm trees) are shown in green.  
  - All other areas are black.  
- **Heatmap**:  
  - Regions with higher pellet density are shown with warm colors (red/yellow).  
  - Obstacles are excluded from the heatmap.  
- **Superimposed Image**:  
  - Heatmap overlaid on the original image for context.  
- **Matrix**:  
  - A numerical representation of the heatmap, normalized between 0 and 10.  

---  

## Project Structure  

- `app.py`: Main Flask application.  
- `static/img/uploads/`: Stores uploaded images.  
- `static/img/processed/`: Stores generated mask, heatmap, and superimposed images.  
- `templates/index.html`: Web interface for uploading and displaying results.  

---  

## Dependencies  

This project uses the following Python libraries:  

- **Flask**: For web application framework.  
- **OpenCV (cv2)**: For image processing.  
- **NumPy**: For numerical computations.  

Install all dependencies using:  
```bash  
pip install flask opencv-python numpy  
```  

---  

## Customization  

### Adjusting Color Ranges  

- **White Object Detection**:  
  Modify the `bajo_blanco` and `alto_blanco` ranges in `procesar_imagen` to detect specific shades of white.  

- **Green Object Detection**:  
  Modify the `bajo_verde` and `alto_verde` ranges to detect green objects like plastic palm trees.  

### Transparency Levels  

Adjust the transparency of the superimposed heatmap by modifying the `alpha` parameter in:  
```python  
imagen_superpuesta = cv2.addWeighted(heatmap_color, alpha, imagen, 1 - alpha, 0)  
```  

---  


## License  

This project is released under the [MIT License](LICENSE).  
