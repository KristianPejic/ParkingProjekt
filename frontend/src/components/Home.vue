<template>
  <div class="home">
    <div class="container">
      <div class="upload-section">
        <h2>🚗 Upload Parking Lot Image</h2>
        <p>Upload an image to detect vehicles and count free parking spaces</p>

        <div class="upload-area" @drop="handleDrop" @dragover.prevent @dragenter.prevent>
          <input 
            type="file" 
            ref="fileInput" 
            @change="handleFileSelect" 
            accept="image/*" 
            style="display: none"
          >

          <div v-if="!selectedFile" class="upload-placeholder" @click="$refs.fileInput.click()">
            <div class="upload-icon">📁</div>
            <p>Click to select or drag and drop an image</p>
            <p class="upload-hint">Supports JPG, PNG, WEBP formats</p>
          </div>

          <div v-else class="file-preview">
            <img :src="imagePreview" alt="Selected image" class="preview-image">
            <button @click="clearFile" class="clear-btn">✕</button>
          </div>
        </div>

        <div class="controls">
          <div class="slots-input">
            <label>Total Parking Slots:</label>
            <input v-model="totalSlots" type="number" min="1" max="100">
          </div>

          <button 
            @click="analyzeImage" 
            :disabled="!selectedFile || loading" 
            class="analyze-btn"
          >
            <span v-if="loading">🔄 Analyzing...</span>
            <span v-else>🔍 Analyze Parking</span>
          </button>
        </div>
      </div>

      <div v-if="result" class="results-section">
        <h3>Detection Results</h3>

        <div class="stats-grid">
          <div class="stat-card free">
            <div class="stat-number">{{ result.free_slots }}</div>
            <div class="stat-label">Free Slots</div>
          </div>

          <div class="stat-card occupied">
            <div class="stat-number">{{ result.occupied_slots }}</div>
            <div class="stat-label">Occupied Slots</div>
          </div>

          <div class="stat-card total">
            <div class="stat-number">{{ result.total_slots }}</div>
            <div class="stat-label">Total Slots</div>
          </div>

          <div class="stat-card confidence">
            <div class="stat-number">{{ (result.confidence * 100).toFixed(1) }}%</div>
            <div class="stat-label">Confidence</div>
          </div>
        </div>

        <div v-if="result.image_base64" class="result-image">
          <h4>Detected Vehicles</h4>
          <img :src="result.image_base64" alt="Detection result" class="detection-image">
          <p class="detection-count">{{ result.detections.length }} vehicles detected</p>
        </div>
      </div>

      <div v-if="error" class="error-message">
        <p>❌ {{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Home',
  data() {
    return {
      selectedFile: null,
      imagePreview: null,
      totalSlots: 20,
      loading: false,
      result: null,
      error: null
    }
  },
  methods: {
    handleFileSelect(event) {
      const file = event.target.files[0]
      this.setSelectedFile(file)
    },

    handleDrop(event) {
      event.preventDefault()
      const file = event.dataTransfer.files[0]
      if (file && file.type.startsWith('image/')) {
        this.setSelectedFile(file)
      }
    },

    setSelectedFile(file) {
      this.selectedFile = file
      this.result = null
      this.error = null

      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => {
        this.imagePreview = e.target.result
      }
      reader.readAsDataURL(file)
    },

    clearFile() {
      this.selectedFile = null
      this.imagePreview = null
      this.result = null
      this.error = null
    },

    async analyzeImage() {
      if (!this.selectedFile) return

      this.loading = true
      this.error = null

      try {
        const formData = new FormData()
        formData.append('file', this.selectedFile)
        formData.append('total_slots', this.totalSlots.toString())

        const response = await axios.post('/api/detect', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        this.result = response.data

      } catch (err) {
        this.error = err.response?.data?.detail || 'Analysis failed. Please try again.'
        console.error('Analysis error:', err)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.home {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 2rem;
}

.container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.upload-section {
  text-align: center;
  margin-bottom: 2rem;
}

.upload-section h2 {
  color: white;
  margin-bottom: 0.5rem;
  font-size: 2rem;
}

.upload-section p {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 2rem;
}

.upload-area {
  border: 2px dashed rgba(255, 255, 255, 0.3);
  border-radius: 15px;
  padding: 2rem;
  margin-bottom: 2rem;
  transition: all 0.3s ease;
  position: relative;
}

.upload-area:hover {
  border-color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.05);
}

.upload-placeholder {
  cursor: pointer;
  color: rgba(255, 255, 255, 0.8);
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.upload-hint {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 0.5rem;
}

.file-preview {
  position: relative;
  display: inline-block;
}

.preview-image {
  max-width: 300px;
  max-height: 200px;
  border-radius: 10px;
}

.clear-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  background: #ff4757;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  font-size: 1rem;
}

.controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.slots-input {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: white;
}

.slots-input input {
  padding: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  width: 80px;
  text-align: center;
}

.analyze-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 25px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.analyze-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.analyze-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.results-section {
  margin-top: 3rem;
  color: white;
}

.results-section h3 {
  text-align: center;
  margin-bottom: 2rem;
  font-size: 1.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 1.5rem;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-card.free {
  background: rgba(46, 204, 113, 0.2);
  border-color: rgba(46, 204, 113, 0.5);
}

.stat-card.occupied {
  background: rgba(231, 76, 60, 0.2);
  border-color: rgba(231, 76, 60, 0.5);
}

.stat-card.total {
  background: rgba(52, 152, 219, 0.2);
  border-color: rgba(52, 152, 219, 0.5);
}

.stat-card.confidence {
  background: rgba(155, 89, 182, 0.2);
  border-color: rgba(155, 89, 182, 0.5);
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
}

.result-image {
  text-align: center;
}

.result-image h4 {
  margin-bottom: 1rem;
}

.detection-image {
  max-width: 100%;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.detection-count {
  margin-top: 1rem;
  color: rgba(255, 255, 255, 0.8);
}

.error-message {
  background: rgba(231, 76, 60, 0.2);
  border: 1px solid rgba(231, 76, 60, 0.5);
  border-radius: 10px;
  padding: 1rem;
  margin-top: 1rem;
  text-align: center;
  color: white;
}
</style>
