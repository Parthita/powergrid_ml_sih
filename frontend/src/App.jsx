import React, { useMemo, useState } from 'react'
import Papa from 'papaparse'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, ScatterChart, Scatter
} from 'recharts'

const COLORS = ['#e5e7eb', '#9ca3af', '#6b7280']

function readCsv(file) {
  return new Promise((resolve, reject) => {
    Papa.parse(file, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: ({ data }) => resolve(data),
      error: reject
    })
  })
}

function metric(value, label) {
  return (
    <div className="glass metric">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
    </div>
  )
}

export default function App() {
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')
  const [showIntro, setShowIntro] = useState(() => {
    try { return localStorage.getItem('pg_hide_intro') !== '1' } catch { return true }
  })

  const onUpload = async (e) => {
    setError('')
    const file = e.target.files?.[0]
    if (!file) return
    try {
      // Try API if available, fallback to local CSV parsing
      const fdata = new FormData()
      fdata.append('file', file)
      try {
        const res = await fetch('https://mlpowegridbackend-production.up.railway.app/predict', { method: 'POST', body: fdata })
        if (res.ok) {
          const json = await res.json()
          if (json?.rows?.length) {
            setRows(json.rows)
            return
          }
        }
      } catch (_) {}
      const data = await readCsv(file)
      setRows(data)
    } catch (err) {
      setError('Failed to parse CSV')
    }
  }

  const stats = useMemo(() => {
    if (!rows.length) return null
    const num = rows.length
    const avg = (arr) => arr.reduce((a, b) => a + (Number(b) || 0), 0) / (arr.length || 1)
    const costs = rows.map(r => Number(r.Predicted_Cost ?? r.TotalCost ?? 0)).filter(n => !Number.isNaN(n))
    const timelines = rows.map(r => Number(r.Predicted_Timeline ?? r.Timeline ?? 0)).filter(n => !Number.isNaN(n))
    const costOverruns = rows.map(r => Number(r.Cost_Overrun_Pct ?? 0)).filter(n => Number.isFinite(n))
    const timeOverruns = rows.map(r => Number(r.Timeline_Overrun_Pct ?? 0)).filter(n => Number.isFinite(n))
    const estCosts = rows.map(r => Number(r.EstimatedCost ?? r.TotalCost ?? 0)).filter(n => Number.isFinite(n))
    const estTimes = rows.map(r => Number(r.EstimatedTimeline ?? r.Timeline ?? 0)).filter(n => Number.isFinite(n))
    const deltasCost = rows.map(r => Number((r.Predicted_Cost ?? 0) - (r.EstimatedCost ?? r.TotalCost ?? 0))).filter(n => Number.isFinite(n))
    const deltasTime = rows.map(r => Number((r.Predicted_Timeline ?? 0) - (r.EstimatedTimeline ?? r.Timeline ?? 0))).filter(n => Number.isFinite(n))
    const diffPctCost = rows
      .map(r => {
        const est = Number(r.EstimatedCost ?? r.TotalCost)
        const pred = Number(r.Predicted_Cost ?? r.TotalCost)
        return Number.isFinite(est) && est !== 0 && Number.isFinite(pred) ? ((pred - est) / est) * 100 : null
      })
      .filter(v => v !== null)
    const diffPctTime = rows
      .map(r => {
        const est = Number(r.EstimatedTimeline ?? r.Timeline)
        const pred = Number(r.Predicted_Timeline ?? r.Timeline)
        return Number.isFinite(est) && est !== 0 && Number.isFinite(pred) ? ((pred - est) / est) * 100 : null
      })
      .filter(v => v !== null)
    const countPredCostAboveEst = rows.filter(r => {
      const est = Number(r.EstimatedCost ?? r.TotalCost)
      const pred = Number(r.Predicted_Cost ?? r.TotalCost)
      return Number.isFinite(est) && Number.isFinite(pred) && pred > est
    }).length
    const countPredTimeAboveEst = rows.filter(r => {
      const est = Number(r.EstimatedTimeline ?? r.Timeline)
      const pred = Number(r.Predicted_Timeline ?? r.Timeline)
      return Number.isFinite(est) && Number.isFinite(pred) && pred > est
    }).length
    return {
      total: num,
      avgCost: avg(costs),
      avgTimeline: avg(timelines),
      avgCostOverrun: avg(costOverruns),
      avgTimelineOverrun: avg(timeOverruns),
      avgEstimatedCost: avg(estCosts),
      avgEstimatedTimeline: avg(estTimes),
      avgCostDelta: avg(deltasCost),
      avgTimeDelta: avg(deltasTime),
      avgCostDiffPct: avg(diffPctCost),
      avgTimeDiffPct: avg(diffPctTime),
      countPredCostAboveEst,
      countPredTimeAboveEst,
      maxCost: costs.length ? Math.max(...costs) : 0,
      minCost: costs.length ? Math.min(...costs) : 0,
      maxTimeline: timelines.length ? Math.max(...timelines) : 0,
      minTimeline: timelines.length ? Math.min(...timelines) : 0
    }
  }, [rows])

  const costSeries = useMemo(() => rows.map((r, i) => ({
    x: i + 1,
    cost: Number(r.Predicted_Cost ?? r.TotalCost ?? 0)
  })), [rows])

  const timelineSeries = useMemo(() => rows.map((r, i) => ({
    x: i + 1,
    timeline: Number(r.Predicted_Timeline ?? r.Timeline ?? 0)
  })), [rows])

  const scatterSeries = useMemo(() => rows
    .filter(r => (r.Predicted_Cost ?? r.TotalCost) && (r.Predicted_Timeline ?? r.Timeline))
    .map(r => ({
      x: Number(r.Predicted_Cost ?? r.TotalCost),
      y: Number(r.Predicted_Timeline ?? r.Timeline),
      name: r.ProjectID ?? ''
    })), [rows])

  const riskCounts = useMemo(() => {
    const counts = {}
    rows.forEach(r => {
      const risk = r.Overall_Risk ?? 'Unknown'
      counts[risk] = (counts[risk] || 0) + 1
    })
    return Object.entries(counts).map(([name, value], i) => ({ name, value, color: COLORS[i % COLORS.length] }))
  }, [rows])

  const byProjectType = useMemo(() => {
    const map = {}
    rows.forEach(r => {
      const key = r.ProjectType ?? 'Unknown'
      const cost = Number(r.Predicted_Cost ?? r.TotalCost ?? 0)
      const tl = Number(r.Predicted_Timeline ?? r.Timeline ?? 0)
      const co = Number(r.Cost_Overrun_Pct ?? 0)
      const to = Number(r.Timeline_Overrun_Pct ?? 0)
      if (!map[key]) map[key] = { name: key, count: 0, sumCost: 0, sumTimeline: 0, sumCO: 0, sumTO: 0 }
      map[key].count += 1
      map[key].sumCost += Number.isFinite(cost) ? cost : 0
      map[key].sumTimeline += Number.isFinite(tl) ? tl : 0
      map[key].sumCO += Number.isFinite(co) ? co : 0
      map[key].sumTO += Number.isFinite(to) ? to : 0
    })
    return Object.values(map).map(d => ({
      name: d.name,
      avgCost: d.count ? d.sumCost / d.count : 0,
      avgTimeline: d.count ? d.sumTimeline / d.count : 0,
      avgCO: d.count ? d.sumCO / d.count : 0,
      avgTO: d.count ? d.sumTO / d.count : 0,
      count: d.count
    }))
  }, [rows])

  const byTerrain = useMemo(() => {
    const map = {}
    rows.forEach(r => {
      const key = r.Terrain ?? 'Unknown'
      const tl = Number(r.Predicted_Timeline ?? r.Timeline ?? 0)
      if (!map[key]) map[key] = { name: key, count: 0, sumTimeline: 0 }
      map[key].count += 1
      map[key].sumTimeline += Number.isFinite(tl) ? tl : 0
    })
    return Object.values(map).map(d => ({ name: d.name, avgTimeline: d.count ? d.sumTimeline / d.count : 0, count: d.count }))
  }, [rows])

  const topCost = useMemo(() => {
    const list = rows.map(r => ({
      ProjectID: r.ProjectID ?? '',
      ProjectType: r.ProjectType ?? '',
      cost: Number(r.Predicted_Cost ?? r.TotalCost ?? 0),
      timeline: Number(r.Predicted_Timeline ?? r.Timeline ?? 0),
      risk: r.Overall_Risk ?? ''
    }))
    return list.sort((a, b) => (b.cost - a.cost)).slice(0, 8)
  }, [rows])

  return (
    <div className="container">
      <div className="header">
        <h1 className="title">PowerGrid Dashboard</h1>
        <div className="subtitle">Minimal glassy black-and-white analytics</div>
      </div>

      {showIntro && (
        <div className="glass" style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', gap: 12 }}>
            <div>
              <div style={{ fontWeight: 600, marginBottom: 8 }}>How to use (one-time)</div>
              <div style={{ color: '#9ca3af', lineHeight: 1.6 }}>
                <p>Upload a CSV with these columns:</p>
                <ul style={{ margin: '6px 0 10px 18px' }}>
                  <li>ProjectID, ProjectType, Terrain, WeatherImpact, DemandSupply, Vendor</li>
                  <li>EstimatedCost, EstimatedTimeline (recommended baselines)</li>
                  <li>Optional drivers: Resources, ProjectLength, RegulatoryTime, HistoricalDelay, StartMonth</li>
                  <li>VendorOnTimeRate, VendorAvgDelay; RegulatoryPermitDays, PermitVariance</li>
                  <li>WeatherSeverityIndex, MaterialAvailabilityIndex, ResourceUtilization</li>
                  <li>HindranceCounts, HindranceRecentDays, MaterialCost, LabourCost</li>
                </ul>
                <p>Charts explain:</p>
                <ul style={{ margin: '6px 0 0 18px' }}>
                  <li>Trends: Predicted cost and timeline across projects</li>
                  <li>Risk: Distribution by Overall_Risk</li>
                  <li>Scatter: Cost vs Timeline</li>
                  <li>Overruns: Percent series and averages by type</li>
                </ul>
              </div>
            </div>
            <button className="btn" onClick={() => { try { localStorage.setItem('pg_hide_intro', '1') } catch{}; setShowIntro(false) }}>Got it</button>
          </div>
        </div>
      )}

      <div className="glass upload">
        <input id="csv-upload" type="file" accept=".csv,text/csv" onChange={onUpload} style={{ display: 'none' }} />
        <label htmlFor="csv-upload" className="btn">Choose CSV File</label>
        <div className="hint">Upload any of the CSVs in test_csvs/ to preview charts</div>
        {error && <div style={{ color: '#ef4444', marginTop: 8 }}>{error}</div>}
      </div>

      {!!rows.length && (
        <>
          <div className="grid grid-4" style={{ marginTop: 16 }}>
            {metric(stats.total, 'Total Projects')}
            {metric(`₹${stats.avgCost.toFixed(1)}L`, 'Average Cost')}
            {metric(`${stats.avgTimeline.toFixed(1)} mo`, 'Average Timeline')}
            {metric((rows.filter(r => (r.Overall_Risk ?? '').toLowerCase() === 'high').length), 'High Risk')}
          </div>

          <div className="grid grid-4" style={{ marginTop: 8 }}>
            {metric(`₹${stats.maxCost.toFixed(1)}L`, 'Max Cost')}
            {metric(`₹${stats.minCost.toFixed(1)}L`, 'Min Cost')}
            {metric(`${stats.maxTimeline.toFixed(1)} mo`, 'Max Timeline')}
            {metric(`${stats.minTimeline.toFixed(1)} mo`, 'Min Timeline')}
          </div>

          <div className="grid grid-2" style={{ marginTop: 8 }}>
            {metric(`${stats.avgCostOverrun.toFixed(1)}%`, 'Avg Cost Overrun')}
            {metric(`${stats.avgTimelineOverrun.toFixed(1)}%`, 'Avg Timeline Overrun')}
          </div>

          <div className="grid grid-4" style={{ marginTop: 8 }}>
            {metric(`₹${stats.avgEstimatedCost.toFixed(1)}L`, 'Avg Estimated Cost')}
            {metric(`${stats.avgEstimatedTimeline.toFixed(1)} mo`, 'Avg Estimated Timeline')}
            {metric(`₹${stats.avgCostDelta.toFixed(1)}L`, 'Avg Cost Delta (Pred-Est)')}
            {metric(`${stats.avgTimeDelta.toFixed(1)} mo`, 'Avg Time Delta (Pred-Est)')}
          </div>

          <div className="grid grid-4" style={{ marginTop: 8 }}>
            {metric(`${stats.avgCostDiffPct.toFixed(1)}%`, 'Avg Cost (Pred-Est) %')}
            {metric(`${stats.avgTimeDiffPct.toFixed(1)}%`, 'Avg Timeline (Pred-Est) %')}
            {metric(stats.countPredCostAboveEst, 'Projects: Pred Cost > Est')}
            {metric(stats.countPredTimeAboveEst, 'Projects: Pred Time > Est')}
          </div>

          <div className="grid grid-2" style={{ marginTop: 16 }}>
            <div className="glass">
              <div style={{ marginBottom: 8, color: '#9ca3af' }}>Cost Trend</div>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={costSeries}>
                  <CartesianGrid stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="x" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip />
                  <Line type="monotone" dataKey="cost" stroke="#e5e7eb" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="glass">
              <div style={{ marginBottom: 8, color: '#9ca3af' }}>Timeline Trend</div>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={timelineSeries}>
                  <CartesianGrid stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="x" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip />
                  <Line type="monotone" dataKey="timeline" stroke="#9ca3af" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-2" style={{ marginTop: 16 }}>
            <div className="glass">
              <div style={{ marginBottom: 8, color: '#9ca3af' }}>Risk Distribution</div>
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie data={riskCounts} dataKey="value" nameKey="name" outerRadius={90}>
                    {riskCounts.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="glass">
              <div style={{ marginBottom: 8, color: '#9ca3af' }}>Cost vs Timeline</div>
              <ResponsiveContainer width="100%" height={260}>
                <ScatterChart>
                  <CartesianGrid stroke="rgba(255,255,255,0.08)" />
                  <XAxis type="number" dataKey="x" name="Cost" stroke="#9ca3af" />
                  <YAxis type="number" dataKey="y" name="Timeline" stroke="#9ca3af" />
                  <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                  <Scatter data={scatterSeries} fill="#e5e7eb" />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-2" style={{ marginTop: 16 }}>
            <div className="glass">
              <div style={{ marginBottom: 8, color: '#9ca3af' }}>Cost Overrun % Series</div>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={[...rows].map((r, i) => ({ x: i + 1, v: Number(r.Cost_Overrun_Pct ?? 0) }))}>
                  <CartesianGrid stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="x" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip />
                  <Line type="monotone" dataKey="v" stroke="#ffffff" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="glass">
              <div style={{ marginBottom: 8, color: '#9ca3af' }}>Timeline Overrun % Series</div>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={[...rows].map((r, i) => ({ x: i + 1, v: Number(r.Timeline_Overrun_Pct ?? 0) }))}>
                  <CartesianGrid stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="x" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip />
                  <Line type="monotone" dataKey="v" stroke="#9ca3af" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="grid grid-2" style={{ marginTop: 16 }}>
            <div className="glass">
              <div style={{ marginBottom: 8, color: '#9ca3af' }}>Average Cost by Project Type</div>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={byProjectType}>
                  <CartesianGrid stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="name" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip />
                  <Line type="monotone" dataKey="avgCost" stroke="#ffffff" strokeWidth={2} dot />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="glass">
              <div style={{ marginBottom: 8, color: '#9ca3af' }}>Average Timeline by Terrain</div>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={byTerrain}>
                  <CartesianGrid stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="name" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip />
                  <Line type="monotone" dataKey="avgTimeline" stroke="#9ca3af" strokeWidth={2} dot />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass" style={{ marginTop: 16 }}>
            <div style={{ marginBottom: 8, color: '#9ca3af' }}>Average Overrun % by Project Type</div>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={byProjectType}>
                <CartesianGrid stroke="rgba(255,255,255,0.08)" />
                <XAxis dataKey="name" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip />
                <Line type="monotone" dataKey="avgCO" stroke="#e5e7eb" strokeWidth={2} dot />
                <Line type="monotone" dataKey="avgTO" stroke="#9ca3af" strokeWidth={2} dot />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="glass" style={{ marginTop: 16 }}>
            <div style={{ marginBottom: 8, color: '#9ca3af' }}>Project Details</div>
            <div style={{ overflowX: 'auto' }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Project ID</th>
                    <th>Type</th>
                    <th>Est. Cost</th>
                    <th>Cost</th>
                    <th>Est. Timeline</th>
                    <th>Timeline</th>
                    <th>Cost Overrun %</th>
                    <th>Timeline Overrun %</th>
                    <th>Cost Escalation</th>
                    <th>Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r, i) => (
                    <tr key={i}>
                      <td>{r.ProjectID ?? ''}</td>
                      <td>{r.ProjectType ?? ''}</td>
                      <td>{Number((r.EstimatedCost ?? r.TotalCost) ?? 0).toFixed(2)}</td>
                      <td>{Number(r.Predicted_Cost ?? r.TotalCost ?? 0).toFixed(2)}</td>
                      <td>{Number((r.EstimatedTimeline ?? r.Timeline) ?? 0).toFixed(1)}</td>
                      <td>{Number(r.Predicted_Timeline ?? r.Timeline ?? 0).toFixed(1)}</td>
                      <td>{Number(r.Cost_Overrun_Pct ?? 0).toFixed(1)}</td>
                      <td>{Number(r.Timeline_Overrun_Pct ?? 0).toFixed(1)}</td>
                      <td>{Number(r.CostEscalation ?? 0).toFixed(1)}</td>
                      <td>{r.Overall_Risk ?? ''}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid grid-2" style={{ marginTop: 16, marginBottom: 24 }}>
            <div className="glass">
              <div style={{ marginBottom: 8, color: '#9ca3af' }}>Top Cost Projects</div>
              <div style={{ overflowX: 'auto' }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Project ID</th>
                      <th>Type</th>
                      <th>Cost</th>
                      <th>Timeline</th>
                      <th>Risk</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topCost.map((r, i) => (
                      <tr key={i}>
                        <td>{r.ProjectID}</td>
                        <td>{r.ProjectType}</td>
                        <td>{r.cost.toFixed(2)}</td>
                        <td>{r.timeline.toFixed(1)}</td>
                        <td>{r.risk}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            <div className="glass">
              <div style={{ marginBottom: 8, color: '#9ca3af' }}>Reading the Dashboard</div>
              <div style={{ color: 'var(--muted)', lineHeight: 1.6 }}>
                <p>Upload a CSV with columns such as ProjectID, ProjectType, TotalCost, Timeline. If Predicted_Cost/Predicted_Timeline exist, those are used; otherwise we fall back to TotalCost/Timeline.</p>
                <p>Cost Trend and Timeline Trend show simple ordered series to visualize spread and volatility. The Risk Distribution pie is driven by the Overall_Risk column if present.</p>
                <p>Average breakdown plots help compare categories at a glance. The Top Cost table highlights the highest-cost projects for quick triage.</p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}


