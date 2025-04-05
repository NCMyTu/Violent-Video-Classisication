# Violent Video Classification
This project classifies CCTV videos as violent or non-violent and can detect violent behaviors in real-time CCTV footage. 

## To train models: 
Run 2 `.ipynb` files in `src` directory.

## To run the web app:
Place `model.keras` in `web/static`directory.
### Without docker:
1. Install dependencies:  
  ```pip install -r requirements.txt```  
2. Start the server:  
```python web/server.py```
3. Now open `http://127.0.0.1:8091` or `http://localhost:8091`.

### With docker:
1. Update these paths in ```web/server.py```:
   ```
   UPLOAD_FOLDER = "/app/web/static/uploads"
   model_path = r"/app/web/static/cnn_lstm.keras"
   ```
2. Build and run the container:
   ```
   docker-compose up --build
   ```
3. Now open `http://127.0.0.1:8091` or `http://localhost:8091`.

Note that the CCTV Monitoring feature requires an `http` URL (not `https`).
