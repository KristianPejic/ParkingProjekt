<template>
  <div class="stats">
    <div class="container">
      <h2>Parking Statistics</h2>
      <p>Overview of parking lot usage and system performance</p>

      <div v-if="loading" class="loading">
        <p>🔄 Loading statistics...</p>
      </div>

      <div v-else-if="!stats" class="no-data">
        <p>📊 No statistics available</p>
      </div>

      <div v-else class="stats-content">
        <div class="main-stats">
          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.total_analyses }}</div>
              <div class="stat-label">Total Analyses</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">🚗</div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.average_occupancy }}</div>
              <div class="stat-label">Avg Occupied Slots</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">🅿️</div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.average_free_slots }}</div>
              <div class="stat-label">Avg Free Slots</div>
            </div>
          </div>
        </div>

        <div v-if="stats.latest_result" class="latest-result">
          <h3>Latest Detection</h3>
          <div class="latest-card">
            <div class="latest-header">
              <span class="timestamp">{{ formatDate(stats.latest_result.timestamp) }}</span>
            </div>

            <div class="latest-stats">
              <div class="occupancy-indicator">
                <div class="occupancy-bar">
                  <div 
                    class="occupancy-fill" 
                    :style="{ 
                      width: (stats.latest_result.occupied_slots / stats.latest_result.total_slots * 100) + '%' 
                    }"
                  ></div>
                </div>
                <div class="occupancy-text">
                  {{ stats.latest_result.occupied_slots }}/{{ stats.latest_result.total_slots }} 
                  ({{ Math.round(stats.latest_result.occupied_slots / stats.latest_result.total_slots * 100) }}% occupied)
                </div>
              </div>

              <div class="latest-numbers">
                <div class="number-item free">
                  <div class="number">{{ stats.latest_result.free_slots }}</div>
                  <div class="label">Free</div>
                </div>
                <div class="number-item occupied">
                  <div class="number">{{ stats.latest_result.occupied_slots }}</div>
                  <div class="label">Occupied</div>
                </div>
                <div class="number-item confidence">
                  <div class="number">{{ (stats.latest_result.confidence * 100).toFixed(1) }}%</div>
                  <div class="label">Confidence</div>
                </div>
              </div>
            </div>

            <div v-if="stats.latest_result.has_image" class="latest-placeholder">
              <div class="placeholder-content">
                <div class="placeholder-icon">📊</div>
                <p>Latest detection completed</p>
                <small>Use live detection to see annotated images</small>
              </div>
            </div>
          </div>
        </div>

        <div class="insights">
          <h3>Insights</h3>
          <div class="insights-grid">
            <div class="insight-card">
              <div class="insight-icon">📈</div>
              <div class="insight-content">
                <h4>Usage Trend</h4>
                <p v-if="stats.average_occupancy > stats.average_free_slots">
                  High occupancy detected. Average {{ stats.average_occupancy }} out of 
                  {{ Math.round(stats.average_occupancy + stats.average_free_slots) }} slots occupied.
                </p>
                <p v-else>
                  Good availability. Average {{ stats.average_free_slots }} free slots available.
                </p>
              </div>
            </div>

            <div class="insight-card">
              <div class="insight-icon">🎯</div>
              <div class="insight-content">
                <h4>Detection Quality</h4>
                <p v-if="stats.latest_result && stats.latest_result.confidence > 0.7">
                  High confidence detection ({{ (stats.latest_result.confidence * 100).toFixed(1) }}%)
                </p>
                <p v-else-if="stats.latest_result">
                  Moderate confidence detection ({{ (stats.latest_result.confidence * 100).toFixed(1) }}%)
                </p>
                <p v-else>
                  No recent detection data available
                </p>
              </div>
            </div>

            <div class="insight-card">
              <div class="insight-icon">⚡</div>
              <div class="insight-content">
                <h4>System Activity</h4>
                <p>
                  {{ stats.total_analyses }} total analyses performed. 
                  System is {{ stats.total_analyses > 10 ? 'actively' : 'occasionally' }} used.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div class="refresh-section">
          <button @click="loadStats" :disabled="loading" class="refresh-btn">
            <span v-if="loading">🔄 Refreshing...</span>
            <span v-else>🔄 Refresh Statistics</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Stats',
  data() {
    return {
      stats: null,
      loading: true,
      showImage: false
    }
  },
  async mounted() {
    await this.loadStats()
  },
  methods: {
    async loadStats() {
      this.loading = true
      try {
        const response = await axios.get('/api/stats')
        this.stats = response.data
      } catch (error) {
        console.error('Error loading stats:', error)
        this.stats = null
      } finally {
        this.loading = false
      }
    },

    formatDate(timestamp) {
      return new Date(timestamp).toLocaleString()
    }
  }
}
</script>

<style scoped>
.stats {
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

h2 {
  color: white;
  text-align: center;
  margin-bottom: 0.5rem;
  font-size: 2rem;
}

.container > p {
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

.main-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: white;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.latest-result {
  margin-bottom: 3rem;
}

.latest-result h3 {
  color: white;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.latest-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
}

.latest-header {
  background: rgba(255, 255, 255, 0.05);
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.timestamp {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.latest-stats {
  padding: 1.5rem;
}

.occupancy-indicator {
  margin-bottom: 1.5rem;
}

.occupancy-bar {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  height: 20px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.occupancy-fill {
  background: linear-gradient(90deg, #2ecc71, #e74c3c);
  height: 100%;
  transition: width 0.5s ease;
}

.occupancy-text {
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  font-size: 0.9rem;
}

.latest-numbers {
  display: flex;
  justify-content: space-around;
}

.number-item {
  text-align: center;
}

.number-item .number {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.number-item .label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
}

.number-item.free .number {
  color: #2ecc71;
}

.number-item.occupied .number {
  color: #e74c3c;
}

.number-item.confidence .number {
  color: #9b59b6;
}

.latest-image {
  padding: 1rem;
}

.latest-image img {
  width: 100%;
  max-height: 300px;
  object-fit: cover;
  border-radius: 10px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.latest-image img:hover {
  transform: scale(1.02);
}

.insights h3 {
  color: white;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.insight-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.insight-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.insight-content h4 {
  color: white;
  margin-bottom: 0.5rem;
}

.insight-content p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  line-height: 1.4;
  margin: 0;
}

.refresh-section {
  text-align: center;
}

.refresh-btn {
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

.refresh-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
