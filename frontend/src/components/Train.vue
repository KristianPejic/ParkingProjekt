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
            <div class="icon">❌</div>
            <div class="info">
              <div class="value">{{ result.dataset.failed_images }}</div>
              <div class="label">Failed</div>
            </div>
          </div>
          <div class="card">
            <div class="icon">📈</div>
            <div class="info">
              <div class="value">{{ (result.dataset.processing_success_rate || 0).toFixed(1) }}%</div>
              <div class="label">Success Rate</div>
            </div>
          </div>
          <div class="card">
            <div class="icon">🧠</div>
            <div class="info">
              <div class="value">{{ result.model_type }}</div>
              <div class="label">Model</div>
            </div>
          </div>
          <div class="card">
            <div class="icon">⭐</div>
            <div class="info">
              <div class="value">{{ (result.clustering_performance?.silhouette_score || 0).toFixed(3) }}</div>
              <div class="label">Silhouette Score</div>
            </div>
          </div>

          <!-- Coverage gauge -->
          <div class="card gauge-card">
            <div class="icon">📦</div>
            <div class="gauge-wrap">
              <svg :width="gSize" :height="gSize" class="gauge">
                <g :transform="`translate(${gSize/2},${gSize/2})`">
                  <circle :r="r" class="gauge-bg" />
                  <circle :r="r" class="gauge-fg" :style="gaugeStyle" />
                  <text x="0" y="6" class="gauge-text" text-anchor="middle">{{ (coverageRate*100).toFixed(0) }}%</text>
                </g>
              </svg>
              <div class="gauge-legend">
                <span class="gl p">{{ result.dataset.processed_images }}</span>
                <span class="sep">/</span>
                <span class="gl t">{{ result.dataset.total_images_found }}</span>
              </div>
              <div class="gauge-label">Dataset Coverage (processed/total)</div>
            </div>
          </div>
        </div>

        <div class="charts">
          <div class="chart">
            <h3>{{ h0Name }} Histogram</h3>
            <svg :width="chartW" :height="chartH" class="svg-chart">
              <g :transform="`translate(${m.l},${m.t})`">
                <rect 
                  v-for="(c, i) in h0Counts" 
                  :key="i"
                  :x="xScale(i)"
                  :y="yScaleH0(c)"
                  :width="barWidth - 2"
                  :height="chartInnerH - yScaleH0(c)"
                  class="bar"
                />
                <line :x1="0" :y1="chartInnerH" :x2="chartInnerW" :y2="chartInnerH" class="axis" />
                <text v-for="tick in h0Ticks" :key="`h0-${tick}`" :x="-6" :y="yScaleH0(tick)" text-anchor="end" dominant-baseline="middle" class="tick">{{ tick }}</text>
              </g>
            </svg>
            <div class="axis-label">Distribution of {{ h0Name }}</div>
          </div>

          <div class="chart">
            <h3>Scatter — PCA classical features (colored by cluster)</h3>
            <svg :width="chartW" :height="chartH" class="svg-chart">
              <g :transform="`translate(${m.l},${m.t})`">
                <circle 
                  v-for="(pt, i) in sPts" 
                  :key="i"
                  :cx="scatterX(pt.x)"
                  :cy="scatterY(pt.y)"
                  r="4"
                  :class="`dot c${(pt.cluster ?? 0)}`"
                />
                <line :x1="0" :y1="chartInnerH" :x2="chartInnerW" :y2="chartInnerH" class="axis" />
                <line :x1="0" :y1="0" :x2="0" :y2="chartInnerH" class="axis" />
                <text :x="chartInnerW/2" :y="chartInnerH + 30" text-anchor="middle" class="axis-title">PC1</text>
                <text :x="-chartInnerH/2" :y="-35" transform="rotate(-90)" text-anchor="middle" class="axis-title">PC2</text>
              </g>
            </svg>
            <div class="legend">
              <div v-for="(cnt, idx) in clusterCounts" :key="idx" class="legend-item">
                <span :class="`swatch c${idx}`"></span> Cluster {{ idx + 1 }} ({{ cnt }})
              </div>
            </div>
          </div>
        </div>

        <!-- New charts from training data -->
        <div class="charts">
          <!-- Cluster Distribution -->
          <div class="chart">
            <h3>Cluster Distribution — samples per KMeans cluster (scene types)</h3>
            <svg :width="chartW" :height="chartH" class="svg-chart">
              <g :transform="`translate(${m.l},${m.t})`">
                <line :x1="0" :y1="chartInnerH" :x2="chartInnerW" :y2="chartInnerH" class="axis" />
                <rect
                  v-for="(cnt, i) in clusterCounts"
                  :key="`cd-${i}`"
                  :x="i * cBarW + 4"
                  :y="yScaleCount(cnt)"
                  :width="cBarW - 8"
                  :height="chartInnerH - yScaleCount(cnt)"
                  class="bar cluster"
                />
                <text
                  v-for="(cnt, i) in clusterCounts"
                  :key="`cdt-${i}`"
                  :x="i * cBarW + cBarW/2"
                  :y="chartInnerH + 16"
                  text-anchor="middle"
                  class="tick"
                >C{{ i+1 }}</text>
                <text class="tick" :x="-6" :y="yScaleCount(cMax)" text-anchor="end" dominant-baseline="middle">{{ cMax }}</text>
                <text class="tick" :x="-6" :y="yScaleCount(Math.max(1, Math.round(cMax/2)))" text-anchor="end" dominant-baseline="middle">{{ Math.max(1, Math.round(cMax/2)) }}</text>
                <text class="tick" :x="-6" :y="yScaleCount(0)" text-anchor="end" dominant-baseline="middle">0</text>
              </g>
            </svg>
            <div class="axis-label">Counts per cluster</div>
          </div>

          <!-- Edge Density Histogram (from scatter points) -->
          <div class="chart">
            <h3>Edge Density Histogram — structure richness across dataset</h3>
            <svg :width="chartW" :height="chartH" class="svg-chart">
              <g :transform="`translate(${m.l},${m.t})`">
                <rect
                  v-for="(c, i) in edgeCounts"
                  :key="`eh-${i}`"
                  :x="i * eBarW"
                  :y="yScaleEdge(c)"
                  :width="eBarW - 2"
                  :height="chartInnerH - yScaleEdge(c)"
                  class="bar edge"
                />
                <line :x1="0" :y1="chartInnerH" :x2="chartInnerW" :y2="chartInnerH" class="axis" />
                <text class="tick" :x="-6" :y="yScaleEdge(edgeMax)" text-anchor="end" dominant-baseline="middle">{{ edgeMax }}</text>
                <text class="tick" :x="-6" :y="yScaleEdge(Math.max(1, Math.round(edgeMax/2)))" text-anchor="end" dominant-baseline="middle">{{ Math.max(1, Math.round(edgeMax/2)) }}</text>
                <text class="tick" :x="-6" :y="yScaleEdge(0)" text-anchor="end" dominant-baseline="middle">0</text>
              </g>
            </svg>
            <div class="axis-label">Bins (0 → 1 edge density)</div>
          </div>

          <!-- Grouped Bars: Cluster Centers -->
          <div class="chart">
            <h3>Feature Importance (Top 10)</h3>
            <svg :width="chartW" :height="chartH" class="svg-chart">
              <g :transform="`translate(${m.l},${m.t})`">
                <line :x1="0" :y1="chartInnerH" :x2="chartInnerW" :y2="chartInnerH" class="axis" />
                <template v-for="(imp, i) in featImp" :key="`fi-${i}`">
                  <rect
                    :x="i * fiBarW + 4"
                    :y="yScaleFI(imp.importance)"
                    :width="fiBarW - 8"
                    :height="chartInnerH - yScaleFI(imp.importance)"
                    class="bar"
                  />
                  <text :x="i * fiBarW + fiBarW/2" :y="chartInnerH + 16" text-anchor="middle" class="tick">{{ shortName(imp.feature) }}</text>
                </template>
                <text class="tick" :x="-6" :y="yScaleFI(fiMax)" text-anchor="end" dominant-baseline="middle">{{ fiMax.toFixed(2) }}</text>
                <text class="tick" :x="-6" :y="yScaleFI(Math.max(0, fiMax/2))" text-anchor="end" dominant-baseline="middle">{{ (fiMax/2).toFixed(2) }}</text>
                <text class="tick" :x="-6" :y="yScaleFI(0)" text-anchor="end" dominant-baseline="middle">0</text>
              </g>
            </svg>
          </div>
        </div>

        <div v-if="result && result.cluster_analysis && result.cluster_analysis.length" class="centers">
          <h3>Cluster Analysis</h3>
          <div class="table-wrap">
            <table class="tl-table">
              <thead>
                <tr>
                  <th>Cluster</th>
                  <th>Size</th>
                  <th>% of Data</th>
                  <th>Occupied Ratio</th>
                  <th>Mean White Ratio</th>
                  <th>Mean Edge Density</th>
                  <th>Mean Brightness</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in result.cluster_analysis" :key="row.cluster_id">
                  <td>#{{
                    (row.cluster_id ?? 0) + 1
                  }}</td>
                  <td>{{ row.size }}</td>
                  <td>{{ (row.percentage || 0).toFixed(1) }}%</td>
                  <td>{{ ((row.occupied_ratio || 0) * 100).toFixed(1) }}%</td>
                  <td>{{ ((row.mean_white_ratio || 0) * 100).toFixed(1) }}%</td>
                  <td>{{ ((row.mean_edge_density || 0) * 100).toFixed(1) }}%</td>
                  <td>{{ (row.mean_brightness || 0).toFixed(1) }}</td>
                </tr>
              </tbody>
            </table>
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
      m: { l: 50, r: 20, t: 20, b: 40 },

      // gauge
      gSize: 110
    }
  },
  computed: {
    chartInnerW() { return this.chartW - this.m.l - this.m.r },
    chartInnerH() { return this.chartH - this.m.t - this.m.b },

    // histogram 0 (first key feature) from visualizations
    h0() {
      return (this.result?.visualizations?.histograms && this.result.visualizations.histograms[0]) || { name: 'Histogram', counts: [] }
    },
    h0Name() { return this.h0?.name || 'Histogram' },
    h0Counts() { return this.h0?.counts || [] },
    h0Max() { return this.h0Counts.length ? Math.max(...this.h0Counts) : 0 },
    barWidth() {
      const n = this.h0Counts.length || 1
      return this.chartInnerW / n
    },
    h0Ticks() {
      const max = this.h0Max
      const step = Math.max(1, Math.round(max / 5))
      const ticks = []
      for (let v = 0; v <= max; v += step) ticks.push(v)
      return ticks
    },

    // coverage gauge
    coverageRate() {
      if (!this.result) return 0
      const p = this.result.dataset.processed_images || 0
      const t = this.result.dataset.total_images_found || 0
      return t > 0 ? p / t : 0
    },
    r() { return (this.gSize / 2) - 8 },
    circumference() { return 2 * Math.PI * this.r },
    gaugeStyle() {
      const dash = this.circumference
      const filled = dash * this.coverageRate
      const gap = dash - filled
      return {
        strokeDasharray: `${filled} ${gap}`,
        transform: 'rotate(-90deg)',
        transformOrigin: 'center'
      }
    },

    // cluster distribution using cluster_analysis sizes
    clusterCounts() {
      return (this.result?.cluster_analysis || []).map(c => Number(c?.size || 0))
    },
    cMax() {
      return this.clusterCounts.length ? Math.max(...this.clusterCounts) : 0
    },
    cBarW() {
      const n = this.clusterCounts.length || 1
      return this.chartInnerW / n
    },

    // edge density histogram (approximate from first scatter) – safe if missing
    edgeCounts() {
      if (!this.result) return []
      const pts = (this.result.visualizations?.scatter_plots?.[0]?.points) || []
      const values = pts.map(p => Number(p?.y || 0))
      if (!values.length) return []
      const bins = 20
      const min = Math.min(...values), max = Math.max(...values)
      const step = (max - min) || 1
      const counts = new Array(bins).fill(0)
      for (const v of values) {
        let idx = Math.floor(((v - min) / step) * bins)
        if (idx < 0) idx = 0
        if (idx >= bins) idx = bins - 1
        counts[idx]++
      }
      return counts
    },
    edgeMax() {
      return this.edgeCounts.length ? Math.max(...this.edgeCounts) : 0
    },
    eBarW() {
      const n = this.edgeCounts.length || 1
      return this.chartInnerW / n
    },

    // scatter points and domain
    sPts() {
      return (this.result?.visualizations?.scatter_plots?.[0]?.points) || []
    },
    sXmin() { return this.sPts.length ? Math.min(...this.sPts.map(p => Number(p?.x || 0))) : 0 },
    sXmax() { return this.sPts.length ? Math.max(...this.sPts.map(p => Number(p?.x || 1))) : 1 },
    sYmin() { return this.sPts.length ? Math.min(...this.sPts.map(p => Number(p?.y || 0))) : 0 },
    sYmax() { return this.sPts.length ? Math.max(...this.sPts.map(p => Number(p?.y || 1))) : 1 },

    // feature importance
    featImp() {
      return (this.result?.feature_importance || []).slice(0, 10)
    },
    fiMax() {
      return this.featImp.length ? Math.max(...this.featImp.map(i => Number(i?.importance || 0))) : 0
    },
    fiBarW() {
      const n = this.featImp.length || 1
      return this.chartInnerW / n
    }
  },
  methods: {
    async runTraining() {
      this.loading = true
      this.error = null
      this.result = null
      try {
        const params = { params: { limit: this.limit } }
        let res
        try {
          res = await axios.get('/train', params)
        } catch (e1) {
          try {
            res = await axios.get('/api/train', params)
          } catch (e2) {
            const detail = e2?.response?.data?.detail || e1?.response?.data?.detail
            throw new Error(detail || (e2?.message || e1?.message || 'Training failed. Please try again.'))
          }
        }
        this.result = res.data
        if (!this.result || this.result.success === false) {
          const msg = this.result?.message || 'Training returned no data.'
          throw new Error(msg)
        }
      } catch (e) {
        console.error(e)
        this.error = e?.message || 'Training failed. Please try again.'
      } finally {
        this.loading = false
      }
    },
    // histogram 0 scales
    xScale(i) {
      return i * this.barWidth
    },
    yScaleH0(v) {
      const max = this.h0Max || 1
      return this.chartInnerH * (1 - (v / max))
    },
    // scatter scales using PCA domain
    scatterX(x) {
      const min = this.sXmin, max = this.sXmax
      const t = (Number(x) - min) / Math.max(1e-9, (max - min))
      return t * this.chartInnerW
    },
    scatterY(y) {
      const min = this.sYmin, max = this.sYmax
      const t = (Number(y) - min) / Math.max(1e-9, (max - min))
      return (1 - t) * this.chartInnerH
    },
    // feature importance y scale
    yScaleFI(v) {
      const max = this.fiMax || 1
      return this.chartInnerH * (1 - (Number(v) / max))
    },
    shortName(s) {
      if (!s) return ''
      return String(s).replace(/_/g, ' ').slice(0, 12)
    },
    // counts scales
    yScaleCount(v) {
      const max = Math.max(1, this.cMax)
      return (1 - (v / max)) * this.chartInnerH
    },
    // edge hist counts
    yScaleEdge(v) {
      const max = Math.max(1, this.edgeMax)
      return (1 - (v / max)) * this.chartInnerH
    },
    // generic [0,1] scale
    yScale01(v) {
      return (1 - Math.max(0, Math.min(1, v))) * this.chartInnerH
    },
    // group x
    gX(i) {
      return i * this.gGroup
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
.gauge-card { align-items: center; gap: 0.75rem; }
.gauge-wrap { display: flex; align-items: center; gap: 0.75rem; }
.gauge {
  display: block;
}
.gauge-bg {
  fill: none;
  stroke: rgba(255,255,255,0.2);
  stroke-width: 10;
}
.gauge-fg {
  fill: none;
  stroke: #74b9ff;
  stroke-width: 10;
  stroke-linecap: round;
  transition: stroke-dasharray 0.6s ease;
}
.gauge-text { fill: white; font-weight: 600; font-size: 0.9rem; }
.gauge-legend { color: rgba(255,255,255,0.85); display: flex; align-items: center; gap: 0.25rem; }
.gauge-label { font-size: 0.8rem; opacity: 0.85; }
.gl.p { color: #74b9ff; }
.gl.t { color: #bbb; }
.sep { color: #777; }

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
  fill: rgba(102, 126, 234, 0.9);
}
.bar.cluster { fill: rgba(255, 159, 67, 0.9); }
.bar.edge { fill: rgba(52, 152, 219, 0.9); }
.bar.gb-f0 { fill: #6c5ce7; } /* white ratio */
.bar.gb-f1 { fill: #e17055; } /* edge density */
.bar.gb-f2 { fill: #9b59b6; } /* brightness */

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
.swatch.sw-wr { background: #6c5ce7; }
.swatch.sw-ed { background: #e17055; }
.swatch.sw-br { background: #9b59b6; }

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
