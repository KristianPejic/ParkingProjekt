<template>
  <div class="train">
    <div class="container">
      <div class="header">
        <h2>🧠 Classic Training Dashboard</h2>
        <p>Run a classic analysis over the dataset and visualize learned structure</p>
        <div class="controls">
          <label>Images to process</label>
          <input type="number" min="10" max="500" v-model.number="limit" />
          <button class="run-btn" :disabled="loading" @click="runTraining">
            <span v-if="loading">🔄 Running...</span>
            <span v-else>▶️ Run Training</span>
          </button>
        </div>
      </div>

      <div v-if="error" class="error">
        ❌ {{ error }}
      </div>

      <div v-if="result" class="results">
        <div class="cards">
          <div class="card">
            <div class="icon">🗂️</div>
            <div class="info">
              <div class="value">{{ result.dataset.total_images_found }}</div>
              <div class="label">Total Images Found</div>
            </div>
          </div>
          <div class="card">
            <div class="icon">⚙️</div>
            <div class="info">
              <div class="value">{{ result.dataset.processed_images }}</div>
              <div class="label">Processed</div>
            </div>
          </div>
          <div class="card">
            <div class="icon">🧩</div>
            <div class="info">
              <div class="value">{{ result.clusters.k }}</div>
              <div class="label">Clusters (KMeans)</div>
            </div>
          </div>
          <div class="card">
            <div class="icon">💡</div>
            <div class="info">
              <div class="value">{{ (result.features_summary.mean_white_ratio * 100).toFixed(1) }}%</div>
              <div class="label">Avg White Ratio</div>
            </div>
          </div>
        </div>

        <div class="charts">
          <div class="chart">
            <h3>White Ratio Histogram</h3>
            <svg :width="chartW" :height="chartH" class="svg-chart">
              <g :transform="`translate(${m.l},${m.t})`">
                <rect 
                  v-for="(c, i) in result.charts.histogram.counts" 
                  :key="i"
                  :x="xScale(i)"
                  :y="yScale(c)"
                  :width="barWidth - 2"
                  :height="chartInnerH - yScale(c)"
                  class="bar"
                />
                <line 
                  :x1="0" :y1="chartInnerH" 
                  :x2="chartInnerW" :y2="chartInnerH" 
                  class="axis"
                />
                <text 
                  v-for="tick in yTicks" :key="`yt${tick}`"
                  :x="-6" :y="yScale(tick)" text-anchor="end" dominant-baseline="middle" class="tick"
                >{{ tick }}</text>
              </g>
            </svg>
            <div class="axis-label">Bins (0 → 1 white ratio)</div>
          </div>

          <div class="chart">
            <h3>Scatter: White Ratio vs Edge Density</h3>
            <svg :width="chartW" :height="chartH" class="svg-chart">
              <g :transform="`translate(${m.l},${m.t})`">
                <circle 
                  v-for="(pt, i) in result.charts.scatter.points" 
                  :key="i"
                  :cx="scatterX(pt.x)"
                  :cy="scatterY(pt.y)"
                  r="4"
                  :class="`dot c${pt.c}`"
                />
                <line :x1="0" :y1="chartInnerH" :x2="chartInnerW" :y2="chartInnerH" class="axis" />
                <line :x1="0" :y1="0" :x2="0" :y2="chartInnerH" class="axis" />
                <text :x="chartInnerW/2" :y="chartInnerH + 30" text-anchor="middle" class="axis-title">White ratio</text>
                <text :x="-chartInnerH/2" :y="-35" transform="rotate(-90)" text-anchor="middle" class="axis-title">Edge density</text>
              </g>
            </svg>
            <div class="legend">
              <div v-for="(cnt, idx) in result.clusters.counts" :key="idx" class="legend-item">
                <span :class="`swatch c${idx}`"></span> Cluster {{ idx + 1 }} ({{ cnt }})
              </div>
            </div>
          </div>
        </div>

        <div class="centers">
          <h3>Cluster Centers</h3>
          <div class="center-grid">
            <div v-for="(c, i) in result.clusters.centers" :key="i" class="center-card">
              <div class="center-title">Cluster {{ i + 1 }}</div>
              <div class="center-row">
                <span>White ratio</span><span>{{ (c[0] * 100).toFixed(1) }}%</span>
              </div>
              <div class="center-row">
                <span>Edge density</span><span>{{ (c[1] * 100).toFixed(1) }}%</span>
              </div>
              <div class="center-row">
                <span>Brightness</span><span>{{ (c[2] * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>

      </div>

      <div v-else-if="!loading" class="placeholder">
        <p>Click "Run Training" to analyze the dataset.</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Train',
  data() {
    return {
      loading: false,
      error: null,
      result: null,
      limit: 50,

      // chart layout
      chartW: 700,
      chartH: 320,
      m: { l: 50, r: 20, t: 20, b: 40 }
    }
  },
  computed: {
    chartInnerW() { return this.chartW - this.m.l - this.m.r },
    chartInnerH() { return this.chartH - this.m.t - this.m.b },
    maxHist() {
      if (!this.result) return 0
      return Math.max(...this.result.charts.histogram.counts, 0)
    },
    barWidth() {
      if (!this.result) return 0
      const n = this.result.charts.histogram.counts.length
      return n ? this.chartInnerW / n : 0
    },
    yTicks() {
      const max = this.maxHist
      const step = Math.max(1, Math.round(max / 5))
      const ticks = []
      for (let v = 0; v <= max; v += step) ticks.push(v)
      return ticks
    }
  },
  methods: {
    async runTraining() {
      this.loading = true
      this.error = null
      this.result = null
      try {
        const res = await axios.get(`/api/train?limit=${this.limit}`)
        this.result = res.data
      } catch (e) {
        console.error(e)
        this.error = e?.response?.data?.detail || 'Training failed. Please try again.'
      } finally {
        this.loading = false
      }
    },
    // histogram scales
    xScale(i) {
      return i * this.barWidth
    },
    yScale(v) {
      const max = this.maxHist || 1
      const t = this.chartInnerH * (1 - (v / max))
      return t
    },
    // scatter scales (x,y in [0,1])
    scatterX(x) {
      return x * this.chartInnerW
    },
    scatterY(y) {
      return (1 - y) * this.chartInnerH
    }
  }
}
</script>

<style scoped>
.train {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 2rem;
}

.container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.header h2 {
  margin-bottom: 0.25rem;
}

.controls {
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
  justify-content: center;
  align-items: center;
}

.controls input {
  width: 90px;
  padding: 0.5rem;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.3);
  background: rgba(255,255,255,0.1);
  color: white;
  text-align: center;
}

.run-btn {
  background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 25px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}
.run-btn:hover:not(:disabled) { transform: translateY(-2px); }
.run-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.error {
  background: rgba(231, 76, 60, 0.2);
  border: 1px solid rgba(231, 76, 60, 0.5);
  border-radius: 10px;
  padding: 1rem;
  text-align: center;
  margin-bottom: 1rem;
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}
.card {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 15px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}
.card .icon { font-size: 2rem; }
.card .info .value { font-size: 1.6rem; font-weight: bold; }
.card .info .label { opacity: 0.8; font-size: 0.9rem; }

.charts {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.chart h3 {
  margin-bottom: 0.5rem;
}

.svg-chart {
  background: rgba(0,0,0,0.2);
  border-radius: 10px;
}

.bar {
  fill: url(#grad);
  fill: rgba(102, 126, 234, 0.9);
}

.axis {
  stroke: rgba(255,255,255,0.6);
  stroke-width: 1;
}

.tick {
  fill: rgba(255,255,255,0.8);
  font-size: 0.8rem;
}

.axis-label, .axis-title {
  color: rgba(255,255,255,0.8);
  font-size: 0.9rem;
  text-align: center;
  margin-top: 0.5rem;
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
.swatch.c0 { background: #ff7675; }
.swatch.c1 { background: #74b9ff; }
.swatch.c2 { background: #55efc4; }
.dot { opacity: 0.9; }
.dot.c0 { fill: #ff7675; }
.dot.c1 { fill: #74b9ff; }
.dot.c2 { fill: #55efc4; }

.centers {
  margin-top: 1rem;
}
.center-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}
.center-card {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 12px;
  padding: 1rem;
}
.center-title {
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.center-row {
  display: flex;
  justify-content: space-between;
  margin: 0.25rem 0;
  font-size: 0.95rem;
  color: rgba(255,255,255,0.9);
}

.placeholder {
  text-align: center;
  color: rgba(255,255,255,0.8);
}
</style>
