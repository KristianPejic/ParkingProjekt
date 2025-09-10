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

        <!-- New Charts -->
        <div v-if="history.length" class="charts">
          <h3 class="charts-title">Parking Usage Charts</h3>
          <div class="charts-grid">
            <!-- Occupancy Trend Line -->
            <div class="chart-card">
              <h4>Occupancy Trend — % of slots occupied per detection (last {{ trendPoints.length }})</h4>
              <svg :width="chartW" :height="chartH" class="svg-chart">
                <g :transform="`translate(${m.l},${m.t})`">
                  <line :x1="0" :y1="innerH" :x2="innerW" :y2="innerH" class="axis" />
                  <line :x1="0" :y1="0" :x2="0" :y2="innerH" class="axis" />
                  <polyline
                    class="line occ-line"
                    :points="trendPolyline"
                    fill="none"
                  />
                  <circle
                    v-for="(p, i) in trendPoints"
                    :key="`occ-${i}`"
                    :cx="xScale(i, trendPoints.length)"
                    :cy="yScale01(p.occRate)"
                    r="3"
                    class="dot occ-dot"
                  />
                  <text :x="-8" :y="yScale01(1)" class="tick" text-anchor="end" dominant-baseline="middle">100%</text>
                  <text :x="-8" :y="yScale01(0.5)" class="tick" text-anchor="end" dominant-baseline="middle">50%</text>
                  <text :x="-8" :y="yScale01(0)" class="tick" text-anchor="end" dominant-baseline="middle">0%</text>
                </g>
              </svg>
              <div class="axis-label">Most recent on the right</div>
            </div>

            <!-- Stacked Bars: Free vs Occupied -->
            <div class="chart-card">
              <h4>Slots per Detection — Free vs Occupied (counts)</h4>
              <svg :width="chartW" :height="chartH" class="svg-chart">
                <g :transform="`translate(${m.l},${m.t})`">
                  <line :x1="0" :y1="innerH" :x2="innerW" :y2="innerH" class="axis" />
                  <template v-for="(p, i) in barPoints" :key="`bar-${i}`">
                    <rect
                      :x="xBand(i, barPoints.length) + 1"
                      :y="yScaleSlots(p.occupied)"
                      :width="bandW - 2"
                      :height="innerH - yScaleSlots(p.occupied)"
                      class="bar occupied"
                    />
                    <rect
                      :x="xBand(i, barPoints.length) + 1"
                      :y="yScaleSlots(p.occupied + p.free)"
                      :width="bandW - 2"
                      :height="yScaleSlots(p.occupied) - yScaleSlots(p.occupied + p.free)"
                      class="bar free"
                    />
                  </template>
                  <text class="tick" :x="-6" :y="yScaleSlots(maxSlots)" text-anchor="end" dominant-baseline="middle">{{ maxSlots }}</text>
                  <text class="tick" :x="-6" :y="yScaleSlots(Math.round(maxSlots/2))" text-anchor="end" dominant-baseline="middle">{{ Math.round(maxSlots/2) }}</text>
                  <text class="tick" :x="-6" :y="yScaleSlots(0)" text-anchor="end" dominant-baseline="middle">0</text>
                </g>
              </svg>
              <div class="legend">
                <div class="legend-item"><span class="swatch sw-occupied"></span>Occupied</div>
                <div class="legend-item"><span class="swatch sw-free"></span>Free</div>
              </div>
            </div>

            <!-- Confidence Histogram -->
            <div class="chart-card">
              <h4>Detection Confidence Distribution — model certainty histogram</h4>
              <svg :width="chartW" :height="chartH" class="svg-chart">
                <g :transform="`translate(${m.l},${m.t})`">
                  <line :x1="0" :y1="innerH" :x2="innerW" :y2="innerH" class="axis" />
                  <rect
                    v-for="(c, i) in confHist.counts"
                    :key="`h-${i}`"
                    :x="i * confBarW + 1"
                    :y="yScaleCounts(c)"
                    :width="confBarW - 2"
                    :height="innerH - yScaleCounts(c)"
                    class="bar conf"
                  />
                  <text class="tick" :x="-6" :y="yScaleCounts(confMax)" text-anchor="end" dominant-baseline="middle">{{ confMax }}</text>
                  <text class="tick" :x="-6" :y="yScaleCounts(Math.max(1, Math.round(confMax/2)))" text-anchor="end" dominant-baseline="middle">{{ Math.max(1, Math.round(confMax/2)) }}</text>
                  <text class="tick" :x="-6" :y="yScaleCounts(0)" text-anchor="end" dominant-baseline="middle">0</text>
                </g>
              </svg>
              <div class="axis-label">Confidence bins (0 → 1)</div>
            </div>
          </div>
        </div>

        <div class="refresh-section">
          <button @click="refreshAll" :disabled="loading" class="refresh-btn">
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
      showImage: false,
      history: [],
      chartW: 700,
      chartH: 280,
      m: { l: 45, r: 15, t: 15, b: 35 }
    }
  },
  computed: {
    innerW() { return this.chartW - this.m.l - this.m.r },
    innerH() { return this.chartH - this.m.t - this.m.b },

    trendPoints() {
      const N = Math.min(30, this.history.length)
      const items = this.history.slice(-N)
      return items.map(r => {
        const total = r.total_slots || (r.free_slots + r.occupied_slots) || 0
        const occRate = total > 0 ? (r.occupied_slots / total) : 0
        return { occRate: Math.max(0, Math.min(1, occRate)) }
      })
    },
    trendPolyline() {
      if (!this.trendPoints.length) return ''
      const n = this.trendPoints.length
      return this.trendPoints.map((p, i) => `${this.xScale(i, n)},${this.yScale01(p.occRate)}`).join(' ')
    },

    barPoints() {
      const N = Math.min(20, this.history.length)
      const items = this.history.slice(-N)
      return items.map(r => ({
        occupied: r.occupied_slots || 0,
        free: r.free_slots || 0,
        total: (r.total_slots || ((r.free_slots || 0) + (r.occupied_slots || 0))) || 0
      }))
    },
    maxSlots() {
      const vals = this.barPoints.map(p => p.total)
      return vals.length ? Math.max(...vals) : 0
    },
    bandW() {
      const n = this.barPoints.length || 1
      return this.innerW / n
    },

    confHist() {
      const bins = 10
      const counts = new Array(bins).fill(0)
      for (const r of this.history) {
        const c = Math.max(0, Math.min(0.999, r.confidence ?? 0))
        const idx = Math.floor(c * bins)
        counts[idx]++
      }
      return { bins, counts }
    },
    confMax() {
      return this.confHist.counts.length ? Math.max(...this.confHist.counts) : 0
    },
    confBarW() {
      const n = this.confHist.counts.length || 1
      return this.innerW / n
    }
  },
  async mounted() {
    await this.refreshAll()
  },
  methods: {
    async refreshAll() {
      this.loading = true
      try {
        await Promise.all([this.loadStats(), this.loadHistory()])
      } finally {
        this.loading = false
      }
    },

    async loadStats() {
      try {
        const response = await axios.get('/api/stats')
        this.stats = response.data
      } catch (error) {
        console.error('Error loading stats:', error)
        this.stats = null
      }
    },

    async loadHistory() {
      try {
        const response = await axios.get(`/api/history?limit=100`)
        this.history = response.data.results || []
      } catch (error) {
        console.error('Error loading history:', error)
        this.history = []
      }
    },

    xScale(i, n) {
      if (!n) return 0
      return (i / Math.max(1, n - 1)) * this.innerW
    },
    yScale01(v) {
      return (1 - v) * this.innerH
    },
    xBand(i, n) {
      if (!n) return 0
      return i * this.bandW
    },
    yScaleSlots(v) {
      const max = Math.max(1, this.maxSlots)
      return (1 - (v / max)) * this.innerH
    },
    yScaleCounts(v) {
      const max = Math.max(1, this.confMax)
      return (1 - (v / max)) * this.innerH
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
  margin-bottom: 2rem;
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

/* New charts */
.charts {
  margin-top: 1rem;
}
.charts-title {
  color: white;
  margin-bottom: 0.75rem;
  font-size: 1.3rem;
}
.charts-grid {
  display: grid;
  grid-template-columns: 1fr; /* stack charts vertically */
  gap: 1.25rem;
  margin-bottom: 2rem;
}
.chart-card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 1rem;
  color: white;
}
.chart-card h4 {
  margin-bottom: 0.5rem;
}
.svg-chart {
  background: rgba(0,0,0,0.2);
  border-radius: 10px;
}
.axis {
  stroke: rgba(255,255,255,0.6);
  stroke-width: 1;
}
.tick {
  fill: rgba(255,255,255,0.8);
  font-size: 0.75rem;
}
.axis-label {
  color: rgba(255,255,255,0.7);
  font-size: 0.85rem;
  margin-top: 0.4rem;
  text-align: center;
}
.line.occ-line {
  stroke: #74b9ff;
  stroke-width: 2;
}
.dot.occ-dot {
  fill: #74b9ff;
}
.bar.occupied {
  fill: rgba(231, 76, 60, 0.8);
}
.bar.free {
  fill: rgba(46, 204, 113, 0.85);
}
.bar.conf {
  fill: rgba(155, 89, 182, 0.85);
}
.legend {
  margin-top: 0.5rem;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  color: rgba(255,255,255,0.9);
}
.legend-item { display: flex; align-items: center; gap: 0.5rem; }
.swatch { width: 14px; height: 14px; border-radius: 3px; display: inline-block; }
.swatch.sw-occupied { background: rgba(231,76,60,0.8); }
.swatch.sw-free { background: rgba(46,204,113,0.85); }

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
