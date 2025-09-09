<template>
  <div class="history">
    <div class="container">
      <h2>Detection History</h2>
      <p>View past parking lot analyses</p>

      <div v-if="loading" class="loading">
        <p>🔄 Loading history...</p>
      </div>

      <div v-else-if="history.length === 0" class="no-data">
        <p>📝 No detection history available</p>
      </div>

      <div v-else class="history-grid">
        <div 
          v-for="(record, index) in history" 
          :key="index" 
          class="history-card"
        >
          <div class="card-header">
            <div class="timestamp">
              📅 {{ formatDate(record.timestamp) }}
            </div>
          </div>

          <div class="card-content">
            <div class="stats-row">
              <div class="stat">
                <span class="stat-label">Free:</span>
                <span class="stat-value free">{{ record.free_slots }}</span>
              </div>
              <div class="stat">
                <span class="stat-label">Occupied:</span>
                <span class="stat-value occupied">{{ record.occupied_slots }}</span>
              </div>
              <div class="stat">
                <span class="stat-label">Total:</span>
                <span class="stat-value">{{ record.total_slots }}</span>
              </div>
            </div>

            <div class="confidence-bar">
              <div class="confidence-label">
                Confidence: {{ (record.confidence * 100).toFixed(1) }}%
              </div>
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: (record.confidence * 100) + '%' }"
                ></div>
              </div>
            </div>

            <div v-if="record.has_image" class="result-placeholder">
              <div class="placeholder-icon">🖼️</div>
              <p>Image processed ({{ record.detections_count || 0 }} detections)</p>
              <small>Images not stored - use live detection for visual results</small>
            </div>
          </div>
        </div>
      </div>

      <div v-if="hasMore" class="load-more">
        <button @click="loadMore" :disabled="loadingMore" class="load-more-btn">
          {{ loadingMore ? '🔄 Loading...' : '⬇️ Load More' }}
        </button>
      </div>
    </div>

    <!-- Modal for enlarged image -->
    <div v-if="selectedRecord" class="modal" @click="closeModal">
      <div class="modal-content" @click.stop>
        <button class="modal-close" @click="closeModal">✕</button>
        <img :src="selectedRecord.image_url" alt="Detection result">
        <div class="modal-info">
          <h3>Detection Details</h3>
          <p>Date: {{ formatDate(selectedRecord.timestamp) }}</p>
          <p>Vehicles detected: {{ selectedRecord.detections?.length || 0 }}</p>
          <p>Free slots: {{ selectedRecord.free_slots }}/{{ selectedRecord.total_slots }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'History',
  data() {
    return {
      history: [],
      loading: true,
      loadingMore: false,
      hasMore: true,
      selectedRecord: null,
      limit: 10
    }
  },
  async mounted() {
    await this.loadHistory()
  },
  methods: {
    async loadHistory() {
      try {
        const response = await axios.get(`/api/history?limit=${this.limit}`)
        this.history = response.data.results || []
        this.hasMore = this.history.length >= this.limit
      } catch (error) {
        console.error('Error loading history:', error)
        this.history = []
      } finally {
        this.loading = false
      }
    },

    async loadMore() {
      if (this.loadingMore) return

      this.loadingMore = true
      try {
        const response = await axios.get(`/api/history?limit=${this.limit + 10}`)
        const newResults = response.data.results || []

        if (newResults.length > this.history.length) {
          this.history = newResults
          this.limit += 10
        } else {
          this.hasMore = false
        }
      } catch (error) {
        console.error('Error loading more history:', error)
      } finally {
        this.loadingMore = false
      }
    },

    formatDate(timestamp) {
      return new Date(timestamp).toLocaleString()
    },

    openModal(record) {
      this.selectedRecord = record
    },

    closeModal() {
      this.selectedRecord = null
    }
  }
}
</script>

<style scoped>
.history {
  max-width: 1200px;
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

h2 {
  color: white;
  text-align: center;
  margin-bottom: 0.5rem;
  font-size: 2rem;
}

p {
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  margin-bottom: 2rem;
}

.loading, .no-data {
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  padding: 3rem;
  font-size: 1.1rem;
}

.history-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.history-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
  transition: transform 0.3s ease;
}

.history-card:hover {
  transform: translateY(-5px);
}

.card-header {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.timestamp {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.card-content {
  padding: 1rem;
}

.stats-row {
  display: flex;
  justify-content: space-around;
  margin-bottom: 1rem;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
}

.stat-value {
  color: white;
  font-weight: bold;
  font-size: 1.2rem;
}

.stat-value.free {
  color: #2ecc71;
}

.stat-value.occupied {
  color: #e74c3c;
}

.confidence-bar {
  margin-bottom: 1rem;
}

.confidence-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.progress-bar {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  height: 8px;
  overflow: hidden;
}

.progress-fill {
  background: linear-gradient(90deg, #667eea, #764ba2);
  height: 100%;
  transition: width 0.3s ease;
}

.result-image img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.result-image img:hover {
  transform: scale(1.02);
}

.load-more {
  text-align: center;
  margin-top: 2rem;
}

.load-more-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 1rem 2rem;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.load-more-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.load-more-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 2rem;
  max-width: 80%;
  max-height: 80%;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.modal-close {
  position: absolute;
  top: 10px;
  right: 15px;
  background: rgba(231, 76, 60, 0.8);
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  font-size: 1rem;
}

.modal-content img {
  max-width: 100%;
  max-height: 60vh;
  border-radius: 10px;
}

.modal-info {
  color: white;
  margin-top: 1rem;
}

.modal-info h3 {
  margin-bottom: 1rem;
}

.modal-info p {
  margin-bottom: 0.5rem;
  text-align: left;
}
</style>
